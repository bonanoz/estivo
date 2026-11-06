"""E3: карточка товара с вариантами без JS, разметка Product, ссылки на коллекции (R3.1, R3.4, R3.5)."""
import re

from django.test import TestCase


from .helpers import json_ld_objects, make_product, norm_space, parse, squash
from .helpers_collections import TABLE_VARIANTS, collection, product_in


class VariantPdpTestCase(TestCase):
    def setUp(self):
        self.table = product_in(name='Стол Новара', slug='stol-novara', price=1000,
                                variants=TABLE_VARIANTS)
        self.variants = list(self.table.variants.all())
        self.other_table = product_in(name='Стол Сиена', slug='stol-siena', price=1000,
                                      variants=[('120×80 см', 'Стекло', 39900)])
        self.chair = make_product(name='Кресло Милан', slug='kreslo-milan', price=42000)

    def pdp(self, product, query=''):
        resp = self.client.get(product.get_absolute_url() + query)
        self.assertEqual(resp.status_code, 200)
        return parse(resp)

    def radios(self, root):
        wrapper = root.find(attrs={'data-variant-list': True})
        self.assertIsNotNone(wrapper, 'нет обёртки [data-variant-list]')
        return wrapper, wrapper.find_all('input', attrs={'name': 'variant'})

    def checked(self, root):
        _, radios = self.radios(root)
        return [r.get('value') for r in radios if r.has_attr('checked')]

    def button_prices(self, root):
        return [squash(n.text) for n in root.find_all(attrs={'data-variant-price': True})]


class E3VariantListTests(VariantPdpTestCase):
    def test_r31_three_variants_listed_with_data_attributes(self):
        root = self.pdp(self.table)
        wrapper, radios = self.radios(root)
        self.assertEqual(len(radios), 3)
        self.assertEqual([r.get('value') for r in radios], [str(v.id) for v in self.variants])
        expected = [('80×80 см', 'HPL compact', '29900'), ('160×90 см', 'Стекло', '54900'),
                    ('160×90 см', 'HPL compact', '44900')]
        for radio, (size, top, price) in zip(radios, expected):
            self.assertEqual(radio.get('data-size'), size)
            self.assertEqual(radio.get('data-top'), top)
            self.assertEqual(radio.get('data-price'), price)
            self.assertEqual(radio.get('data-label'), f'{size}, {top}')
            self.assertIn(price, squash(radio.closest('label').text if radio.closest('label') else wrapper.text))
            self.assertEqual(radio.closest('form').get('id'), 'pdp-form')

    def test_r31_list_text_shows_sizes_tabletops_and_prices(self):
        wrapper, _ = self.radios(self.pdp(self.table))
        text = norm_space(wrapper.text)
        for part in ('80×80 см', '160×90 см', 'Стекло', 'HPL compact'):
            self.assertIn(part, text)
        for price in ('29900', '54900', '44900'):
            self.assertIn(price, squash(wrapper.text))

    def test_r31_from_price_is_minimum(self):
        root = self.pdp(self.table)
        self.assertIn('от29900', squash(root.find(cls='pdp-price').text))

    def test_r31_first_variant_checked_by_default(self):
        root = self.pdp(self.table)
        self.assertEqual(self.checked(root), [str(self.variants[0].id)])

    def test_r31_button_shows_first_variant_price(self):
        root = self.pdp(self.table)
        prices = self.button_prices(root)
        self.assertTrue(prices)
        self.assertTrue(all('29900' in p for p in prices), prices)
        button = root.find(attrs={'data-add-to-cart': True})
        self.assertIn('29900', squash(button.text))
        self.assertTrue(any(n.closest(attrs={'data-add-to-cart': True}) for n in
                            root.find_all(attrs={'data-variant-price': True})),
                        'цена варианта должна быть внутри кнопки «В корзину»')

    def test_r31_variant_from_query_is_preselected(self):
        second = self.variants[1]
        root = self.pdp(self.table, f'?variant={second.id}')
        self.assertEqual(self.checked(root), [str(second.id)])
        self.assertTrue(all('54900' in p for p in self.button_prices(root)))

    def test_r31_foreign_garbage_unknown_and_empty_variant_fall_back_to_first(self):
        foreign = self.other_table.variants.get().id
        for value in (str(foreign), 'abc', '999999999', '', '-1', '1.5'):
            with self.subTest(variant=value):
                root = self.pdp(self.table, f'?variant={value}')
                self.assertEqual(self.checked(root), [str(self.variants[0].id)])
                self.assertTrue(all('29900' in p for p in self.button_prices(root)))

    def test_r31_exactly_one_radio_checked(self):
        root = self.pdp(self.table, f'?variant={self.variants[2].id}')
        self.assertEqual(len(self.checked(root)), 1)

    def test_r31_variant_without_tabletop_has_label_equal_to_size(self):
        round_table = product_in(name='Стол Круглый', slug='stol-kruglyj', price=1,
                                 variants=[('Ø 55 см', None, 12000)])
        _, radios = self.radios(self.pdp(round_table))
        self.assertEqual(radios[0].get('data-top'), '')
        self.assertEqual(radios[0].get('data-label'), 'Ø 55 см')

    def test_r31_product_without_variants_has_no_variant_block(self):
        root = self.pdp(self.chair)
        self.assertIsNone(root.find(attrs={'data-variant-list': True}))
        self.assertEqual(root.find_all('input', attrs={'name': 'variant'}), [])
        button = root.find(attrs={'data-add-to-cart': True})
        self.assertIn('42000', squash(button.text))

    def test_r31_variant_query_ignored_for_product_without_variants(self):
        resp = self.client.get(self.chair.get_absolute_url() + f'?variant={self.variants[0].id}')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(parse(resp).find_all('input', attrs={'name': 'variant'}), [])


