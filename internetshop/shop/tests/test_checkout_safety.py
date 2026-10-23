"""Checkout и формы: защита от переполнения, спама, потери заявок и лишних сессий."""
from unittest import mock

from django.test import TestCase
from django.urls import reverse

from shop.cart import MAX_QUANTITY
from shop.models import Lead, Order
from shop.tests.helpers import make_product
from shop.utils import TELEGRAM_MAX_LEN, notify_telegram

ORDER_DATA = {
    'customer_name': 'Иван',
    'customer_phone': '+7 900 123-45-67',
    'customer_email': '',
    'delivery_address': 'Тольятти',
    'comment': '',
}
LEAD_DATA = {'name': 'Анна', 'phone': '+7 900 123-45-67', 'email': '', 'lead_type': 'private', 'message': ''}


class CheckoutSafetyTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.product = make_product(name='Кресло Тест', price=42000)

    def checkout(self, data=ORDER_DATA, sent=True):
        with mock.patch('shop.views.notify_telegram', return_value=sent) as notify:
            resp = self.client.post(reverse('checkout'), data)
        return resp, notify

    def test_huge_quantity_is_capped_and_checkout_succeeds(self):
        self.client.post(reverse('cart_add', args=[self.product.id]), {'quantity': 10 ** 12})
        self.client.post(reverse('cart_add', args=[self.product.id]), {'quantity': 5})
        resp, _ = self.checkout()
        self.assertRedirects(resp, reverse('order_success'))
        order = Order.objects.get()
        self.assertEqual(order.items.get().quantity, MAX_QUANTITY)
        self.assertEqual(order.total_price, 42000 * MAX_QUANTITY)

    def test_order_kept_and_cart_cleared_when_telegram_fails(self):
        self.client.post(reverse('cart_add', args=[self.product.id]))
        resp, _ = self.checkout(sent=False)
        self.assertRedirects(resp, reverse('order_success'))
        order = Order.objects.get()
        self.assertEqual(order.items.count(), 1)
        self.assertFalse(order.telegram_notified)
        self.assertFalse(self.client.session.get('cart'))

    def test_honeypot_checkout_creates_nothing(self):
        self.client.post(reverse('cart_add', args=[self.product.id]))
        resp, notify = self.checkout({**ORDER_DATA, 'website': 'http://spam'})
        self.assertRedirects(resp, reverse('order_success'))
        self.assertFalse(Order.objects.exists())
        notify.assert_not_called()

    def test_unavailable_product_is_not_ordered(self):
        self.client.post(reverse('cart_add', args=[self.product.id]))
        type(self.product).objects.filter(pk=self.product.pk).update(is_available=False)
        resp, _ = self.checkout()
        self.assertRedirects(resp, reverse('cart_detail'))
        self.assertFalse(Order.objects.exists())

    def test_header_count_skips_unavailable_product(self):
        other = make_product(name='Кресло Снятое', price=1000)
        self.client.post(reverse('cart_add', args=[self.product.id]))
        self.client.post(reverse('cart_add', args=[other.id]), {'quantity': 3})
        type(other).objects.filter(pk=other.pk).update(is_available=False)
        resp = self.client.get(reverse('cart_detail'))
        self.assertEqual(resp.context['cart'].count, 1)

    def test_invalid_email_rejected(self):
        self.client.post(reverse('cart_add', args=[self.product.id]))
        resp, _ = self.checkout({**ORDER_DATA, 'customer_email': 'abc'})
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(Order.objects.exists())


class LeadSpamTests(TestCase):
    def test_honeypot_lead_creates_nothing(self):
        with mock.patch('shop.views.notify_telegram') as notify:
            resp = self.client.post(reverse('contacts_page'), {**LEAD_DATA, 'website': 'x'})
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(Lead.objects.exists())
        notify.assert_not_called()


class SessionTests(TestCase):
    def test_anonymous_visit_does_not_create_session(self):
        make_product(name='Кресло Тест', price=42000)
        resp = self.client.get(reverse('catalog_list'))
        self.assertEqual(resp.status_code, 200)
        self.assertNotIn('sessionid', resp.cookies)


class TelegramTests(TestCase):
    def test_long_message_is_truncated(self):
        with mock.patch('shop.utils.bot.send_message') as send:
            self.assertTrue(notify_telegram('я' * 10000))
        self.assertLessEqual(len(send.call_args.args[1]), TELEGRAM_MAX_LEN)
