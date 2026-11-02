"""E1 (audit-fixes): эксплуатация — Telegram, логи, БД, хосты, поля форм.

Лимит POST проверяется в test_throttle.py.
"""
import json
import logging
import os
import subprocess
import sys
from pathlib import Path
from unittest import mock

from django.conf import settings
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from shop.forms import LeadForm, OrderForm
from shop.models import Lead, Order
from shop.tests.helpers import make_product, parse
from shop.tests.helpers_audit import VALID_TOKEN, add_to_cart, telegram_env
from shop.utils import notify_telegram

ORDER_DATA = {
    'customer_name': 'Иван',
    'customer_phone': '+7 900 123-45-67',
    'customer_email': '',
    'delivery_address': 'Тольятти',
    'comment': '',
}
LEAD_DATA = {'name': 'Анна', 'phone': '+7 900 123-45-67', 'email': '', 'lead_type': 'private', 'message': ''}
LEAD_PAGES = ['contacts_page', 'b2b_page', 'designers_page']
BASE_DIR = Path(settings.BASE_DIR)


def run_settings(**env):
    """Загружает internetshop.settings в отдельном процессе с подменёнными переменными окружения.

    Отдельный процесс: настройки текущего прогона тестов не затрагиваются.
    """
    code = (
        'import json, sys; sys.path.insert(0, sys.argv[1]);'
        'import internetshop.settings as s;'
        'print(json.dumps({"ALLOWED_HOSTS": s.ALLOWED_HOSTS, "CSRF": s.CSRF_TRUSTED_ORIGINS,'
        '"DB": {k: v for k, v in s.DATABASES["default"].items() if k in ("CONN_MAX_AGE", "CONN_HEALTH_CHECKS")}}))'
    )
    full_env = {**os.environ, 'DEBUG': 'True', **env}
    out = subprocess.run([sys.executable, '-c', code, str(BASE_DIR)], env=full_env,
                         capture_output=True, text=True, timeout=120, cwd=str(BASE_DIR))
    assert out.returncode == 0, out.stderr[-2000:]
    return json.loads(out.stdout.strip().splitlines()[-1])


class E1TelegramImportTests(SimpleTestCase):
    """Сайт не падает при пустом, отсутствующем или кривом токене."""

    def assert_imports(self, **env):
        with telegram_env(**env):
            import shop.utils
            self.assertTrue(callable(shop.utils.notify_telegram))

    def test_e1_import_survives_empty_token(self):
        self.assert_imports(BOT_TOKEN='', CHAT_ID='42')

    def test_e1_import_survives_missing_token(self):
        self.assert_imports(BOT_TOKEN=None, CHAT_ID='42')

    def test_e1_import_survives_token_without_colon(self):
        self.assert_imports(BOT_TOKEN='garbage', CHAT_ID='42')

    def test_e1_import_survives_empty_chat_id(self):
        self.assert_imports(BOT_TOKEN=VALID_TOKEN, CHAT_ID='')

    def test_e1_import_survives_missing_chat_id(self):
        self.assert_imports(BOT_TOKEN=VALID_TOKEN, CHAT_ID=None)


