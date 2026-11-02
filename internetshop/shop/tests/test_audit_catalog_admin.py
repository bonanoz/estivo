"""E2 (audit-fixes): каталог — цена 0 в фильтре и сортировке; админка — slug и позиция «по запросу»."""
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from shop.models import Category, Collection, Material, Order, OrderItem, Product
from shop.tests.helpers import make_product, parse, squash
from shop.utils import ru_slugify

HX = {'HTTP_HX_REQUEST': 'true'}


def names(resp):
    return [p.name for p in resp.context['page_obj']]


class E2PriceFilterTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.cheap = make_product(name='Товар дешёвый', price=5000)
        cls.dear = make_product(name='Товар дорогой', price=20000)
        cls.ask = make_product(name='Товар по запросу', price=0)

    def get(self, **params):
        return self.client.get(reverse('catalog_list'), params)

    def test_e2_price_max_hides_price_on_request(self):
        resp = self.get(price_max=10000)
        self.assertEqual(names(resp), ['Товар дешёвый'])

    def test_e2_price_min_zero_hides_price_on_request(self):
        resp = self.get(price_min=0)
        self.assertEqual(set(names(resp)), {'Товар дорогой', 'Товар дешёвый'})

    def test_e2_price_max_zero_shows_nothing(self):
        resp = self.get(price_max=0)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(names(resp), [])

    def test_e2_price_range_keeps_only_priced_products_inside(self):
        resp = self.get(price_min=1000, price_max=30000)
        self.assertEqual(set(names(resp)), {'Товар дорогой', 'Товар дешёвый'})

    def test_e2_price_min_alone_hides_price_on_request(self):
        resp = self.get(price_min=10000)
        self.assertEqual(names(resp), ['Товар дорогой'])

    def test_e2_without_price_filter_price_on_request_is_listed(self):
        resp = self.get()
        self.assertIn('Товар по запросу', names(resp))
        self.assertEqual(len(names(resp)), 3)

    def test_e2_other_filters_do_not_hide_price_on_request(self):
        resp = self.get(sort='new')
        self.assertIn('Товар по запросу', names(resp))

    def test_e2_garbage_price_filter_is_ignored(self):
        resp = self.get(price_max='abc')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('Товар по запросу', names(resp))
        self.assertEqual(len(names(resp)), 3)

    def test_e2_negative_price_filter_is_ignored(self):
        resp = self.get(price_max='-5')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(names(resp)), 3)

    def test_e2_live_counter_matches_listing(self):
        for params in ({'price_max': 10000}, {'price_min': 0}, {'price_min': 1000, 'price_max': 30000}, {}):
            with self.subTest(params=params):
                count = self.client.get(reverse('catalog_count'), params, **HX).context['count']
                self.assertEqual(count, self.get(**params).context['total_count'])
        self.assertEqual(self.client.get(reverse('catalog_count'), {'price_max': 10000}, **HX).context['count'], 1)

    def test_e2_material_page_applies_same_rule(self):
        rotang = Material.objects.create(name='Ротанг', slug='rotang')
        for product in (self.cheap, self.ask):
            Product.objects.filter(pk=product.pk).update(material=rotang)
        resp = self.client.get(reverse('catalog_by_material', args=['rotang']), {'price_max': 10000})
        self.assertEqual(names(resp), ['Товар дешёвый'])


