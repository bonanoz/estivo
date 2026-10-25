"""Скорость переходов: число запросов не растёт с числом карточек, предзагрузка ссылок и её сброс после POST.

На проде каждый запрос к БД стоит ~25 мс, поэтому N+1 в карточках заметен на каждом переходе.
"""
from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext

from shop.models import Category, Material

from .helpers import make_product


class NoNPlusOneTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.material = Material.objects.create(name='Ротанг', slug='rotang')
        cls.categories = [Category.objects.create(name=f'Кат {i}', slug=f'kat-{i}') for i in range(6)]

    def add_products(self, n, **kw):
        return [make_product(material=self.material, category=self.categories[i % 6], **kw) for i in range(n)]

    def queries(self, url):
        self.client.get('/')  # сессия создана, как у вернувшегося посетителя
        with CaptureQueriesContext(connection) as ctx:
            self.assertIn(self.client.get(url).status_code, (200, 404))
        return len(ctx.captured_queries)

    def assert_flat(self, url_fn, **kw):
        self.add_products(2, **kw)
        few = self.queries(url_fn())
        self.add_products(6, **kw)
        self.assertEqual(self.queries(url_fn()), few)

    def test_home(self):
        self.assert_flat(lambda: '/', is_featured=True)

    def test_product_related(self):
        main = make_product(material=self.material, category=self.categories[0])
        for _ in range(2):
            make_product(material=self.material, category=self.categories[0])
        few = self.queries(main.get_absolute_url())
        for _ in range(4):
            make_product(material=self.material, category=self.categories[0])
        self.assertEqual(self.queries(main.get_absolute_url()), few)

    def test_404_bestsellers(self):
        self.assert_flat(lambda: '/net-takoy-stranicy/', is_bestseller=True)


class PrefetchTests(TestCase):
    def test_pages_declare_hover_prefetch_but_not_for_cart(self):
        html = self.client.get('/').content.decode()
        self.assertIn('<script type="speculationrules">', html)
        self.assertIn('"/cart/*"', html)

    def test_post_clears_prefetch_cache(self):
        p = make_product()
        resp = self.client.post(f'/cart/add/{p.id}/', {'quantity': 1})
        self.assertEqual(resp['Clear-Site-Data'], '"prefetchCache"')
        self.assertNotIn('Clear-Site-Data', self.client.get('/'))
