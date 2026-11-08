"""E-A (tilda-migration, a1-a4): токены и базовые стили.

Контракт читает исходники как текст (CSS, TS, шаблоны). Цвета сверяются с tokens.css из estivo-tilda (архив,
палитра не менялась); размеры и веса после ui-refresh (docs/specs/ui-refresh/SPEC.md) заданы литералами ниже.
Источник правил: docs/specs/tilda-migration/SPEC.md (эпик a) и
docs/design-system/estivo-tilda/MAPPING.md (таблицы 1 и 2, пробелы П1-П8).
Шаг a5 (документы) и браузерные проверки (прокрутка, 44x44) здесь не покрываются.

Допущения парсера:
- CSS разбирается регулярками по «листовым» блокам `селектор { объявления }` (без вложенных
  скобок); @layer/@media-обёртки игнорируются, комментарии вырезаются.
- font-weight: в CSS разрешены var(--weight-body-regular|bold|ui) и 300-800 (лицензия Gilroy 300-800,
  владелец 23.10.2026). 100/200/900 допустимы только в правиле с font-family: var(--font-display)
  (Cormorant Garamond), иначе это Gilroy без файла начертания.
- font-size: px < 14 и rem/em < 0.875 запрещены (em считается как rem - допущение);
  в clamp(...) проверяется первый (минимальный) аргумент.
"""
import re
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase, TestCase, override_settings

BASE = Path(settings.BASE_DIR)
SRC = BASE / 'frontend' / 'src'
MAIN_CSS = SRC / 'styles' / 'main.css'
TEMPLATES = BASE / 'shop' / 'templates'
DS = BASE.parent / 'docs' / 'design-system' / 'estivo-tilda'
LOGO = BASE / 'shop' / 'static' / 'img' / 'estivo-logo.svg'


def strip_comments(text):
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.S)
    return re.sub(r'\{#.*?#\}|\{%\s*comment\s*%\}.*?\{%\s*endcomment\s*%\}', '', text, flags=re.S)


def read(path):
    return strip_comments(Path(path).read_text(encoding='utf-8'))


def css_files():
    return sorted((SRC / 'styles').glob('*.css'))


def ts_files():
    return sorted(SRC.rglob('*.ts'))


def template_files():
    return sorted(TEMPLATES.rglob('*.html'))


def all_sources():
    return css_files() + ts_files() + template_files()


def rules(css):
    """[(selector, body)] для листовых блоков."""
    return [(m.group(1).strip(), m.group(2)) for m in re.finditer(r'([^{}]+)\{([^{}]*)\}', css)]


def decls(body):
    return {m.group(1): m.group(2).strip() for m in re.finditer(r'([\w-]+)\s*:\s*([^;]+);?', body)}


def all_rules():
    out = []
    for f in css_files():
        out += [(f.name, sel, body) for sel, body in rules(read(f))]
    return out


def theme_tokens():
    css = read(MAIN_CSS)
    m = re.search(r'@theme\s*\{([^{}]*)\}', css)
    assert m, '@theme не найден в main.css'
    return {k: v.strip() for k, v in re.findall(r'(--[\w*-]+)\s*:\s*([^;]+);', m.group(1))}


def ds_tokens():
    css = (DS / 'tokens.css').read_text(encoding='utf-8')
    out = {}
    for k, v in re.findall(r'(--[\w-]+)\s*:\s*([^;]+);', css):
        out.setdefault(k, v.strip())
    return out


def norm(v):
    """Регистр, пробелы, rgb(...) -> hex, '.6' -> '0.6', '0' -> '0px'."""
    v = re.sub(r'\s+', '', v.lower())
    m = re.fullmatch(r'rgb\((\d+),(\d+),(\d+)\)', v)
    if m:
        return '#%02x%02x%02x' % tuple(int(x) for x in m.groups())
    v = re.sub(r'(?<![\d])\.(\d)', r'0.\1', v)
    return 'px'.join([v, '']) if v == '0' else v


