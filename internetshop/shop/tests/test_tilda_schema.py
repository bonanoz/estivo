"""Эпик c1: схема под импорт Tilda — `Product.tilda_id` и nullable температура.

Контракт интерфейсов (воркер обязан реализовать так):
- `Product.tilda_id = BigIntegerField(null=True, blank=True, unique=True)`.
- `temp_min_c` / `temp_max_c` — `null=True, blank=True`, без дефолта (новый товар → None).
- Одна миграция `shop/migrations/0010_product_tilda_id_nullable_temp.py`: схема + данные —
  у существующих товаров материала со slug `rotang` ставится −50/+50, у остальных (и без
  материала) — None. Обратная миграция возможна (данные назад: None → −70/+70).
- PDP: строка «Температура эксплуатации» выводится только если обе границы заданы.
"""
from django.db import IntegrityError, connection, transaction
from django.db.migrations.executor import MigrationExecutor
from django.test import TestCase, TransactionTestCase

from shop.models import Material, Product

from .helpers import make_product

BEFORE = ('shop', '0009_product_offer_ends_at')
AFTER = ('shop', '0010_product_tilda_id_nullable_temp')


class C1ModelTests(TestCase):
    def test_tilda_id_defaults_to_none_and_is_unique(self):
        a = make_product()
        b = make_product()
        self.assertIsNone(a.tilda_id)
        self.assertIsNone(b.tilda_id)  # несколько None не конфликтуют
        a.tilda_id = 123456789012
        a.save()
        b.tilda_id = 123456789012
        with self.assertRaises(IntegrityError), transaction.atomic():
            b.save()

    def test_temps_default_to_none(self):
        p = make_product()
        p.refresh_from_db()
        self.assertIsNone(p.temp_min_c)
        self.assertIsNone(p.temp_max_c)

    def test_pdp_hides_temperature_when_unset(self):
        p = make_product()
        html = self.client.get(p.get_absolute_url()).content.decode()
        self.assertNotIn('Температура эксплуатации', html)
        self.assertNotIn('None', html)

    def test_pdp_shows_temperature_when_set(self):
        p = make_product(temp_min_c=-50, temp_max_c=50)
        html = self.client.get(p.get_absolute_url()).content.decode()
        self.assertIn('Температура эксплуатации', html)
        self.assertIn('50', html)


class C1DataMigrationTests(TransactionTestCase):
    def migrate(self, target):
        executor = MigrationExecutor(connection)
        executor.loader.build_graph()
        executor.migrate([target])
        return executor.loader.project_state([target]).apps

    def tearDown(self):
        self.migrate(MigrationExecutor(connection).loader.graph.leaf_nodes('shop')[0])

    def test_rattan_gets_range_others_none(self):
        apps = self.migrate(BEFORE)
        M = apps.get_model('shop', 'Material')
        P = apps.get_model('shop', 'Product')
        rotang = M.objects.create(name='Ротанг', slug='rotang')
        roup = M.objects.create(name='Роуп', slug='roup')
        P.objects.create(name='Р1', slug='r1', price=1, material=rotang)
        P.objects.create(name='Р2', slug='r2', price=1, material=roup)
        P.objects.create(name='Р3', slug='r3', price=1)

        apps = self.migrate(AFTER)
        P = apps.get_model('shop', 'Product')
        temps = {p.slug: (p.temp_min_c, p.temp_max_c) for p in P.objects.all()}
        self.assertEqual(temps, {'r1': (-50, 50), 'r2': (None, None), 'r3': (None, None)})

    def test_migration_is_reversible(self):
        apps = self.migrate(AFTER)
        apps.get_model('shop', 'Product').objects.create(name='Р4', slug='r4', price=1)
        apps = self.migrate(BEFORE)  # не должно падать на NOT NULL
        p = apps.get_model('shop', 'Product').objects.get(slug='r4')
        self.assertEqual((p.temp_min_c, p.temp_max_c), (-70, 70))
