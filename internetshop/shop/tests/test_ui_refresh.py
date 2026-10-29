"""Контракт ui-refresh (docs/specs/ui-refresh/SPEC.md): сетка 1360/12, единая шкала заголовков, правило кнопок.

Один класс на эпик: FoundationTests (E1), HomeTests (E2), CatalogTests (E3), ProductTests (E4), CartTests (E5),
PagesTests (E6), DocsTests (E7). Воркер прогоняет свой класс: `python manage.py test shop.tests.test_ui_refresh.HomeTests`.

CSS, шаблоны и документы читаются как текст (регулярки по правилам и токенам), страницы — через клиент и разбор HTML.
Допущения парсера CSS те же, что в test_design_tokens: листовые блоки `селектор { объявления }`, @layer/@media-обёртки
игнорируются, комментарии вырезаются; var(--токен) раскрывается по блоку @theme.

Ручная проверка (тестами не покрыть): размеры на 390/1440 (контент >= 1340px, нет горизонтальной прокрутки),
фото hero и «Кто мы» во всю ширину, 4 карточки в ряд, липкая панель и кнопка чата на 390, `aiw-ru scan docs/design-system.md`
и `site-copy-check` по новым текстам.
"""
import re
from pathlib import Path

from django.conf import settings
from django.template.loader import get_template, render_to_string
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from shop.context_processors import SITE_INFO
from shop.models import Category, Material, Review

from .helpers import has_number, make_product, norm_space, parse
from .test_design_tokens import MAIN_CSS, SRC, TEMPLATES, css_files, decls, norm, read, rules, template_files, theme_tokens
from .test_pages_ui import HOME_SECTIONS

BASE = Path(settings.BASE_DIR)
ROOT = BASE.parent
STYLES = SRC / 'styles'
HEADINGS = r'(?:^|[\s>+~])(?:h1|h2|\.page-h1|\.page-h2)(?:::?[\w-]+)?$'


# --- общие помощники --------------------------------------------------------------------------

def selector_items(selector):
    return [s.strip() for s in selector.split(',') if s.strip()]


def css_rules(files=None):
    """[(файл, селектор-элемент, объявления)] — по одному на каждый элемент списка селекторов."""
    out = []
    for f in files or css_files():
        for sel, body in rules(read(f)):
            for item in selector_items(sel):
                out.append((f.name, item, decls(body)))
    return out


def merged(selector, files=None):
    """Объявления правил с ровно этим селектором; поздние перекрывают ранние."""
    result = {}
    for _, item, d in css_rules(files):
        if item == selector:
            result.update({k: re.sub(r'\s*!important', '', v).strip() for k, v in d.items()})
    return result


def resolve(value):
    """var(--токен) -> значение из @theme (рекурсивно), rem -> px, без пробелов, строчные."""
    theme = theme_tokens()
    for _ in range(5):
        value = re.sub(r'var\(\s*(--[\w-]+)\s*(?:,[^)]*)?\)', lambda m: theme.get(m.group(1), m.group(0)), value)
    value = norm(value)
    return re.sub(r'(\d*\.?\d+)rem', lambda m: f'{float(m.group(1)) * 16:g}px', value)


def tpl(name):
    return read(TEMPLATES / name)


def order_index(root, node):
    return next(i for i, n in enumerate(root.iter()) if n is node)


def eyebrow_before_h1(root):
    h1 = root.find('h1')
    return [e for e in root.find_all(cls='eyebrow') if order_index(root, e) < order_index(root, h1)]


def count_class(text, cls):
    return len(re.findall(rf'(?<![\w-]){re.escape(cls)}(?![\w-])', text))


# --- E1 ---------------------------------------------------------------------------------------