class E_A_ThemeBlockTests(SimpleTestCase):
    """E-A a1: блок @theme в main.css."""

    # estivo-tilda (tokens.css) -> токен проекта; hex сравнивается именно с tokens.css
    COLOR_MAP = {
        '--surface': '--color-bg',
        '--surface-white': '--color-surface',
        '--surface-muted': '--color-surface-alt',
        '--ink': '--color-ink',
        '--ink-black': '--color-ink-black',
        '--ink-soft': '--color-ink-soft',
        '--muted': '--color-ink-muted',
        '--graphite': '--color-graphite',
        '--brand': '--color-brand',
        '--accent': '--color-accent',
        '--border-input': '--color-border-input',
        '--on-dark': '--color-on-dark',
    }
    REMOVED = [
        '--shadow-md', '--radius-lg', '--color-accent-dark', '--color-accent-soft',
        '--color-accent-text', '--color-line', '--color-line-strong', '--color-error',
        '--color-dark', '--color-dark-ink', '--ease-out',
    ]
    ADDED = [
        '--color-ink-black', '--color-graphite', '--color-brand', '--color-on-accent',
        '--color-on-dark', '--color-border-input', '--color-scrim', '--page-pad', '--weight-ui',
        '--control-height', '--tap-min', '--radius-none',
    ]

    def test_removed_tokens_absent(self):
        theme = theme_tokens()
        present = [t for t in self.REMOVED if t in theme]
        self.assertEqual(present, [], 'токены, помеченные в MAPPING «удалить»')

    def test_duration_scales_removed(self):
        theme = theme_tokens()
        bad = [t for t in theme if t.startswith('--duration-') or (t.startswith('--dur-') and t != '--dur-fast')]
        self.assertEqual(bad, [])
        self.assertEqual(norm(theme.get('--dur-fast', '')), '200ms')

    def test_added_tokens_present(self):
        theme = theme_tokens()
        self.assertEqual([t for t in self.ADDED if t not in theme], [])

    def test_colors_match_tokens_css(self):
        theme, ds = theme_tokens(), ds_tokens()
        for ds_name, our in self.COLOR_MAP.items():
            self.assertIn(our, theme, our)
            self.assertEqual(norm(theme[our]), norm(ds[ds_name]), f'{our} != tokens.css {ds_name}')

    def test_colors_match_spec_literals(self):
        theme = theme_tokens()
        expected = {
            '--color-bg': '#fdfdfd', '--color-surface': '#ffffff', '--color-surface-alt': '#f4f4f4',
            '--color-ink': '#281913', '--color-ink-black': '#141414', '--color-ink-soft': '#3c3c3c',
            '--color-ink-muted': '#6d6d6d', '--color-graphite': '#333333', '--color-brand': '#b83400',
            '--color-on-dark': '#ffffff', '--color-border-input': '#c9c9c9', '--color-accent': '#d9783e',
        }
        for k, v in expected.items():
            self.assertEqual(norm(theme.get(k, '')), v, k)

    def test_on_accent_is_ink_and_scrim(self):
        theme = theme_tokens()
        self.assertIn(norm(theme.get('--color-on-accent', '')), ('var(--color-ink)', '#281913'))
        self.assertEqual(norm(theme.get('--color-scrim', '')), 'rgba(0,0,0,0.6)')

    def test_sizes_match_spec_literals(self):
        theme = theme_tokens()
        expected = {
            '--radius-sm': '4px', '--radius-md': '5px', '--radius-pill': '30px', '--container': '1360px',
            '--container-narrow': '692px', '--control-height': '52px', '--tap-min': '44px',
            '--page-pad': 'clamp(16px,4vw,48px)',
            '--weight-body-regular': '400', '--weight-body-bold': '800', '--weight-ui': '600',
        }
        for k, v in expected.items():
            self.assertEqual(norm(theme.get(k, '')), v, k)

    def test_module_and_gutter_removed(self):
        theme = theme_tokens()
        self.assertEqual([t for t in ('--module', '--gutter') if t in theme], [])