class E1NotifyTelegramTests(SimpleTestCase):
    def test_e1_empty_token_returns_false_without_network(self):
        with telegram_env(BOT_TOKEN='', CHAT_ID='42'), \
                mock.patch('telebot.TeleBot.send_message') as send, \
                mock.patch('requests.sessions.Session.request') as http:
            self.assertIs(notify_telegram('текст'), False)
        send.assert_not_called()
        http.assert_not_called()

    def test_e1_garbage_token_returns_false_without_network(self):
        with telegram_env(BOT_TOKEN='garbage', CHAT_ID='42'), \
                mock.patch('telebot.TeleBot.send_message') as send, \
                mock.patch('requests.sessions.Session.request') as http:
            self.assertIs(notify_telegram('текст'), False)
        send.assert_not_called()
        http.assert_not_called()

    def test_e1_empty_chat_id_returns_false_without_network(self):
        for chat in ('', None):
            with self.subTest(chat=chat), telegram_env(BOT_TOKEN=VALID_TOKEN, CHAT_ID=chat), \
                    mock.patch('telebot.TeleBot.send_message') as send, \
                    mock.patch('requests.sessions.Session.request') as http:
                self.assertIs(notify_telegram('текст'), False)
                send.assert_not_called()
                http.assert_not_called()

    def test_e1_empty_token_logs_not_configured_warning(self):
        with telegram_env(BOT_TOKEN='', CHAT_ID='42'), self.assertLogs('shop', level='WARNING') as logs:
            notify_telegram('текст')
        self.assertTrue(any('telegram' in r.getMessage().lower() for r in logs.records), logs.output)
        self.assertTrue(all(r.levelno == logging.WARNING for r in logs.records), logs.output)

    def test_e1_empty_chat_id_logs_warning(self):
        with telegram_env(BOT_TOKEN=VALID_TOKEN, CHAT_ID=''), self.assertLogs('shop', level='WARNING') as logs:
            notify_telegram('текст')
        self.assertTrue(any('telegram' in r.getMessage().lower() for r in logs.records), logs.output)

    def test_e1_send_failure_logs_warning_with_label_and_traceback(self):
        with telegram_env(BOT_TOKEN=VALID_TOKEN, CHAT_ID='42'), \
                mock.patch('telebot.TeleBot.send_message', side_effect=RuntimeError('boom')), \
                self.assertLogs('shop', level='WARNING') as logs:
            result = notify_telegram('текст', label='заявка №4')
        self.assertIs(result, False)
        record = logs.records[0]
        self.assertEqual(record.levelno, logging.WARNING)
        self.assertIn('заявка №4', record.getMessage())
        self.assertTrue(record.exc_info, 'в записи должен быть трейсбэк (exc_info)')

    def test_e1_send_failure_without_label_says_no_number(self):
        with telegram_env(BOT_TOKEN=VALID_TOKEN, CHAT_ID='42'), \
                mock.patch('telebot.TeleBot.send_message', side_effect=RuntimeError('boom')), \
                self.assertLogs('shop', level='WARNING') as logs:
            self.assertIs(notify_telegram('текст'), False)
        self.assertIn('без номера', logs.records[0].getMessage())

    def test_e1_log_has_no_personal_data(self):
        text = '📩 Новая заявка\nИмя: Иван Петров\nТелефон: +7 900 111-22-33\nEmail: ivan@example.com'
        with telegram_env(BOT_TOKEN=VALID_TOKEN, CHAT_ID='42'), \
                mock.patch('telebot.TeleBot.send_message', side_effect=RuntimeError('boom')), \
                self.assertLogs('shop', level='WARNING') as logs:
            notify_telegram(text, label='лид №7')
        formatter = logging.Formatter()
        for record in logs.records:
            rendered = formatter.format(record)
            for secret in ('Иван', 'Петров', '900 111', 'ivan@example.com'):
                self.assertNotIn(secret, rendered)

    def test_e1_network_error_with_url_does_not_leak_token_or_pd_into_log(self):
        import requests
        import shop.utils
        leak = '/bot123:SECRETTOKEN/sendMessage?text=Иван +79990001122'
        try:
            try:
                raise OSError(leak)
            except OSError as inner:
                raise requests.exceptions.ConnectionError(leak) from inner
        except requests.exceptions.ConnectionError as err:
            error = err
        with telegram_env(BOT_TOKEN=VALID_TOKEN, CHAT_ID='42'),                 mock.patch.object(shop.utils.bot, 'send_message', side_effect=error),                 self.assertLogs('shop', level='WARNING') as logs:
            self.assertIs(notify_telegram('текст', label='заявка №4'), False)
        record = logs.records[0]
        self.assertTrue(record.exc_info, 'трейсбэк должен остаться')
        rendered = logging.Formatter().format(record)
        self.assertIn('Traceback', rendered)
        for secret in ('SECRETTOKEN', 'Иван', '79990001122'):
            self.assertNotIn(secret, rendered)

    def test_e1_success_returns_true_and_does_not_warn(self):
        with telegram_env(BOT_TOKEN=VALID_TOKEN, CHAT_ID='42'), \
                mock.patch('telebot.TeleBot.send_message') as send:
            with self.assertNoLogs('shop', level='WARNING'):
                self.assertIs(notify_telegram('текст', label='заявка №1'), True)
        send.assert_called_once()


