"""Эпик (f): тексты по §14 аудита и правилам estivo-tilda.

Контракт (интерфейсы — существующие имена URL, новых нет):
- Все страницы проверяются по видимому тексту (html -> unescape -> схлопнутые пробелы/NBSP).
- Hero главной — элемент `[data-section="hero"]` (уже есть в home.html).
- Срок: оба всегда — «Отгрузка в течение 3 дней» (в наличии) и «Изготовление от 4 недель» (под заказ); решение 23.10.2026.
- Температура ротанга выводится как «−50…+50» (U+2212, U+2026); у не-ротанга не выводится вовсе.
- Заголовок категории: «{Категория} из {материала в род. падеже} — купить в Тольятти и Самаре | ESTIVO»
  (допущение: поля падежа у Material нет — тесты проверяют «Ротанг» -> «ротанга», «Роуп» -> «роупа»).
- «[уточнить» не выводится нигде на отрендеренных страницах (решение владельца 23.10.2026).

Ручная проверка: «6–8 товаров с ценами в первых двух экранах» и «полоса распродажи после них» (f1),
кнопка «Другие модели» (место не задано спекой), порядок и вёрстка блоков.
"""
import re
from html import unescape
from io import StringIO
from pathlib import Path

from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from shop.models import Category, Material, Product, Review

from .helpers import make_product, norm_space, parse

SHOP_DIR = Path(__file__).resolve().parents[1]

FORBIDDEN_PATTERNS = [
    r'Error get alias', r'BUY NOW', r'More products', r'Copy:', r'натуральн', r'Rolls-Royce',
    r'Эверест', r'в любую точку мира', r'(?<![\d])5\s*лет', r'24\s*месяц',
    r'(?<![\w])[-−]70(?![\d]|px|rem|em|vh|vw)', r'Оформить заказ', r'ИП\s+Мелихов',
]
FORBIDDEN_RE = [re.compile(p, re.I) for p in FORBIDDEN_PATTERNS]


def forbidden_in(text):
    return [r.pattern for r in FORBIDDEN_RE if r.search(text)]


def text_of(resp):
    return norm_space(unescape(resp.content.decode()))


def visible(node):
    return norm_space(node.text)


class FWorld(TestCase):
    """Общие данные: ротанг в наличии (−50…+50), роуп под заказ с заданной температурой."""

    @classmethod
    def setUpTestData(cls):
        cls.rotang = Material.objects.create(name='Ротанг', slug='rotang')
        cls.roup = Material.objects.create(name='Роуп', slug='roup')
        cls.kresla = Category.objects.create(name='Кресла', slug='kresla')
        cls.p_rotang = make_product(
            name='Кресло Ротангово', slug='kreslo-rotangovo', price=30000, material=cls.rotang,
            category=cls.kresla, is_available=True, temp_min_c=-50, temp_max_c=50, is_featured=True)
        cls.p_roup = make_product(
            name='Кресло Роупово', slug='kreslo-roupovo', price=40000, material=cls.roup,
            category=cls.kresla, is_available=False, temp_min_c=-33, temp_max_c=44, is_featured=True)
        Review.objects.create(product=cls.p_rotang, author='Мария', rating=5, text='Чудесно', is_published=True)

    def add(self, product):
        self.client.post(reverse('cart_add', args=[product.id]), {'quantity': 1})

    def get_text(self, url):
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200, url)
        return text_of(resp)

    def content_urls(self):
        return {n: reverse(n) for n in (
            'b2b_page', 'designers_page', 'about_page', 'delivery_payment_page',
            'privacy_page', 'warranty_page', 'faq_page', 'contacts_page')}

    def all_pages(self):
        """name -> html-текст всех проверяемых страниц (корзина с товаром, checkout, order_success)."""
        pages = {
            'home': reverse('home'),
            'catalog': reverse('catalog_list'),
            'catalog_sale': reverse('catalog_list') + '?flag=sale',
            'material': reverse('catalog_by_material', args=['rotang']),
            'category': reverse('catalog_by_category', args=['rotang', 'kresla']),
            'pdp_rotang': self.p_rotang.get_absolute_url(),
            'pdp_roup': self.p_roup.get_absolute_url(),
            **self.content_urls(),
        }
        out = {name: self.get_text(url) for name, url in pages.items()}
        self.add(self.p_rotang)
        self.add(self.p_roup)
        out['cart'] = self.get_text(reverse('cart_detail'))
        out['checkout'] = self.get_text(reverse('checkout'))
        out['order_success'] = self.get_text(reverse('order_success'))
        return out