class E2PriceSortTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # создаём в «неудобном» порядке, чтобы id не совпадал с ценой
        make_product(name='Товар по запросу', price=0)
        make_product(name='Товар дорогой', price=20000)
        make_product(name='Товар дешёвый', price=5000)

    def order(self, sort):
        return names(self.client.get(reverse('catalog_list'), {'sort': sort}))

    def test_e2_price_asc_puts_price_on_request_last(self):
        self.assertEqual(self.order('price_asc'), ['Товар дешёвый', 'Товар дорогой', 'Товар по запросу'])

    def test_e2_price_desc_puts_price_on_request_last(self):
        self.assertEqual(self.order('price_desc'), ['Товар дорогой', 'Товар дешёвый', 'Товар по запросу'])

    def test_e2_several_price_on_request_all_after_priced(self):
        make_product(name='Ещё по запросу', price=0)
        make_product(name='Средний', price=9000)
        for sort in ('price_asc', 'price_desc'):
            with self.subTest(sort=sort):
                result = self.order(sort)
                self.assertEqual(set(result[-2:]), {'Товар по запросу', 'Ещё по запросу'})
                self.assertNotIn('Товар по запросу', result[:-2])

    def test_e2_sort_with_price_filter_keeps_order_and_hides_price_on_request(self):
        resp = self.client.get(reverse('catalog_list'), {'sort': 'price_desc', 'price_max': 30000})
        self.assertEqual(names(resp), ['Товар дорогой', 'Товар дешёвый'])

    def test_e2_unknown_sort_does_not_break_page(self):
        resp = self.client.get(reverse('catalog_list'), {'sort': 'nonsense'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(names(resp)), 3)


class AdminTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.superuser = get_user_model().objects.create_superuser('boss', 'boss@example.com', 'pw-for-tests-123')

    def setUp(self):
        self.client.force_login(self.superuser)


class E2AdminSlugTests(AdminTestCase):
    PRODUCT_FORM = {
        'name': 'Кресло Йорк', 'slug': '', 'sku': '', 'short_description': '', 'description': 'Описание',
        'price': '15000', 'max_load_kg': '120', 'warranty_years': '3', 'is_available': 'on',
        'gallery-TOTAL_FORMS': '0', 'gallery-INITIAL_FORMS': '0',
        'gallery-MIN_NUM_FORMS': '0', 'gallery-MAX_NUM_FORMS': '1000',
    }

    def test_e2_no_prepopulated_slug_in_any_admin(self):
        for model in (Material, Category, Collection, Product):
            with self.subTest(model=model.__name__):
                self.assertFalse(admin.site._registry[model].prepopulated_fields)

    def test_e2_add_forms_have_no_prepopulated_slug_script_data(self):
        for model in ('product', 'category', 'material', 'collection'):
            with self.subTest(model=model):
                root = parse(self.client.get(reverse(f'admin:shop_{model}_add')))
                script = root.find('script', attrs={'id': 'django-admin-prepopulated-fields-constants'})
                self.assertIsNotNone(script)
                self.assertEqual(script.get('data-prepopulated-fields'), '[]')

    def test_e2_slug_not_required_for_material_category_collection(self):
        for model in (Material, Category, Collection):
            with self.subTest(model=model.__name__):
                self.assertTrue(model._meta.get_field('slug').blank)

    def test_e2_product_from_admin_with_empty_slug(self):
        resp = self.client.post(reverse('admin:shop_product_add'), self.PRODUCT_FORM)
        self.assertEqual(resp.status_code, 302, getattr(resp, 'context', None) and resp.context['adminform'].form.errors)
        self.assertEqual(Product.objects.get().slug, 'kreslo-york')

    def test_e2_category_from_admin_with_empty_slug(self):
        resp = self.client.post(reverse('admin:shop_category_add'), {'name': 'Пуфы и щиты', 'slug': '', 'order': '0'})
        self.assertEqual(resp.status_code, 302, getattr(resp, 'context', None) and resp.context['adminform'].form.errors)
        self.assertEqual(Category.objects.get().slug, ru_slugify('Пуфы и щиты'))
        self.assertEqual(Category.objects.get().slug, 'pufy-i-schity')

    def test_e2_material_from_admin_with_empty_slug(self):
        resp = self.client.post(reverse('admin:shop_material_add'),
                                {'name': 'Шпон дуба', 'slug': '', 'description': '', 'order': '0'})
        self.assertEqual(resp.status_code, 302, getattr(resp, 'context', None) and resp.context['adminform'].form.errors)
        self.assertEqual(Material.objects.get().slug, ru_slugify('Шпон дуба'))

    def test_e2_collection_from_admin_with_empty_slug(self):
        resp = self.client.post(reverse('admin:shop_collection_add'),
                                {'name': 'Летняя серия', 'slug': '', 'description': '', 'order': '0'})
        self.assertEqual(resp.status_code, 302, getattr(resp, 'context', None) and resp.context['adminform'].form.errors)
        self.assertEqual(Collection.objects.get().slug, ru_slugify('Летняя серия'))

    def test_e2_manual_slug_is_kept(self):
        resp = self.client.post(reverse('admin:shop_product_add'), {**self.PRODUCT_FORM, 'slug': 'moy-adres'})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Product.objects.get().slug, 'moy-adres')

    def test_e2_manual_slug_kept_for_category(self):
        self.client.post(reverse('admin:shop_category_add'), {'name': 'Пуфы', 'slug': 'my-pufy', 'order': '0'})
        self.assertEqual(Category.objects.get().slug, 'my-pufy')

    def test_e2_duplicate_slug_shows_error_and_creates_nothing(self):
        Category.objects.create(name='Кресла', slug='kresla')
        resp = self.client.post(reverse('admin:shop_category_add'), {'name': 'Другие кресла', 'slug': 'kresla', 'order': '0'})
        self.assertEqual(resp.status_code, 200)
        self.assertIn('slug', resp.context['adminform'].form.errors)
        self.assertEqual(Category.objects.count(), 1)

    def test_e2_duplicate_product_slug_shows_error(self):
        make_product(name='Первый', slug='kreslo-york')
        resp = self.client.post(reverse('admin:shop_product_add'), {**self.PRODUCT_FORM, 'slug': 'kreslo-york'})
        self.assertEqual(resp.status_code, 200)
        self.assertIn('slug', resp.context['adminform'].form.errors)
        self.assertEqual(Product.objects.count(), 1)

    def test_e2_empty_slug_colliding_with_existing_product_shows_error(self):
        make_product(name='Первый йорк', slug=ru_slugify('Кресло Йорк'))
        resp = self.client.post(reverse('admin:shop_product_add'), self.PRODUCT_FORM)  # name='Кресло Йорк', slug=''
        self.assertEqual(resp.status_code, 200)
        self.assertIn('slug', resp.context['adminform'].form.errors)
        self.assertEqual(Product.objects.count(), 1)

    def test_e2_empty_slug_colliding_with_existing_category_shows_error(self):
        Category.objects.create(name='Другие пуфы', slug=ru_slugify('Пуфы и щиты'))
        resp = self.client.post(reverse('admin:shop_category_add'), {'name': 'Пуфы и щиты', 'slug': '', 'order': '0'})
        self.assertEqual(resp.status_code, 200)
        self.assertIn('slug', resp.context['adminform'].form.errors)
        self.assertEqual(Category.objects.count(), 1)

    def test_e2_existing_slug_is_not_recalculated_on_rename(self):
        product = make_product(name='Старое имя', slug='staryy-adres')
        form = {**self.PRODUCT_FORM, 'name': 'Новое имя', 'slug': 'staryy-adres'}
        resp = self.client.post(reverse('admin:shop_product_change', args=[product.pk]), form)
        self.assertEqual(resp.status_code, 302)
        product.refresh_from_db()
        self.assertEqual((product.name, product.slug), ('Новое имя', 'staryy-adres'))

    def test_e2_no_model_changes_without_migration(self):
        call_command('makemigrations', '--check', '--dry-run', verbosity=0)


class E2AdminOrderItemTests(AdminTestCase):
    def order_page(self, unit_price, quantity=2):
        product = make_product(name='Кресло Админка', price=unit_price)
        order = Order.objects.create(customer_name='Иван', customer_phone='+7 900 123-45-67',
                                     total_price=unit_price * quantity)
        OrderItem.objects.create(order=order, product=product, quantity=quantity, unit_price=unit_price)
        resp = self.client.get(reverse('admin:shop_order_change', args=[order.pk]))
        self.assertEqual(resp.status_code, 200)
        return resp.content.decode()

    def test_e2_zero_price_item_shows_price_on_request(self):
        self.assertIn('Цена по запросу', self.order_page(0))

    def test_e2_priced_item_shows_price_without_marker(self):
        page = self.order_page(15000)
        self.assertNotIn('Цена по запросу', page)
        self.assertIn('15000', squash(page))

    def test_e2_item_still_readonly_and_page_lists_product(self):
        page = self.order_page(0)
        self.assertIn('Кресло Админка', page)