class E1ServerWithoutTelegramTests(TestCase):
    """Заявки и лиды принимаются без настроенного Telegram."""

    @classmethod
    def setUpTestData(cls):
        cls.product = make_product(name='Кресло Тест', price=42000)

    def test_e1_order_saved_without_token(self):
        with telegram_env(BOT_TOKEN='', CHAT_ID=''), \
                mock.patch('telebot.TeleBot.send_message') as send:
            add_to_cart(self.client, self.product)
            resp = self.client.post(reverse('checkout'), ORDER_DATA)
        self.assertRedirects(resp, reverse('order_success'))
        order = Order.objects.get()
        self.assertFalse(order.telegram_notified)
        self.assertEqual(order.items.count(), 1)
        send.assert_not_called()
        self.assertEqual(self.client.get(reverse('order_success')).status_code, 200)

    def test_e1_order_saved_with_garbage_token(self):
        with telegram_env(BOT_TOKEN='garbage', CHAT_ID='42'):
            add_to_cart(self.client, self.product)
            resp = self.client.post(reverse('checkout'), ORDER_DATA)
        self.assertRedirects(resp, reverse('order_success'))
        self.assertFalse(Order.objects.get().telegram_notified)

    def test_e1_lead_saved_without_token(self):
        with telegram_env(BOT_TOKEN='', CHAT_ID=''), mock.patch('telebot.TeleBot.send_message') as send:
            resp = self.client.post(reverse('contacts_page'), LEAD_DATA)
        self.assertRedirects(resp, reverse('contacts_page'))
        self.assertFalse(Lead.objects.get().telegram_notified)
        send.assert_not_called()


class E1LoggingAndSettingsTests(SimpleTestCase):
    def test_e1_logging_config_has_console_handler_for_django_and_shop(self):
        config = settings.LOGGING
        console = [name for name, h in config['handlers'].items() if h.get('class') == 'logging.StreamHandler']
        self.assertTrue(console, 'нужен консольный обработчик logging.StreamHandler')
        for name in ('django', 'shop'):
            with self.subTest(logger=name):
                logger_cfg = config['loggers'][name]
                self.assertEqual(logger_cfg['level'], 'WARNING')
                self.assertTrue(set(logger_cfg['handlers']) & set(console))

    def test_e1_shop_logger_is_wired_to_a_stream_handler(self):
        logger = logging.getLogger('shop')
        self.assertLessEqual(logger.getEffectiveLevel(), logging.WARNING)
        self.assertTrue(any(isinstance(h, logging.StreamHandler) for h in logger.handlers))

    def test_e1_env_list_splits_and_strips(self):
        from internetshop.settings import env_list
        with mock.patch.dict(os.environ, {'AUDIT_TEST_LIST': 'estivo63.ru, www.estivo63.ru'}):
            self.assertEqual(env_list('AUDIT_TEST_LIST'), ['estivo63.ru', 'www.estivo63.ru'])

    def test_e1_env_list_drops_empty_items(self):
        from internetshop.settings import env_list
        with mock.patch.dict(os.environ, {'AUDIT_TEST_LIST': 'a.ru,, ,b.ru,'}):
            self.assertEqual(env_list('AUDIT_TEST_LIST'), ['a.ru', 'b.ru'])

    def test_e1_env_list_missing_or_empty_variable_is_empty_list(self):
        from internetshop.settings import env_list
        with mock.patch.dict(os.environ):
            os.environ.pop('AUDIT_TEST_LIST', None)
            self.assertEqual(env_list('AUDIT_TEST_LIST'), [])
            os.environ['AUDIT_TEST_LIST'] = ''
            self.assertEqual(env_list('AUDIT_TEST_LIST'), [])

    def test_e1_allowed_hosts_with_spaces_after_comma(self):
        result = run_settings(ALLOWED_HOSTS='estivo63.ru, www.estivo63.ru',
                              CSRF_TRUSTED_ORIGINS='https://estivo63.ru, https://www.estivo63.ru')
        self.assertIn('estivo63.ru', result['ALLOWED_HOSTS'])
        self.assertIn('www.estivo63.ru', result['ALLOWED_HOSTS'])
        self.assertIn('https://www.estivo63.ru', result['CSRF'])
        for value in result['ALLOWED_HOSTS'] + result['CSRF']:
            self.assertEqual(value, value.strip())
            self.assertTrue(value)

    def test_e1_loaded_settings_have_no_blank_hosts(self):
        for value in list(settings.ALLOWED_HOSTS) + list(settings.CSRF_TRUSTED_ORIGINS):
            self.assertEqual(value, value.strip())
            self.assertTrue(value)

    def test_e1_database_url_enables_connection_health_checks(self):
        result = run_settings(DATABASE_URL='postgres://user:pass@db.example.com:5432/shop')
        self.assertEqual(result['DB']['CONN_MAX_AGE'], 600)
        self.assertIs(result['DB']['CONN_HEALTH_CHECKS'], True)


