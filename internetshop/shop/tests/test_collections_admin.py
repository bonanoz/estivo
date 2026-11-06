"""E1: админка справочников, инлайн вариантов, фильтры, скидка, заявка (R1.1-R1.4, R3.3 в админке)."""
from django.contrib import admin
from django.contrib.admin import TabularInline
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from shop import models as m
from shop.models import Order, OrderItem, Product

from .helpers import make_product, squash
from .helpers_collections import add_variants, collection, product_in, tabletop, zone


class AdminTestCase(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_superuser('boss', 'boss@example.com', 'pw-for-tests-123')
        self.client.force_login(user)


def product_form(**extra):
    form = {
        'name': 'Стол Новара', 'slug': '', 'sku': '', 'short_description': '', 'description': 'Описание',
        'price': '15000', 'max_load_kg': '120', 'warranty_years': '3', 'is_available': 'on',
        'gallery-TOTAL_FORMS': '0', 'gallery-INITIAL_FORMS': '0',
        'gallery-MIN_NUM_FORMS': '0', 'gallery-MAX_NUM_FORMS': '1000',
    }
    form.update(extra)
    return form


def variants_formset(rows, initial=0):
    """rows: [(size, tabletop_id|'', price, order)] -> поля инлайна variants-*."""
    data = {
        'variants-TOTAL_FORMS': str(len(rows)), 'variants-INITIAL_FORMS': str(initial),
        'variants-MIN_NUM_FORMS': '0', 'variants-MAX_NUM_FORMS': '1000',
    }
    for i, (size, top, price, order) in enumerate(rows):
        data.update({f'variants-{i}-size': size, f'variants-{i}-tabletop': str(top),
                     f'variants-{i}-price': str(price), f'variants-{i}-order': str(order)})
    return data


def errors_of(resp):
    return getattr(resp, 'context', None) and resp.context['adminform'].form.errors


class E1AdminRegistrationTests(AdminTestCase):
    def test_r11_reference_models_registered(self):
        self.assertIn(m.Zone, admin.site._registry)
        self.assertIn(m.TabletopType, admin.site._registry)

    def test_r12_product_admin_has_collections_zone_and_filters(self):
        pa = admin.site._registry[Product]
        self.assertIn('collections', pa.filter_horizontal)
        self.assertIn('collections', pa.list_filter)
        self.assertIn('zone', pa.list_filter)
        self.assertNotIn('collection', pa.list_filter)

    def test_r13_product_admin_has_variant_inline(self):
        pa = admin.site._registry[Product]
        inlines = [i for i in pa.inlines if i.model is m.ProductVariant]
        self.assertEqual(len(inlines), 1)
        self.assertTrue(issubclass(inlines[0], TabularInline))

    def test_r12_changelist_filters_by_collection_and_zone(self):
        milan, bari = collection('Милан'), collection('Бари')
        lounge = zone('Лаунж-зона')
        a = product_in(collections=[milan], zone_obj=lounge, name='Диван Милан тест')
        b = product_in(collections=[bari], name='Стол Бари тест')
        for query, expected in ((f'collections__id__exact={milan.pk}', a), (f'zone__id__exact={lounge.pk}', a),
                                (f'collections__id__exact={bari.pk}', b)):
            with self.subTest(query=query):
                resp = self.client.get(f'/admin/shop/product/?{query}')
                self.assertEqual(resp.status_code, 200)
                self.assertEqual(list(resp.context['cl'].result_list), [expected])


class E1AdminReferenceTests(AdminTestCase):
    def test_r11_zone_with_empty_slug_gets_latin_slug(self):
        resp = self.client.post(reverse('admin:shop_zone_add'), {'name': 'Барная зона', 'slug': '', 'order': '0'})
        self.assertEqual(resp.status_code, 302, errors_of(resp))
        self.assertEqual(m.Zone.objects.get(name='Барная зона').slug, 'barnaya-zona')

    def test_r11_duplicate_zone_slug_shows_error_at_field(self):
        m.Zone.objects.create(name='Первая зона', slug='odna')
        resp = self.client.post(reverse('admin:shop_zone_add'), {'name': 'Вторая зона', 'slug': 'odna', 'order': '0'})
        self.assertEqual(resp.status_code, 200)
        self.assertIn('slug', resp.context['adminform'].form.errors)
        self.assertFalse(m.Zone.objects.filter(name='Вторая зона').exists())

    def test_r11_empty_slug_taken_by_name_shows_error_not_500(self):
        m.Zone.objects.create(name='Другая', slug='barnaya-zona')
        resp = self.client.post(reverse('admin:shop_zone_add'), {'name': 'Барная зона', 'slug': '', 'order': '0'})
        self.assertEqual(resp.status_code, 200)
        self.assertIn('slug', resp.context['adminform'].form.errors)

    def test_r11_tabletop_added_in_admin_is_available_in_variant_form(self):
        resp = self.client.post(reverse('admin:shop_tabletoptype_add'), {'name': 'Керамика', 'order': '5'})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(m.TabletopType.objects.get(name='Керамика').order, 5)
        p = make_product(price=1000)
        resp = self.client.get(reverse('admin:shop_product_change', args=[p.pk]))
        self.assertContains(resp, 'Керамика')


class E1AdminProductVariantsTests(AdminTestCase):
    def setUp(self):
        super().setUp()
        self.glass, self.hpl = tabletop('Стекло'), tabletop('HPL compact')

    def rows(self):
        return [('80×80 см', self.hpl.pk, 29900, 0), ('160×90 см', self.glass.pk, 54900, 1),
                ('160×90 см', self.hpl.pk, 44900, 2)]

    def post_new(self, rows, **extra):
        return self.client.post(reverse('admin:shop_product_add'),
                                {**product_form(**extra), **variants_formset(rows)})

    def test_r12_product_saved_with_two_collections_and_zone(self):
        milan, bari, lounge = collection('Милан'), collection('Бари'), zone('Лаунж-зона')
        resp = self.post_new([], collections=[milan.pk, bari.pk], zone=lounge.pk)
        self.assertEqual(resp.status_code, 302, errors_of(resp))
        p = Product.objects.get(name='Стол Новара')
        self.assertEqual(set(p.collections.all()), {milan, bari})
        self.assertEqual(p.zone, lounge)

    def test_r12_product_saved_without_collections_and_zone(self):
        resp = self.post_new([])
        self.assertEqual(resp.status_code, 302, errors_of(resp))
        p = Product.objects.get(name='Стол Новара')
        self.assertEqual(p.collections.count(), 0)
        self.assertIsNone(p.zone)

    def test_r13_three_variants_saved_and_price_is_minimum(self):
        resp = self.post_new(self.rows())
        self.assertEqual(resp.status_code, 302, errors_of(resp))
        p = Product.objects.get(name='Стол Новара')
        self.assertEqual(p.variants.count(), 3)
        self.assertEqual(p.price, 29900)

    def test_r14_manual_price_is_overwritten_by_variants_minimum(self):
        self.post_new(self.rows(), price='1000')
        self.assertEqual(Product.objects.get(name='Стол Новара').price, 29900)

    def test_r14_catalog_shows_price_from_minimum(self):
        self.post_new([('160×90 см', self.glass.pk, 54900, 0), ('160×90 см', self.hpl.pk, 44900, 1)])
        html = self.client.get(reverse('catalog_list')).content.decode()
        self.assertIn('44900', squash(html))

    def test_r13_empty_size_rejected(self):
        resp = self.post_new([('', self.glass.pk, 54900, 0)])
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(m.ProductVariant.objects.count(), 0)
        self.assertEqual(Product.objects.count(), 0)

    def test_r13_zero_price_rejected(self):
        resp = self.post_new([('160×90 см', self.glass.pk, 0, 0)])
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(m.ProductVariant.objects.count(), 0)

    def test_r13_empty_price_rejected(self):
        resp = self.post_new([('160×90 см', self.glass.pk, '', 0)])
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(m.ProductVariant.objects.count(), 0)

    def test_r13_duplicate_size_and_tabletop_rejected_nothing_saved(self):
        resp = self.post_new([('160×90 см', self.glass.pk, 54900, 0), ('160×90 см', self.glass.pk, 60000, 1)])
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(m.ProductVariant.objects.count(), 0)
        self.assertEqual(Product.objects.count(), 0)

    def test_r13_variant_without_tabletop_is_accepted(self):
        resp = self.post_new([('Ø 55 см', '', 12000, 0)])
        self.assertEqual(resp.status_code, 302, errors_of(resp))
        self.assertIsNone(m.ProductVariant.objects.get().tabletop)

    def test_r14_deleting_cheapest_variant_in_admin_raises_price(self):
        p = make_product(price=1000)
        cheap, dear = add_variants(p, [('A', None, 44900), ('B', None, 54900)])
        form = {**product_form(name=p.name, slug=p.slug, price='44900'),
                **variants_formset([('A', '', 44900, 0), ('B', '', 54900, 1)], initial=2),
                'variants-0-id': cheap.pk, 'variants-1-id': dear.pk,
                'variants-0-product': p.pk, 'variants-1-product': p.pk, 'variants-0-DELETE': 'on'}
        resp = self.client.post(reverse('admin:shop_product_change', args=[p.pk]), form)
        self.assertEqual(resp.status_code, 302, errors_of(resp))
        p.refresh_from_db()
        self.assertEqual(p.variants.count(), 1)
        self.assertEqual(p.price, 54900)


class E1AdminEnableSaleTests(AdminTestCase):
    def act(self, *products):
        return self.client.post('/admin/shop/product/', {
            'action': 'enable_sale', '_selected_action': [p.pk for p in products]}, follow=True)

    def test_r14_enable_sale_skips_products_with_variants(self):
        p = make_product(price=1000, sale_price=500)
        add_variants(p, [('A', None, 44900)])
        self.act(p)
        p.refresh_from_db()
        self.assertEqual((p.price, p.old_price), (44900, None))

    def test_r14_enable_sale_still_works_for_plain_products(self):
        variant_product = make_product(price=1000, sale_price=500)
        add_variants(variant_product, [('A', None, 44900)])
        plain = make_product(price=28900, sale_price=6900)
        self.act(variant_product, plain)
        plain.refresh_from_db()
        self.assertEqual((plain.price, plain.old_price, plain.sale_price), (6900, 28900, None))


class E1AdminOrderVariantTests(AdminTestCase):
    def make_order(self):
        table = make_product(price=1000)
        variant = add_variants(table, [('160×90 см', 'Стекло', 54900)])[0]
        order = Order.objects.create(customer_name='Иван', customer_phone='+7 900 123-45-67', total_price=54900)
        OrderItem.objects.create(
            order=order, product=table, quantity=1, unit_price=54900,
            selected_colors={'Размер': '160×90 см', 'Столешница': 'Стекло', 'Плетение': 'Графит'})
        return order, variant

    def page(self, order):
        resp = self.client.get(reverse('admin:shop_order_change', args=[order.pk]))
        self.assertEqual(resp.status_code, 200)
        return resp.content.decode()

    def test_r33_order_item_shows_buyer_choice_and_price(self):
        order, _ = self.make_order()
        html = self.page(order)
        self.assertIn('Выбор покупателя', html)
        for text in ('Размер', '160×90 см', 'Столешница', 'Стекло', 'Графит'):
            self.assertIn(text, html)
        self.assertIn('54900', squash(html))

    def test_r33_order_opens_and_keeps_choice_after_variant_deleted(self):
        order, variant = self.make_order()
        variant.delete()
        html = self.page(order)
        self.assertIn('160×90 см', html)
        self.assertIn('54900', squash(html))