class FoundationTests(SimpleTestCase):
    """E1: токены, типографика, общие компоненты."""

    def test_e1_theme_tokens_new_values(self):
        theme = theme_tokens()
        expected = {
            '--container': '1360px', '--control-height': '52px', '--weight-body-regular': '400',
            '--weight-body-bold': '800', '--weight-ui': '600', '--page-pad': 'clamp(16px,4vw,48px)',
        }
        for token, value in expected.items():
            self.assertEqual(norm(theme.get(token, '')), value, token)

    def test_e1_module_and_gutter_removed_everywhere(self):
        pattern = re.compile(r'(?<![\w-])--(?:module|gutter)(?![\w-])')
        found = []
        for f in css_files() + template_files():
            found += [f'{f.name}: {m.group(0)}' for m in pattern.finditer(read(f))]
        self.assertEqual(found, [])

    def test_e1_no_uppercase_in_h1_h2_rules(self):
        bad = []
        for name, item, d in css_rules():
            if re.search(HEADINGS, item) and 'uppercase' in d.get('text-transform', ''):
                bad.append(f'{name}: {item}')
        self.assertEqual(bad, [])

    def test_e1_heading_weight_400(self):
        bad = []
        for name, item, d in css_rules():
            if item in ('h1', 'h2', '.page-h1', '.page-h2') and 'font-weight' in d and norm(d['font-weight']) != '400':
                bad.append(f'{name}: {item} {{ font-weight: {d["font-weight"]} }}')
        self.assertEqual(bad, [])

    def test_e1_single_heading_scale(self):
        """display 44-76/1.02, h2 32-48/1.05, h3 24/1.2; .page-hN либо та же шкала, либо наследуют от hN."""
        scale = {
            'h1': ('clamp(44px,6vw,76px)', '1.02'), 'h2': ('clamp(32px,3.6vw,48px)', '1.05'), 'h3': ('24px', '1.2'),
        }
        for tag, (size, line) in scale.items():
            for selector, required in ((tag, True), (f'.page-{tag}', False)):
                d = merged(selector)
                got_size, got_line = d.get('font-size'), d.get('line-height')
                if got_size is None and not required:
                    got_size = None
                else:
                    self.assertEqual(resolve(got_size or ''), size, f'{selector} font-size')
                if got_line is None and not required:
                    continue
                self.assertEqual(resolve(got_line or ''), line, f'{selector} line-height')

    def test_e1_eyebrow_component(self):
        d = merged('.eyebrow', [MAIN_CSS])
        self.assertTrue(d, '.eyebrow не найден в main.css')
        self.assertEqual(resolve(d.get('font-size', '')), '14px')
        self.assertEqual(norm(d.get('font-weight', '')), '500')
        self.assertEqual(norm(d.get('text-transform', '')), 'uppercase')
        self.assertEqual(norm(d.get('letter-spacing', '')), '0.08em')
        self.assertIn(norm(d.get('color', '')), ('var(--color-ink-muted)', '#6d6d6d'))

    def test_e1_buttons_use_weight_ui_and_body_regular(self):
        for selector in ('.btn', '.btn-primary'):
            self.assertEqual(norm(merged(selector, [MAIN_CSS]).get('font-weight', '')), 'var(--weight-ui)', selector)
        self.assertEqual(norm(merged('body', [MAIN_CSS]).get('font-weight', '')), 'var(--weight-body-regular)')

    def test_e1_controls_follow_control_height(self):
        for selector in ('.btn-lg', '.form-input'):
            self.assertEqual(norm(merged(selector, [MAIN_CSS]).get('min-height', '')), 'var(--control-height)', selector)

    def test_e1_section_modifiers(self):
        selectors = {item for _, item, _ in css_rules([STYLES / 'pages.css'])}
        self.assertIn('.page-section--tight', selectors)
        self.assertIn('.page-section--loose', selectors)
        for selector, pair in (('.page-section--tight', {'40px', '64px'}), ('.page-section--loose', {'64px', '128px'})):
            paddings = set()
            for _, item, d in css_rules([STYLES / 'pages.css']):
                if item == selector:
                    paddings |= {resolve(d[k]) for k in ('padding-block', 'padding-top', 'padding-bottom') if k in d}
            self.assertTrue(pair <= paddings, f'{selector}: отступы {paddings}, нужны {pair}')

    def test_e1_section_dark_removed(self):
        found = [f.name for f in css_files() + template_files() + sorted(SRC.rglob('*.ts'))
                 if 'page-section--dark' in read(f)]
        self.assertEqual(found, [])

    def test_e1_facts_strip_partial(self):
        info = dict(SITE_INFO, warranty='ГАРАНТИЯ-ТЕСТ', production_term='СРОК-ТЕСТ')
        html = render_to_string('partials/_facts_strip.html', {'site_info': info})
        self.assertIn('data-facts-strip', html)
        self.assertIn('ГАРАНТИЯ-ТЕСТ', html)
        self.assertIn('СРОК-ТЕСТ', html)
        real = norm_space(parse(render_to_string('partials/_facts_strip.html', {'site_info': SITE_INFO})).text)
        for phrase in (SITE_INFO['warranty'], SITE_INFO['production_term'], 'Доставка ТК по России', 'Работаем по договору'):
            self.assertIn(phrase, real)

    def test_e1_page_container_uses_page_pad(self):
        d = merged('.page-container', [STYLES / 'pages.css'])
        self.assertIn('var(--page-pad)', ' '.join(d.values()))

    def test_e1_header_footer_promo_use_page_pad(self):
        css_pad = ' '.join(item for _, item, d in css_rules() if 'var(--page-pad)' in ' '.join(d.values()))
        for name, css_word in (('_header.html', 'header'), ('_footer.html', 'footer'), ('_promo_bar.html', 'promo')):
            text = read(TEMPLATES / 'partials' / name)
            via_template = 'var(--page-pad)' in text or 'page-container' in text
            via_css = css_word in css_pad
            self.assertTrue(via_template or via_css, f'{name} не использует --page-pad')
            self.assertNotRegex(text, r'max-w-\[var\(--container\)\][^"]*\bpx-4\b', f'{name}: поля 16/24px вместо --page-pad')

    def test_e1_home_css_imported(self):
        self.assertTrue((STYLES / 'home.css').exists(), 'нет frontend/src/styles/home.css')
        self.assertRegex(read(MAIN_CSS), r'@import\s+["\']\./home\.css["\']')