class E1FormLengthTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.product = make_product(name='Кресло Тест', price=42000)

    def test_e1_comment_2001_chars_rejected(self):
        form = OrderForm({**ORDER_DATA, 'comment': 'я' * 2001})
        self.assertFalse(form.is_valid())
        self.assertIn('comment', form.errors)

    def test_e1_comment_exactly_2000_chars_accepted(self):
        form = OrderForm({**ORDER_DATA, 'comment': 'я' * 2000})
        self.assertTrue(form.is_valid(), form.errors)

    def test_e1_delivery_address_501_chars_rejected(self):
        form = OrderForm({**ORDER_DATA, 'delivery_address': 'я' * 501})
        self.assertFalse(form.is_valid())
        self.assertIn('delivery_address', form.errors)

    def test_e1_delivery_address_exactly_500_chars_accepted(self):
        form = OrderForm({**ORDER_DATA, 'delivery_address': 'я' * 500})
        self.assertTrue(form.is_valid(), form.errors)

    def test_e1_lead_message_2001_chars_rejected(self):
        form = LeadForm({**LEAD_DATA, 'message': 'я' * 2001})
        self.assertFalse(form.is_valid())
        self.assertIn('message', form.errors)

    def test_e1_lead_message_exactly_2000_chars_accepted(self):
        form = LeadForm({**LEAD_DATA, 'message': 'я' * 2000})
        self.assertTrue(form.is_valid(), form.errors)

    def test_e1_long_comment_checkout_not_saved_and_input_kept(self):
        add_to_cart(self.client, self.product)
        with mock.patch('shop.views.notify_telegram', return_value=True) as notify:
            resp = self.client.post(reverse('checkout'), {
                **ORDER_DATA, 'customer_name': 'Сохранённое имя', 'comment': 'я' * 2001})
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(Order.objects.exists())
        self.assertIn('comment', resp.context['form'].errors)
        self.assertContains(resp, 'Сохранённое имя')
        notify.assert_not_called()
        self.assertTrue(self.client.session.get('cart'), 'корзина должна остаться')

    def test_e1_long_address_checkout_not_saved(self):
        add_to_cart(self.client, self.product)
        with mock.patch('shop.views.notify_telegram', return_value=True):
            resp = self.client.post(reverse('checkout'), {**ORDER_DATA, 'delivery_address': 'я' * 501})
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(Order.objects.exists())
        self.assertIn('delivery_address', resp.context['form'].errors)

    def test_e1_long_lead_message_not_saved_error_at_field(self):
        with mock.patch('shop.views.notify_telegram', return_value=True) as notify:
            resp = self.client.post(reverse('contacts_page'), {**LEAD_DATA, 'message': 'я' * 2001})
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(Lead.objects.exists())
        self.assertIn('message', resp.context['form'].errors)
        field = parse(resp).find('textarea', attrs={'name': 'message'})
        self.assertEqual(field.get('aria-invalid'), 'true')
        notify.assert_not_called()

    def test_e1_form_fields_declare_limits(self):
        self.assertEqual(OrderForm().fields['comment'].max_length, 2000)
        self.assertEqual(OrderForm().fields['delivery_address'].max_length, 500)
        self.assertEqual(LeadForm().fields['message'].max_length, 2000)


