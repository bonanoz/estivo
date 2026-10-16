"""E2: header search suggestions endpoint GET /search/suggest/?q=…"""
from django.test import TestCase

from .helpers import make_product, parse, product_hrefs

SUGGEST_URL = '/search/suggest/'
HX = {'HTTP_HX_REQUEST': 'true'}


class E2SearchSuggestTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.chairs = [make_product(name=f'Кресло модель {i}') for i in range(8)]
        cls.hidden = make_product(name='Кресло скрытое', is_available=False)
        cls.by_sku = make_product(name='Диван Альфа', sku='ZX-9001')
        cls.by_desc = make_product(name='Шезлонг Бета', description='Уникальный плетёный кокон для сада')
        cls.other = make_product(name='Столик Гамма', description='Кофейный столик')

    def suggest(self, q):
        resp = self.client.get(SUGGEST_URL, {'q': q}, **HX)
        self.assertEqual(resp.status_code, 200)
        return resp

    def test_at_most_six_products(self):
        links = product_hrefs(parse(self.suggest('крес')))
        self.assertEqual(len(links), 6, links)
        chair_urls = {p.get_absolute_url() for p in self.chairs}
        self.assertTrue(links <= chair_urls)

    def test_only_available(self):
        links = product_hrefs(parse(self.suggest('скрыт')))
        self.assertNotIn(self.hidden.get_absolute_url(), links)

    def test_matches_sku(self):
        links = product_hrefs(parse(self.suggest('ZX-9001')))
        self.assertEqual(links, {self.by_sku.get_absolute_url()})

    def test_matches_description(self):
        links = product_hrefs(parse(self.suggest('кокон')))
        self.assertEqual(links, {self.by_desc.get_absolute_url()})

    def test_matches_name_case_insensitive(self):
        links = product_hrefs(parse(self.suggest('гамма')))
        self.assertEqual(links, {self.other.get_absolute_url()})

    def test_short_query_returns_empty_fragment(self):
        for q in ['', 'к']:
            resp = self.suggest(q)
            self.assertEqual(resp.content.strip(), b'', f'q={q!r}')

    def test_missing_q_returns_empty_fragment(self):
        resp = self.client.get(SUGGEST_URL, **HX)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content.strip(), b'')

    def test_returns_fragment_not_full_page(self):
        self.assertNotIn(b'<html', self.suggest('крес').content.lower())
