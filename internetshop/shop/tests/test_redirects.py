"""Эпик d: редиректы по redirect_map.csv (301/410, tilda_id, /news/tpost/*).

Контракт интерфейсов:
- Данные: `shop/data/redirect_map.csv` (UTF-8 с BOM, `;`, колонки как в docs/marketing-audit/redirect_map.csv),
  строка `/promo` заполнена: 301 -> `/catalog/?flag=sale`.
- Middleware в MIDDLEWARE после CommonMiddleware, реагирует только на 404.
- Страница 410 — HTML (extends base.html) со ссылкой на `/catalog/`.
"""
import csv
import re

from django.conf import settings
from django.test import TestCase

from .helpers import make_product

COPY = settings.BASE_DIR / 'shop' / 'data' / 'redirect_map.csv'
SOURCE = settings.BASE_DIR.parent / 'docs' / 'marketing-audit' / 'redirect_map.csv'


def load(path):
    with open(path, encoding='utf-8-sig', newline='') as f:
        rows = list(csv.reader(f, delimiter=';'))
    return [(r[0], r[4], r[5]) for r in rows[1:]]  # old_path, action, new_path


def tproduct_id(path):
    return int(re.search(r'/tproduct/(\d+)-', path).group(1))


class E_d_MapFileTests(TestCase):
    def test_e_d_copy_matches_source(self):
        self.assertTrue(COPY.exists(), f'нет {COPY}')
        copy, src = load(COPY), load(SOURCE)
        self.assertEqual(len(copy), 276)
        self.assertNotIn('решение', [a for _, a, _ in copy])
        self.assertEqual({p for p, _, _ in copy}, {p for p, _, _ in src})
        self.assertEqual(
            {r for r in copy if r[0] != '/promo'}, {r for r in src if r[0] != '/promo'})
        self.assertIn(('/promo', '301', '/catalog/?flag=sale'), copy)


class E_d_RedirectTests(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = load(COPY)  # до super(): иначе упавший setUpClass ломает соседние классы
        super().setUpClass()

    def test_e_d_every_row(self):
        for old, action, new in self.rows:
            with self.subTest(old=old):
                r = self.client.get(old)
                if old == '/':
                    self.assertEqual(r.status_code, 200)
                elif action == '301':
                    self.assertEqual(r.status_code, 301)
                    if new.startswith('/product/'):
                        # товаров в тестовой БД нет — запасной 301 в раздел каталога
                        self.assertTrue(r['Location'].startswith('/catalog/'), r['Location'])
                    else:
                        self.assertEqual(r['Location'], new)
                elif action == '410':
                    self.assertEqual(r.status_code, 410)
                else:
                    self.fail(f'неожиданное действие {action!r}')

    def test_e_d_no_404_and_no_chains(self):
        for old, action, new in self.rows:
            if old == '/':
                continue
            with self.subTest(old=old):
                r = self.client.get(old)
                self.assertNotEqual(r.status_code, 404)
                if action == '301':
                    nxt = self.client.get(r['Location'])
                    self.assertFalse(300 <= nxt.status_code < 400,
                                     f'цепочка: {old} -> {r["Location"]} -> {nxt.status_code}')

    def test_e_d_410_page_is_html_with_catalog_link(self):
        r = self.client.get('/tproduct/121969165582-sac-marin-yellow')
        self.assertEqual(r.status_code, 410)
        self.assertIn('text/html', r['Content-Type'])
        html = r.content.decode()
        self.assertGreater(len(html), 500)
        self.assertIn('href="/catalog/"', html)

    def test_e_d_slash_variants(self):
        # /b2b/ — живая Django-страница, поэтому вариант со слэшем проверяем только на /aksessuary
        new = next(n for o, _, n in self.rows if o == '/aksessuary')
        r = self.client.get('/aksessuary/')
        self.assertEqual(r.status_code, 301)
        self.assertEqual(r['Location'], new)
        r = self.client.get('/b2b')
        self.assertEqual(r.status_code, 301)
        self.assertEqual(r['Location'], '/b2b/')
        self.assertEqual(self.client.get('/b2b/').status_code, 200)

    def test_e_d_product_by_tilda_id_follows_new_slug(self):
        rows = [o for o, a, _ in self.rows if a == '301' and '/tproduct/' in o]
        with_section = next(o for o in rows if not o.startswith('/tproduct/'))
        bare = next(o for o in rows if o.startswith('/tproduct/'))
        p1 = make_product(slug='novyy-slug-test', tilda_id=tproduct_id(with_section))
        p2 = make_product(slug='novyy-slug-bare', tilda_id=tproduct_id(bare))
        for old, p in ((with_section, p1), (bare, p2), (with_section + '/', p1)):
            with self.subTest(old=old):
                r = self.client.get(old)
                self.assertEqual(r.status_code, 301)
                self.assertEqual(r['Location'], p.get_absolute_url())
        self.assertEqual(p1.get_absolute_url(), '/product/novyy-slug-test/')

    def test_e_d_missing_product_falls_back_to_section(self):
        """Товар из карты не импортирован (ручная проверка) — 301 в раздел, не в 404."""
        old = '/komplektyroup/tproduct/248028431432-komplekt-mebeli-iz-roupa-1'
        self.assertEqual(self.client.get(old)['Location'], '/catalog/roup/komplekty/')
        self.assertEqual(self.client.get('/tproduct/685095834682-copy-komplekt-mebeli-iz-rotang-25')['Location'],
                         '/catalog/')
        # раздел с query (/salerotang → /catalog/?flag=sale&…) — без query: скидки у импорта выключены
        self.assertEqual(self.client.get('/salerotang/tproduct/517437746363-kokon-komo-iz-rotanga')['Location'],
                         '/catalog/')
        make_product(slug='komplekt-mebeli-iz-roupa-1')
        self.assertEqual(self.client.get(old)['Location'], '/product/komplekt-mebeli-iz-roupa-1/')

    def test_e_d_news_tpost(self):
        for path in ('/news/tpost/lyuboy-adres', '/news/tpost/abc-123/'):
            with self.subTest(path=path):
                r = self.client.get(path)
                self.assertEqual(r.status_code, 301)
                self.assertEqual(r['Location'], '/')

    def test_e_d_django_urls_untouched(self):
        for path in ('/', '/catalog/', '/b2b/', '/privacy/'):
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code, 200)
        self.assertEqual(self.client.get('/net-takoy-stranicy-123/').status_code, 404)