class E_A_ForbiddenPatternsTests(SimpleTestCase):
    """E-A a2/a3: запрещённые конструкции в styles/*.css, frontend/src/**/*.ts, templates/**/*.html."""

    REMOVED_COLOR_NAMES = r'accent-text|accent-dark|accent-soft|error|dark-ink|dark|line-strong|line'
    TW_COLOR_CLASS = re.compile(
        r'(?<![\w-])(?:[\w\[\]&:.>-]*:)?-?(?:bg|text|border|ring|fill|stroke|from|to|via|outline|divide|decoration|placeholder)-'
        r'(?:' + REMOVED_COLOR_NAMES + r')(?![\w-])')

    def offenders(self, regex, files=None, flags=0):
        found = []
        for f in files or all_sources():
            for m in re.finditer(regex, read(f), flags):
                found.append(f'{f.name}: {m.group(0)[:60]}')
        return found

    def test_no_box_shadow_except_none(self):
        bad = []
        for f in all_sources():
            for m in re.finditer(r'box-shadow\s*:\s*([^;}"\']+)', read(f)):
                if re.sub(r'\s*!important', '', m.group(1)).strip() != 'none':
                    bad.append(f'{f.name}: {m.group(0)[:60]}')
        self.assertEqual(bad, [])

    def test_no_tailwind_shadow_utilities_in_templates(self):
        bad = self.offenders(r'(?<![\w-])(?:[\w:-]*:)?shadow-(?:xs|sm|md|lg|xl|2xl|inner|\[[^\]]*\])(?![\w-])',
                             template_files() + ts_files())
        self.assertEqual(bad, [])

    def test_no_gradients(self):
        bad = self.offenders(r'(?:linear|radial|conic)-gradient|bg-gradient-|(?<![\w-])bg-(?:linear|radial|conic)-')
        self.assertEqual(bad, [])

    def test_no_removed_variables(self):
        bad = self.offenders(r'var\(\s*--(?:color-accent-text|color-error|radius-lg|shadow-md)\s*[,)]')
        self.assertEqual(bad, [])

    def test_no_removed_token_utility_classes(self):
        bad = []
        for f in template_files() + ts_files():
            bad += [f'{f.name}: {m.group(0)}' for m in self.TW_COLOR_CLASS.finditer(read(f))]
        self.assertEqual(bad, [])

    def test_font_weight_only_licensed_for_body_font(self):
        ok_values = {'var(--weight-body-regular)', 'var(--weight-body-bold)', 'var(--weight-ui)', 'inherit', 'normal', 'bold',
                     '300', '400', '500', '600', '700', '800'}
        bad = []
        for name, sel, body in all_rules():
            d = decls(body)
            w = d.get('font-weight')
            if w is None or re.sub(r'\s*!important', '', w).strip() in ok_values:
                continue
            if 'var(--font-display)' in d.get('font-family', ''):
                continue
            bad.append(f'{name}: {sel} {{ font-weight: {w} }}')
        self.assertEqual(bad, [])

    def test_no_unlicensed_tailwind_font_weight_classes(self):
        bad = []
        for f in template_files() + ts_files():
            bad += [f'{f.name}: {m.group(0)}' for m in
                    re.finditer(r'(?<![\w-])font-(?:thin|extralight|black)(?![\w-])', read(f))]
        self.assertEqual(bad, [])

    def test_no_font_size_below_14px(self):
        bad = []
        for f in css_files() + template_files() + ts_files():
            for m in re.finditer(r'font-size\s*:\s*([^;}"\']+)', read(f)):
                px = self._min_px(m.group(1))
                if px is not None and px < 14:
                    bad.append(f'{f.name}: {m.group(0).strip()}')
            for m in re.finditer(r'(?<![\w-])(?:[\w:-]*:)?text-\[(\d*\.?\d+)(px|rem|em)\]', read(f)):
                if self._to_px(float(m.group(1)), m.group(2)) < 14:
                    bad.append(f'{f.name}: {m.group(0)}')
            bad += [f'{f.name}: {m.group(0)}' for m in
                    re.finditer(r'(?<![\w-])(?:[\w:-]*:)?text-(?:xs|2xs|3xs)(?![\w-])', read(f))]
        self.assertEqual(bad, [])

    def test_no_transform_in_hover_or_active(self):
        bad = []
        for name, sel, body in all_rules():
            if re.search(r':(?:hover|active)', sel) and re.search(r'(?<![-\w])(?:transform|scale|translate|rotate)\s*:', body):
                bad.append(f'{name}: {sel}')
        bad += self.offenders(r'(?<![\w-])(?:group-)?(?:hover|active):-?(?:scale|translate|rotate)-',
                              template_files() + ts_files())
        self.assertEqual(bad, [])

    def test_svg_stroke_width_1_5(self):
        """П7: линия иконок 1,5px; SVG из Lucide по умолчанию с stroke-width="2"."""
        bad = self.offenders(r'stroke-width="(?!1\.5")[^"]*"', template_files() + ts_files())
        self.assertEqual(bad, [])

    @staticmethod
    def _to_px(num, unit):
        return num if unit == 'px' else num * 16

    def _min_px(self, value):
        value = value.strip()
        m = re.match(r'clamp\(\s*([^,]+),', value)
        first = m.group(1).strip() if m else value
        m = re.fullmatch(r'(\d*\.?\d+)(px|rem|em)', first)
        return self._to_px(float(m.group(1)), m.group(2)) if m else None