class E3JsonLdTests(VariantPdpTestCase):
    def offers(self, product):
        objs = [o for o in json_ld_objects(self.pdp(product)) if o.get('@type') == 'Product']
        self.assertEqual(len(objs), 1)
        return objs[0]['offers']

    def test_r34_aggregate_offer_with_range_and_count(self):
        offers = self.offers(self.table)
        self.assertEqual(offers['@type'], 'AggregateOffer')
        self.assertEqual(int(offers['lowPrice']), 29900)
        self.assertEqual(int(offers['highPrice']), 54900)
        self.assertEqual(int(offers['offerCount']), 3)

    def test_r34_range_follows_variant_changes(self):
        self.variants[2].delete()
        offers = self.offers(self.table)
        self.assertEqual((int(offers['lowPrice']), int(offers['highPrice']), int(offers['offerCount'])),
                         (29900, 54900, 2))

    def test_r34_product_without_variants_has_plain_price_and_no_offer_count(self):
        # SPEC пишет «Offer», но существующие тесты (test_product_ui, test_audit_product_checkout)
        # фиксируют AggregateOffer с lowPrice = цене «от» для товаров без вариантов; "как раньше".
        offers = self.offers(self.chair)
        self.assertEqual(int(offers['lowPrice']), 42000)
        self.assertNotIn('offerCount', offers)
        self.assertNotIn('highPrice', offers)


class E3CollectionLinkTests(VariantPdpTestCase):
    def line(self, root):
        found = [n for n in root.iter() if re.match(r'^Коллекци[яи]:', norm_space(n.text))]
        return found[-1] if found else None

    def test_r35_one_collection(self):
        milan = collection('Милан', order=1)
        self.chair.collections.set([milan])
        root = self.pdp(self.chair)
        line = self.line(root)
        self.assertIsNotNone(line)
        self.assertEqual(norm_space(line.text), 'Коллекция: Милан')
        self.assertEqual([a.get('href') for a in line.find_all('a')], ['/kollekcii/milan/'])

    def test_r35_line_is_under_the_title(self):
        self.chair.collections.set([collection('Милан', order=1)])
        root = self.pdp(self.chair)
        nodes = list(root.iter())
        self.assertLess(nodes.index(root.find('h1')), nodes.index(self.line(root)))

    def test_r35_two_collections(self):
        self.chair.collections.set([collection('Милан', order=1), collection('Бари', order=2)])
        line = self.line(self.pdp(self.chair))
        self.assertEqual(norm_space(line.text), 'Коллекции: Милан, Бари')
        self.assertEqual([a.get('href') for a in line.find_all('a')], ['/kollekcii/milan/', '/kollekcii/bari/'])

    def test_r35_no_line_without_collections(self):
        self.assertIsNone(self.line(self.pdp(self.chair)))

    def test_r35_no_line_for_unavailable_product(self):
        self.chair.collections.set([collection('Милан', order=1)])
        self.chair.is_available = False
        self.chair.save()
        self.assertIsNone(self.line(self.pdp(self.chair)))