# --- данные для страниц -----------------------------------------------------------------------

class World(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.rotang = Material.objects.create(name='Ротанг', slug='rotang')
        cls.roup = Material.objects.create(name='Роуп', slug='roup')
        cls.kresla = Category.objects.create(name='Кресла', slug='kresla')
        cls.products = [
            make_product(name=f'Кресло Рефреш {i}', slug=f'kreslo-refresh-{i}', price=20000 + i,
                         material=cls.rotang, category=cls.kresla, is_featured=True)
            for i in range(3)
        ]
        cls.product = cls.products[0]
        Review.objects.create(product=cls.product, author='Мария', rating=5, text='Чудесно', is_published=True)


# --- E2 ---------------------------------------------------------------------------------------

class HomeTests(World):
    def setUp(self):
        resp = self.client.get(reverse('home'))
        self.assertEqual(resp.status_code, 200)
        self.resp = resp
        self.root = parse(resp)

    def test_e2_hero_one_primary_no_outline_catalog_links(self):
        hero = self.root.find(attrs={'data-section': 'hero'})
        self.assertIsNotNone(hero)
        self.assertEqual(len(hero.find_all(cls='btn-primary')), 1)
        self.assertEqual(len(hero.find_all(cls='btn-outline')), 0)
        hrefs = {a.get('href') for a in hero.find_all('a', attrs={'href': True})}
        for slug in ('rotang', 'roup'):
            self.assertIn(reverse('catalog_by_material', args=[slug]), hrefs)

    def test_e2_h1_text_and_eyebrow_above(self):
        h1 = self.root.find('h1')
        self.assertEqual(norm_space(h1.text), 'Плетёная мебель из ротанга и роупа')
        above = eyebrow_before_h1(self.root)
        self.assertTrue(any(norm_space(e.text) == 'Своё производство · Тольятти' for e in above),
                        f'над h1 нет .eyebrow «Своё производство · Тольятти»: {[norm_space(e.text) for e in above]}')

    def test_e2_template_has_at_most_one_alt_and_no_dark(self):
        text = tpl('home.html')
        self.assertLessEqual(count_class(text, 'page-section--alt'), 1)
        self.assertEqual(count_class(text, 'page-section--dark'), 0)

    def test_e2_why_estivo_without_page_card_and_only_on_home(self):
        self.assertEqual(count_class(read(TEMPLATES / 'partials' / '_why_estivo.html'), 'page-card'), 0)
        includers = sorted(f.name for f in template_files() if '_why_estivo.html' in read(f))
        self.assertEqual(includers, ['home.html'])

    def test_e2_sections_in_order(self):
        order = [n.get('data-section') for n in self.root.find_all(attrs={'data-section': True})
                 if n.get('data-section') in HOME_SECTIONS]
        self.assertEqual(order, HOME_SECTIONS)


# --- E3 ---------------------------------------------------------------------------------------

class CatalogTests(World):
    def test_e3_facts_strip_instead_of_why_estivo(self):
        resp = self.client.get(reverse('catalog_by_category', args=['rotang', 'kresla']))
        self.assertEqual(resp.status_code, 200)
        root = parse(resp)
        self.assertIsNone(root.find(attrs={'data-section': 'why-estivo'}))
        self.assertEqual(root.find_all(cls='page-card'), [])
        self.assertIsNotNone(root.find(attrs={'data-facts-strip': True}))

    def test_e3_banner_eyebrow_with_product_count(self):
        for url in (reverse('catalog_by_category', args=['rotang', 'kresla']), reverse('catalog_by_material', args=['rotang'])):
            root = parse(self.client.get(url))
            texts = [norm_space(e.text) for e in root.find_all(cls='eyebrow')]
            self.assertTrue(any(re.search(r'(?<![\d.,])3\s+модел', t) for t in texts), f'{url}: подписи {texts}')
        material_texts = [norm_space(e.text) for e in
                          parse(self.client.get(reverse('catalog_by_material', args=['rotang']))).find_all(cls='eyebrow')]
        self.assertTrue(any('Ротанг' in t for t in material_texts), material_texts)

    def test_e3_empty_catalog_primary_request_link(self):
        resp = self.client.get(reverse('catalog_by_category', args=['roup', 'kresla']))
        self.assertEqual(resp.status_code, 200)
        root = parse(resp)
        title = root.find(pred=lambda n: n.tag in ('h2', 'h3') and 'Ничего не найдено' in n.text)
        self.assertIsNotNone(title, 'нет пустого состояния «Ничего не найдено»')
        box = title.parent
        link = box.find('a', pred=lambda a: 'Оставить заявку' in a.text) or \
            box.parent.find('a', pred=lambda a: 'Оставить заявку' in a.text)
        self.assertIsNotNone(link, 'в пустом каталоге нет ссылки «Оставить заявку»')
        self.assertTrue(link.has_class('btn-primary'), link.classes())


# --- E4 ---------------------------------------------------------------------------------------

class ProductTests(World):
    def get(self, product):
        resp = self.client.get(product.get_absolute_url())
        self.assertEqual(resp.status_code, 200)
        return parse(resp)

    def test_e4_checkout_primary_add_to_cart_dark(self):
        root = self.get(self.product)
        checkout = root.find_all('button', attrs={'name': 'checkout'})
        self.assertTrue(checkout)
        for btn in checkout:
            self.assertTrue(btn.has_class('btn-primary'), btn.classes())
        for btn in root.find_all('button', pred=lambda n: 'Оформить заявку' in n.text):
            self.assertTrue(btn.has_class('btn-primary'), f'липкая панель: {btn.classes()}')
        adds = root.find_all(attrs={'data-add-to-cart': True})
        self.assertTrue(adds)
        for btn in adds:
            self.assertTrue(btn.has_class('btn-dark'), btn.classes())
            self.assertFalse(btn.has_class('btn-primary'))

    def test_e4_eyebrow_above_h1_with_category_and_material(self):
        root = self.get(self.product)
        texts = [norm_space(e.text) for e in eyebrow_before_h1(root)]
        self.assertTrue(any('Кресла' in t and 'Ротанг' in t and t.index('Кресла') < t.index('Ротанг') and '·' in t
                            for t in texts), f'подписи над h1: {texts}')

    def test_e4_facts_strip_instead_of_why_estivo(self):
        resp = self.client.get(self.product.get_absolute_url())
        root = parse(resp)
        self.assertIsNone(root.find(attrs={'data-section': 'why-estivo'}))
        self.assertIsNotNone(root.find(attrs={'data-facts-strip': True}))
        self.assertTemplateNotUsed(resp, 'partials/_why_estivo.html')

    def test_e4_price_request_is_not_primary(self):
        free = make_product(name='Кресло Без Цены', slug='kreslo-bez-ceny', price=0,
                            material=self.rotang, category=self.kresla)
        root = self.get(free)
        links = root.find_all(pred=lambda n: n.tag in ('a', 'button') and 'Узнать цену' in n.text
                              and n.closest(cls='product-card') is None)
        self.assertTrue(links, 'на странице товара без цены нет «Узнать цену»')
        for link in links:
            self.assertFalse(link.has_class('btn-primary'), link.classes())
        self.assertTrue(any((a.get('href') or '').startswith(reverse('contacts_page')) for a in links))


# --- E5 ---------------------------------------------------------------------------------------

class CartTests(World):
    def setUp(self):
        self.client.post(reverse('cart_add', args=[self.product.id]))
        resp = self.client.get(reverse('cart_detail'))
        self.assertEqual(resp.status_code, 200)
        self.root = parse(resp)

    def test_e5_one_primary_and_continue_is_text_link(self):
        primary = self.root.find_all(cls='btn-primary')
        self.assertEqual(len(primary), 1, [p.text for p in primary])
        self.assertIn('Перейти к заявке', primary[0].text)
        links = self.root.find_all('a', pred=lambda a: 'Продолжить покупки' in a.text)
        self.assertTrue(links)
        for link in links:
            self.assertFalse(link.has_class('btn'), link.classes())

    def test_e5_cart_body_class_chat_inline(self):
        self.assertTrue(self.root.find('body').has_class('chat-inline'))

    def _assert_no_surface_alt(self, nodes, css_files_):
        for node in nodes:
            self.assertNotIn('surface-alt', node.get('class', ''), node.classes())
            for cls in node.classes():
                d = merged(f'.{cls}', css_files_)
                self.assertNotIn('surface-alt', ' '.join(d.values()), f'.{cls}')

    def test_e5_cart_summary_not_gray(self):
        button = self.root.find(cls='btn-primary')
        chain = []
        for anc in button.ancestors():
            if anc.get('id') == 'cart-lines' or anc.tag == 'main':
                break
            chain.append(anc)
        self.assertTrue(chain)
        self._assert_no_surface_alt(chain, [STYLES / 'cart.css', STYLES / 'request.css'])
        for name in ('cart.html', 'checkout.html', 'partials/htmx/_cart_lines.html', 'partials/htmx/_cart_drawer.html'):
            self.assertNotRegex(tpl(name), r'bg-surface-alt|--color-surface-alt', name)

    def test_e5_checkout_summary_not_gray(self):
        root = parse(self.client.get(reverse('checkout')))
        aside = root.find('aside')
        self.assertIsNotNone(aside)
        totals = [n for n in aside.iter() if any('total' in c for c in n.classes())]
        self._assert_no_surface_alt([aside, *totals], [STYLES / 'cart.css', STYLES / 'request.css'])


# --- E6 ---------------------------------------------------------------------------------------

ZONE_TEMPLATES = ['about', 'b2b', 'designers', 'contacts', 'faq', 'delivery_payment', 'warranty', 'privacy',
                  '404', '410', '500', 'order_success']
ZONE_PARTIALS = ['_cta_section', '_lead_form', '_breadcrumbs']
CONTENT_PAGES = ['about_page', 'b2b_page', 'designers_page', 'contacts_page', 'faq_page', 'delivery_payment_page',
                 'warranty_page', 'privacy_page', 'order_success']


def heading_gaps(scope):
    gaps, prev = [], 0
    for node in scope.iter():
        if re.fullmatch(r'h[1-6]', node.tag):
            level = int(node.tag[1])
            if level > prev + 1:
                gaps.append(f'{node.tag} «{norm_space(node.text)[:30]}» после h{prev}')
            prev = level
    return gaps


class PagesTests(World):
    def page(self, name):
        """(статус, html) для страницы зоны: 404/410 — реальные URL, 500 — рендер статического шаблона."""
        if name == '404':
            resp = self.client.get('/takoy-stranicy-net/')
            return 404, resp.status_code, resp.content.decode()
        if name == '410':
            resp = self.client.get('/tproduct/121969165582-sac-marin-yellow')
            return 410, resp.status_code, resp.content.decode()
        if name == '500':
            return 500, 500, get_template('500.html').render({})
        resp = self.client.get(reverse(name))
        return 200, resp.status_code, resp.content.decode()

    def test_e6_zone_templates_at_most_one_alt_no_dark(self):
        for name in ZONE_TEMPLATES:
            text = tpl(f'{name}.html')
            self.assertLessEqual(count_class(text, 'page-section--alt'), 1, name)
            self.assertEqual(count_class(text, 'page-section--dark'), 0, name)
        for name in ZONE_PARTIALS:
            text = read(TEMPLATES / 'partials' / f'{name}.html')
            self.assertLessEqual(count_class(text, 'page-section--alt'), 1, name)
            self.assertEqual(count_class(text, 'page-section--dark'), 0, name)

    def test_e6_lead_form_submit_is_primary(self):
        for name in ('contacts_page', 'b2b_page', 'designers_page'):
            root = parse(self.client.get(reverse(name)))
            form = root.find('form', pred=lambda f: f.find('input', attrs={'name': 'phone'}) is not None)
            self.assertIsNotNone(form, name)
            submit = form.find('button', pred=lambda b: b.get('type', 'submit') == 'submit')
            self.assertIsNotNone(submit, name)
            self.assertTrue(submit.has_class('btn-primary'), f'{name}: {submit.classes()}')

    def test_e6_cta_section_request_is_primary(self):
        root = parse(render_to_string('partials/_cta_section.html', {'site_info': SITE_INFO}))
        link = root.find('a', pred=lambda a: 'Оставить заявку' in a.text)
        self.assertIsNotNone(link)
        self.assertTrue(link.has_class('btn-primary'), link.classes())

    def test_e6_form_pages_have_chat_inline(self):
        for name in ('contacts_page', 'b2b_page', 'designers_page'):
            body = parse(self.client.get(reverse(name))).find('body')
            self.assertTrue(body.has_class('chat-inline'), name)

    def test_e6_pages_status_single_h1_heading_levels(self):
        for name in [*CONTENT_PAGES, '404', '410', '500']:
            with self.subTest(page=name):
                expected, status, html = self.page(name)
                self.assertEqual(status, expected)
                root = parse(html)
                self.assertEqual(len(root.find_all('h1')), 1, 'нужен ровно один h1')
                self.assertEqual(heading_gaps(root.find('main') or root), [])


# --- E7 ---------------------------------------------------------------------------------------

class DocsTests(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ds = (ROOT / 'docs' / 'design-system.md').read_text(encoding='utf-8')
        cls.claude = (ROOT / 'CLAUDE.md').read_text(encoding='utf-8')

    # сообщения короткие: assertNotRegex/assertIn печатают весь документ
    def absent(self, pattern, text, flags=0):
        m = re.search(pattern, text, flags)
        self.assertIsNone(m, f'найдено устаревшее: {m.group(0)!r}' if m else '')

    def present(self, needle, text):
        self.assertTrue(needle in text, f'нет «{needle}»')

    def test_e7_design_system_does_not_cite_tilda_as_source(self):
        for pattern in (r'Источник стиля:\*\*[^\n]*estivo-tilda', r'прав[аы]?\s+`?estivo-tilda',
                        r'estivo-tilda[^\n]*источник (?:правды|стиля)', r'источник (?:правды|стиля)[^\n]*estivo-tilda'):
            self.absent(pattern, self.ds, re.I)
        if 'estivo-tilda' in self.ds:
            self.present('архив', self.ds.lower())

    def test_e7_design_system_has_no_old_values_as_current(self):
        self.absent(r'1160', self.ds)
        self.absent(r'--(?:module|gutter)', self.ds)
        self.absent(r'--control-height[^\n]*60\s*px|60\s*px[^\n]*--control-height', self.ds)
        self.absent(r'--weight-body-regular`?[^\n]{0,20}300', self.ds)

    def test_e7_design_system_describes_new_contract(self):
        for needle in ('1360', '--page-pad', '--weight-ui', '12 колон', '.eyebrow', '.btn-primary', '.btn-dark'):
            self.present(needle, self.ds)
        self.assertIsNotNone(re.search(r'(?i)строк[аиу] фактов', self.ds), 'нет описания строки фактов')

    def test_e7_mapping_marked_as_archive(self):
        head = (ROOT / 'docs' / 'design-system' / 'estivo-tilda' / 'MAPPING.md').read_text(encoding='utf-8')[:1500]
        self.present('архив', head.lower())

    def test_e7_project_claude_md_facts(self):
        self.absent(r'(?i)defaults stay[^\n]*\(300\)', self.claude)
        self.absent(r'(?i)Design source of truth:\s*`?docs/design-system/estivo-tilda', self.claude)
        self.absent(r'--weight-body-regular`?\s*\(300\)', self.claude)
        self.present('1360', self.claude)
