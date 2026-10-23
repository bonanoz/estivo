"""Эпик (g): Метрика, e-commerce, UTM first-touch, цели.

Контракт — раздел (g) SPEC «Допущения и контракт интерфейсов»:
- cookie `cookie_consent` = analytics|necessary; view `cookie_consent` (POST, поле `choice`, next).
- полоса `data-cookie-banner`; счётчик `mc.yandex.ru/metrika` только при analytics.
- `dataLayer`: detail на PDP, purchase на order_success (один раз), HX-Trigger `ecommerce:add`.
- `pending_goals` -> `<script id="pending-goals" type="application/json">` на следующей странице.
- `data-goal` на tel:/t.me/wa.me/max.ru; AttributionMiddleware; поля Order/Lead; `Источник:` в Telegram.
Выбрано здесь (в SPEC нет): имя URL `cookie_consent` == '/cookie-consent/'; в pending-goals JSON
имена целей встречаются как подстроки текста (формат массива не фиксируется).
Ручная проверка: высота полосы <= ~10% на 390px, реальная отправка целей, Telegram, вид полосы.
"""
import json
from unittest import mock

from django.contrib import admin
from django.test import TestCase
from django.urls import reverse

from shop.models import Lead, Order

from .helpers import make_product, parse

HX = {'HTTP_HX_REQUEST': 'true'}
COUNTER = '93915751'
ORDER_DATA = {
    'customer_name': 'Иван', 'customer_phone': '+7 900 123-45-67', 'customer_email': '',
    'delivery_address': 'Тольятти', 'comment': '',
}
LEAD = {'name': 'Анна', 'phone': '+7 900 123-45-67', 'email': '', 'lead_type': 'private', 'message': ''}
FIELDS = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term',
          'yclid', 'ym_client_id', 'landing_page']
FIRST = '/?utm_source=a&utm_campaign=b&yclid=123'


def set_consent(client, value):
    client.cookies['cookie_consent'] = value


def order_via_checkout(client, product, **extra):
    client.post(reverse('cart_add', args=[product.id]), {'quantity': 2})
    with mock.patch('shop.views.notify_telegram', return_value=False) as notify:
        resp = client.post(reverse('checkout'), ORDER_DATA, **extra)
    return resp, notify


class G1ConsentTests(TestCase):
    def test_g1_no_consent_no_counter_but_banner(self):
        html = self.client.get(reverse('home')).content.decode()
        self.assertNotIn('mc.yandex.ru/metrika', html)
        self.assertIn('data-cookie-banner', html)

    def test_g1_analytics_consent_loads_counter_and_webvisor(self):
        set_consent(self.client, 'analytics')
        html = self.client.get(reverse('home')).content.decode()
        self.assertIn('mc.yandex.ru/metrika', html)
        self.assertIn(COUNTER, html)
        self.assertRegex(html, r'webvisor\s*:\s*true')
        self.assertNotIn('data-cookie-banner', html)

    def test_g1_necessary_consent_no_counter_no_banner(self):
        set_consent(self.client, 'necessary')
        html = self.client.get(reverse('home')).content.decode()
        self.assertNotIn('mc.yandex.ru/metrika', html)
        self.assertNotIn('data-cookie-banner', html)

    def test_g1_cookie_settings_shows_banner_again(self):
        set_consent(self.client, 'necessary')
        html = self.client.get(reverse('home') + '?cookie_settings=1').content.decode()
        self.assertIn('data-cookie-banner', html)

    def test_g1_footer_has_cookie_settings_link(self):
        set_consent(self.client, 'necessary')
        root = parse(self.client.get(reverse('home')))
        links = root.find_all('a', pred=lambda a: 'cookie_settings=1' in a.get('href', ''))
        self.assertTrue(links)

    def test_g1_banner_links_to_privacy_cookie(self):
        root = parse(self.client.get(reverse('home')))
        banner = root.find(attrs={'data-cookie-banner': True})
        self.assertIsNotNone(banner)
        self.assertTrue(banner.find_all('a', pred=lambda a: '/privacy/#cookie' in a.get('href', '')))


class G1ConsentViewTests(TestCase):
    def url(self):
        return reverse('cookie_consent')

    def test_g1_url_path(self):
        self.assertEqual(self.url(), '/cookie-consent/')

    def test_g1_choice_sets_cookie(self):
        for choice in ('analytics', 'necessary'):
            with self.subTest(choice=choice):
                resp = self.client.post(self.url(), {'choice': choice})
                self.assertEqual(resp.status_code, 302)
                morsel = resp.cookies['cookie_consent']
                self.assertEqual(morsel.value, choice)
                self.assertAlmostEqual(int(morsel['max-age']), 365 * 86400, delta=86400)
                self.assertEqual(morsel['samesite'], 'Lax')

    def test_g1_safe_next_redirect(self):
        resp = self.client.post(self.url(), {'choice': 'analytics', 'next': '/kontakty/'})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], '/kontakty/')

    def test_g1_external_next_not_followed(self):
        for bad in ('https://evil.example/x', '//evil.example/x'):
            with self.subTest(next=bad):
                resp = self.client.post(self.url(), {'choice': 'necessary', 'next': bad})
                self.assertEqual(resp.status_code, 302)
                self.assertNotIn('evil.example', resp['Location'])

    def test_g1_unknown_choice_400(self):
        resp = self.client.post(self.url(), {'choice': 'everything'})
        self.assertEqual(resp.status_code, 400)
        self.assertNotIn('cookie_consent', resp.cookies)


