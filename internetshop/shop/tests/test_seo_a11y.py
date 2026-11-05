"""E7: cross-cutting SEO/a11y on every public page + legacy static removal."""
import re
from pathlib import Path
from urllib.parse import urlsplit

from django.test import TestCase, override_settings
from django.urls import reverse

from shop.models import Category, ColorOption, Material
from shop.templatetags.shop_tags import absolute

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


@override_settings(SITE_URL='https://estivo63.ru', ALLOWED_HOSTS=['testserver', 'estivo.onrender.com'])
class SiteUrlTests(TestCase):
    """Canonical, og, robots и sitemap ведут на SITE_URL, а не на хост запроса (*.onrender.com)."""

    @classmethod
    def setUpTestData(cls):
        material = Material.objects.create(name='Ротанг', slug='rotang')
        category = Category.objects.create(name='Кресла', slug='kresla')
        cls.product = make_product(name='Кресло Домен', material=material, category=category)

    def test_canonical_and_og_url_use_site_url(self):
        root = parse(self.client.get(self.product.get_absolute_url(), HTTP_HOST='estivo.onrender.com'))
        expected = 'https://estivo63.ru' + self.product.get_absolute_url()
        self.assertEqual(root.find('link', attrs={'rel': 'canonical'}).get('href'), expected)
        self.assertEqual(root.find('meta', attrs={'property': 'og:url'}).get('content'), expected)

    def test_noindex_header_only_on_demo(self):
        self.assertNotIn('X-Robots-Tag', self.client.get('/'))
        with self.settings(SEO_NOINDEX=True):
            for url in ('/', self.product.get_absolute_url(), '/robots.txt', '/sitemap.xml'):
                self.assertEqual(self.client.get(url)['X-Robots-Tag'], 'noindex, nofollow', url)

    def test_favicon(self):
        icon = parse(self.client.get('/')).find('link', attrs={'rel': 'icon'})
        href = icon.get('href') if icon else ''
        self.assertTrue(href.endswith('.svg'), href)
        self.assertRedirects(self.client.get('/favicon.ico'), href, fetch_redirect_response=False)

    def test_robots_sitemap_line(self):
        body = self.client.get('/robots.txt', HTTP_HOST='estivo.onrender.com').content.decode()
        self.assertIn('Sitemap: https://estivo63.ru/sitemap.xml', body)

    def test_sitemap_has_catalog_pages_on_site_url(self):
        body = self.client.get('/sitemap.xml', HTTP_HOST='estivo.onrender.com').content.decode()
        locs = re.findall(r'<loc>(.*?)</loc>', body)
        self.assertTrue(locs and all(loc.startswith('https://estivo63.ru/') for loc in locs), locs)
        self.assertIn('https://estivo63.ru/catalog/rotang/', locs)
        self.assertIn('https://estivo63.ru/catalog/rotang/kresla/', locs)

    def test_absolute_keeps_s3_urls(self):
        self.assertEqual(absolute('https://cdn.example.com/p.jpg'), 'https://cdn.example.com/p.jpg')
        self.assertEqual(absolute('/media/p.jpg'), 'https://estivo63.ru/media/p.jpg')


def jsonld(resp):
    """Все JSON-LD блоки страницы, по @type."""
    import json
    blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', resp.content.decode(), re.S)
    return {d['@type']: d for d in map(json.loads, blocks)}


