"""E2: catalog filters, sorting, 24-per-page pagination, /catalog/count/ endpoint."""
from django.http import QueryDict
from django.test import TestCase
from django.urls import reverse

from shop.models import Category, ColorOption, Material, Product

from .helpers import has_number, make_product, parse, query

COUNT_URL = '/catalog/count/'
HX = {'HTTP_HX_REQUEST': 'true'}


def page_products(resp):
    return list(resp.context['page_obj'].object_list)


def page_names(resp):
    return {p.name for p in page_products(resp)}


class E2CatalogFilterTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.rotang = Material.objects.create(name='Ротанг', slug='rotang')
        cls.roup = Material.objects.create(name='Роуп', slug='roup')
        cls.kresla = Category.objects.create(name='Кресла', slug='kresla')
        cls.divany = Category.objects.create(name='Диваны', slug='divany')
        cls.stoly = Category.objects.create(name='Столы', slug='stoly')
        cls.graphite = ColorOption.objects.create(name='Графит', finish_type=ColorOption.WEAVE, hex='#3b3a36')
        cls.mocca = ColorOption.objects.create(name='Мокко', finish_type=ColorOption.WEAVE, hex='#6f5b45')

        cls.a = make_product(name='Альфа', price=5000, material=cls.rotang, category=cls.kresla,
                             length_cm=60, colors=[cls.graphite])
        cls.b = make_product(name='Бета', price=20000, old_price=30000, material=cls.rotang,
                             category=cls.divany, length_cm=200, colors=[cls.mocca])
        cls.c = make_product(name='Гамма', price=40000, old_price=35000, material=cls.roup,
                             category=cls.stoly, length_cm=150)
        cls.d = make_product(name='Дельта', price=70000, material=cls.roup, category=cls.kresla,
                             length_cm=90, colors=[cls.graphite, cls.mocca])
        cls.hidden = make_product(name='Скрытый', price=20000, material=cls.rotang, category=cls.kresla,
                                  is_available=False, colors=[cls.graphite])

    def get(self, params='', url=None):
        resp = self.client.get((url or reverse('catalog_list')) + params)
        self.assertEqual(resp.status_code, 200)
        return resp

    def test_color_filter(self):
        self.assertEqual(page_names(self.get(f'?color={self.graphite.id}')), {'Альфа', 'Дельта'})

    def test_color_filter_no_duplicates(self):
        resp = self.get(f'?color={self.graphite.id}&color={self.mocca.id}')
        products = page_products(resp)
        self.assertEqual(len(products), len({p.pk for p in products}))

    def test_price_range(self):
        resp = self.get('?price_min=10000&price_max=50000')
        self.assertEqual(page_names(resp), {'Бета', 'Гамма'})
        for p in page_products(resp):
            self.assertTrue(10000 <= p.price <= 50000)

    def test_length_range(self):
        self.assertEqual(page_names(self.get('?length_min=100&length_max=180')), {'Гамма'})

    def test_flag_sale_only_old_price_greater_than_price(self):
        # Гамма has old_price < price — not a sale.
        self.assertEqual(page_names(self.get('?flag=sale')), {'Бета'})

    def test_category_multi_is_union(self):
        self.assertEqual(page_names(self.get('?category=kresla&category=divany')), {'Альфа', 'Бета', 'Дельта'})

    def test_material_filter_on_catalog_root(self):
        self.assertEqual(page_names(self.get('?material=roup')), {'Гамма', 'Дельта'})

    def test_unavailable_never_listed(self):
        self.assertNotIn('Скрытый', page_names(self.get(f'?color={self.graphite.id}')))

    def test_invalid_price_ignored(self):
        resp = self.get('?price_min=abc')
        self.assertEqual(page_names(resp), {'Альфа', 'Бета', 'Гамма', 'Дельта'})

    def test_other_invalid_values_ignored(self):
        for params in ['?price_max=-', '?color=abc', '?length_min=x', '?flag=bogus', '?page=abc', '?page=999']:
            self.get(params)  # asserts 200
        self.assertEqual(page_names(self.get('?color=abc')), {'Альфа', 'Бета', 'Гамма', 'Дельта'})

    def test_sort_price_asc(self):
        prices = [p.price for p in page_products(self.get('?sort=price_asc'))]
        self.assertEqual(prices, sorted(prices))
        self.assertEqual(len(prices), 4)

    def test_sort_price_desc(self):
        prices = [p.price for p in page_products(self.get('?sort=price_desc'))]
        self.assertEqual(prices, sorted(prices, reverse=True))

    def test_sort_new_ok(self):
        self.assertEqual(len(page_products(self.get('?sort=new'))), 4)

    def test_unknown_sort_uses_default_ordering(self):
        expected = [p.pk for p in Product.objects.filter(is_available=True)]
        self.assertEqual([p.pk for p in page_products(self.get('?sort=bogus'))], expected)
        self.assertEqual([p.pk for p in page_products(self.get('?sort=recommended'))], expected)

    def test_material_category_route_still_works(self):
        url = reverse('catalog_by_category', args=['rotang', 'kresla'])
        self.assertEqual(page_names(self.get(url=url)), {'Альфа'})

    def test_filters_apply_on_top_of_material_category_route(self):
        url = reverse('catalog_by_category', args=['roup', 'kresla'])
        self.assertEqual(page_names(self.get('?price_max=10000', url=url)), set())
        self.assertEqual(page_names(self.get('?price_min=60000', url=url)), {'Дельта'})

    def test_filters_apply_on_top_of_material_route(self):
        url = reverse('catalog_by_material', args=['rotang'])
        self.assertEqual(page_names(self.get('?flag=sale', url=url)), {'Бета'})

    def test_search_still_works(self):
        self.assertEqual(page_names(self.get('?search=Гамм')), {'Гамма'})