class E1MobileFieldAttrsTests(TestCase):
    """inputmode/autocomplete у полей контактов."""

    @classmethod
    def setUpTestData(cls):
        cls.product = make_product(name='Кресло Тест', price=42000)

    def assert_contact_attrs(self, root, name_field, phone_field, email_field):
        phone = root.find('input', attrs={'name': phone_field})
        self.assertIsNotNone(phone, phone_field)
        self.assertEqual(phone.get('inputmode'), 'tel')
        self.assertEqual(phone.get('autocomplete'), 'tel')
        self.assertEqual(root.find('input', attrs={'name': name_field}).get('autocomplete'), 'name')
        self.assertEqual(root.find('input', attrs={'name': email_field}).get('autocomplete'), 'email')

    def test_e1_checkout_form_attrs(self):
        add_to_cart(self.client, self.product)
        root = parse(self.client.get(reverse('checkout')))
        self.assert_contact_attrs(root, 'customer_name', 'customer_phone', 'customer_email')

    def test_e1_lead_form_attrs_on_every_lead_page(self):
        for url_name in LEAD_PAGES:
            with self.subTest(page=url_name):
                root = parse(self.client.get(reverse(url_name)))
                self.assert_contact_attrs(root, 'name', 'phone', 'email')

    def test_e1_honeypot_stays_out_of_autofill(self):
        root = parse(self.client.get(reverse('contacts_page')))
        trap = root.find('input', attrs={'name': 'website'})
        self.assertEqual(trap.get('autocomplete'), 'off')


class E1PhoneAndNameRegressionTests(TestCase):
    """Регрессия: неверный телефон и пустое имя отклоняются (зелёные сразу)."""

    HINT = 'Введите номер телефона'

    @classmethod
    def setUpTestData(cls):
        cls.product = make_product(name='Кресло Тест', price=42000)

    def test_e1_checkout_rejects_wrong_phone(self):
        add_to_cart(self.client, self.product)
        with mock.patch('shop.views.notify_telegram', return_value=True) as notify:
            resp = self.client.post(reverse('checkout'), {**ORDER_DATA, 'customer_phone': '12345'})
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(Order.objects.exists())
        self.assertContains(resp, self.HINT)
        field = parse(resp).find('input', attrs={'name': 'customer_phone'})
        self.assertEqual(field.get('aria-invalid'), 'true')
        notify.assert_not_called()

    def test_e1_lead_pages_reject_wrong_phone(self):
        for url_name in LEAD_PAGES:
            with self.subTest(page=url_name), mock.patch('shop.views.notify_telegram', return_value=True):
                resp = self.client.post(reverse(url_name), {**LEAD_DATA, 'phone': 'abc'})
                self.assertEqual(resp.status_code, 200)
                self.assertFalse(Lead.objects.exists())
                self.assertContains(resp, self.HINT)
                field = parse(resp).find('input', attrs={'name': 'phone'})
                self.assertEqual(field.get('aria-invalid'), 'true')

    def test_e1_lead_rejects_empty_name(self):
        with mock.patch('shop.views.notify_telegram', return_value=True) as notify:
            resp = self.client.post(reverse('contacts_page'), {**LEAD_DATA, 'name': ''})
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(Lead.objects.exists())
        self.assertIn('name', resp.context['form'].errors)
        self.assertEqual(parse(resp).find('input', attrs={'name': 'name'}).get('aria-invalid'), 'true')
        notify.assert_not_called()

    def test_e1_checkout_rejects_empty_name(self):
        add_to_cart(self.client, self.product)
        resp = self.client.post(reverse('checkout'), {**ORDER_DATA, 'customer_name': ''})
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(Order.objects.exists())

    def test_e1_valid_russian_phone_formats_still_accepted(self):
        for phone in ('+7 900 123-45-67', '8 (900) 123-45-67', '+79001234567'):
            with self.subTest(phone=phone):
                self.assertTrue(LeadForm({**LEAD_DATA, 'phone': phone}).is_valid())
