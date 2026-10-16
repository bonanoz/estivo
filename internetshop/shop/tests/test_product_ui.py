"""E4: product page UI — buy button, swatch fieldsets, reviews section + form, trust block, 3D, JSON-LD, heart."""
from django.test import TestCase
from django.urls import reverse

from shop.models import Category, ColorOption, Material, Review

from .helpers import has_number, json_ld_objects, make_product, parse, squash

HX = {'HTTP_HX_REQUEST': 'true'}


def find_product_ld(root):
    for obj in json_ld_objects(root):
        types = obj.get('@type')
        if types == 'Product' or (isinstance(types, list) and 'Product' in types):
            return obj
    return None


class E4ProductPageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.material = Material.objects.create(name='Ротанг', slug='rotang')
        cls.category = Category.objects.create(name='Кресла', slug='kresla')
        cls.weave1 = ColorOption.objects.create(name='Графит', finish_type=ColorOption.WEAVE, hex='#3b3a36')
        cls.weave2 = ColorOption.objects.create(name='Мокко', finish_type=ColorOption.WEAVE, hex='#6f5b45')
        cls.cushion = ColorOption.objects.create(name='Беж', finish_type=ColorOption.CUSHION, hex='#d9cbb3')
        cls.product = make_product(
            name='Кресло Витрина', slug='kreslo-vitrina', price=45000, warranty_years=17,
            material=cls.material, category=cls.category,
            colors=[cls.weave1, cls.weave2, cls.cushion],
        )

    def setUp(self):
        self.resp = self.client.get(self.product.get_absolute_url())
        self.assertEqual(self.resp.status_code, 200)
        self.root = parse(self.resp)

    def add_button(self):
        cart_url = reverse('cart_add', args=[self.product.id])
        for btn in self.root.find_all('button'):
            if 'В корзину' in btn.text and btn.closest('form', attrs={'action': cart_url}):
                return btn
        return None

    def test_add_button_shows_price_and_posts_via_htmx(self):
        btn = self.add_button()
        self.assertIsNotNone(btn, 'expected «В корзину» button inside <form action="cart_add">')
        self.assertIn('45000', squash(btn.text), 'button text must include the price')
        cart_url = reverse('cart_add', args=[self.product.id])
        hx_owner = btn.closest(pred=lambda n: n.has_attr('hx-post'))
        self.assertIsNotNone(hx_owner, 'button or its form needs hx-post')
        self.assertEqual(hx_owner.get('hx-post'), cart_url)

    def test_add_form_works_without_js(self):
        form = self.add_button().closest('form')
        self.assertEqual(form.get('method', '').lower(), 'post')
        self.assertIsNotNone(form.find('input', attrs={'name': 'csrfmiddlewaretoken'}))

    def test_checkout_button_kept(self):
        self.assertIsNotNone(self.root.find('button', attrs={'name': 'checkout'}))

    def test_swatches_are_radio_groups_in_fieldsets(self):
        for finish_type in ('weave', 'cushion'):
            radios = self.root.find_all('input', attrs={'type': 'radio', 'name': f'color_{finish_type}'})
            self.assertTrue(radios, finish_type)
            for radio in radios:
                fieldset = radio.closest('fieldset')
                self.assertIsNotNone(fieldset, f'{finish_type} radios must be inside <fieldset>')
                self.assertIsNotNone(fieldset.find('legend'), f'{finish_type} fieldset needs <legend>')
        self.assertIsNone(self.root.find('input', attrs={'name': 'color_frame'}), 'empty groups are skipped')

    def test_color_label_element(self):
        labels = self.root.find_all(attrs={'data-color-label': True})
        self.assertTrue(labels, 'expected element(s) with data-color-label')
        self.assertTrue(any('Графит' in lbl.text for lbl in labels))
        weave_fieldset = self.root.find('input', attrs={'name': 'color_weave'}).closest('fieldset')
        self.assertIn('Плетение', weave_fieldset.find('legend').text)

    def test_trust_block_shows_warranty(self):
        self.assertIn('17', self.root.find('main').text)

    def test_heart_on_pdp(self):
        heart = self.root.find(pred=lambda n: n.get('hx-post') == f'/wishlist/toggle/{self.product.id}/')
        self.assertIsNotNone(heart, 'PDP heart needs hx-post to /wishlist/toggle/<id>/')
        pressed = heart.closest(pred=lambda n: n.has_attr('aria-pressed')) or heart.find(attrs={'aria-pressed': True})
        self.assertIsNotNone(pressed, 'PDP heart must expose aria-pressed')

    def test_no_model_viewer_without_model(self):
        self.assertIsNone(self.root.find('model-viewer'))
        srcs = [s.get('src', '') for s in self.root.find_all('script')]
        self.assertFalse(any('model-viewer' in s for s in srcs))

    def test_json_ld_product_without_reviews(self):
        ld = find_product_ld(self.root)
        self.assertIsNotNone(ld, 'expected JSON-LD with @type Product')
        self.assertEqual(ld['name'], 'Кресло Витрина')
        offers = ld['offers'][0] if isinstance(ld['offers'], list) else ld['offers']
        self.assertEqual(float(offers['price']), 45000)
        self.assertEqual(offers['priceCurrency'], 'RUB')
        self.assertNotIn('aggregateRating', ld)


