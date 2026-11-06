"""E1: data-миграция коллекций (R1.5) и перенос старых связей FK -> M2M (R1.2 «старые связи»).

Контракт: в миграции, чей файл оканчивается на ``_collections_data.py``, есть функция
``seed_collections(apps, schema_editor)``; она идемпотентна. Все миграции E1 обратимы
(RunPython с reverse_code=noop), иначе тест старых связей не сможет откатиться на 0014.
"""
import importlib
from pathlib import Path

from django.apps import apps as global_apps
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TestCase, TransactionTestCase

import shop.migrations
from shop import models as m
from shop.models import Category, Collection, Material, Product

MIGRATIONS_DIR = Path(shop.migrations.__file__).parent


def run_seed():
    files = sorted(MIGRATIONS_DIR.glob('*_collections_data.py'))
    if not files:
        raise AssertionError('нет миграции *_collections_data.py с функцией seed_collections')
    module = importlib.import_module(f'shop.migrations.{files[-1].stem}')
    module.seed_collections(global_apps, None)


def product(name, category_name, material_name='Роуп'):
    cat, _ = Category.objects.get_or_create(name=category_name)
    mat, _ = Material.objects.get_or_create(name=material_name)
    return Product.objects.create(name=name, description='d', price=1000, category=cat, material=mat)


def placement(p):
    p = Product.objects.get(pk=p.pk)
    zone = p.zone.name if p.zone else None
    return set(p.collections.values_list('name', flat=True)), zone


class E1SeedReferenceTests(TestCase):
    def test_r15_reference_data_created(self):
        m.Zone.objects.all().delete()
        m.TabletopType.objects.all().delete()
        Collection.objects.all().delete()
        run_seed()
        self.assertTrue({'Обеденная группа', 'Лаунж-зона'} <= set(m.Zone.objects.values_list('name', flat=True)))
        self.assertTrue({'Стекло', 'HPL compact', 'HPL', 'Шпон', 'ДПК'}
                        <= set(m.TabletopType.objects.values_list('name', flat=True)))
        self.assertEqual(set(Collection.objects.values_list('slug', 'name')),
                         {('milan', 'Милан'), ('bari', 'Бари'), ('asti', 'Асти')})

    def test_r15_empty_database_no_errors(self):
        Product.objects.all().delete()
        m.Zone.objects.all().delete()
        m.TabletopType.objects.all().delete()
        Collection.objects.all().delete()
        run_seed()
        self.assertEqual(Collection.objects.count(), 3)
        self.assertEqual(m.Zone.objects.count(), 2)
        self.assertEqual(m.TabletopType.objects.count(), 5)

    def test_r15_second_run_does_not_duplicate_anything(self):
        p1 = product('Стол Бари со шпоном 210х100 см (роуп)', 'Столы обеденные')
        p2 = product('Кресло Милан Лаунж (роуп)', 'Кресла')
        run_seed()
        before = (Collection.objects.count(), m.Zone.objects.count(), m.TabletopType.objects.count(),
                  placement(p1), placement(p2), Product.collections.through.objects.count())
        run_seed()
        after = (Collection.objects.count(), m.Zone.objects.count(), m.TabletopType.objects.count(),
                 placement(p1), placement(p2), Product.collections.through.objects.count())
        self.assertEqual(before, after)
        self.assertEqual(Collection.objects.filter(name='Милан').count(), 1)
        self.assertEqual(m.Zone.objects.filter(name='Лаунж-зона').count(), 1)

    def test_r15_demo_collections_removed_products_stay(self):
        demo = [Collection.objects.create(name=n, slug=s)
                for n, s in (('Терраса', 'terrasa'), ('Лаунж', 'launzh'), ('Сад', 'sad'))]
        keeper = product('Кресло Кокон (роуп)', 'Подвесные кресла')
        keeper.collections.set(demo)
        run_seed()
        self.assertFalse(Collection.objects.filter(slug__in=['terrasa', 'launzh', 'sad']).exists())
        self.assertTrue(Product.objects.filter(pk=keeper.pk).exists())


