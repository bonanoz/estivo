"""Эпик (e): страница /privacy/ и реквизиты одного продавца.

Контракт интерфейсов (в SPEC имена URL заданы, пути выбраны здесь):
- `reverse('privacy_page')` == '/privacy/' (GET, 200), в sitemap.xml.
- Остальные страницы — существующие имена: home, product_detail, cart_detail, checkout,
  contacts_page ('/kontakty/'), b2b_page ('/b2b/').
- Телефон ищется в видимом тексте и в tel:/wa.me-ссылках, любое форматирование.

Ручная проверка: текст политики требует юриста; плейсхолдеры «[уточнить: …]» допустимы.
"""
import re

from django.test import TestCase
from django.urls import reverse

from .helpers import make_product, parse

NEW_PHONE = '79272689404'
FORBIDDEN_PHONES = ['79272004303', '79178246722', '78482789404']
FORBIDDEN_TEXT = ['ИП Мелихова', 'ОГРИП', '632147606449']

PHONE_RE = re.compile(r'(?<![\d])(?:\+7|8|7)[\s\-().  ]*\d{3}[\s\-().  ]*\d{3}'
                      r'[\s\-.  ]*\d{2}[\s\-.  ]*\d{2}(?!\d)')
HREF_RE = re.compile(r'(?:tel:|wa\.me/|phone=)\+?(\d{10,11})')


def phones_in(html):
    """Множество телефонов вида 7XXXXXXXXXX, найденных в html (текст и ссылки)."""
    found = set()
    for raw in PHONE_RE.findall(html) + HREF_RE.findall(html):
        digits = re.sub(r'\D', '', raw)
        if len(digits) == 11 and digits[0] == '8':
            digits = '7' + digits[1:]
        if len(digits) == 10:
            digits = '7' + digits
        found.add(digits)
    return found


class E1PrivacyPageTests(TestCase):
    def test_e2_privacy_page_content(self):
        resp = self.client.get(reverse('privacy_page'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(reverse('privacy_page'), '/privacy/')
        html = resp.content.decode()
        for needle in ['ООО «Эстиво»', '6321368220', 'Метрик', 'cookie']:
            self.assertIn(needle, html)

    def test_e2_sitemap_has_privacy(self):
        resp = self.client.get('/sitemap.xml')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('/privacy/', resp.content.decode())


class E1SingleSellerTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.product = make_product(name='Кресло Е', slug='kreslo-e', price=30000)

    def pages(self):
        self.client.post(reverse('cart_add', args=[self.product.id]), {'quantity': 1})
        return {
            'home': reverse('home'),
            'pdp': self.product.get_absolute_url(),
            'cart': reverse('cart_detail'),
            'contacts': reverse('contacts_page'),
            'b2b': reverse('b2b_page'),
            'privacy': reverse('privacy_page'),
        }

    def test_e1_only_new_phone_and_no_ip_requisites(self):
        for name, url in self.pages().items():
            with self.subTest(page=name):
                resp = self.client.get(url)
                self.assertEqual(resp.status_code, 200)
                html = resp.content.decode()
                phones = phones_in(html)
                self.assertIn(NEW_PHONE, phones, 'нового телефона нет на странице')
                self.assertEqual(phones, {NEW_PHONE}, f'лишние телефоны: {phones - {NEW_PHONE}}')
                digits = re.sub(r'\D', '', html)
                for old in FORBIDDEN_PHONES:
                    self.assertNotIn(old, digits)
                for text in FORBIDDEN_TEXT:
                    self.assertNotIn(text, html)

    def test_e1_footer_shows_seller(self):
        html = self.client.get(reverse('home')).content.decode()
        self.assertIn('ООО «Эстиво»', html)
        self.assertIn('6321368220', html)


class E3PrivacyLinkInFormsTests(TestCase):
    def assert_forms_link_privacy(self, url):
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        root = parse(resp)
        forms = [f for f in root.find_all('form')
                 if f.get('method', '').lower() == 'post'
                 and (f.find('input', attrs={'name': 'phone'}) or f.find('input', attrs={'name': 'customer_phone'}))]
        self.assertTrue(forms, 'на странице нет формы заявки')
        for form in forms:
            links = form.find_all('a', pred=lambda a: a.get('href', '').rstrip('/').endswith('/privacy'))
            self.assertTrue(links, f'форма {form.attrs.get("action")} без ссылки на /privacy/')

    def test_e3_lead_form_contacts(self):
        self.assert_forms_link_privacy(reverse('contacts_page'))

    def test_e3_lead_form_b2b(self):
        self.assert_forms_link_privacy(reverse('b2b_page'))

    def test_e3_checkout_form(self):
        product = make_product(name='Кресло Ч', slug='kreslo-ch', price=20000)
        self.client.post(reverse('cart_add', args=[product.id]), {'quantity': 1})
        resp = self.client.get(reverse('checkout'))
        self.assertEqual(resp.status_code, 200)
        self.assert_forms_link_privacy(reverse('checkout'))
