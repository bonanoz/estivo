"""Оставшиеся minor аудита 02.11.2026: вход в админку, страница успеха, лиды, поиск, избранное, отзыв, акции, фото."""
import io
from datetime import timedelta
from unittest import mock

from django.contrib.auth.models import User
from django.contrib.sessions.backends.db import SessionStore
from django.core.cache import cache
from django.core.files.base import ContentFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from PIL import Image

from shop.models import Category, Lead, Material, Order
from shop.storage import compress_image

from .helpers import make_product
from .test_checkout_safety import LEAD_DATA, ORDER_DATA

LOCMEM = {'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}}


@override_settings(CACHES=LOCMEM)
class AdminLoginThrottleTests(TestCase):
    def setUp(self):
        cache.clear()
        User.objects.create_superuser('boss', 'b@example.com', 'right-pass-123')
        self.url = reverse('admin:login')

    def login(self, password):
        return self.client.post(self.url, {'username': 'boss', 'password': password})

    def test_sixth_attempt_after_five_failures_is_blocked(self):
        codes = [self.login('wrong').status_code for _ in range(5)]
        self.assertEqual(codes, [200] * 5)
        self.assertEqual(self.login('right-pass-123').status_code, 429)

    def test_successful_logins_are_not_counted(self):
        for _ in range(6):
            self.assertEqual(self.login('right-pass-123').status_code, 302)
            self.client.logout()


class OrderSuccessTests(TestCase):
    def setUp(self):
        self.product = make_product(price=42000)

    def checkout(self, data=ORDER_DATA):
        self.client.post(reverse('cart_add', args=[self.product.id]))
        with mock.patch('shop.views.notify_telegram', return_value=True):
            return self.client.post(reverse('checkout'), data)

    def test_direct_visit_redirects_home(self):
        self.assertRedirects(self.client.get(reverse('order_success')), reverse('home'))

    def test_after_order_shown_once(self):
        self.checkout()
        self.assertContains(self.client.get(reverse('order_success')), 'Заявка')
        self.assertRedirects(self.client.get(reverse('order_success')), reverse('home'))

    def test_honeypot_gets_same_page(self):
        self.checkout({**ORDER_DATA, 'website': 'http://spam'})
        self.assertEqual(self.client.get(reverse('order_success')).status_code, 200)
        self.assertFalse(Order.objects.exists())

    def test_cart_is_saved_empty_before_telegram(self):
        self.client.post(reverse('cart_add', args=[self.product.id]))
        key = self.client.session.session_key
        seen = {}

        def notify(*args, **kwargs):
            seen['cart'] = SessionStore(session_key=key).load().get('cart')
            return True

        with mock.patch('shop.views.notify_telegram', side_effect=notify):
            self.client.post(reverse('checkout'), ORDER_DATA)
        self.assertFalse(seen['cart'])


class LeadTests(TestCase):
    def post(self, url_name, data, url_suffix=''):
        with mock.patch('shop.views.notify_telegram', return_value=True):
            return self.client.post(reverse(url_name) + url_suffix, data)

    def test_lead_type_comes_from_page(self):
        self.post('b2b_page', {**LEAD_DATA, 'lead_type': 'private'})
        self.assertEqual(Lead.objects.get().lead_type, 'b2b')

    def test_price_request_line_not_duplicated(self):
        product = make_product(name='Кресло Цена', price=0)
        self.post('contacts_page', {**LEAD_DATA, 'price_request_for': product.slug,
                                    'message': 'Узнать цену: Кресло Цена\nНужно два'})
        self.assertEqual(Lead.objects.get().message, 'Узнать цену: Кресло Цена\nНужно два')

    def test_price_request_line_added_when_erased(self):
        product = make_product(name='Кресло Цена', price=0)
        self.post('contacts_page', {**LEAD_DATA, 'price_request_for': product.slug, 'message': 'Нужно два'})
        self.assertEqual(Lead.objects.get().message, 'Узнать цену: Кресло Цена\nНужно два')


class SearchTests(TestCase):
    def test_full_results_find_sku_and_ignore_spaces(self):
        make_product(name='Кресло Артикул', sku='ES-777')
        resp = self.client.get(reverse('catalog_list'), {'search': '  ES-777 '})
        self.assertContains(resp, 'Кресло Артикул')


class WishlistTests(TestCase):
    def test_count_skips_unavailable(self):
        kept, gone = make_product(), make_product()
        for p in (kept, gone):
            self.client.post(reverse('wishlist_toggle', args=[p.id]))
        type(gone).objects.filter(pk=gone.pk).update(is_available=False)
        resp = self.client.get(reverse('home'))
        self.assertEqual(resp.context['wishlist'].count, 1)

    def test_heart_is_a_form_without_js(self):
        product = make_product()
        html = self.client.get(reverse('catalog_list')).content.decode()
        self.assertIn(f'<form method="post" action="{reverse("wishlist_toggle", args=[product.id])}"', html)
        html = self.client.get(product.get_absolute_url()).content.decode()
        self.assertIn(f'<form method="post" action="{reverse("wishlist_toggle", args=[product.id])}" class="pdp-heart"', html)


class CookieBannerTests(TestCase):
    def test_next_keeps_query(self):
        resp = self.client.get(reverse('catalog_list'), {'sort': 'price_asc'})
        self.assertContains(resp, 'name="next" value="/catalog/?sort=price_asc"')


class ReviewFormAriaTests(TestCase):
    def test_errors_linked_to_fields(self):
        product = make_product()
        resp = self.client.post(reverse('review_create', args=[product.slug]), {'author': '', 'rating': 9, 'text': ''},
                                HTTP_HX_REQUEST='true')
        html = resp.content.decode()
        self.assertIn('aria-invalid="true"', html)
        self.assertIn('aria-describedby="id_author-error"', html)
        self.assertIn('id="id_author-error"', html)


class OfferTests(TestCase):
    def setUp(self):
        self.rotang = Material.objects.create(name='Ротанг', slug='rotang')
        self.roup = Material.objects.create(name='Роуп', slug='roup')
        ends = timezone.localdate() + timedelta(days=5)
        self.offer = make_product(name='Акция Ротанг', material=self.rotang, price=9000, old_price=12000,
                                  offer_ends_at=ends)
        make_product(name='Акция Роуп', material=self.roup, price=9000, old_price=12000, offer_ends_at=ends)

    def test_offers_follow_section_and_are_not_repeated(self):
        resp = self.client.get(reverse('catalog_by_material', args=['rotang']), {'flag': 'sale'})
        self.assertEqual([p.name for p in resp.context['offers']], ['Акция Ротанг'])
        self.assertNotIn(self.offer, resp.context['page_obj'].object_list)
        self.assertEqual(resp.context['total_count'], 1)


class PageTextTests(TestCase):
    def test_pdp_has_one_lead_time_line(self):
        html = self.client.get(make_product().get_absolute_url()).content.decode()
        self.assertIn('Отгрузка за 3 дня, если модель есть на складе, иначе изготовление от 4 недель', html)
        self.assertNotIn('В наличии: Отгрузка', html)

    def test_about_h1_is_short(self):
        self.assertContains(self.client.get(reverse('about_page')), 'ESTIVO — плетёная мебель из Тольятти</h1>')


class HugeImageTests(TestCase):
    def test_image_over_pixel_cap_is_kept_as_is(self):
        out = io.BytesIO()
        Image.new('RGB', (300, 200)).save(out, 'PNG')
        with mock.patch('shop.storage.MAX_PIXELS', 1000):
            self.assertIsNone(compress_image(ContentFile(out.getvalue())))