class FForbiddenTextsTests(FWorld):
    def test_f_sources_have_no_forbidden_phrases(self):
        files = [p for p in (SHOP_DIR / 'templates').rglob('*') if p.is_file()]
        files += [SHOP_DIR / 'management' / 'commands' / 'seed_demo.py', SHOP_DIR / 'context_processors.py']
        self.assertGreater(len(files), 20)
        for path in files:
            with self.subTest(file=str(path.relative_to(SHOP_DIR))):
                self.assertEqual(forbidden_in(path.read_text(encoding='utf-8')), [])

    def test_f_rendered_pages_have_no_forbidden_phrases(self):
        for name, text in self.all_pages().items():
            with self.subTest(page=name):
                self.assertEqual(forbidden_in(text), [])

    def test_f_no_clarify_placeholders_anywhere(self):
        for name, text in self.all_pages().items():
            with self.subTest(page=name):
                self.assertNotIn('[уточнить', text)

    def test_f_no_old_delivery_and_payment_wording(self):
        for name, text in self.all_pages().items():
            with self.subTest(page=name):
                low = text.lower()
                self.assertNotIn('от 3 дней', low)
                self.assertNotIn('оплата при получении', low)
                self.assertNotIn('по реквизитам ип', low)

    def test_f_no_callback_time_promised(self):
        for name in ('cart', 'checkout', 'order_success'):
            with self.subTest(page=name):
                text = self.all_pages()[name]
                self.assertIsNone(re.search(r'перезвон\w*\s+в течение', text, re.I))


class FHomeTests(FWorld):
    def setUp(self):
        resp = self.client.get(reverse('home'))
        self.assertEqual(resp.status_code, 200)
        self.root = parse(resp)
        self.text = text_of(resp)
        self.hero = self.root.find(attrs={'data-section': 'hero'})

    def test_f1_h1_matches_audit(self):
        h1s = self.root.find_all('h1')
        self.assertEqual(len(h1s), 1)
        # ui-refresh: «Тольятти» ушло из h1 в подпись над ним, остаётся в <title> и meta description
        self.assertEqual(visible(h1s[0]), 'Плетёная мебель из ротанга и роупа')
        self.assertIn('Тольятти', visible(self.root.find('title')))

    def test_f1_hero_buttons(self):
        self.assertIsNotNone(self.hero)
        labels = {visible(a) for a in self.hero.find_all('a')} | {visible(b) for b in self.hero.find_all('button')}
        for label in ('Подобрать комплект', 'Каталог ротанга', 'Каталог роупа'):
            self.assertIn(label, labels)

    def test_f1_hero_subtitle_says_metal_frame(self):
        self.assertRegex(visible(self.hero), r'(?i)металл')
        self.assertNotIn('алюмини', visible(self.hero).lower())

    def test_f1_hero_has_no_sale_strip(self):
        self.assertIsNotNone(self.hero)
        self.assertNotRegex(visible(self.hero), r'(?i)распродаж|акци[яи]|скидк')
        for node in self.hero.iter():
            self.assertNotIn('sale', ' '.join(node.classes()).lower())
            self.assertNotIn('sale', node.get('data-section', '').lower())

    def test_f1_confirmed_production_claim(self):
        self.assertIn('Своё производство в Тольятти', self.text)
        self.assertIn('3 цеха и склад 650 м²', self.text)