class G4AttributionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.product = make_product(name='Кресло Г', slug='kreslo-g', price=30000)

    def test_g4_order_first_touch(self):
        self.client.get(FIRST)
        self.client.get(reverse('catalog_list'))
        order_via_checkout(self.client, self.product)
        order = Order.objects.get()
        self.assertEqual((order.utm_source, order.utm_campaign, order.yclid), ('a', 'b', '123'))
        self.assertEqual(order.landing_page, FIRST)

    def test_g4_repeat_entry_does_not_overwrite(self):
        self.client.get(FIRST)
        self.client.get('/?utm_source=zzz&utm_campaign=other&yclid=999')
        order_via_checkout(self.client, self.product)
        order = Order.objects.get()
        self.assertEqual((order.utm_source, order.utm_campaign, order.yclid), ('a', 'b', '123'))
        self.assertEqual(order.landing_page, FIRST)

    def test_g4_all_utm_fields_saved(self):
        url = '/?utm_source=s&utm_medium=m&utm_campaign=c&utm_content=ct&utm_term=t&yclid=9'
        self.client.get(url)
        order_via_checkout(self.client, self.product)
        order = Order.objects.get()
        self.assertEqual([order.utm_source, order.utm_medium, order.utm_campaign,
                          order.utm_content, order.utm_term, order.yclid],
                         ['s', 'm', 'c', 'ct', 't', '9'])

    def test_g4_no_attribution_gives_empty_fields(self):
        order_via_checkout(self.client, self.product)
        order = Order.objects.get()
        self.assertEqual(order.utm_source, '')
        self.assertEqual(order.yclid, '')

    def test_g4_skips_htmx_and_service_paths(self):
        self.client.get('/?utm_source=htmx', **HX)
        self.client.get('/robots.txt?utm_source=robots')
        self.client.get('/?utm_source=real')
        order_via_checkout(self.client, self.product)
        self.assertEqual(Order.objects.get().utm_source, 'real')

    def test_g4_b2b_lead_first_touch(self):
        self.client.get(FIRST)
        self.client.get('/?utm_source=zzz')
        with mock.patch('shop.views.notify_telegram', return_value=False):
            self.client.post(reverse('b2b_page'), {**LEAD, 'lead_type': 'b2b'})
        lead = Lead.objects.get()
        self.assertEqual((lead.utm_source, lead.utm_campaign, lead.yclid), ('a', 'b', '123'))
        self.assertEqual(lead.landing_page, FIRST)

    def test_g4_price_request_lead_first_touch(self):
        self.client.get(FIRST)
        with mock.patch('shop.views.notify_telegram', return_value=False):
            self.client.post(reverse('contacts_page'), {**LEAD, 'price_request_for': self.product.slug})
        lead = Lead.objects.get()
        self.assertEqual((lead.utm_source, lead.utm_campaign, lead.yclid), ('a', 'b', '123'))
        self.assertEqual(lead.landing_page, FIRST)

    def test_g4_ym_uid_to_client_id(self):
        self.client.cookies['_ym_uid'] = '42'
        order_via_checkout(self.client, self.product)
        self.assertEqual(Order.objects.get().ym_client_id, '42')
        with mock.patch('shop.views.notify_telegram', return_value=False):
            self.client.post(reverse('b2b_page'), {**LEAD, 'lead_type': 'b2b'})
        self.assertEqual(Lead.objects.get().ym_client_id, '42')

    def test_g4_non_numeric_ym_uid_ignored(self):
        self.client.cookies['_ym_uid'] = 'abc<x>'
        order_via_checkout(self.client, self.product)
        self.assertEqual(Order.objects.get().ym_client_id, '')


class G3DataLayerTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.product = make_product(name='Кресло Данные', slug='kreslo-dannye', price=30000)

    def test_g3_datalayer_on_every_page(self):
        self.assertIn('dataLayer', self.client.get(reverse('home')).content.decode())

    def test_g3_pdp_detail(self):
        html = self.client.get(self.product.get_absolute_url()).content.decode()
        self.assertIn('dataLayer', html)
        self.assertIn('"detail"', html)
        self.assertIn('RUB', html)
        self.assertIn('Кресло Данные', html)

    def test_g3_purchase_once(self):
        order_via_checkout(self.client, self.product)
        order = Order.objects.get()
        html = self.client.get(reverse('order_success')).content.decode()
        self.assertIn('"purchase"', html)
        self.assertIn(str(order.id), html)
        self.assertIn('60000', html)
        again = self.client.get(reverse('order_success')).content.decode()
        self.assertNotIn('"purchase"', again)

    def test_g3_no_purchase_without_order(self):
        self.assertNotIn('"purchase"', self.client.get(reverse('order_success')).content.decode())

    def test_g3_htmx_cart_add_triggers_ecommerce_add(self):
        resp = self.client.post(reverse('cart_add', args=[self.product.id]), {'quantity': 1}, **HX)
        self.assertEqual(resp.status_code, 200)
        trigger = json.loads(resp['HX-Trigger'])
        self.assertIn('ecommerce:add', trigger)
        self.assertIn(str(self.product.id), json.dumps(trigger['ecommerce:add']))


