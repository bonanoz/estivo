"""Эпик c (c2–c6): импорт товаров с Tilda — `manage.py import_tilda`, `Product.sale_price`,
админ-действие `enable_sale`, `|linebreaks` в описании PDP.

Контракт интерфейсов (воркер обязан реализовать так):
- `call_command('import_tilda', <csv_path>, '--dry-run', '--with-photos', '--report=<path>')`.
  Итог печатается в stdout команды: «создано N, обновлено N, без изменений N,
  пропущено N (демо N, цвета N, юбки N, Copy N, варианты N), ручная проверка N».
  «ручная проверка» = дубли по названию + явный список R12 + «натуральн».
- Фото качаются ТОЛЬКО через `urllib.request.urlopen(...)` (вызов через атрибут модуля:
  `import urllib.request; urllib.request.urlopen(url)`, не `from ... import urlopen`) —
  иначе мок `patch('urllib.request.urlopen')` не сработает. Ответ используется как
  `resp.read()` (допустим `with urlopen(...) as resp`).
- Отчёт `--report=<path>`: CSV, разделитель `;`, столбцы `tilda_id;title;price;reason`.
- `Product.sale_price = IntegerField(null=True, blank=True)`.
- `ProductAdmin.actions` содержит `enable_sale` («Включить скидку»).
- Товары без `tilda_id` команда не трогает.

Фикстура `fixtures/tilda_store_sample.csv` — 22 родительские строки + 4 строки-варианта:
  создаются 12: Лима, Асти (роуп), Рома (варианты), Бали (комплект, featured), Нова (новинка),
  Венто (по запросу), Арко (получает текст из Copy), Фьюжн (Copy без оригинала), Бари (sale),
  Верона (Error get alias), Комод, Мальта (кофейный стол);
  пропущено 10: демо 1, цвета 2, юбки 1, Copy 2 (Лима, Арко), варианты 4;
  ручная проверка 4: дубль «Кресло Дуэт» ×2, Милан (R12), Сорренто («натуральн»).
"""
import base64
import csv
import io
import re
import shutil
import tempfile
from pathlib import Path
from unittest import mock

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase, override_settings

from shop.models import Category, ColorOption, Material, Product

from .helpers import make_product

FIXTURE = Path(__file__).parent / 'fixtures' / 'tilda_store_sample.csv'

LIMA, ASTI, ROMA, BALI, NOVA, VENTO = 1001, 1002, 1003, 1004, 1005, 1006
DEMO, COPY_LIMA, ARKO, COPY_ARKO, COPY_FUSION = 1007, 1008, 1009, 1010, 1011
GRAPHITE, MOCHA, SKIRT, DUET, DUET_SALE, BARI = 1012, 1013, 1014, 1015, 1016, 1017
MILAN, SORRENTO, VERONA, KOMOD, MALTA = 1018, 1019, 1020, 1021, 1022

CREATED = {LIMA, ASTI, ROMA, BALI, NOVA, VENTO, ARKO, COPY_FUSION, BARI, VERONA, KOMOD, MALTA}
NOT_CREATED = {DEMO, COPY_LIMA, COPY_ARKO, GRAPHITE, MOCHA, SKIRT, DUET, DUET_SALE, MILAN, SORRENTO,
               2001, 2002, 2003, 2004}

# 1x1 PNG
PNG = base64.b64decode(
    'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=='
)


def run(path=FIXTURE, *args):
    out = io.StringIO()
    call_command('import_tilda', str(path), *args, stdout=out, stderr=io.StringIO())
    return out.getvalue()


def by_tid(tid):
    return Product.objects.get(tilda_id=tid)


def fake_urlopen():
    resp = mock.MagicMock()
    resp.read.return_value = PNG
    resp.__enter__.return_value = resp
    return mock.MagicMock(return_value=resp)