class E_A_BaseStylesTests(SimpleTestCase):
    """E-A a2: body 16/24, фокус 2px brand."""

    def test_body_16_24(self):
        bodies = [decls(b) for sel, b in rules(read(MAIN_CSS)) if sel == 'body']
        self.assertTrue(bodies, 'правило body не найдено')
        d = {}
        for x in bodies:
            d.update(x)
        self.assertIn(norm(d.get('font-size', '')), ('16px', '1rem'))
        self.assertIn(norm(d.get('line-height', '')), ('24px', '1.5', '1.5rem'))

    def test_focus_visible_2px_brand(self):
        ok = [b for sel, b in rules(read(MAIN_CSS))
              if re.search(r':focus-visible', sel)
              and re.search(r'outline\s*:\s*2px\s+solid\s+var\(--color-brand\)', b)]
        self.assertTrue(ok, ':focus-visible с outline 2px solid var(--color-brand) не найден в main.css')


class E_A_ComponentsTests(SimpleTestCase):
    """E-A a3/a4: кнопки, промо-полоса, футер."""

    def blocks(self, selector):
        return [decls(b) for sel, b in rules(read(MAIN_CSS)) if sel == selector]

    def test_btn_primary_text_on_accent(self):
        colors = [d.get('color') for d in self.blocks('.btn-primary') if 'color' in d]
        self.assertIn('var(--color-on-accent)', colors)

    def test_btn_dark_exists(self):
        bs = self.blocks('.btn-dark')
        self.assertTrue(bs, '.btn-dark не определён')
        merged = {}
        for d in bs:
            merged.update(d)
        self.assertIn('var(--color-graphite)', merged.get('background', merged.get('background-color', '')))
        self.assertEqual(merged.get('color'), 'var(--color-on-dark)')

    def test_btn_light_removed(self):
        bad = [f.name for f in css_files() + template_files() + ts_files() if 'btn-light' in read(f)]
        self.assertEqual(bad, [])

    def test_promo_bar_and_footer_have_no_accent(self):
        for name in ('_promo_bar.html', '_footer.html'):
            text = read(TEMPLATES / 'partials' / name)
            self.assertIsNone(re.search(r'accent|btn-primary|btn-light', text), name)


class E_A_LogoTests(TestCase):
    """E-A a4: логотип estivo-logo.svg в шапке и футере."""

    def test_logo_file_copied_from_design_system(self):
        self.assertTrue(LOGO.exists(), 'shop/static/img/estivo-logo.svg отсутствует')
        src = (DS / 'assets' / 'Logos' / 'estivo-logo.svg').read_text(encoding='utf-8')
        self.assertEqual(LOGO.read_text(encoding='utf-8').replace('\r\n', '\n'), src.replace('\r\n', '\n'))

    def test_header_and_footer_templates_reference_logo(self):
        for name in ('_header.html', '_footer.html'):
            self.assertIn('estivo-logo.svg', read(TEMPLATES / 'partials' / name), name)

    # Манифест collectstatic в тестах не нужен: проверяем имя файла в разметке.
    @override_settings(STORAGES={
        'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
        'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
    })
    def test_home_renders_logo_in_header_and_footer(self):
        html = self.client.get('/').content.decode()
        self.assertGreaterEqual(len(re.findall(r'estivo-logo\.svg', html)), 2)