class E4ReviewsSectionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.product = make_product(name='Кресло Рейтинг', slug='kreslo-reiting', price=30000)
        Review.objects.create(product=cls.product, author='Анна', rating=5, text='Публичный один', is_published=True)
        Review.objects.create(product=cls.product, author='Борис', rating=4, text='Публичный два', is_published=True)
        Review.objects.create(product=cls.product, author='Вера', rating=1, text='Скрытый отзыв', is_published=False)

    def setUp(self):
        self.root = parse(self.client.get(self.product.get_absolute_url()))

    def test_rating_link_and_reviews_section(self):
        self.assertIsNotNone(self.root.find('a', attrs={'href': '#reviews'}), 'expected rating link to #reviews')
        section = self.root.get_by_id('reviews')
        self.assertIsNotNone(section, 'expected element id="reviews"')
        self.assertRegex(section.text, r'4[.,]5')
        self.assertTrue(has_number(section.text, 2), section.text)
        self.assertIn('Публичный один', section.text)
        self.assertNotIn('Скрытый отзыв', self.root.text)

    def test_review_form_fields_and_honeypot(self):
        action = f'/product/{self.product.slug}/review/'
        form = self.root.find('form', pred=lambda n: action in (n.get('action', ''), n.get('hx-post', '')))
        self.assertIsNotNone(form, 'expected review form posting to /product/<slug>/review/')
        for name in ('author', 'rating', 'text'):
            self.assertIsNotNone(form.find(pred=lambda n, nm=name: n.get('name') == nm), name)
        honeypot = form.find('input', attrs={'name': 'website'})
        self.assertIsNotNone(honeypot, 'expected honeypot input name="website"')
        hidden = honeypot.get('type') == 'hidden' or honeypot.closest(
            pred=lambda n: n.has_attr('hidden') or n.get('aria-hidden') == 'true' or n.get('tabindex') == '-1'
        ) is not None
        self.assertTrue(hidden, 'honeypot must be hidden from users (type=hidden / hidden / aria-hidden / tabindex=-1)')

    def test_review_form_submits_via_htmx(self):
        action = f'/product/{self.product.slug}/review/'
        self.assertIsNotNone(self.root.find(pred=lambda n: n.get('hx-post') == action))
        resp = self.client.post(action, {'author': 'Гость', 'rating': '5', 'text': 'Хорошо', 'website': ''}, **HX)
        self.assertEqual(resp.status_code, 200)
        self.assertIn('модерац', resp.content.decode().lower())

    def test_json_ld_aggregate_rating(self):
        ld = find_product_ld(self.root)
        self.assertIsNotNone(ld)
        agg = ld['aggregateRating']
        self.assertAlmostEqual(float(agg['ratingValue']), 4.5)
        self.assertEqual(int(agg.get('reviewCount', agg.get('ratingCount'))), 2)