class E1SeedPlacementTests(TestCase):
    def test_r15_dining_table(self):
        p = product('Стол Бари со шпоном 210х100 см (роуп)', 'Столы обеденные')
        run_seed()
        self.assertEqual(placement(p), ({'Бари'}, 'Обеденная группа'))

    def test_r15_lounge_chair(self):
        p = product('Кресло Милан Лаунж (роуп)', 'Кресла')
        run_seed()
        self.assertEqual(placement(p), ({'Милан'}, 'Лаунж-зона'))

    def test_r15_plain_chair_goes_to_dining(self):
        p = product('Кресло Милан (роуп)', 'Кресла')
        run_seed()
        self.assertEqual(placement(p), ({'Милан'}, 'Обеденная группа'))

    def test_r15_sofa(self):
        p = product('Диван Милан 2XL (роуп)', 'Диваны')
        run_seed()
        self.assertEqual(placement(p), ({'Милан'}, 'Лаунж-зона'))

    def test_r15_hpl_coffee_table(self):
        p = product('Стол Бари Лаунж (HPL)', 'Столы кофейные', material_name='HPL')
        run_seed()
        self.assertEqual(placement(p), ({'Бари'}, 'Лаунж-зона'))

    def test_r15_bar_chair_and_chaise_have_collection_but_no_zone(self):
        bar = product('Кресло Барное Милан (роуп)', 'Кресла')
        chaise = product('Шезлонг Бари (роуп)', 'Шезлонги')
        run_seed()
        self.assertEqual(placement(bar), ({'Милан'}, None))
        self.assertEqual(placement(chaise), ({'Бари'}, None))

    def test_r15_asti_word_goes_to_asti(self):
        p = product('Диван Асти 3 (роуп)', 'Диваны')
        run_seed()
        self.assertEqual(placement(p), ({'Асти'}, 'Лаунж-зона'))

    def test_r15_rattan_product_untouched(self):
        p = product('Кресло Милан Ретта (ротанг)', 'Кресла', material_name='Ротанг')
        run_seed()
        self.assertEqual(placement(p), (set(), None))

    def test_r15_word_must_be_whole(self):
        a = product('Стол Бастион', 'Столы обеденные')
        b = product('Кресло Миланезе', 'Кресла')
        run_seed()
        self.assertEqual(placement(a)[0], set())
        self.assertEqual(placement(b)[0], set())

    def test_r15_product_without_series_word_has_no_collection(self):
        p = product('Кресло Кокон (роуп)', 'Подвесные кресла')
        run_seed()
        self.assertEqual(placement(p)[0], set())


class E1OldLinksMigrationTests(TransactionTestCase):
    """Товар с полем collection до миграции входит в ту же коллекцию после."""

    BEFORE = [('shop', '0014_slug_blank')]

    def shop_leaf(self):
        return [n for n in MigrationExecutor(connection).loader.graph.leaf_nodes() if n[0] == 'shop']

    def tearDown(self):
        MigrationExecutor(connection).migrate(self.shop_leaf())

    def test_r12_old_collection_link_becomes_membership(self):
        executor = MigrationExecutor(connection)
        executor.migrate(self.BEFORE)
        old = executor.loader.project_state(self.BEFORE).apps
        OldCollection, OldProduct = old.get_model('shop', 'Collection'), old.get_model('shop', 'Product')
        coll = OldCollection.objects.create(name='Старая серия', slug='staraya-seriya')
        linked = OldProduct.objects.create(name='Стол без серии в названии', slug='stol-a', description='d',
                                           price=1000, collection=coll)
        lone = OldProduct.objects.create(name='Стол без связи', slug='stol-b', description='d', price=1000)

        executor = MigrationExecutor(connection)
        target = self.shop_leaf()
        executor.migrate(target)
        new = executor.loader.project_state(target).apps
        NewProduct = new.get_model('shop', 'Product')
        self.assertEqual(list(NewProduct.objects.get(pk=linked.pk).collections.values_list('slug', flat=True)),
                         ['staraya-seriya'])
        self.assertEqual(NewProduct.objects.get(pk=lone.pk).collections.count(), 0)