@override_settings(SITE_URL='https://estivo63.ru')
class StructuredDataAndIndexingTests(TestCase):
    """GEO/SEO: разметка компании, FAQ и крошек, noindex служебных страниц, og:image разделов, llms.txt."""

    @classmethod
    def setUpTestData(cls):
        cls.material = Material.objects.create(name='Ротанг', slug='rotang')
        cls.category = Category.objects.create(name='Кресла', slug='kresla')
        cls.product = make_product(name='Кресло </script><b>', material=cls.material, category=cls.category,
                                   main_image='products/kreslo.webp')

    def test_home_has_organization(self):
        org = jsonld(self.client.get('/'))['FurnitureStore']
        self.assertEqual(org['address']['addressLocality'], 'Тольятти')
        self.assertEqual(org['url'], 'https://estivo63.ru/')
        self.assertIn(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
                      [h['dayOfWeek'] for h in org['openingHoursSpecification']])
        self.assertTrue(all('wa.me' not in u for u in org['sameAs']))

    def test_faq_page_markup_matches_visible_items(self):
        from shop.views import FAQ_ITEMS
        faq = jsonld(self.client.get(reverse('faq_page')))['FAQPage']
        self.assertEqual([q['name'] for q in faq['mainEntity']], [q for q, _ in FAQ_ITEMS])

    def test_breadcrumbs_markup(self):
        resp = self.client.get(self.product.get_absolute_url())
        crumbs = jsonld(resp)['BreadcrumbList']['itemListElement']
        self.assertEqual(crumbs[0], {'@type': 'ListItem', 'position': 1, 'name': 'Главная', 'item': 'https://estivo63.ru/'})
        self.assertEqual(crumbs[-1]['name'], self.product.name)
        self.assertNotIn('item', crumbs[-1])
        # Название из админки не закрывает <script>: «<» экранирован внутри JSON.
        self.assertNotIn('</script><b>', resp.content.decode())

    def test_service_pages_noindex(self):
        for url in (reverse('cart_detail'), reverse('wishlist'), reverse('catalog_list') + '?search=кресло'):
            meta = parse(self.client.get(url)).find('meta', attrs={'name': 'robots'})
            self.assertEqual(meta and meta.get('content'), 'noindex, follow', url)
        self.assertIsNone(parse(self.client.get(reverse('catalog_list'))).find('meta', attrs={'name': 'robots'}))

    def test_catalog_og_image_is_product_photo(self):
        url = reverse('catalog_by_category', args=['rotang', 'kresla'])
        og = parse(self.client.get(url)).find('meta', attrs={'property': 'og:image'}).get('content')
        self.assertTrue(og.endswith('/products/kreslo.webp'), og)

    def test_llms_txt(self):
        resp = self.client.get('/llms.txt')
        self.assertEqual(resp['Content-Type'], 'text/plain; charset=utf-8')
        body = resp.content.decode()
        self.assertTrue(body.startswith('# ESTIVO\n'))
        self.assertIn('[Кресла из ротанга](https://estivo63.ru/catalog/rotang/kresla/)', body)
        self.assertIn('### Какой вес выдерживает плетёная мебель?', body)
        self.assertNotIn('&quot;', body)

    def test_material_section_title(self):
        title = parse(self.client.get(reverse('catalog_by_material', args=['rotang']))).find('title').text
        self.assertEqual(title.strip(), 'Мебель из ротанга — купить в Тольятти и Самаре | ESTIVO')
        h1 = parse(self.client.get(reverse('catalog_by_material', args=['rotang']))).find('h1').text
        self.assertEqual(' '.join(h1.split()), 'Мебель из ротанга')

    def test_materials_compare_page(self):
        resp = self.client.get(reverse('materials_compare_page'))
        root = parse(resp)
        self.assertEqual(len(root.find('table', cls='compare-table').find_all('tr')), 11)
        self.assertEqual(jsonld(resp)['BreadcrumbList']['itemListElement'][-1]['name'], 'Роуп или ротанг')
        self.assertIn('https://estivo63.ru/roup-ili-rotang/', self.client.get('/sitemap.xml').content.decode())
        footer_links = [a.get('href') for a in root.find('footer').find_all('a')]
        self.assertIn(reverse('materials_compare_page'), footer_links)

    def test_full_faq_only_on_faq_page(self):
        from shop.views import CATALOG_FAQ_COUNT, FAQ_ITEMS
        catalog = parse(self.client.get(reverse('catalog_list')))
        self.assertEqual(len(catalog.find_all('details', cls='faq-item')), CATALOG_FAQ_COUNT)
        self.assertEqual(len(parse(self.client.get(reverse('faq_page'))).find_all('details', cls='faq-item')), len(FAQ_ITEMS))


class SeoDescriptionTests(TestCase):
    """Сниппет товара собирается из полей, а не из импортированного прайса в description."""

    @classmethod
    def setUpTestData(cls):
        cls.roup = Material.objects.create(name='Роуп', slug='roup')

    def test_generated_from_fields(self):
        from shop.templatetags.shop_tags import seo_description
        p = make_product(name='Кресло «Милан»', material=self.roup, price=34900, length_cm=80, width_cm=75,
                         height_cm=85, description='Кресло - 20.800х4=83.200 Итого')
        self.assertEqual(seo_description(p), 'Кресло «Милан» из роупа ручной работы, 80×75×85 см. Цена от 34 900 ₽, '
                                             'гарантия 3 года, изготовление от 4 недель, доставка по России.')

    def test_short_description_material_in_name_and_no_price(self):
        from shop.templatetags.shop_tags import seo_description
        self.assertTrue(seo_description(make_product(short_description='Лаунж-кресло.', material=self.roup))
                        .startswith('Лаунж-кресло. Цена от 10 000 ₽'))
        self.assertTrue(seo_description(make_product(name='Кресло (роуп)', material=self.roup, price=0))
                        .startswith('Кресло (роуп) ручной работы. Цена по запросу,'))

    def test_product_page_uses_it(self):
        p = make_product(name='Диван «Ривьера»', material=self.roup, description='Диван - 72.900 Итого')
        resp = self.client.get(p.get_absolute_url())
        root = parse(resp)
        expected = 'Диван «Ривьера» из роупа ручной работы. Цена от 10 000 ₽, гарантия 3 года, изготовление от 4 недель, доставка по России.'
        self.assertEqual(root.find('meta', attrs={'name': 'description'}).get('content'), expected)
        self.assertEqual(root.find('meta', attrs={'property': 'og:description'}).get('content'), expected)
        self.assertEqual(jsonld(resp)['Product']['description'], expected)


class MediaPreconnectTests(TestCase):
    def test_preconnect_only_with_bucket_domain(self):
        self.assertNotIn('rel="preconnect" href="https://cdn.example.com"', self.client.get('/').content.decode())
        with self.settings(AWS_S3_CUSTOM_DOMAIN='cdn.example.com/storage/v1/object/public/media'):
            self.assertContains(self.client.get('/'), '<link rel="preconnect" href="https://cdn.example.com">')

    def test_fonts_preloaded_and_banner_role_valid(self):
        root = parse(self.client.get('/'))
        preloads = [l.get('href') for l in root.find_all('link', attrs={'rel': 'preload'})]
        self.assertTrue(any('Gilroy-Regular' in h for h in preloads) and any('Gilroy-SemiBold' in h for h in preloads), preloads)
        banner = root.find('form', attrs={'data-cookie-banner': ''})
        self.assertIsNotNone(banner)
        self.assertIsNone(banner.get('role'))  # role="region" на <form> — недопустимая роль ARIA
