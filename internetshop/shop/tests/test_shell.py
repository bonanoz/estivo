"""E1: Foundation — base.html shell, header, promo bar, contact button, product card, footer."""

from django.test import TestCase
from django.urls import reverse

from shop.context_processors import SITE_INFO
from shop.models import Category, ColorOption, Material, Review, SiteSettings

from .helpers import has_number, make_product, parse, product_card_for, squash

WISHLIST_URL = '/wishlist/'


class E1BaseShellTests(TestCase):
    """GET / renders without a built Vite dist (dev_mode in tests) and has the base shell."""

    @classmethod
    def setUpTestData(cls):
        cls.material = Material.objects.create(name='Ротанг', slug='rotang')
        cls.category = Category.objects.create(name='Кресла', slug='kresla')
        cls.product = make_product(name='Кресло Шелл', material=cls.material, category=cls.category)

    def setUp(self):
        self.resp = self.client.get(reverse('home'))
        self.root = parse(self.resp)

    def test_home_renders_without_dist(self):
        self.assertEqual(self.resp.status_code, 200)

    def test_skip_link_and_main_landmark(self):
        skip = self.root.find('a', attrs={'href': '#main'}, cls='skip-link')
        self.assertIsNotNone(skip, 'expected <a class="skip-link" href="#main">')
        self.assertIsNotNone(self.root.find('main', attrs={'id': 'main'}), 'expected <main id="main">')

    def test_canonical_and_og_title(self):
        self.assertIsNotNone(self.root.find('link', attrs={'rel': 'canonical', 'href': True}))
        og = self.root.find('meta', attrs={'property': 'og:title'})
        self.assertIsNotNone(og)
        self.assertTrue(og.get('content', '').strip())

    def test_vite_bundle_script_tag(self):
        scripts = [s for s in self.root.find_all('script', attrs={'src': True})
                   if s.get('type') == 'module' and 'main' in s.get('src')
                   and (s.get('src').endswith('.ts') or '/dist/' in s.get('src'))]
        self.assertTrue(scripts, 'expected the Vite entry <script type="module" src="...main.ts|dist/...">')

    def test_body_sends_csrf_header_for_htmx(self):
        body = self.root.find('body')
        self.assertIsNotNone(body)
        self.assertIn('X-CSRFToken', body.get('hx-headers', ''))

    def test_html_lang_ru(self):
        html = self.root.find('html')
        self.assertEqual(html.get('lang'), 'ru')


class E1HeaderTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        make_product(name='Кресло Хедер')

    def setUp(self):
        self.root = parse(self.client.get(reverse('home')))

    def test_search_button(self):
        btn = self.root.find('button', attrs={'aria-label': 'Поиск'})
        self.assertIsNotNone(btn, 'expected <button aria-label="Поиск">')
        self.assertTrue(btn.has_attr('aria-expanded'))

    def test_search_overlay_uses_suggest_endpoint_and_catalog_submit(self):
        suggest = self.root.find(pred=lambda n: n.get('hx-get', '').startswith('/search/suggest/'))
        self.assertIsNotNone(suggest, 'search overlay needs hx-get to /search/suggest/')
        forms = [f for f in self.root.find_all('form')
                 if f.get('action') == reverse('catalog_list')
                 and f.get('method', 'get').lower() == 'get'
                 and f.find('input', attrs={'name': 'search'})]
        self.assertTrue(forms, 'Enter in search must GET /catalog/?search=…')

    def test_cart_link_with_counter(self):
        links = self.root.find_all('a', attrs={'href': reverse('cart_detail')})
        self.assertTrue(any(
            a.has_attr('data-cart-count') or a.find(attrs={'data-cart-count': True}) for a in links
        ), 'cart link must carry/contain data-cart-count')

    def test_wishlist_link_with_counter(self):
        links = self.root.find_all('a', attrs={'href': WISHLIST_URL})
        self.assertTrue(any(
            a.has_attr('data-wishlist-count') or a.find(attrs={'data-wishlist-count': True}) for a in links
        ), 'expected a link to /wishlist/ with data-wishlist-count')

    def test_hamburger_has_aria_controls(self):
        buttons = [b for b in self.root.find_all('button', attrs={'aria-controls': True})
                   if b.get('aria-label') != 'Поиск']
        self.assertTrue(buttons, 'hamburger button needs aria-controls')
        self.assertTrue(any(self.root.get_by_id(b.get('aria-controls')) for b in buttons),
                        'aria-controls must reference an existing element id')


