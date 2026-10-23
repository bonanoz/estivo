"""Импорт товаров из CSV-экспорта Tilda Store. Идемпотентно по Product.tilda_id.

Товары без tilda_id (демо seed_demo) не трогаются. Правила разбора — в
docs/specs/tilda-migration/SPEC.md, раздел (c).
"""
import csv
import html
import re
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.html import strip_tags

from shop.models import Category, ColorOption, Material, Product, ProductImage
from shop.utils import ru_slugify

MATERIALS = {'rotang': 'Ротанг', 'roup': 'Роуп', 'hpl': 'HPL', 'shpon': 'Шпон'}
CATEGORIES = {
    'kresla': 'Кресла', 'divany': 'Диваны', 'stoly-obedennye': 'Столы обеденные',
    'stoly-kofeynye': 'Столы кофейные', 'shezlongi': 'Шезлонги', 'komplekty': 'Комплекты',
    'podvesnye-kresla': 'Подвесные кресла', 'aksessuary': 'Аксессуары',
}
NONE = '-'  # раздел явно без категории

# раздел (casefold) -> (материал, категория); None = определить по названию
SECTIONS = {
    'кресла и стулья ротанг': ('rotang', 'kresla'),
    'стулья и кресла роуп': ('roup', 'kresla'),
    'диваны': ('rotang', 'divany'),
    'угловые и п-образные диваны': ('rotang', 'divany'),
    'диваны роуп': ('roup', 'divany'),
    'столы': ('rotang', None),
    'столы роуп': ('roup', 'stoly-obedennye'),
    'столы кофейные': (None, 'stoly-kofeynye'),
    'шезлонги': ('rotang', 'shezlongi'),
    'шезлонги роуп': ('roup', 'shezlongi'),
    'подвесные кресла-коконы': ('rotang', 'podvesnye-kresla'),
    'аксессуары': ('rotang', 'aksessuary'),
    'аксессуары роуп': ('roup', 'aksessuary'),
    'места для хранения': (None, NONE),
    'комплекты': ('rotang', 'komplekty'),
    'комплекты роуп': ('roup', 'komplekty'),
}
COLORS_SECTION = 'цвета ротанга'
R12_MANUAL = {'стол милан с hpl 180х110 см (роуп)'}

DIM_RE = re.compile(
    r'(?:Габариты|Размер)\s*:?\s*(\d+)\s*[хxX×Х]\s*(\d+)\s*[хxX×Х]\s*(\d+)\s*(мм|см)?', re.IGNORECASE,
)


def norm(title):
    return ' '.join(title.split()).casefold()


def clean_text(raw):
    t = re.sub(r'(?i)<br\s*/?>|</(p|div|li)>', '\n', raw or '')
    t = html.unescape(strip_tags(t))
    t = re.sub(r'Error get alias|BUY NOW|Copy:', '', t)
    lines = [' '.join(ln.split()) for ln in t.splitlines()]
    return re.sub(r'\n{3,}', '\n\n', '\n'.join(lines)).strip()


def parse_price(value):
    try:
        return int(float((value or '').replace(',', '.').replace(' ', '') or 0))
    except ValueError:
        return 0


def parse_dims(text):
    m = DIM_RE.search(text)
    if not m:
        return None, None, None
    dims = [int(x) for x in m.groups()[:3]]
    if m.group(4) == 'мм':
        dims = [round(d / 10) for d in dims]
    return tuple(dims)


def title_materials(title):
    low = title.casefold()
    return [k for k, w in (('rotang', 'ротанг'), ('roup', 'роуп'), ('hpl', 'hpl'), ('shpon', 'шпон')) if w in low]


def title_category(title):
    low = title.casefold()
    if 'комплект' in low:
        return 'komplekty'
    if 'кокон' in low:
        return 'podvesnye-kresla'
    if any(w in low for w in ('кресл', 'стул', 'пуф')):
        return 'kresla'
    if 'диван' in low:
        return 'divany'
    if 'шезлонг' in low:
        return 'shezlongi'
    if 'стол' in low:
        return 'stoly-kofeynye' if ('кофейн' in low or 'лаунж' in low) else 'stoly-obedennye'
    if any(w in low for w in ('кашпо', 'чехол', 'доска')):
        return 'aksessuary'
    return NONE