class FWhyEstivoTests(FWorld):
    def pages(self):
        return {
            'home': reverse('home'),
            'catalog': reverse('catalog_list'),
            'pdp': self.p_rotang.get_absolute_url(),
        }

    def test_f2_block_present_with_points(self):
        # ui-refresh: полный блок только на главной
        text = self.get_text(self.pages()['home'])
        self.assertIn('Почему ESTIVO', text)
        self.assertIn('3 года', text)
        self.assertIn('от 4 недель', text)
        self.assertIn('50%', text)
        self.assertIn('до двери', text)

    def test_f2_catalog_and_pdp_have_facts_strip_instead(self):
        for name in ('catalog', 'pdp'):
            with self.subTest(page=name):
                text = self.get_text(self.pages()[name])
                self.assertNotIn('Почему ESTIVO', text)
                self.assertIn('3 года', text)
                self.assertIn('от 4 недель', text)

    def test_f2_no_instalment_point(self):
        for name, url in self.pages().items():
            with self.subTest(page=name):
                self.assertNotIn('рассрочк', self.get_text(url).lower())


class FProductPageTests(FWorld):
    def test_f3_rotang_pdp_template(self):
        resp = self.client.get(self.p_rotang.get_absolute_url())
        text = text_of(resp)
        self.assertIn('Отгрузка в течение 3 дней', text)
        self.assertRegex(text, r'Гарантия\s*3 года')
        self.assertIn('50%', text)
        self.assertRegex(text, r'(?i)каркас\s*[—–-]\s*металл')
        self.assertIn('−50…+50', text)
        links = parse(resp).find_all('a', pred=lambda a: a.get('href', '').rstrip('/').endswith('/garantiya'))
        self.assertTrue(links, 'нет ссылки на /garantiya/')
        self.assertEqual(reverse('warranty_page'), '/garantiya/')

    def test_f3_pdp_shows_both_terms(self):
        # решение 23.10.2026: is_available = «показан на сайте», не наличие → оба срока всегда
        text = self.get_text(self.p_rotang.get_absolute_url())
        self.assertIn('Отгрузка в течение 3 дней', text)
        self.assertIn('Изготовление от 4 недель', text)

    def test_f3_roup_does_not_show_temperature(self):
        resp = self.client.get(self.p_roup.get_absolute_url())
        text = text_of(resp)
        for needle in ('−33', '-33', '+44', '33…', 'Температур'):
            self.assertNotIn(needle, text)

    def test_f3_rotang_shows_temperature_exact_format(self):
        self.assertIn('−50…+50', self.get_text(self.p_rotang.get_absolute_url()))


