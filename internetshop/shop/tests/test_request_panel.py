"""Эпик (b): карточка товара, промо-карточка, панель заявки.

Контракт интерфейсов (в SPEC нет — выбрано здесь, воркер обязан реализовать так):
- «Узнать цену» шлёт POST на существующий `contacts_page` (`reverse('contacts_page')`,
  `lead_create` в проекте нет) с полями LeadForm (`name`, `phone`, `email`, `lead_type`,
  `message`) + ещё одно поле `price_request_for` = slug товара. View при наличии этого поля
  берёт товар по slug, дописывает его название в `Lead.message` и ставит
  `Lead.source_page = 'price-request:<slug>'` (вместо имени шаблона).
- cart_add для товара с price=0: корзина не меняется; редирект (или HX-Redirect) ведёт на
  URL, содержащий slug товара (форма «Узнать цену»), и не на cart_detail.
- Счётчик корзины в шапке — элемент с атрибутом `data-cart-count` (уже есть).
- Промо-карточка: на `?flag=sale` содержит текст «Акция до <j E Y>» (напр. «30 ноября 2026»),
  новую и старую цену и название товара.
- Блок фактов панели — элемент с классом `es-facts` (Срок / Доставка / Гарантия / Оплата).
- Ссылка «Перейти к заявке» в панели ведёт на `checkout`.

Ручная проверка (не тестами): 390px/1000px без горизонтальной прокрутки, текст >= 14px,
контролы >= 44px, подчёркивание ссылки «3 года», вид тоста.
"""
import re
from datetime import date, timedelta
from pathlib import Path
from unittest import mock

from django.conf import settings
from django.template.defaultfilters import date as date_filter
from django.test import TestCase
from django.urls import reverse

from shop.models import Lead, Product

from .helpers import make_product, norm_space, parse, squash

HX = {'HTTP_HX_REQUEST': 'true'}
LEAD = {'name': 'Анна', 'phone': '+7 900 123-45-67', 'email': '', 'lead_type': 'private', 'message': ''}


def visible_text(node):
    return norm_space(node.text)


def without_pod_zakaz(text):
    return re.sub(r'под\s+заказ', '', text, flags=re.I)


class EbPriceOnRequestTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.free = make_product(name='Кресло Нулевое', slug='kreslo-nulevoe', price=0)
        cls.paid = make_product(name='Кресло Платное', slug='kreslo-platnoe', price=30000)

    def card(self, product):
        root = parse(self.client.get(reverse('catalog_list')))
        for card in root.find_all(cls='product-card'):
            if product.get_absolute_url() in {a.get('href') for a in card.find_all('a', attrs={'href': True})}:
                return card
        self.fail(f'нет карточки {product.name} в каталоге')

    def test_b1_card_with_zero_price(self):
        card = self.card(self.free)
        text = visible_text(card)
        self.assertIn('Цена по запросу', text)
        self.assertIn('Узнать цену', text)
        self.assertNotIn('В корзину', text)
        cart_url = reverse('cart_add', args=[self.free.id])
        self.assertFalse(card.find_all('form', pred=lambda f: f.get('action') == cart_url))
        self.assertFalse(card.find_all(pred=lambda n: n.get('hx-post') == cart_url))

    def test_b1_card_with_price_unchanged(self):
        text = visible_text(self.card(self.paid))
        self.assertNotIn('Цена по запросу', text)
        self.assertIn('30000', squash(text))

    def test_b1_pdp_with_zero_price(self):
        root = parse(self.client.get(self.free.get_absolute_url()))
        self.assertIn('Цена по запросу', root.text)
        self.assertIn('Узнать цену', root.text)
        cart_url = reverse('cart_add', args=[self.free.id])
        self.assertFalse(root.find_all('form', pred=lambda f: f.get('action') == cart_url))
        self.assertFalse(root.find_all(pred=lambda n: n.get('hx-post') == cart_url))

    def test_b2_cart_add_rejected_plain(self):
        resp = self.client.post(reverse('cart_add', args=[self.free.id]), {'quantity': 1})
        self.assertFalse(self.client.session.get('cart'))
        self.assertEqual(resp.status_code, 302)
        self.assertNotEqual(resp['Location'], reverse('cart_detail'))
        self.assertIn(self.free.slug, resp['Location'], 'редирект должен вести к форме «Узнать цену» товара')

    def test_b2_cart_add_rejected_htmx(self):
        resp = self.client.post(reverse('cart_add', args=[self.free.id]), {'quantity': 1}, **HX)
        self.assertFalse(self.client.session.get('cart'))
        blob = resp.content.decode() + ' '.join(f'{k}: {v}' for k, v in resp.headers.items())
        self.assertNotIn('Добавлено в заявку', blob)
        self.assertIn(self.free.slug, blob)

    def test_b2_cart_add_rejected_with_checkout_flag(self):
        self.client.post(reverse('cart_add', args=[self.free.id]), {'checkout': '1'})
        self.assertFalse(self.client.session.get('cart'))

    def test_b3_price_request_creates_lead(self):
        data = {**LEAD, 'price_request_for': self.free.slug}
        with mock.patch('shop.views.notify_telegram', return_value=False):
            self.client.post(reverse('contacts_page'), data)
        lead = Lead.objects.get()
        self.assertIn('Кресло Нулевое', lead.message)
        self.assertEqual(lead.source_page, 'price-request:kreslo-nulevoe')

    def test_b3_ordinary_contact_lead_is_not_price_request(self):
        with mock.patch('shop.views.notify_telegram', return_value=False):
            self.client.post(reverse('contacts_page'), LEAD)
        self.assertFalse(Lead.objects.get().source_page.startswith('price-request:'))


class EbRequestPanelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.product = make_product(name='Кресло Панель', slug='kreslo-panel', price=42000)

    def drawer(self):
        resp = self.client.post(reverse('cart_add', args=[self.product.id]), {'quantity': 1}, **HX)
        self.assertEqual(resp.status_code, 200)
        return parse(resp)

    def cart_page(self):
        self.client.post(reverse('cart_add', args=[self.product.id]), {'quantity': 1})
        resp = self.client.get(reverse('cart_detail'))
        self.assertEqual(resp.status_code, 200)
        root = parse(resp)
        return root.find('main') or root

    def assert_panel(self, root):
        text = visible_text(root)
        for phrase in ('Ваша заявка', 'Оплаты на сайте нет', 'Перейти к заявке'):
            self.assertIn(phrase, text)
        facts = root.find(cls='es-facts')
        self.assertIsNotNone(facts, 'нет блока es-facts')
        facts_text = visible_text(facts)
        for word in ('Срок', 'Доставка', 'Гарантия', 'Оплата'):
            self.assertIn(word, facts_text)
        clean = without_pod_zakaz(text).lower()
        for banned in ('заказ', 'купить', 'оплатить'):
            self.assertNotIn(banned, clean)

    def test_b4_drawer_panel(self):
        self.assert_panel(self.drawer())

    def test_b4_cart_page_panel(self):
        self.assert_panel(self.cart_page())

    def test_b4_request_button_goes_to_checkout(self):
        for root in (self.drawer(), self.cart_page()):
            link = root.find('a', pred=lambda a: 'Перейти к заявке' in a.text)
            self.assertIsNotNone(link)
            self.assertEqual(link.get('href'), reverse('checkout'))

    def test_b5_toast_after_add(self):
        root = self.drawer()
        self.assertIn('Добавлено в заявку', root.text)
        link = root.find('a', pred=lambda a: a.get('href') == reverse('cart_detail'))
        self.assertIsNotNone(link, 'в уведомлении нет ссылки на корзину')

    def test_b7_card_and_pdp_have_header_and_cart_counter(self):
        for url in (self.product.get_absolute_url(), reverse('catalog_list')):
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, 200, url)
            root = parse(resp)
            self.assertIsNotNone(root.find('header'), url)
            self.assertIsNotNone(root.find(attrs={'data-cart-count': True}), url)


class EbOfferCardTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        future = date.today() + timedelta(days=60)
        cls.future_text = f'Акция до {date_filter(future, "j E Y")}'
        cls.live = make_product(name='Диван Акция', slug='divan-akciya', price=50000, old_price=65000,
                                offer_ends_at=future)
        cls.no_date = make_product(name='Стол БезДаты', slug='stol-bez-daty', price=20000, old_price=26000)
        cls.expired = make_product(name='Пуф Прошлый', slug='puf-proshlyj', price=9000, old_price=12000,
                                   offer_ends_at=date.today() - timedelta(days=1))

    def sale_page(self):
        resp = self.client.get(reverse('catalog_list'), {'flag': 'sale'})
        self.assertEqual(resp.status_code, 200)
        return parse(resp)

    def test_b6_live_offer_shows_both_prices_and_date(self):
        root = self.sale_page()
        marker = root.find(pred=lambda n: self.future_text in norm_space(n.text)
                           and not any(self.future_text in norm_space(c.text) for c in n.iter()))
        self.assertIsNotNone(marker, f'нет «{self.future_text}»')
        for node in [marker, *marker.ancestors()]:
            t = squash(node.text)
            if '50000' in t and '65000' in t and 'Диван Акция' in node.text:
                return
        self.fail('рядом с датой нет названия и обеих цен (новая и старая)')

    def test_b6_no_card_without_date_or_after_date(self):
        text = visible_text(self.sale_page())
        self.assertEqual(text.count('Акция до'), 1, 'промо-карточка только у товара с будущей датой')

    def test_b6_model_field(self):
        self.assertIsNone(Product.objects.get(pk=self.no_date.pk).offer_ends_at)
        self.assertIsNotNone(Product.objects.get(pk=self.live.pk).offer_ends_at)


class EbAccentTests(TestCase):
    ALLOWED = {'_cart_drawer.html', '_cart_lines.html', 'cart.html', 'checkout.html', '_offer_card.html', 'home.html'}

    def test_b8_btn_primary_only_in_allowed_templates(self):
        root = Path(settings.BASE_DIR) / 'shop' / 'templates'
        found = {}
        for path in root.rglob('*.html'):
            n = len(re.findall(r'(?<![\w-])btn-primary(?![\w-])', path.read_text(encoding='utf-8')))
            if n:
                found[path.name] = n
        extra = set(found) - self.ALLOWED
        self.assertFalse(extra, f'btn-primary вне разрешённых файлов: {extra}')
        self.assertLessEqual(found.get('home.html', 0), 1)


class EbAdminTests(TestCase):
    def test_b9_offer_ends_at_in_product_admin_form(self):
        from django.contrib import admin
        from django.test import RequestFactory
        from django.contrib.auth.models import User
        request = RequestFactory().get('/')
        request.user = User(is_superuser=True, is_staff=True, is_active=True)
        form = admin.site._registry[Product].get_form(request)
        self.assertIn('offer_ends_at', form.base_fields)