class G2PendingGoalsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.product = make_product(name='Кресло Цель', slug='kreslo-tsel', price=30000)

    def goals(self, url):
        node = parse(self.client.get(url)).get_by_id('pending-goals')
        return None if node is None else node.text

    def test_g2_checkout_goal_once(self):
        order_via_checkout(self.client, self.product)
        text = self.goals(reverse('order_success'))
        self.assertIsNotNone(text)
        self.assertIn('checkout_submit', text)
        self.assertIsNone(self.goals(reverse('home')))

    def test_g2_b2b_lead_goal_once(self):
        with mock.patch('shop.views.notify_telegram', return_value=False):
            self.client.post(reverse('b2b_page'), {**LEAD, 'lead_type': 'b2b'})
        text = self.goals(reverse('b2b_page'))
        self.assertIsNotNone(text)
        self.assertIn('lead_submit_b2b', text)
        self.assertIsNone(self.goals(reverse('home')))

    def test_g2_price_request_goal(self):
        with mock.patch('shop.views.notify_telegram', return_value=False):
            self.client.post(reverse('contacts_page'), {**LEAD, 'price_request_for': self.product.slug})
        text = self.goals(reverse('contacts_page'))
        self.assertIsNotNone(text)
        self.assertIn('price_request', text)
        self.assertIsNone(self.goals(reverse('home')))

    def test_g2_no_goals_by_default(self):
        self.assertIsNone(self.goals(reverse('home')))


class G2ClickGoalTests(TestCase):
    PAGES = ['home', 'contacts_page', 'b2b_page', 'cart_detail']
    MARKER_GOALS = [('tel:', 'click_tel'), ('t.me/', 'click_telegram'),
                    ('wa.me/', 'click_whatsapp'), ('max.ru', 'click_max')]

    def test_g2_links_have_goal(self):
        seen = set()
        for name in self.PAGES:
            root = parse(self.client.get(reverse(name)))
            for a in root.find_all('a', attrs={'href': True}):
                href = a.get('href')
                for marker, goal in self.MARKER_GOALS:
                    if marker in href:
                        seen.add(goal)
                        with self.subTest(page=name, href=href):
                            self.assertEqual(a.get('data-goal'), goal)
        self.assertIn('click_tel', seen)
        self.assertIn('click_telegram', seen)


class G5TelegramSourceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.product = make_product(name='Кресло ТГ', slug='kreslo-tg', price=30000)

    def source_line(self, notify):
        text = notify.call_args[0][0]
        lines = [ln for ln in text.splitlines() if ln.startswith('Источник:')]
        self.assertEqual(len(lines), 1, text)
        return lines[0]

    def test_g5_order_source_line(self):
        self.client.get('/?utm_source=ya&yclid=777')
        _, notify = order_via_checkout(self.client, self.product)
        line = self.source_line(notify)
        self.assertIn('ya', line)
        self.assertIn('777', line)

    def test_g5_order_direct(self):
        _, notify = order_via_checkout(self.client, self.product)
        self.assertIn('прямой заход', self.source_line(notify))

    def test_g5_lead_source_line(self):
        self.client.get('/?utm_source=ya&yclid=777')
        with mock.patch('shop.views.notify_telegram', return_value=False) as notify:
            self.client.post(reverse('b2b_page'), {**LEAD, 'lead_type': 'b2b'})
        line = self.source_line(notify)
        self.assertIn('ya', line)
        self.assertIn('777', line)

    def test_g5_lead_direct(self):
        with mock.patch('shop.views.notify_telegram', return_value=False) as notify:
            self.client.post(reverse('contacts_page'), LEAD)
        self.assertIn('прямой заход', self.source_line(notify))


class G5SchemaAdminTests(TestCase):
    def test_g5_model_fields(self):
        for model in (Order, Lead):
            for name in FIELDS:
                with self.subTest(model=model.__name__, field=name):
                    field = model._meta.get_field(name)
                    self.assertTrue(field.blank)
                    expected = {'yclid': 64, 'ym_client_id': 64, 'landing_page': 500}.get(name, 255)
                    self.assertEqual(field.max_length, expected)

    def test_g5_admin_readonly(self):
        for model in (Order, Lead):
            ro = admin.site._registry[model].readonly_fields
            for name in FIELDS:
                with self.subTest(model=model.__name__, field=name):
                    self.assertIn(name, ro)
