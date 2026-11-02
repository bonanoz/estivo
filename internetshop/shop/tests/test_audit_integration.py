"""Сведение audit-fixes (E1 + E3 + views): подпись уведомления и стык лимита с htmx-отзывом.

Красные до сведения — ожидаемо: ни один воркер эти тесты не чинит, их закрывает оркестратор.
"""
import logging
from unittest import mock

from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse

from shop.models import Lead, Order
from shop.tests.helpers import make_product
from shop.tests.helpers_audit import VALID_TOKEN, add_to_cart, telegram_env

ORDER_DATA = {
    'customer_name': 'Иван Секретов', 'customer_phone': '+7 900 111-22-33', 'customer_email': '',
    'delivery_address': 'Тольятти', 'comment': '',
}
LEAD_DATA = {'name': 'Анна Секретова', 'phone': '+7 900 111-22-33', 'email': '', 'lead_type': 'private', 'message': ''}
REVIEW = {'author': 'Ольга', 'rating': '5', 'usage_duration': '', 'text': 'Хорошее кресло, всем советую', 'website': ''}
HX = {'HTTP_HX_REQUEST': 'true'}


def failing_telegram():
    return mock.patch('telebot.TeleBot.send_message', side_effect=RuntimeError('boom'))


class NotificationLabelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.product = make_product(name='Кресло Тест', price=42000)

    def assert_no_personal_data(self, logs):
        formatter = logging.Formatter()
        for record in logs.records:
            rendered = formatter.format(record)
            for secret in ('Секретов', 'Секретова', '900 111', 'Тольятти'):
                self.assertNotIn(secret, rendered)

    def test_audit_failed_order_notification_names_the_order(self):
        with telegram_env(BOT_TOKEN=VALID_TOKEN, CHAT_ID='42'), failing_telegram(), \
                self.assertLogs('shop', level='WARNING') as logs:
            add_to_cart(self.client, self.product)
            resp = self.client.post(reverse('checkout'), ORDER_DATA)
        self.assertRedirects(resp, reverse('order_success'))
        order = Order.objects.get()
        self.assertFalse(order.telegram_notified)
        self.assertTrue(any(f'заявка №{order.id}' in r.getMessage() for r in logs.records), logs.output)
        self.assert_no_personal_data(logs)

    def test_audit_failed_lead_notification_names_the_lead(self):
        with telegram_env(BOT_TOKEN=VALID_TOKEN, CHAT_ID='42'), failing_telegram(), \
                self.assertLogs('shop', level='WARNING') as logs:
            resp = self.client.post(reverse('contacts_page'), LEAD_DATA)
        self.assertRedirects(resp, reverse('contacts_page'))
        lead = Lead.objects.get()
        self.assertFalse(lead.telegram_notified)
        self.assertTrue(any(f'лид №{lead.id}' in r.getMessage() for r in logs.records), logs.output)
        self.assert_no_personal_data(logs)

    def test_audit_lead_label_on_b2b_and_designers_pages(self):
        for url_name in ('b2b_page', 'designers_page'):
            with self.subTest(page=url_name), telegram_env(BOT_TOKEN=VALID_TOKEN, CHAT_ID='42'), \
                    failing_telegram(), self.assertLogs('shop', level='WARNING') as logs:
                self.client.post(reverse(url_name), LEAD_DATA)
                lead = Lead.objects.latest('id')
            self.assertTrue(any(f'лид №{lead.id}' in r.getMessage() for r in logs.records), logs.output)

    def test_audit_successful_notification_writes_no_warning(self):
        with telegram_env(BOT_TOKEN=VALID_TOKEN, CHAT_ID='42'), mock.patch('telebot.TeleBot.send_message'):
            with self.assertNoLogs('shop', level='WARNING'):
                add_to_cart(self.client, self.product)
                self.client.post(reverse('checkout'), ORDER_DATA)
        self.assertTrue(Order.objects.get().telegram_notified)


@override_settings(CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}})
class ReviewThrottleJoinTests(TestCase):
    """Стык E1 и E3: htmx-отзыв с ошибкой не тратит лимит, успешный тратит."""

    @classmethod
    def setUpTestData(cls):
        cls.product = make_product(name='Кресло Отзывное', slug='kreslo-otzyvnoe')

    def setUp(self):
        cache.clear()
        self.url = f'/product/{self.product.slug}/review/'

    def test_audit_invalid_htmx_reviews_never_hit_the_limit(self):
        codes = [self.client.post(self.url, {**REVIEW, 'text': ''}, **HX).status_code for _ in range(7)]
        self.assertEqual(codes, [200] * 7)

    def test_audit_sixth_successful_htmx_review_is_limited(self):
        codes = [self.client.post(self.url, REVIEW, **HX).status_code for _ in range(5)]
        self.assertEqual(codes, [200] * 5)
        self.assertEqual(self.client.post(self.url, REVIEW, **HX).status_code, 429)

    def test_audit_plain_review_posts_count_as_redirects(self):
        codes = [self.client.post(self.url, REVIEW).status_code for _ in range(5)]
        self.assertEqual(codes, [302] * 5)
        self.assertEqual(self.client.post(self.url, REVIEW).status_code, 429)
