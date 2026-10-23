"""E2: HTMX branch of cart_add (drawer fragment), POST /cart/undo/, PDP colour preselection from GET."""
from django.test import TestCase
from django.urls import reverse

from shop.models import Category, ColorOption

from .helpers import make_product, parse, squash

HX = {'HTTP_HX_REQUEST': 'true'}
UNDO_URL = '/cart/undo/'


class E2CartAddHtmxTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name='Кресла', slug='kresla')
        cls.product = make_product(name='Кресло Драйвер', price=42000, category=cls.category)

    def test_htmx_add_returns_drawer_fragment(self):
        resp = self.client.post(reverse('cart_add', args=[self.product.id]), {'quantity': 2}, **HX)
        self.assertEqual(resp.status_code, 200)
        html = resp.content.decode()
        self.assertTrue(resp['Content-Type'].startswith('text/html'))
        self.assertNotIn('<html', html.lower(), 'HTMX response must be a fragment')
        self.assertIn('Кресло Драйвер', html)
        self.assertIn('84000', squash(parse(resp).text), 'drawer must show the cart total')
        self.assertEqual(next(iter(self.client.session['cart'].values()))['quantity'], 2)

    def test_plain_post_still_redirects(self):
        resp = self.client.post(reverse('cart_add', args=[self.product.id]))
        self.assertRedirects(resp, reverse('cart_detail'), fetch_redirect_response=False)

    def test_checkout_button_still_redirects_to_checkout(self):
        resp = self.client.post(reverse('cart_add', args=[self.product.id]), {'checkout': '1'})
        self.assertRedirects(resp, reverse('checkout'), fetch_redirect_response=False)


class E2CartUndoTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.weave = ColorOption.objects.create(name='Графит', finish_type=ColorOption.WEAVE, hex='#3b3a36')
        cls.product = make_product(name='Кресло Андо', price=30000, colors=[cls.weave])
        cls.other = make_product(name='Стол Андо', price=10000)

    def test_remove_then_undo_restores_line(self):
        self.client.post(reverse('cart_add', args=[self.product.id]),
                         {'color_weave': self.weave.id, 'quantity': 3})
        self.client.post(reverse('cart_add', args=[self.other.id]))
        cart_before = dict(self.client.session['cart'])
        line_id = next(k for k, v in cart_before.items() if v['product_id'] == self.product.id)

        self.client.post(reverse('cart_remove'), {'line_id': line_id})
        self.assertNotIn(line_id, self.client.session['cart'])

        resp = self.client.post(UNDO_URL)
        self.assertLess(resp.status_code, 400)
        cart = self.client.session['cart']
        self.assertIn(line_id, cart)
        self.assertEqual(cart[line_id]['quantity'], 3)
        self.assertEqual(cart[line_id]['colors'], {'weave': self.weave.id})
        self.assertEqual(len(cart), 2)

    def test_undo_via_htmx_remove(self):
        self.client.post(reverse('cart_add', args=[self.product.id]), {'quantity': 2})
        line_id = next(iter(self.client.session['cart']))
        self.client.post(reverse('cart_remove'), {'line_id': line_id}, **HX)
        self.client.post(UNDO_URL, **HX)
        cart = self.client.session['cart']
        self.assertIn(line_id, cart)
        self.assertEqual(cart[line_id]['quantity'], 2)

    def test_undo_with_nothing_removed_is_harmless(self):
        resp = self.client.post(UNDO_URL)
        self.assertLess(resp.status_code, 400)
        self.assertFalse(self.client.session.get('cart'))


class E2PdpColorPreselectTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.weave1 = ColorOption.objects.create(name='Графит', finish_type=ColorOption.WEAVE, hex='#3b3a36')
        cls.weave2 = ColorOption.objects.create(name='Мокко', finish_type=ColorOption.WEAVE, hex='#6f5b45')
        cls.cushion = ColorOption.objects.create(name='Беж', finish_type=ColorOption.CUSHION, hex='#d9cbb3')
        cls.cushion2 = ColorOption.objects.create(name='Олива', finish_type=ColorOption.CUSHION, hex='#6b6f4f')
        cls.foreign = ColorOption.objects.create(name='Чужой', finish_type=ColorOption.WEAVE, hex='#000000')
        cls.product = make_product(name='Кресло Пресет',
                                   colors=[cls.weave1, cls.weave2, cls.cushion, cls.cushion2])

    def radios(self, params, finish_type):
        resp = self.client.get(self.product.get_absolute_url() + params)
        self.assertEqual(resp.status_code, 200)
        return parse(resp).find_all('input', attrs={'type': 'radio', 'name': f'color_{finish_type}'})

    def checked_values(self, radios):
        return [r.get('value') for r in radios if r.has_attr('checked')]

    def test_weave_preselected_from_get(self):
        radios = self.radios(f'?weave={self.weave2.id}', 'weave')
        self.assertEqual(self.checked_values(radios), [str(self.weave2.id)])

    def test_cushion_preselected_from_get(self):
        radios = self.radios(f'?weave={self.weave2.id}&cushion={self.cushion2.id}', 'cushion')
        self.assertEqual(self.checked_values(radios), [str(self.cushion2.id)])

    def test_foreign_id_ignored(self):
        radios = self.radios(f'?weave={self.foreign.id}', 'weave')
        values = [r.get('value') for r in radios]
        self.assertNotIn(str(self.foreign.id), values)
        self.assertEqual(len(self.checked_values(radios)), 1)

    def test_id_of_other_finish_type_ignored(self):
        radios = self.radios(f'?weave={self.cushion2.id}', 'weave')
        self.assertEqual(len(self.checked_values(radios)), 1)
        self.assertIn(self.checked_values(radios)[0], {str(self.weave1.id), str(self.weave2.id)})

    def test_garbage_ignored(self):
        radios = self.radios('?weave=abc&frame=', 'weave')
        self.assertEqual(len(self.checked_values(radios)), 1)
