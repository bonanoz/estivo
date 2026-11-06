"""E1: модели Zone, TabletopType, ProductVariant, Product.zone/collections, цена «от» по вариантам (R1.1-R1.4)."""
from django.core.exceptions import FieldDoesNotExist, ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from shop import models as m
from shop.models import Product

from .helpers import make_product
from .helpers_collections import add_variants, collection, product_in, tabletop


class E1ReferenceTests(TestCase):
    def test_r11_zone_slug_from_name(self):
        z = m.Zone.objects.create(name='Барная зона')
        self.assertEqual(z.slug, 'barnaya-zona')

    def test_r11_zone_slug_is_unique(self):
        m.Zone.objects.create(name='Первая', slug='odna')
        with self.assertRaises(IntegrityError), transaction.atomic():
            m.Zone.objects.create(name='Вторая', slug='odna')

    def test_r11_zones_and_tabletops_ordered_by_order_field(self):
        b = m.Zone.objects.create(name='Б зона', order=50)
        a = m.Zone.objects.create(name='Я зона', order=40)
        zones = [z for z in m.Zone.objects.all() if z.pk in (a.pk, b.pk)]
        self.assertEqual(zones, [a, b])
        t2 = m.TabletopType.objects.create(name='Тест Б', order=60)
        t1 = m.TabletopType.objects.create(name='Тест Я', order=55)
        tops = [t for t in m.TabletopType.objects.all() if t.pk in (t1.pk, t2.pk)]
        self.assertEqual(tops, [t1, t2])

    def test_r11_new_tabletop_is_usable_in_any_variant(self):
        ceramic = m.TabletopType.objects.create(name='Керамика')
        product = make_product(price=1000)
        variant = m.ProductVariant.objects.create(product=product, size='120×80 см', tabletop=ceramic, price=39900)
        self.assertEqual(variant.tabletop.name, 'Керамика')


class E1ProductCollectionsTests(TestCase):
    def test_r12_old_collection_fk_is_gone(self):
        with self.assertRaises(FieldDoesNotExist):
            Product._meta.get_field('collection')

    def test_r12_product_in_two_collections(self):
        milan, bari = collection('Милан'), collection('Бари')
        table = product_in(collections=[milan, bari], name='Стол Новара')
        self.assertEqual(set(table.collections.all()), {milan, bari})
        self.assertIn(table, milan.products.all())
        self.assertIn(table, bari.products.all())

    def test_r12_product_without_collections_and_zone_is_valid(self):
        p = make_product()
        self.assertEqual(p.collections.count(), 0)
        self.assertIsNone(p.zone)

    def test_r12_deleting_zone_keeps_products_with_empty_zone(self):
        lounge = m.Zone.objects.create(name='Лаунж-зона тест')
        p = product_in(zone_obj=lounge)
        lounge.delete()
        p.refresh_from_db()
        self.assertIsNone(p.zone)

    def test_r12_deleting_collection_keeps_products_and_other_collections(self):
        milan, bari = collection('Милан'), collection('Бари')
        p = product_in(collections=[milan, bari], is_available=True)
        milan.delete()
        p.refresh_from_db()
        self.assertTrue(p.is_available)
        self.assertEqual(list(p.collections.all()), [bari])

    def test_r12_zone_is_single_valued(self):
        self.assertFalse(Product._meta.get_field('zone').many_to_many)
        self.assertTrue(Product._meta.get_field('collections').many_to_many)


class E1VariantFieldsTests(TestCase):
    def setUp(self):
        self.product = make_product(price=1000)

    def variant(self, **kw):
        kw = {'product': self.product, 'size': '160×90 см', 'price': 54900, **kw}
        return m.ProductVariant(**kw)

    def test_r13_three_variants_saved(self):
        add_variants(self.product)
        self.assertEqual(self.product.variants.count(), 3)

    def test_r13_variants_follow_order_field(self):
        v1, v2, v3 = add_variants(self.product)
        v3.order, v1.order = -1, 5
        v3.save()
        v1.save()
        self.assertEqual(list(self.product.variants.all()), [v3, v2, v1])

    def test_r13_tabletop_is_optional(self):
        v = self.variant(tabletop=None)
        v.full_clean()
        v.save()
        self.assertIsNone(v.tabletop)

    def test_r13_empty_size_is_rejected(self):
        with self.assertRaises(ValidationError) as ctx:
            self.variant(size='').full_clean()
        self.assertIn('size', ctx.exception.message_dict)

    def test_r13_zero_price_is_rejected(self):
        with self.assertRaises(ValidationError) as ctx:
            self.variant(price=0).full_clean()
        self.assertIn('price', ctx.exception.message_dict)

    def test_r13_negative_price_is_rejected(self):
        with self.assertRaises(ValidationError) as ctx:
            self.variant(price=-5).full_clean()
        self.assertIn('price', ctx.exception.message_dict)

    def test_r13_empty_price_is_rejected(self):
        with self.assertRaises(ValidationError) as ctx:
            self.variant(price=None).full_clean()
        self.assertIn('price', ctx.exception.message_dict)

    def test_r13_duplicate_size_and_tabletop_is_rejected(self):
        glass = tabletop('Стекло')
        self.variant(tabletop=glass).save()
        with self.assertRaises(ValidationError):
            self.variant(tabletop=glass, price=60000).full_clean()

    def test_r13_same_size_with_other_tabletop_is_allowed(self):
        self.variant(tabletop=tabletop('Стекло')).save()
        other = self.variant(tabletop=tabletop('HPL compact'), price=44900)
        other.full_clean()
        other.save()
        self.assertEqual(self.product.variants.count(), 2)

    def test_r13_same_size_for_another_product_is_allowed(self):
        glass = tabletop('Стекло')
        self.variant(tabletop=glass).save()
        other_product = make_product(price=1000)
        self.variant(product=other_product, tabletop=glass).full_clean()


class E1PriceFromVariantsTests(TestCase):
    def setUp(self):
        self.product = make_product(price=1000)

    def price(self):
        return Product.objects.get(pk=self.product.pk).price

    def test_r14_price_is_minimum_of_variants(self):
        add_variants(self.product, [('A', None, 54900), ('B', None, 44900)])
        self.assertEqual(self.price(), 44900)

    def test_r14_price_follows_each_added_variant(self):
        add_variants(self.product, [('A', None, 54900)])
        self.assertEqual(self.price(), 54900)
        m.ProductVariant.objects.create(product=self.product, size='B', price=29900)
        self.assertEqual(self.price(), 29900)

    def test_r14_deleting_cheapest_raises_price(self):
        cheap, _dear = add_variants(self.product, [('A', None, 44900), ('B', None, 54900)])
        cheap.delete()
        self.assertEqual(self.price(), 54900)

    def test_r14_editing_variant_price_recalculates(self):
        a, b = add_variants(self.product, [('A', None, 44900), ('B', None, 54900)])
        a.price = 70000
        a.save()
        self.assertEqual(self.price(), 54900)
        b.price = 10000
        b.save()
        self.assertEqual(self.price(), 10000)

    def test_r14_deleting_all_variants_keeps_last_computed_price(self):
        only, = add_variants(self.product, [('A', None, 44900)])
        only.delete()
        self.assertEqual(self.price(), 44900)

    def test_r14_product_without_variants_keeps_its_price(self):
        self.product.save()
        self.assertEqual(self.price(), 1000)

    def test_r14_other_products_price_is_untouched(self):
        other = make_product(price=777)
        add_variants(self.product, [('A', None, 44900)])
        other.refresh_from_db()
        self.assertEqual(other.price, 777)
