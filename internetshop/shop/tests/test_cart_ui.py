"""E5: cart drawer fragment, /cart/ stepper + undo toast + empty state, reduced checkout, order success, wishlist page."""
from django.test import TestCase
from django.urls import reverse

from shop.context_processors import SITE_INFO
from shop.models import Category

from .helpers import make_product, parse, product_hrefs

HX = {'HTTP_HX_REQUEST': 'true'}
UNDO_URL = '/cart/undo/'
WISHLIST_URL = '/wishlist/'


class E5DrawerTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.kresla = Category.objects.create(name='Кресла', slug='kresla')
        cls.stoly = Category.objects.create(name='Столы', slug='stoly')
        cls.product = make_product(name='Кресло Дровер', category=cls.kresla)
        cls.same_category = [make_product(name=f'Кресло Похожее {i}', category=cls.kresla) for i in range(6)]
        cls.other_category = make_product(name='Стол Чужой', category=cls.stoly)

    def setUp(self):
        resp = self.client.post(reverse('cart_add', args=[self.product.id]), **HX)
        self.assertEqual(resp.status_code, 200)
        self.root = parse(resp)
        self.dialog = self.root.find(attrs={'role': 'dialog'})

    def test_dialog_semantics(self):
        self.assertIsNotNone(self.dialog, 'drawer fragment needs role="dialog"')
        self.assertEqual(self.dialog.get('aria-modal'), 'true')
        labelledby = self.dialog.get('aria-labelledby')
        self.assertTrue(labelledby)
        self.assertIsNotNone(self.root.get_by_id(labelledby), 'aria-labelledby must point to an element in the fragment')

    def test_close_button(self):
        close = self.dialog.find('button', pred=lambda n: bool(n.get('aria-label', '').strip()))
        self.assertIsNotNone(close, 'drawer needs a close button with aria-label')

    def test_checkout_and_continue_actions(self):
        hrefs = [a.get('href') for a in self.dialog.find_all('a', attrs={'href': True})]
        self.assertIn(reverse('checkout'), hrefs)
        self.assertIn('Продолжить покупки', self.dialog.text)

    def test_recommendations_up_to_four_same_category(self):
        recos = product_hrefs(self.dialog) - {self.product.get_absolute_url()}
        same = {p.get_absolute_url() for p in self.same_category}
        self.assertTrue(recos, 'expected «Вам может понравиться» products')
        self.assertLessEqual(len(recos), 4)
        self.assertTrue(recos <= same, recos)
        self.assertIn('Вам может понравиться', self.dialog.text)


class E5CartPageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.product = make_product(name='Кресло Корзинное', price=20000)

    def add(self, quantity=2):
        self.client.post(reverse('cart_add', args=[self.product.id]), {'quantity': quantity})
        return next(iter(self.client.session['cart']))

    def test_stepper_buttons(self):
        self.add()
        root = parse(self.client.get(reverse('cart_detail')))
        for label in ('Уменьшить', 'Увеличить'):
            btn = root.find('button', attrs={'aria-label': label})
            self.assertIsNotNone(btn, label)
            owner = btn.closest(pred=lambda n: n.has_attr('hx-post'))
            self.assertIsNotNone(owner, f'{label}: needs hx-post (on button or its form)')
            self.assertEqual(owner.get('hx-post'), reverse('cart_update'))

    def test_quantity_zero_removes_line(self):
        line_id = self.add()
        resp = self.client.post(reverse('cart_update'), {'line_id': line_id, 'quantity': 0}, **HX)
        self.assertEqual(resp.status_code, 200)
        self.assertNotIn(line_id, self.client.session['cart'])

    def test_htmx_update_returns_html(self):
        line_id = self.add()
        resp = self.client.post(reverse('cart_update'), {'line_id': line_id, 'quantity': 3}, **HX)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp['Content-Type'].startswith('text/html'))
        self.assertEqual(self.client.session['cart'][line_id]['quantity'], 3)

    def test_remove_shows_undo_toast(self):
        line_id = self.add()
        resp = self.client.post(reverse('cart_remove'), {'line_id': line_id}, **HX)
        self.assertEqual(resp.status_code, 200)
        root = parse(resp)
        undo = root.find(pred=lambda n: n.get('hx-post') == UNDO_URL or (
            n.tag == 'form' and n.get('action') == UNDO_URL and n.get('method', '').lower() == 'post'))
        self.assertIsNotNone(undo, 'toast needs a POST /cart/undo/ form')
        container = undo.closest('form') or undo
        self.assertIn('Вернуть', container.text)

    def test_empty_cart_state(self):
        resp = self.client.get(reverse('cart_detail'))
        main = parse(resp).find('main')
        links = [a for a in main.find_all('a', attrs={'href': reverse('catalog_list')})
                 if 'Продолжить покупки' in a.text]
        self.assertTrue(links, 'empty cart needs «Продолжить покупки» link to the catalog')


class E5EmptyCartRecommendationsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.hit = make_product(name='Кресло Хит Корзины', is_bestseller=True)

    def test_empty_cart_shows_bestsellers(self):
        main = parse(self.client.get(reverse('cart_detail'))).find('main')
        self.assertIn(self.hit.get_absolute_url(), product_hrefs(main))


class E5CheckoutTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.product = make_product(name='Кресло Чекаут', price=42000)

    def setUp(self):
        self.client.post(reverse('cart_add', args=[self.product.id]))
        resp = self.client.get(reverse('checkout'))
        self.assertEqual(resp.status_code, 200)
        self.root = parse(resp)

    def test_reduced_header(self):
        self.assertIsNone(self.root.find('nav', attrs={'aria-label': 'Основная навигация'}))
        self.assertIsNone(self.root.find('button', attrs={'aria-label': 'Поиск'}))
        self.assertIsNone(self.root.find(pred=lambda n: '/search/suggest/' in n.get('hx-get', '')))

    def test_logo_phone_and_messengers(self):
        hrefs = [a.get('href', '') for a in self.root.find_all('a')]
        self.assertIn(reverse('home'), hrefs)
        self.assertTrue(any(h.startswith('tel:') for h in hrefs))
        self.assertIn(SITE_INFO['social_links']['telegram'], hrefs)
        self.assertIn(SITE_INFO['social_links']['whatsapp'], hrefs)

    def test_order_summary_and_form(self):
        main = self.root.find('main')
        self.assertIn('Кресло Чекаут', main.text)
        for name in ('customer_name', 'customer_phone'):
            self.assertIsNotNone(main.find(pred=lambda n, nm=name: n.get('name') == nm), name)


class E5OrderSuccessTests(TestCase):
    def test_next_step_link_to_catalog(self):
        main = parse(self.client.get(reverse('order_success'))).find('main')
        self.assertIsNotNone(main.find('a', attrs={'href': reverse('catalog_list')}))


class E5WishlistPageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.product = make_product(name='Кресло Вишлист')

    def test_uses_shared_product_card(self):
        self.client.post(f'/wishlist/toggle/{self.product.id}/', **HX)
        resp = self.client.get(WISHLIST_URL)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'partials/_product_card.html')
        self.assertIn(self.product.get_absolute_url(), product_hrefs(parse(resp).find('main')))