class Command(BaseCommand):
    help = 'Импортирует товары из CSV-экспорта Tilda Store (идемпотентно по tilda_id).'

    def add_arguments(self, parser):
        parser.add_argument('csv_path')
        parser.add_argument('--dry-run', action='store_true', help='Ничего не писать в БД')
        parser.add_argument('--with-photos', action='store_true', help='Скачать фото по URL')
        parser.add_argument('--report', default='import_report.csv', help='Путь отчёта (CSV)')

    def handle(self, *args, **opts):
        try:
            with open(opts['csv_path'], encoding='utf-8-sig', newline='') as f:
                rows = list(csv.DictReader(f, delimiter=';'))
        except OSError as e:
            raise CommandError(str(e))
        self.photos = opts['with_photos'] and not opts['dry_run']
        self.stats = Counter()
        self.report = []  # (tilda_id, title, price, reason)
        with transaction.atomic():
            self.run(rows)
            if opts['dry_run']:
                transaction.set_rollback(True)
        self.write_report(opts['report'])
        s = self.stats
        self.stdout.write(
            f"{'[dry-run] ' if opts['dry_run'] else ''}создано {s['created']}, обновлено {s['updated']}, "
            f"без изменений {s['same']}, пропущено {s['demo'] + s['colors'] + s['skirts'] + s['copy'] + s['variants']} "
            f"(демо {s['demo']}, цвета {s['colors']}, юбки {s['skirts']}, Copy {s['copy']}, "
            f"варианты {s['variants']}), ручная проверка {s['manual']}"
        )

    def write_report(self, path):
        with open(Path(path), 'w', encoding='utf-8-sig', newline='') as f:
            w = csv.writer(f, delimiter=';')
            w.writerow(['tilda_id', 'title', 'price', 'reason'])
            w.writerows(self.report)

    def skip_manual(self, row, reason):
        self.stats['manual'] += 1
        self.report.append((row['Tilda UID'], row['Title'], row['Price'], reason))

    def run(self, rows):
        variants = defaultdict(list)
        parents = []
        for r in rows:
            if (r['Parent UID'] or '').strip():
                variants[r['Parent UID'].strip()].append(r)
                self.stats['variants'] += 1
            else:
                parents.append(r)

        # Первичные отсевы: цвета, демо, юбки.
        candidates = []
        for r in parents:
            sections = [x.strip() for x in (r['Category'] or '').split(';') if x.strip()]
            r['_sections'] = sections
            if COLORS_SECTION in (s.casefold() for s in sections):
                self.stats['colors'] += 1
                ColorOption.objects.get_or_create(
                    name=r['Title'].strip(), finish_type=ColorOption.WEAVE,
                    defaults={'order': self.stats['colors']},
                )
            elif not sections:
                self.stats['demo'] += 1
            elif 'юбк' in r['Title'].casefold():
                self.stats['skirts'] += 1
                self.report.append((r['Tilda UID'], r['Title'], r['Price'], 'юбка для ёлки — [уточнить]'))
            else:
                candidates.append(r)

        # Copy: сливаем с оригиналом или импортируем под чистым названием.
        originals = {norm(r['Title']): r for r in candidates if 'copy:' not in r['Title'].casefold()}
        items = []
        for r in candidates:
            if 'copy:' not in r['Title'].casefold():
                items.append(r)
                continue
            r['Title'] = re.sub(r'(?i)copy:\s*', '', r['Title']).strip()
            orig = originals.get(norm(r['Title']))
            if orig is None:
                items.append(r)
                continue
            self.stats['copy'] += 1
            if not clean_text(orig['Text'] or orig['Description']):
                orig['Text'], orig['Description'] = r['Text'], r['Description']
            if not orig['Photo'].strip():
                orig['Photo'] = r['Photo']

        # Дубли по названию и список R12 — на ручную проверку.
        groups = Counter(norm(r['Title']) for r in items)
        for r in items:
            n = norm(r['Title'])
            text = clean_text(r['Text'] or r['Description'])
            if groups[n] > 1:
                self.skip_manual(r, 'то же название')
            elif n in R12_MANUAL:
                self.skip_manual(r, 'расхождение цены (R12)')
            elif 'натуральн' in text.casefold():
                self.skip_manual(r, 'в тексте «натуральный»')
            else:
                self.import_row(r, text, variants.get(r['Tilda UID'].strip(), []))

    def import_row(self, r, text, variant_rows):
        title = ' '.join(r['Title'].split())
        sections = r['_sections']
        mat_key, cat_key = None, None
        for s in sections:
            if s.casefold() in SECTIONS:
                mat_key, cat_key = SECTIONS[s.casefold()]
                break
        found = title_materials(title)
        # ровно один маркер материала в названии важнее раздела
        mat_key = found[0] if len(found) == 1 else (mat_key or (found[0] if found else None))
        cat_key = cat_key or title_category(title)

        price = parse_price(r['Price'])
        sale_price = None
        if variant_rows:
            prices = [p for p in (parse_price(v['Price']) for v in variant_rows) if p > 0]
            price = min(prices) if prices else 0
        else:
            old = parse_price(r['Price Old'])
            if price > 0 and old > price:
                price, sale_price = old, price

        length, width, height = parse_dims(text)
        description = text
        if variant_rows:
            seen, lines = set(), []
            for v in variant_rows:
                line = f"{v['Editions'].strip()} — {parse_price(v['Price']):,} ₽".replace(',', ' ')
                if v['Editions'].strip() and line not in seen:
                    seen.add(line)
                    lines.append(line)
            if lines:
                description = (text + '\n\n' if text else '') + 'Варианты:\n' + '\n'.join(lines)

        material = self.lookup(Material, mat_key, MATERIALS)
        category = None if cat_key == NONE else self.lookup(Category, cat_key, CATEGORIES)
        fields = {
            'name': title, 'description': description, 'short_description': '',
            'material': material, 'category': category,
            'price': price, 'old_price': None, 'sale_price': sale_price,
            'warranty_years': 3,
            'temp_min_c': -50 if mat_key == 'rotang' else None,
            'temp_max_c': 50 if mat_key == 'rotang' else None,
            'length_cm': length, 'width_cm': width, 'height_cm': height,
            'is_featured': 'популярные: главная' in (s.casefold() for s in sections),
            'is_new': 'новинка' in (s.casefold() for s in sections),
        }
        tid = int(r['Tilda UID'])
        product = Product.objects.filter(tilda_id=tid).first()
        if product is None:
            slug = ru_slugify(title)[:160] or f'tilda-{tid}'
            if Product.objects.filter(slug=slug).exists():
                slug = f'{slug[:160 - len(str(tid)) - 1]}-{tid}'
            product = Product.objects.create(tilda_id=tid, slug=slug, **fields)
            self.stats['created'] += 1
        else:
            changed = [k for k, v in fields.items() if getattr(product, k) != v]
            for k in changed:
                setattr(product, k, fields[k])
            if changed:
                product.save(update_fields=changed)
                self.stats['updated'] += 1
            else:
                self.stats['same'] += 1
        if self.photos and not product.main_image:
            self.download_photos(product, r['Photo'])

    @staticmethod
    def lookup(model, key, names):
        if not key:
            return None
        return model.objects.get_or_create(slug=key, defaults={'name': names[key]})[0]

    def download_photos(self, product, raw):
        for i, url in enumerate(u for u in re.split(r'[\s,]+', raw or '') if u.startswith('http')):
            try:
                with urllib.request.urlopen(url, timeout=20) as resp:
                    data = resp.read()
                name = url.rsplit('/', 1)[-1] or f'{product.slug}.jpg'
                with transaction.atomic():  # savepoint: упавший INSERT не ломает внешнюю транзакцию
                    if not product.main_image:
                        product.main_image.save(name, ContentFile(data))
                    else:
                        ProductImage.objects.create(product=product, order=i, image=ContentFile(data, name=name))
            except Exception as e:  # сеть/диск не должны ронять импорт
                self.stderr.write(f'Фото не скачано ({product.name}): {url}: {e}')
                self.report.append((product.tilda_id, product.name, product.price, f'фото не скачано: {url}'))