class TildaImportBase(TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.report = self.tmp / 'import_report.csv'

    def do_import(self, *args, path=FIXTURE):
        return run(path, f'--report={self.report}', *args)


class C2ImportTests(TildaImportBase):
    def test_c2_summary_numbers(self):
        out = self.do_import()
        self.assertEqual(Product.objects.count(), 12)
        for fragment in ('создано 12', 'обновлено 0', 'пропущено 10', 'демо 1', 'цвета 2',
                         'юбки 1', 'Copy 2', 'варианты 4', 'ручная проверка 4'):
            self.assertIn(fragment, out)

    def test_c2_exact_set_created(self):
        self.do_import()
        self.assertEqual(set(Product.objects.values_list('tilda_id', flat=True)), CREATED)

    def test_c2_tilda_id_everywhere_and_ascii_slug(self):
        self.do_import()
        for p in Product.objects.all():
            self.assertIsNotNone(p.tilda_id, p.name)
            self.assertRegex(p.slug, r'^[a-z0-9-]+$', p.name)

    def test_c2_slug_from_ru_slugify(self):
        self.do_import()
        self.assertEqual(by_tid(LIMA).slug, 'kreslo-lima')

    def test_c2_warranty_three_years(self):
        self.do_import()
        self.assertEqual(set(Product.objects.values_list('warranty_years', flat=True)), {3})

    def test_c2_idempotent_second_run(self):
        self.do_import()
        out = self.do_import()
        self.assertEqual(Product.objects.count(), 12)
        self.assertEqual(ColorOption.objects.filter(name__in=['Графит', 'Мокко']).count(), 2)
        self.assertIn('создано 0', out)
        self.assertIn('обновлено 0', out)
        self.assertIn('без изменений 12', out)

    def test_c2_changed_price_updates_only_that_product(self):
        self.do_import()
        modified = self.tmp / 'modified.csv'
        text = FIXTURE.read_text(encoding='utf-8-sig')
        self.assertIn('18800.00', text)
        modified.write_text(text.replace('18800.00', '19900.00'), encoding='utf-8-sig')
        out = self.do_import('--update', path=modified)
        self.assertIn('создано 0', out)
        self.assertIn('обновлено 1', out)
        self.assertEqual(Product.objects.count(), 12)
        self.assertEqual(by_tid(LIMA).price, 19900)

    def test_c2_reimport_without_update_keeps_admin_edits(self):
        self.do_import()
        Product.objects.filter(tilda_id=LIMA).update(price=15000, old_price=18800, description='правка')
        out = self.do_import()
        self.assertIn('обновлено 0', out)
        lima = by_tid(LIMA)
        self.assertEqual((lima.price, lima.old_price, lima.description), (15000, 18800, 'правка'))

    def test_c2_dry_run_writes_nothing(self):
        before = (Product.objects.count(), ColorOption.objects.count(),
                  Material.objects.count(), Category.objects.count())
        self.do_import('--dry-run')
        after = (Product.objects.count(), ColorOption.objects.count(),
                 Material.objects.count(), Category.objects.count())
        self.assertEqual(before, after)

    def test_c2_products_without_tilda_id_untouched(self):
        demo = make_product(name='Демо-кресло seed', slug='demo-seed', price=777)
        self.do_import()
        self.do_import()
        demo.refresh_from_db()
        self.assertEqual((demo.name, demo.price, demo.tilda_id), ('Демо-кресло seed', 777, None))
        self.assertEqual(Product.objects.filter(tilda_id__isnull=True).count(), 1)

    def test_c2_price_on_request_is_zero(self):
        self.do_import()
        self.assertEqual(by_tid(VENTO).price, 0)

    def test_c2_temperature_only_for_rattan(self):
        self.do_import()
        for tid in (LIMA, VENTO, ROMA):
            p = by_tid(tid)
            self.assertEqual((p.temp_min_c, p.temp_max_c), (-50, 50), p.name)
        for tid in (ASTI, BARI):
            p = by_tid(tid)
            self.assertEqual((p.temp_min_c, p.temp_max_c), (None, None), p.name)

    def test_c2_material_and_category_by_section(self):
        self.do_import()
        expected = {
            LIMA: ('rotang', 'kresla'),
            ASTI: ('roup', 'kresla'),
            BARI: ('roup', 'kresla'),
            ROMA: ('rotang', 'divany'),
            BALI: ('rotang', 'komplekty'),
            NOVA: ('rotang', 'kresla'),
            MALTA: ('rotang', 'stoly-kofeynye'),
            KOMOD: (None, None),
        }
        for tid, (mat, cat) in expected.items():
            p = by_tid(tid)
            self.assertEqual(p.material.slug if p.material else None, mat, p.name)
            self.assertEqual(p.category.slug if p.category else None, cat, p.name)

    def test_c2_flags(self):
        self.do_import()
        self.assertTrue(by_tid(BALI).is_featured)
        self.assertFalse(by_tid(LIMA).is_featured)
        self.assertTrue(by_tid(NOVA).is_new)
        self.assertFalse(by_tid(LIMA).is_new)

    def test_c2_dimensions_parsed_from_text(self):
        self.do_import()
        p = by_tid(LIMA)
        self.assertEqual((p.length_cm, p.width_cm, p.height_cm), (63, 65, 85))
        v = by_tid(VERONA)  # «70x65x80 см»
        self.assertEqual((v.length_cm, v.width_cm, v.height_cm), (70, 65, 80))
        self.assertIsNone(by_tid(KOMOD).length_cm)


class C3SkipTests(TildaImportBase):
    def test_c3_demo_copy_colors_skirt_absent(self):
        self.do_import()
        names = ' | '.join(Product.objects.values_list('name', flat=True))
        for bad in ('Dining Chair', 'Copy', 'Графит', 'Мокко', 'Юбка', 'юбк'):
            self.assertNotIn(bad, names)
        self.assertFalse(Product.objects.filter(tilda_id__in=NOT_CREATED).exists())

    def test_c3_colors_in_color_option_as_weave(self):
        self.do_import()
        for name in ('Графит', 'Мокко'):
            self.assertEqual(ColorOption.objects.filter(name=name, finish_type='weave').count(), 1)

    def test_c3_copy_with_original_merges_text_when_empty(self):
        self.do_import()
        self.assertIn('Текст из копии Арко', by_tid(ARKO).description)
        # у оригинала текст уже есть — копия его не затирает
        self.assertNotIn('Текст копии', by_tid(LIMA).description)

    def test_c3_copy_without_original_imported_under_clean_name(self):
        self.do_import()
        p = by_tid(COPY_FUSION)
        self.assertEqual(p.name, 'Кресло Фьюжн')

    def test_c3_dry_run_creates_no_colors(self):
        self.do_import('--dry-run')
        self.assertFalse(ColorOption.objects.filter(name__in=['Графит', 'Мокко']).exists())


class C4ReportTests(TildaImportBase):
    def rows(self):
        raw = self.report.read_text(encoding='utf-8-sig')
        reader = csv.DictReader(io.StringIO(raw), delimiter=';')
        self.assertEqual(reader.fieldnames, ['tilda_id', 'title', 'price', 'reason'])
        return {r['tilda_id']: r for r in reader}

    def test_c4_report_has_manual_review_rows_with_reasons(self):
        self.do_import()
        rows = self.rows()
        for tid in (DUET, DUET_SALE):
            self.assertIn('то же название', rows[str(tid)]['reason'])
        self.assertIn(str(MILAN), rows)
        self.assertTrue(rows[str(MILAN)]['reason'])
        self.assertIn('натуральн', rows[str(SORRENTO)]['reason'])
        self.assertIn('юбк', rows[str(SKIRT)]['reason'].lower())

    def test_c4_duplicates_and_r12_not_created(self):
        self.do_import()
        self.assertFalse(Product.objects.filter(name__icontains='Дуэт').exists())
        self.assertFalse(Product.objects.filter(name__icontains='Милан').exists())
        self.assertFalse(Product.objects.filter(name__icontains='Сорренто').exists())

    def test_c4_created_products_not_in_report_as_manual(self):
        self.do_import()
        self.assertNotIn(str(LIMA), self.rows())


class C6TextTests(TildaImportBase):
    def test_c6_garbage_removed_and_plain_text(self):
        self.do_import()
        d = by_tid(VERONA).description
        for bad in ('Error get alias', 'BUY NOW', 'Copy:', '&amp;'):
            self.assertNotIn(bad, d)
        self.assertIn('кресло & пуф', d)
        for p in Product.objects.all():
            self.assertNotRegex(p.description, r'</?[a-zA-Z][^>]*>', p.name)
            self.assertNotIn('натуральн', p.description.lower())

    def test_c6_br_becomes_newline_and_blank_lines_collapsed(self):
        self.do_import()
        d = by_tid(LIMA).description
        self.assertIn('Габариты:', d)
        self.assertIn('630Х650Х850 мм', d)
        self.assertIn('\n', d)
        self.assertNotIn('\n\n\n', d)
        self.assertEqual(by_tid(LIMA).short_description, '')


class VariantsTests(TildaImportBase):
    def test_variants_one_product_min_price_and_sizes_in_description(self):
        self.do_import()
        self.assertEqual(Product.objects.filter(name__startswith='Диван Рома').count(), 1)
        p = by_tid(ROMA)
        self.assertEqual(p.price, 48000)
        d = p.description
        self.assertRegex(d, r'900х900х700мм\s*—\s*52[\s  ,]?000\s*₽')
        self.assertRegex(d, r'2000х900х700мм\s*—\s*61[\s  ,]?000\s*₽')
        self.assertEqual(d.count('1500х800х700мм'), 1)  # дубль варианта схлопнут


class SalePriceImportTests(TildaImportBase):
    def test_price_old_greater_keeps_full_price_and_stores_sale(self):
        self.do_import()
        p = by_tid(BARI)
        self.assertEqual((p.price, p.sale_price, p.old_price), (28900, 6900, None))
        self.assertIsNone(by_tid(LIMA).sale_price)

    def test_pdp_has_no_discount_badge_and_no_sale_price(self):
        self.do_import()
        html = self.client.get(by_tid(BARI).get_absolute_url()).content.decode()
        self.assertNotIn('Скидка', html)
        self.assertNotIn('badge-sale', html)
        self.assertNotRegex(re.sub(r'[\s  ,]', '', html), r'(?<!\d)6900(?!\d)')


class PhotosTests(TildaImportBase):
    def test_without_flag_no_photos_and_no_network(self):
        with mock.patch('urllib.request.urlopen', fake_urlopen()) as m, \
                override_settings(MEDIA_ROOT=self.tmp):
            self.do_import()
        m.assert_not_called()
        self.assertFalse([p for p in Product.objects.all() if p.main_image])

    def test_with_photos_fills_main_image_and_gallery(self):
        with mock.patch('urllib.request.urlopen', fake_urlopen()) as m, \
                override_settings(MEDIA_ROOT=self.tmp):
            self.do_import('--with-photos')
            lima, asti = by_tid(LIMA), by_tid(ASTI)
            self.assertTrue(lima.main_image)
            self.assertTrue(asti.main_image)
            self.assertEqual(asti.gallery.count(), 1)  # второе фото из «a b» → ProductImage
            self.assertFalse(by_tid(BALI).main_image)  # у остальных Photo пусто
            calls = m.call_count
            self.do_import('--with-photos')
            self.assertEqual(m.call_count, calls)  # фото уже есть — не качаем снова
            self.assertEqual(asti.gallery.count(), 1)

    def test_download_error_does_not_break_import(self):
        with mock.patch('urllib.request.urlopen', side_effect=OSError('boom')), \
                override_settings(MEDIA_ROOT=self.tmp):
            out = self.do_import('--with-photos')
        self.assertEqual(Product.objects.count(), 12)
        self.assertFalse(by_tid(LIMA).main_image)
        self.assertIn('создано 12', out)


class SalePriceFieldTests(TestCase):
    def test_sale_price_stored_and_hidden_on_site(self):
        p = make_product(price=28950, sale_price=6137)
        p.refresh_from_db()
        self.assertEqual(p.sale_price, 6137)
        self.assertIsNone(make_product().sale_price)

        pdp = self.client.get(p.get_absolute_url()).content.decode()
        catalog = self.client.get('/catalog/').content.decode()
        for html in (pdp, catalog):
            self.assertNotRegex(re.sub(r'[\s  ,]', '', html), r'(?<!\d)6137(?!\d)')
            self.assertNotIn('Скидка', html)
        self.assertIn(p.name, catalog)  # карточка в каталоге вообще есть

    def test_pdp_description_uses_linebreaks(self):
        p = make_product(description='Первая строка\nВторая строка\n\nТретья строка')
        html = self.client.get(p.get_absolute_url()).content.decode()
        self.assertRegex(html, r'Первая строка<br\s*/?>\s*Вторая строка')
        self.assertRegex(html, r'Вторая строка</p>\s*<p[^>]*>Третья строка')


class EnableSaleAdminTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_superuser('boss', 'boss@example.com', 'pw-test-123')
        self.client.force_login(user)

    def act(self, *products):
        return self.client.post('/admin/shop/product/', {
            'action': 'enable_sale',
            '_selected_action': [p.pk for p in products],
        }, follow=True)

    def test_action_listed_with_russian_label(self):
        make_product()
        html = self.client.get('/admin/shop/product/').content.decode()
        self.assertIn('Включить скидку', html)

    def test_enable_sale_moves_prices(self):
        p = make_product(price=28900, sale_price=6900)
        self.act(p)
        p.refresh_from_db()
        self.assertEqual((p.price, p.old_price, p.sale_price), (6900, 28900, None))

    def test_products_without_sale_price_untouched(self):
        plain = make_product(price=5000, old_price=7000)
        sale = make_product(price=100, sale_price=50)
        self.act(plain, sale)
        plain.refresh_from_db()
        sale.refresh_from_db()
        self.assertEqual((plain.price, plain.old_price, plain.sale_price), (5000, 7000, None))
        self.assertEqual((sale.price, sale.old_price, sale.sale_price), (50, 100, None))
