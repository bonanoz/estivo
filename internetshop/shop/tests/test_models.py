"""E2: new model fields, Product.badges, migrations, admin, seed_demo, 404 bestsellers context."""
from io import StringIO

from django.contrib import admin
from django.core.management import call_command
from django.test import TestCase

from shop.models import Product, SiteSettings

from .helpers import make_product


def badges_of(product):
    badges = product.badges
    if callable(badges):
        badges = badges()
    return list(badges)


class E2ModelFieldTests(TestCase):
    def test_product_flags_default_false(self):
        for name in ('is_new', 'is_bestseller'):
            field = Product._meta.get_field(name)
            self.assertFalse(field.default, name)

    def test_site_settings_promo_fields(self):
        self.assertFalse(SiteSettings._meta.get_field('promo_enabled').default)
        SiteSettings._meta.get_field('promo_text')
        SiteSettings._meta.get_field('promo_url')
        solo = SiteSettings.get_solo()
        self.assertFalse(solo.promo_enabled)
        self.assertFalse(solo.promo_text)

    def test_no_missing_migrations(self):
        try:
            call_command('makemigrations', 'shop', '--check', '--dry-run', stdout=StringIO(), stderr=StringIO())
        except SystemExit:
            self.fail('models have changes not reflected in migrations')


class E2ProductBadgesTests(TestCase):
    """Product.badges -> list of codes: 'new', 'bestseller', 'sale' (sale = old_price > price)."""

    def test_no_badges(self):
        self.assertEqual(badges_of(make_product()), [])

    def test_new(self):
        self.assertEqual(badges_of(make_product(is_new=True)), ['new'])

    def test_bestseller(self):
        self.assertEqual(badges_of(make_product(is_bestseller=True)), ['bestseller'])

    def test_sale_only_when_old_price_greater(self):
        self.assertEqual(badges_of(make_product(price=45000, old_price=60000)), ['sale'])
        self.assertEqual(badges_of(make_product(price=45000, old_price=45000)), [])
        self.assertEqual(badges_of(make_product(price=45000, old_price=30000)), [])
        self.assertEqual(badges_of(make_product(price=45000, old_price=None)), [])

    def test_all_badges(self):
        product = make_product(is_new=True, is_bestseller=True, price=1000, old_price=2000)
        self.assertEqual(set(badges_of(product)), {'new', 'bestseller', 'sale'})


class E2AdminTests(TestCase):
    def test_product_admin_exposes_flags(self):
        model_admin = admin.site._registry[Product]
        for name in ('is_new', 'is_bestseller'):
            self.assertIn(name, model_admin.list_filter, name)
            self.assertIn(name, model_admin.list_editable, name)


class E2SeedDemoTests(TestCase):
    def test_seed_demo_twice_and_has_flags(self):
        call_command('seed_demo', stdout=StringIO())
        count = Product.objects.count()
        call_command('seed_demo', stdout=StringIO())
        self.assertEqual(Product.objects.count(), count, 'seed_demo must be idempotent')
        self.assertTrue(Product.objects.filter(is_new=True).exists())
        self.assertTrue(Product.objects.filter(is_bestseller=True).exists())


class E2NotFoundContextTests(TestCase):
    """Unknown URL -> 404 with `bestsellers` in the template context (up to 8)."""

    URL = '/takoy-stranicy-net/'

    def test_bestsellers_in_context_up_to_eight(self):
        for i in range(10):
            make_product(name=f'Хит {i}', is_bestseller=True)
        make_product(name='Не хит')
        resp = self.client.get(self.URL)
        self.assertEqual(resp.status_code, 404)
        bestsellers = list(resp.context['bestsellers'])
        self.assertEqual(len(bestsellers), 8)
        self.assertTrue(all(p.is_bestseller for p in bestsellers))

    def test_falls_back_to_featured(self):
        featured = make_product(name='Избранное', is_featured=True)
        make_product(name='Обычное')
        resp = self.client.get(self.URL)
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(list(resp.context['bestsellers']), [featured])
