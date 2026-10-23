import csv
import io
import tempfile
from pathlib import Path
from unittest import mock

from django.core.management import call_command
from django.test import TestCase, override_settings

from shop.models import Product

HEADER = ('Tilda UID;Brand;SKU;Mark;Category;Title;Description;Text;Photo;Price;Quantity;Price Old;'
          'Editions;Modifications;External ID;Parent UID;Characteristics:Тип;Weight;Length;Width;Height')


def row(tid, section, title, text='', photo=''):
    return f'{tid};;;;"{section}";{title};;{text};{photo};1000;;;;;e{tid};;;0;0;0;0'


class ExtraTests(TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.report = self.tmp / 'r.csv'

    def run_csv(self, *rows, args=()):
        p = self.tmp / 'in.csv'
        p.write_text('\n'.join([HEADER, *rows]), encoding='utf-8-sig')
        call_command('import_tilda', str(p), f'--report={self.report}', *args,
                     stdout=io.StringIO(), stderr=io.StringIO())

    def test_dims_only_with_label(self):
        self.run_csv(
            row(1, 'Комплекты', 'Комплект А', 'Стол 135х65х50 см'),
            row(2, 'Столы', 'Стол Б', 'Размер: 800х450х900 мм'),
        )
        a, b = Product.objects.get(tilda_id=1), Product.objects.get(tilda_id=2)
        self.assertIsNone(a.length_cm)
        self.assertEqual((b.length_cm, b.width_cm, b.height_cm), (80, 45, 90))

    def test_photo_error_in_report(self):
        with mock.patch('urllib.request.urlopen', side_effect=OSError('x')), \
                override_settings(MEDIA_ROOT=self.tmp):
            self.run_csv(row(1, 'Столы', 'Стол Б', 'т', 'https://e.com/a.jpg'), args=('--with-photos',))
        rows = list(csv.DictReader(io.StringIO(self.report.read_text(encoding='utf-8-sig')), delimiter=';'))
        self.assertTrue(any('фото не скачано' in r['reason'] for r in rows))

    def test_material_by_single_title_marker(self):
        self.run_csv(
            row(1, 'Аксессуары', 'Разделочная доска из HPL', 'т'),
            row(2, 'Шезлонги;Шезлонги роуп', 'Шезлонг Ретта из ротанга/роупа', 'т'),
        )
        a, b = Product.objects.get(tilda_id=1), Product.objects.get(tilda_id=2)
        self.assertEqual(a.material.slug, 'hpl')
        self.assertIsNone(a.temp_min_c)
        self.assertEqual(b.material.slug, 'rotang')