def _hex_channels(h):
    h = h.lstrip('#')
    return [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]


def wcag_ratio(fg, bg):
    def lum(h):
        r, g, b = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in _hex_channels(h)]
        return 0.2126 * r + 0.7152 * g + 0.0722 * b
    hi, lo = sorted((lum(fg), lum(bg)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def apca_lc(fg, bg):
    """APCA-W3 0.0.98G-4g; знак: + тёмный текст на светлом, - светлый на тёмном."""
    def y(h):
        r, g, b = _hex_channels(h)
        v = 0.2126729 * r ** 2.4 + 0.7151522 * g ** 2.4 + 0.0721750 * b ** 2.4
        return v + (0.022 - v) ** 1.414 if v < 0.022 else v
    yt, yb = y(fg), y(bg)
    if abs(yb - yt) < 0.0005:
        return 0.0
    if yb > yt:
        s = (yb ** 0.56 - yt ** 0.57) * 1.14
        return 0.0 if s < 0.1 else (s - 0.027) * 100
    s = (yb ** 0.65 - yt ** 0.62) * 1.14
    return 0.0 if s > -0.1 else (s + 0.027) * 100


class ContrastTests(SimpleTestCase):
    """Контраст пар токенов: WCAG 2 AA (основная цель) и APCA Bronze (вторая проверка), docs/design-system.md §2.1."""

    BODY, CONTENT = 75, 60  # APCA Bronze: основной текст / прочий текст (подписи, кнопки, бейджи)
    # (текст, фон, порог APCA)
    PAIRS = [
        ('ink', 'bg', BODY), ('ink', 'surface', BODY), ('ink-soft', 'bg', BODY), ('ink-soft', 'surface', BODY),
        ('ink-black', 'surface', BODY),
        ('ink-muted', 'bg', CONTENT), ('ink-muted', 'surface', CONTENT), ('ink-muted', 'surface-alt', CONTENT),
        ('brand', 'bg', CONTENT), ('brand', 'surface-alt', CONTENT), ('white', 'brand', CONTENT),
        ('on-dark', 'graphite', CONTENT), ('bg', 'ink', CONTENT), ('on-accent', 'accent', CONTENT),
    ]
    # Осознанные отступления по APCA, см. §2.1: на средне-оранжевом WCAG 2 и APCA требуют противоположный цвет текста.
    APCA_EXCEPTIONS = {('on-accent', 'accent')}

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        raw = theme_tokens()

        def color(name):
            v = raw[f'--color-{name}']
            m = re.fullmatch(r'var\((--color-[\w-]+)\)', v)
            return raw[m.group(1)] if m else v
        cls.color = staticmethod(color)

    def test_apca_reference_values(self):
        # контрольные значения из эталонной реализации apca-w3
        self.assertAlmostEqual(apca_lc('#000000', '#ffffff'), 106.04, places=1)
        self.assertAlmostEqual(apca_lc('#888888', '#ffffff'), 63.06, places=1)
        self.assertAlmostEqual(apca_lc('#ffffff', '#888888'), -68.54, places=1)

    def test_wcag_aa(self):
        for fg, bg, _ in self.PAIRS:
            with self.subTest(f'{fg} на {bg}'):
                self.assertGreaterEqual(wcag_ratio(self.color(fg), self.color(bg)), 4.5)

    def test_apca(self):
        for fg, bg, need in self.PAIRS:
            if (fg, bg) in self.APCA_EXCEPTIONS:
                continue
            with self.subTest(f'{fg} на {bg}'):
                self.assertGreaterEqual(abs(apca_lc(self.color(fg), self.color(bg))), need)
