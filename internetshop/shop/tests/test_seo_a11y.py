"""E7: cross-cutting SEO/a11y on every public page + legacy static removal."""
import re
from pathlib import Path
from urllib.parse import urlsplit

from django.test import TestCase
from django.urls import reverse

from shop.models import Category, ColorOption, Material

from .helpers import make_product, parse

SHOP_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = SHOP_DIR / 'templates'
STATIC_DIR = SHOP_DIR / 'static'

LEGACY_STATIC = [
    'css/variables.css', 'css/base.css', 'css/layout.css', 'css/components.css', 'css/pages.css',
    'js/main.js', 'js/forms.js', 'js/cart.js', 'js/product-gallery.js', 'js/product-3d.js',
]


class E7PublicPagesTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        material = Material.objects.create(name='Ротанг', slug='rotang', description='Про ротанг')
        category = Category.objects.create(name='Кресла', slug='kresla')
        weave = ColorOption.objects.create(name='Графит', finish_type=ColorOption.WEAVE, hex='#3b3a36')
        cls.product = make_product(name='Кресло СЕО', material=material, category=category, colors=[weave])
        make_product(name='Кресло СЕО Два', material=material, category=category)

    def sitemap_paths(self):
        resp = self.client.get('/sitemap.xml')
        self.assertEqual(resp.status_code, 200)
        locs = re.findall(r'<loc>(.*?)</loc>', resp.content.decode())
        paths = [urlsplit(loc).path for loc in locs]
        self.assertIn(self.product.get_absolute_url(), paths)
        return paths

    def assert_page_ok(self, path):
        resp = self.client.get(path)
        self.assertEqual(resp.status_code, 200, path)
        root = parse(resp)
        self.assertEqual(root.find('html').get('lang'), 'ru', path)
        self.assertEqual(len(root.find_all('h1')), 1, f'{path}: exactly one <h1>')
        desc = root.find('meta', attrs={'name': 'description'})
        self.assertIsNotNone(desc, f'{path}: meta description')
        self.assertTrue(desc.get('content', '').strip(), f'{path}: empty meta description')
        self.assertIsNotNone(root.find('link', attrs={'rel': 'canonical', 'href': True}), f'{path}: canonical')

    def test_sitemap_pages(self):
        for path in self.sitemap_paths():
            self.assert_page_ok(path)

    def test_catalog_subpages(self):
        self.assert_page_ok(reverse('catalog_by_material', args=['rotang']))
        self.assert_page_ok(reverse('catalog_by_category', args=['rotang', 'kresla']))

    def test_cart_wishlist_checkout(self):
        self.assert_page_ok(reverse('cart_detail'))
        self.assert_page_ok('/wishlist/')
        self.client.post(reverse('cart_add', args=[self.product.id]))
        self.assert_page_ok(reverse('cart_detail'))
        self.assert_page_ok(reverse('checkout'))


class E7LegacyStaticRemovedTests(TestCase):
    def test_templates_do_not_reference_legacy_static(self):
        offenders = []
        for template in TEMPLATES_DIR.rglob('*.html'):
            text = template.read_text(encoding='utf-8')
            for legacy in LEGACY_STATIC:
                if legacy in text:
                    offenders.append(f'{template.relative_to(TEMPLATES_DIR)}: {legacy}')
        self.assertEqual(offenders, [])

    def test_legacy_files_deleted(self):
        existing = [p for p in LEGACY_STATIC if (STATIC_DIR / p).exists()]
        self.assertEqual(existing, [])

    def test_vendored_model_viewer_kept(self):
        self.assertTrue((STATIC_DIR / 'js' / 'vendor' / 'model-viewer.min.js').exists())
