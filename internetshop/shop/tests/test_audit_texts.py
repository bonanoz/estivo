"""E4 (audit-fixes): срок звонка с рабочим временем, исключение «купить» в §5, черновик для юриста."""
import re
from pathlib import Path
from unittest import mock

from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from shop.context_processors import SITE_INFO
from shop.tests.helpers import make_product, norm_space, parse
from shop.tests.helpers_audit import add_to_cart, just_ordered

REPO_ROOT = Path(settings.BASE_DIR).parent
DESIGN_SYSTEM = REPO_ROOT / 'docs' / 'design-system.md'
LEGAL_DRAFT = REPO_ROOT / 'docs' / 'legal' / 'privacy-telegram-draft.md'

LEAD_IN = 'Перезваниваем или пишем в течение 5 минут в рабочее время'
HOURS_LINE = 'Пн-Пт 10:00–19:00, Сб 10:00–18:00, Вс 10:00–17:00'
BARE_PROMISE = re.compile(r'в течение 5 минут(?! в рабочее время)')


def page_text(resp):
    return norm_space(parse(resp).text)


class E4CallbackNoteTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.product = make_product(name='Кресло Тест', price=42000)

    def setUp(self):
        just_ordered(self.client)

    def checkout_text(self):
        add_to_cart(self.client, self.product)
        return page_text(self.client.get(reverse('checkout')))

    def test_e4_checkout_page_promises_callback_in_working_hours(self):
        text = self.checkout_text()
        self.assertIn(LEAD_IN, text)
        self.assertIn('Пн-Пт 10:00–19:00', text)
        self.assertIn(HOURS_LINE, text)

    def test_e4_footer_on_home_has_same_text(self):
        text = page_text(self.client.get(reverse('home')))
        self.assertIn(LEAD_IN, text)
        self.assertIn(HOURS_LINE, text)

    def test_e4_order_success_page_has_same_text(self):
        text = page_text(self.client.get(reverse('order_success')))
        self.assertIn(LEAD_IN, text)
        self.assertIn(HOURS_LINE, text)

    def test_e4_no_bare_five_minute_promise_anywhere(self):
        add_to_cart(self.client, self.product)
        for name in ('home', 'checkout', 'order_success', 'contacts_page', 'cart_detail'):
            with self.subTest(page=name):
                text = page_text(self.client.get(reverse(name)))
                self.assertIsNone(BARE_PROMISE.search(text), BARE_PROMISE.search(text))

    def test_e4_hours_come_from_single_source(self):
        new_hours = [('Пн-Пт', '08:00–17:00'), ('Сб', '09:00–14:00')]
        add_to_cart(self.client, self.product)
        with mock.patch.dict(SITE_INFO, {'work_hours': new_hours}):
            for name in ('checkout', 'home', 'order_success'):
                with self.subTest(page=name):
                    text = page_text(self.client.get(reverse(name)))
                    self.assertIn(f'{LEAD_IN}: Пн-Пт 08:00–17:00, Сб 09:00–14:00', text)
                    for stale in ('10:00–19:00', '10:00–18:00', '10:00–17:00'):
                        self.assertNotIn(stale, text)

    def test_e4_site_info_callback_note_is_built_from_work_hours(self):
        from shop.context_processors import site_info
        request = mock.Mock()
        note = site_info(request)['site_info']['callback_note']
        self.assertEqual(note, f'{LEAD_IN}: {HOURS_LINE}')
        with mock.patch.dict(SITE_INFO, {'work_hours': [('Пн', '11:00–12:00')]}):
            self.assertEqual(site_info(request)['site_info']['callback_note'], f'{LEAD_IN}: Пн 11:00–12:00')


def section(markdown, number):
    match = re.search(rf'^## {number}\. .*?(?=^## \d+\. |\Z)', markdown, flags=re.S | re.M)
    return match.group(0) if match else ''


class E4DesignSystemTests(TestCase):
    def test_e4_section_5_allows_buy_in_category_title_with_date(self):
        sec = section(DESIGN_SYSTEM.read_text(encoding='utf-8'), 5)
        self.assertTrue(sec, 'нет раздела 5')
        chunks = re.split(r'\n\s*\n|\n(?=- )', sec)
        exception = [c for c in chunks if re.search('исключ', c, re.I) and 'купить' in c]
        self.assertTrue(exception, 'в §5 нет исключения для «купить»')
        chunk = exception[0]
        self.assertRegex(chunk.lower(), r'title|заголов')
        self.assertIn('категори', chunk.lower())
        self.assertRegex(chunk, r'02\.11\.2026|2026-11-02')

    def test_e4_section_5_still_bans_buy_elsewhere(self):
        sec = section(DESIGN_SYSTEM.read_text(encoding='utf-8'), 5)
        self.assertIn('«купить»', sec)
        self.assertIn('«оплатить»', sec)


class E4LegalDraftTests(TestCase):
    def draft(self):
        self.assertTrue(LEGAL_DRAFT.is_file(), f'нет файла {LEGAL_DRAFT}')
        return LEGAL_DRAFT.read_text(encoding='utf-8')

    def test_e4_draft_is_marked_as_unapproved_draft_about_telegram(self):
        text = self.draft().lower()
        self.assertIn('черновик', text)
        self.assertIn('telegram', text)
        self.assertRegex(text, r'не утвержд|неутвержд|не согласован')

    def test_e4_draft_lists_fields_sent_to_telegram(self):
        text = self.draft().lower()
        for word in ('имя', 'телефон', 'email', 'адрес', 'комментар', 'состав заявки'):
            with self.subTest(field=word):
                self.assertIn(word, text)

    def test_e4_draft_has_questions_for_lawyer_section(self):
        self.assertRegex(self.draft(), r'(?im)^#{1,4} .*вопрос.*юрист')

    def test_e4_draft_mentions_foreign_hosting(self):
        text = self.draft().lower()
        self.assertRegex(text, r'за рубеж|за границ|зарубеж')
        self.assertIn('render', text)

    def test_e4_draft_proposes_wording_for_policy_and_consent(self):
        text = self.draft().lower()
        self.assertIn('политик', text)
        self.assertIn('согласи', text)


class E4PrivacyPageUntouchedTests(TestCase):
    def test_e4_privacy_keeps_no_third_party_clause_and_has_no_telegram(self):
        resp = self.client.get(reverse('privacy_page'))
        self.assertEqual(resp.status_code, 200)
        root = parse(resp)
        text = norm_space((root.find('main') or root).text)  # подвал со ссылкой на соцсеть Telegram не в счёт
        self.assertIn('Персональные данные Пользователя никогда, ни при каких условиях не будут переданы третьим лицам', text)
        self.assertNotIn('telegram', text.lower())
