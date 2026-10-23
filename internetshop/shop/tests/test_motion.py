"""site-motion: анимации на весь сайт (docs/specs/site-motion/SPEC.md).

Контракт читает исходники как текст; поведение в браузере (скролл, переходы) — ручная проверка.
"""
import re

from django.test import SimpleTestCase

from .test_design_tokens import BASE, MAIN_CSS, SRC, TEMPLATES, decls, read, rules

MOTION_TS = SRC / 'motion' / 'index.ts'
DOCS = BASE.parent / 'docs' / 'design-system.md'
CLAUDE_MD = BASE.parent / 'CLAUDE.md'


def rule(css, selector_regex):
    return [decls(body) for sel, body in rules(css) if re.fullmatch(selector_regex, sel)]


class MotionTests(SimpleTestCase):
    def setUp(self):
        self.css = read(MAIN_CSS)

    def test_reveal_rules(self):
        hidden = rule(self.css, r'\[data-reveal\]')
        self.assertTrue(hidden, '[data-reveal] не найден')
        self.assertEqual(hidden[0].get('opacity'), '0')
        self.assertIn('translateY', hidden[0].get('transform', ''))
        shown = rule(self.css, r'\[data-reveal\]\.is-in')
        self.assertTrue(shown, '[data-reveal].is-in не найден')
        self.assertEqual(shown[0].get('opacity'), '1')
        self.assertEqual(shown[0].get('transform'), 'none')

    def test_view_transition_only_without_reduced_motion(self):
        self.assertIn('@view-transition', self.css)
        m = re.search(r'@media\s*\(prefers-reduced-motion:\s*no-preference\)\s*\{(.*?)\n\}', self.css, re.S)
        self.assertTrue(m, 'нет блока prefers-reduced-motion: no-preference')
        self.assertRegex(m.group(1), r'@view-transition\s*\{\s*navigation:\s*auto;?\s*\}')
        self.assertEqual(self.css.count('@view-transition'), 1, '@view-transition вне reduced-motion-гарда')

    def test_bump_animation(self):
        self.assertTrue(rule(self.css, r'\.is-bumped'), '.is-bumped не найден')
        self.assertRegex(self.css, r'@keyframes\s+count-bump')

    def test_accordions_animate(self):
        sels = [sel for sel, _ in rules(self.css) if '::details-content' in sel]
        joined = ' '.join(sels)
        for cls in ('.faq-item', '.pdp-acc', '.filter-group', '.review-write'):
            self.assertIn(cls, joined)

    def test_motion_module(self):
        self.assertTrue(MOTION_TS.exists(), 'frontend/src/motion/index.ts отсутствует')
        ts = MOTION_TS.read_text(encoding='utf-8')
        self.assertIn('prefers-reduced-motion', ts)
        self.assertIn('IntersectionObserver', ts)
        self.assertIn('htmx:load', ts)

    def test_header_has_view_transition_class(self):
        html = (TEMPLATES / 'partials' / '_header.html').read_text(encoding='utf-8')
        headers = re.findall(r'<header\b[^>]*>', html)
        self.assertEqual(len(headers), 2)
        for h in headers:
            self.assertRegex(h, r'class="[^"]*\bsite-header\b')

    def test_design_system_documents_motion(self):
        doc = DOCS.read_text(encoding='utf-8')
        self.assertNotIn('Другой системы\n  движения нет', doc)
        for word in ('data-reveal', 'view-transition', 'count-bump', 'details-content'):
            self.assertIn(word, doc)
        self.assertIn('motion', CLAUDE_MD.read_text(encoding='utf-8'))