class E1PromoBarTests(TestCase):
    """Promo bar is driven by SiteSettings.promo_enabled / promo_text / promo_url."""

    PROMO = 'Скидка 10% на коллекцию Терраса'

    def _set(self, **fields):
        SiteSettings.objects.update_or_create(pk=1, defaults=fields)

    def _bar(self):
        return parse(self.client.get(reverse('home'))).find(attrs={'data-promo-bar': True})

    def test_rendered_when_enabled_with_text(self):
        self._set(promo_enabled=True, promo_text=self.PROMO, promo_url='/catalog/')
        bar = self._bar()
        self.assertIsNotNone(bar, 'expected an element with data-promo-bar')
        self.assertIn(self.PROMO, bar.text)
        close = bar.find('button', attrs={'aria-label': True})
        self.assertIsNotNone(close, 'promo bar needs a close button with aria-label')
        self.assertTrue(close.get('aria-label').strip())

    def test_links_to_promo_url(self):
        self._set(promo_enabled=True, promo_text=self.PROMO, promo_url='/catalog/rotang/')
        bar = self._bar()
        self.assertIsNotNone(bar.find('a', attrs={'href': '/catalog/rotang/'}))

    def test_hidden_when_disabled(self):
        self._set(promo_enabled=False, promo_text=self.PROMO)
        resp = self.client.get(reverse('home'))
        self.assertIsNone(parse(resp).find(attrs={'data-promo-bar': True}))
        self.assertNotContains(resp, self.PROMO)

    def test_hidden_when_text_empty(self):
        self._set(promo_enabled=True, promo_text='')
        self.assertIsNone(self._bar())


class E1ContactButtonTests(TestCase):
    """Floating contact button (data-contact-button) on every page, incl. checkout."""

    @classmethod
    def setUpTestData(cls):
        cls.material = Material.objects.create(name='Ротанг', slug='rotang')
        cls.category = Category.objects.create(name='Кресла', slug='kresla')
        cls.product = make_product(name='Кресло Контакт', material=cls.material, category=cls.category)

    def assert_contact_button(self, resp, label):
        self.assertEqual(resp.status_code, 200, label)
        box = parse(resp).find(attrs={'data-contact-button': True})
        self.assertIsNotNone(box, f'{label}: expected element with data-contact-button')
        hrefs = [a.get('href', '') for a in box.find_all('a')]
        self.assertIn(SITE_INFO['social_links']['telegram'], hrefs, label)
        self.assertIn(SITE_INFO['social_links']['whatsapp'], hrefs, label)
        self.assertTrue(any(h.startswith('tel:') for h in hrefs), label)

    def test_present_on_public_pages(self):
        urls = [
            reverse('home'), reverse('catalog_list'), self.product.get_absolute_url(),
            reverse('cart_detail'), WISHLIST_URL, reverse('faq_page'), reverse('contacts_page'),
        ]
        for url in urls:
            self.assert_contact_button(self.client.get(url), url)

    def test_present_on_checkout(self):
        self.client.post(reverse('cart_add', args=[self.product.id]))
        self.assert_contact_button(self.client.get(reverse('checkout')), 'checkout')