class E2CatalogFlagTests(TestCase):
    """Flags new / bestseller require the new Product fields."""

    @classmethod
    def setUpTestData(cls):
        make_product(name='Новинка Один', is_new=True)
        make_product(name='Хит Один', is_bestseller=True)
        make_product(name='Обычный', price=1000)

    def test_flag_new(self):
        resp = self.client.get(reverse('catalog_list') + '?flag=new')
        self.assertEqual(page_names(resp), {'Новинка Один'})

    def test_flag_bestseller(self):
        resp = self.client.get(reverse('catalog_list') + '?flag=bestseller')
        self.assertEqual(page_names(resp), {'Хит Один'})


class E2PaginationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        Product.objects.bulk_create([
            Product(name=f'Товар {i:02d}', slug=f'tovar-{i:02d}', description='d', price=1000 + i)
            for i in range(30)
        ])

    def test_24_per_page(self):
        resp = self.client.get(reverse('catalog_list'))
        self.assertEqual(len(page_products(resp)), 24)
        resp = self.client.get(reverse('catalog_list') + '?page=2')
        self.assertEqual(len(page_products(resp)), 6)

    def test_pagination_links_preserve_params(self):
        resp = self.client.get(reverse('catalog_list') + '?price_min=1&sort=price_asc')
        links = [a.get('href') for a in parse(resp).find_all('a', attrs={'href': True})
                 if query(a.get('href')).get('page') == ['2']]
        self.assertTrue(links, 'expected a pagination link to page 2')
        for href in links:
            q = query(href)
            self.assertEqual(q.get('price_min'), ['1'], href)
            self.assertEqual(q.get('sort'), ['price_asc'], href)

    def test_page_param_not_duplicated(self):
        resp = self.client.get(reverse('catalog_list') + '?page=2&sort=price_desc')
        for a in parse(resp).find_all('a', attrs={'href': True}):
            q = query(a.get('href'))
            if 'page' in q:
                self.assertEqual(len(q['page']), 1, a.get('href'))


class E2CatalogCountTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.graphite = ColorOption.objects.create(name='Графит', finish_type=ColorOption.WEAVE, hex='#3b3a36')
        for price in (5000, 12000, 20000, 33000, 70000):
            make_product(price=price)
        make_product(price=15000, colors=[cls.graphite])
        make_product(price=16000, is_available=False)

    def test_count_with_filters(self):
        resp = self.client.get(COUNT_URL + '?price_min=10000&price_max=40000', **HX)
        self.assertEqual(resp.status_code, 200)
        text = resp.content.decode()
        self.assertNotIn('<html', text.lower(), 'count endpoint must return a fragment')
        self.assertTrue(has_number(parse(resp).text, 4), text)

    def test_count_with_color(self):
        resp = self.client.get(COUNT_URL + f'?color={self.graphite.id}', **HX)
        self.assertTrue(has_number(parse(resp).text, 1), resp.content.decode())

    def test_count_without_params_counts_available(self):
        resp = self.client.get(COUNT_URL, **HX)
        self.assertTrue(has_number(parse(resp).text, 6), resp.content.decode())

    def test_count_invalid_params_ignored(self):
        resp = self.client.get(COUNT_URL + '?price_min=abc', **HX)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(has_number(parse(resp).text, 6), resp.content.decode())


class E2ApplyFiltersFunctionTests(TestCase):
    """shop.catalog_filters.apply_filters(queryset, params) -> (queryset, active_filters)."""

    @classmethod
    def setUpTestData(cls):
        cls.cheap = make_product(name='Дешёвый', price=5000)
        cls.mid = make_product(name='Средний', price=25000)

    def test_returns_filtered_queryset_and_active_filters(self):
        from shop.catalog_filters import apply_filters
        result = apply_filters(Product.objects.all(), QueryDict('price_min=10000'))
        self.assertEqual(len(result), 2)
        qs, _active = result
        self.assertEqual(list(qs), [self.mid])

    def test_invalid_params_ignored(self):
        from shop.catalog_filters import apply_filters
        qs, _active = apply_filters(Product.objects.all(), QueryDict('price_min=abc&color=x&flag=zzz'))
        self.assertEqual(set(qs), {self.cheap, self.mid})