class FCartAndFormsTests(FWorld):
    def test_f4_cart_available(self):
        self.add(self.p_rotang)
        text = self.get_text(reverse('cart_detail'))
        for needle in ('Гарантия 3 года', 'Отгрузка в течение 3 дней', '50%', 'Ваша заявка', 'Перейти к заявке',
                       'менеджер перезвонит', 'уточнит цвет, сроки и стоимость доставки'):
            self.assertIn(needle, text)

    def test_f4_cart_shows_both_terms(self):
        self.add(self.p_rotang)
        self.assertIn('Изготовление от 4 недель', self.get_text(reverse('cart_detail')))

    def test_f4_cart_link_to_checkout(self):
        self.add(self.p_rotang)
        root = parse(self.client.get(reverse('cart_detail')))
        link = root.find('a', pred=lambda a: 'Перейти к заявке' in a.text)
        self.assertIsNotNone(link)
        self.assertEqual(link.get('href'), reverse('checkout'))

    def test_f4_checkout_captions(self):
        self.add(self.p_rotang)
        resp = self.client.get(reverse('checkout'))
        root = parse(resp)
        text = text_of(resp)
        self.assertIn('Ваша заявка', text)
        form = root.find('form', pred=lambda f: f.find('input', attrs={'name': 'customer_phone'}) is not None)
        self.assertIsNotNone(form)
        buttons = [visible(b) for b in form.find_all('button')]
        self.assertIn('Получить расчёт', buttons)
        self.assertNotIn('Отправить заявку', text)

    def test_f4_order_success(self):
        text = self.get_text(reverse('order_success'))
        self.assertIn('Заявка принята', text)
        self.assertIn('+7 927 268-94-04', text)
        self.assertIn('Перезвоним с номера', text)

    def test_f4_lead_forms_caption(self):
        for name in ('contacts_page', 'b2b_page', 'designers_page'):
            with self.subTest(page=name):
                resp = self.client.get(reverse(name))
                root = parse(resp)
                form = root.find('form', pred=lambda f: f.find('input', attrs={'name': 'phone'}) is not None)
                self.assertIsNotNone(form)
                self.assertIn('Получить консультацию', [visible(b) for b in form.find_all('button')])
                self.assertNotIn('Отправить заявку', text_of(resp))


class FContentPagesTests(FWorld):
    def test_f5_payment_contract_50_50(self):
        text = self.get_text(reverse('delivery_payment_page'))
        self.assertIn('50%', text)
        self.assertRegex(text, r'(?i)договор')
        self.assertRegex(text, r'(?i)фото- и видеоотчёт')

    def test_f5_single_warranty_value(self):
        text = self.get_text(reverse('warranty_page'))
        self.assertIn('3 года', text)
        years = set(re.findall(r'(?<![\d,.])(\d+)\s*(?:лет|года|год)\b', text))
        self.assertEqual(years - {'3'}, set(), 'на странице гарантии несколько разных сроков')

    def test_f5_material_wording(self):
        texts = [self.get_text(reverse(n)) for n in
                 ('about_page', 'warranty_page', 'delivery_payment_page', 'b2b_page', 'faq_page')]
        self.assertTrue(any(re.search(r'(?i)искусственн\w+ ротанг\s*\(ПЭ\)', t) for t in texts))
        self.assertTrue(any(re.search(r'(?i)ручное плетение', t) for t in texts))


class FCategoryTitleTests(FWorld):
    def title(self, material_slug):
        root = parse(self.client.get(reverse('catalog_by_category', args=[material_slug, 'kresla'])))
        return visible(root.find('title'))

    def test_f7_category_title_template(self):
        self.assertEqual(self.title('rotang'), 'Кресла из ротанга — купить в Тольятти и Самаре | ESTIVO')
        self.assertEqual(self.title('roup'), 'Кресла из роупа — купить в Тольятти и Самаре | ESTIVO')


class FSeedDemoTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('seed_demo', stdout=StringIO())

    def test_f6_warranty_and_temperature_rule(self):
        products = list(Product.objects.select_related('material'))
        self.assertTrue(products)
        for p in products:
            with self.subTest(product=p.name):
                self.assertEqual(p.warranty_years, 3)
                if p.material and p.material.name == 'Ротанг':
                    self.assertEqual((p.temp_min_c, p.temp_max_c), (-50, 50))
                else:
                    self.assertEqual((p.temp_min_c, p.temp_max_c), (None, None))

    def test_f6_seeded_texts_have_no_forbidden_phrases(self):
        from shop.models import Collection
        for model in (Material, Category, Collection, Product, Review):
            for obj in model.objects.all():
                blob = ' '.join(str(v) for f in obj._meta.get_fields()
                                if getattr(f, 'concrete', False) and not f.is_relation
                                for v in [getattr(obj, f.attname)] if isinstance(v, str))
                with self.subTest(obj=f'{model.__name__}:{obj}'):
                    self.assertEqual(forbidden_in(blob), [])