class E1ProductCardColorsTests(TestCase):
    """Card: "+N" for >4 colors, heart with aria-pressed (no new model fields needed)."""

    @classmethod
    def setUpTestData(cls):
        colors = [ColorOption.objects.create(name=f'Цвет {i}', finish_type=ColorOption.WEAVE, hex='#111111')
                  for i in range(6)]
        cls.many = make_product(name='Кресло Много Цветов', colors=colors)
        cls.four = make_product(name='Кресло Четыре Цвета', colors=colors[:4])

    def setUp(self):
        self.root = parse(self.client.get(reverse('catalog_list')))

    def test_more_than_four_colors_shows_plus_n(self):
        card = product_card_for(self.root, self.many)
        self.assertIsNotNone(card, 'cards must have class product-card and link to the product')
        self.assertRegex(card.text, r'\+\s*2(?!\d)')

    def test_four_colors_no_plus(self):
        card = product_card_for(self.root, self.four)
        self.assertNotRegex(card.text, r'\+\s*\d')

    def test_heart_has_aria_pressed(self):
        card = product_card_for(self.root, self.four)
        heart = card.find('button', attrs={'aria-pressed': True})
        self.assertIsNotNone(heart, 'card heart must be a button with aria-pressed')
        self.assertEqual(heart.get('aria-pressed'), 'false')


class E1ProductCardBadgeTests(TestCase):
    """Badges «Новинка» / «Хит» / «Скидка» from is_new / is_bestseller / old_price > price."""

    @classmethod
    def setUpTestData(cls):
        cls.new = make_product(name='Кресло Новое', is_new=True)
        cls.hit = make_product(name='Кресло Хитовое', is_bestseller=True)
        cls.sale = make_product(name='Кресло Акционное', price=45000, old_price=60000)
        cls.plain = make_product(name='Кресло Обычное', old_price=5000, price=10000)

    def setUp(self):
        self.root = parse(self.client.get(reverse('catalog_list')))

    def card(self, product):
        card = product_card_for(self.root, product)
        self.assertIsNotNone(card, product.name)
        return card

    def test_new_badge(self):
        self.assertIn('Новинка', self.card(self.new).text)

    def test_bestseller_badge(self):
        self.assertIn('Хит', self.card(self.hit).text)

    def test_sale_badge_and_old_price_strikethrough(self):
        card = self.card(self.sale)
        self.assertIn('Скидка', card.text)
        s = card.find('s')
        self.assertIsNotNone(s, 'old price must be inside <s>')
        self.assertIn('60000', squash(s.text))

    def test_plain_product_has_no_badges(self):
        text = self.card(self.plain).text
        for badge in ('Новинка', 'Хит', 'Скидка'):
            self.assertNotIn(badge, text)


class E1FooterTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.material = Material.objects.create(name='Ротанг', slug='rotang')
        cls.category = Category.objects.create(name='Кресла', slug='kresla')
        cls.product = make_product(name='Кресло Футер', material=cls.material, category=cls.category)

    def footer(self):
        footer = parse(self.client.get(reverse('home'))).find('footer')
        self.assertIsNotNone(footer)
        return footer

    def test_category_seo_links(self):
        hrefs = [a.get('href') for a in self.footer().find_all('a', attrs={'href': True})]
        self.assertIn(reverse('catalog_by_category', args=['rotang', 'kresla']), hrefs)

    def test_reviews_summary_average_and_count(self):
        Review.objects.create(product=self.product, author='А', rating=5, text='Отлично', is_published=True)
        Review.objects.create(product=self.product, author='Б', rating=4, text='Хорошо', is_published=True)
        Review.objects.create(product=self.product, author='В', rating=1, text='Скрыт', is_published=False)
        block = self.footer().find(attrs={'data-reviews-summary': True})
        self.assertIsNotNone(block, 'expected footer element with data-reviews-summary')
        self.assertRegex(block.text, r'4[.,]5')
        self.assertTrue(has_number(block.text, 2), block.text)

    def test_reviews_summary_hidden_without_reviews(self):
        self.assertIsNone(self.footer().find(attrs={'data-reviews-summary': True}))

    def test_unpublished_reviews_do_not_count(self):
        Review.objects.create(product=self.product, author='В', rating=1, text='Скрыт', is_published=False)
        self.assertIsNone(self.footer().find(attrs={'data-reviews-summary': True}))
