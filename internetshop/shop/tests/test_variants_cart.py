"""E3: вариант стола в корзине (R3.2)."""
import json

from django.test import TestCase
from django.urls import reverse

from shop.models import ColorOption

from .helpers import make_product, norm_space, parse, squash
from .helpers_collections import TABLE_VARIANTS, product_in

HX = {'HTTP_HX_REQUEST': 'true'}


class VariantCartTestCase(TestCase):
    def setUp(self):
        self.weave = ColorOption.objects.create(name='Графит', finish_type=ColorOption.WEAVE, hex='#3b3a36')
        self.table = product_in(name='Стол Новара', slug='stol-novara', price=1000, variants=TABLE_VARIANTS)
        self.table.available_colors.set([self.weave])
        self.small, self.glass, self.hpl = list(self.table.variants.all())  # 80x80 HPL, 160x90 Стекло, 160x90 HPL
        self.other = product_in(name='Стол Сиена', slug='stol-siena', price=1000,
                                variants=[('120×80 см', 'Стекло', 39900)])
        self.chair = make_product(name='Кресло Милан', slug='kreslo-milan', price=42000)

    def add(self, product, variant=None, **extra):
        data = dict(extra)
        if variant is not None:
            data['variant'] = variant.id if hasattr(variant, 'id') else variant
        return self.client.post(reverse('cart_add', args=[product.id]), data)

    def lines(self):
        resp = self.client.get(reverse('cart_detail'))
        self.assertEqual(resp.status_code, 200)
        return list(resp.context['cart']), resp

    def only_line(self):
        lines, resp = self.lines()
        self.assertEqual(len(lines), 1)
        return lines[0], resp


class E3CartAddTests(VariantCartTestCase):
    def test_r32_two_sizes_are_two_lines_with_own_prices_and_total(self):
        self.add(self.table, self.glass)
        self.add(self.table, self.small)
        lines, resp = self.lines()
        self.assertEqual(sorted(l['unit_price'] for l in lines), [29900, 54900])
        self.assertEqual(len(lines), 2)
        self.assertIn('84800', squash(parse(resp).text))

    def test_r32_same_variant_twice_is_one_line_quantity_two(self):
        self.add(self.table, self.glass)
        self.add(self.table, self.glass)
        line, resp = self.only_line()
        self.assertEqual((line['quantity'], line['line_total']), (2, 109800))
        self.assertIn('109800', squash(parse(resp).text))

    def test_r32_label_lists_size_tabletop_then_colors(self):
        self.add(self.table, self.glass, color_weave=self.weave.id)
        line, resp = self.only_line()
        self.assertEqual(line['colors_display'],
                         [('Размер', '160×90 см'), ('Столешница', 'Стекло'), ('Плетение', 'Графит')])
        chips = [norm_space(li.text) for li in parse(resp).find_all(cls='chip')]
        self.assertEqual(chips, ['Размер: 160×90 см', 'Столешница: Стекло', 'Плетение: Графит'])

    def test_r32_variant_without_tabletop_has_no_tabletop_label(self):
        round_table = product_in(name='Стол Круглый', slug='stol-kruglyj', price=1, variants=[('Ø 55 см', None, 12000)])
        self.add(round_table, round_table.variants.get())
        line, _ = self.only_line()
        self.assertEqual(line['colors_display'], [('Размер', 'Ø 55 см')])

    def test_r32_same_variant_different_colors_are_separate_lines(self):
        self.add(self.table, self.glass)
        self.add(self.table, self.glass, color_weave=self.weave.id)
        lines, _ = self.lines()
        self.assertEqual(len(lines), 2)

    def test_r32_no_variant_field_takes_first_variant_by_order(self):
        self.add(self.table)
        line, _ = self.only_line()
        self.assertEqual(line['unit_price'], 29900)
        self.assertEqual(line['colors_display'][0], ('Размер', '80×80 см'))

    def test_r32_first_by_order_not_cheapest(self):
        pricey_first = product_in(name='Стол Дорогой', slug='stol-dorogoj', price=1,
                                  variants=[('210×100 см', 'Стекло', 90000), ('80×80 см', 'Стекло', 20000)])
        self.add(pricey_first)
        line, _ = self.only_line()
        self.assertEqual(line['unit_price'], 90000)

    def test_r32_foreign_garbage_and_unknown_variant_fall_back_to_first(self):
        foreign = self.other.variants.get().id
        for value in (foreign, 'abc', '999999999', '', '-1'):
            with self.subTest(variant=value):
                session = self.client.session
                session['cart'] = {}
                session.save()
                self.add(self.table, value)
                line, _ = self.only_line()
                self.assertEqual(line['unit_price'], 29900)
                self.assertEqual(line['colors_display'][0], ('Размер', '80×80 см'))

    def test_r32_variant_for_product_without_variants_is_ignored(self):
        self.add(self.chair, self.glass)
        line, _ = self.only_line()
        self.assertEqual(line['unit_price'], 42000)
        self.assertEqual(line['colors_display'], [])
        self.assertEqual(len(self.client.session['cart']), 1)

    def test_r32_cart_page_shows_size_and_tabletop_text(self):
        self.add(self.table, self.glass)
        text = norm_space(parse(self.client.get(reverse('cart_detail'))).text)
        self.assertIn('Размер: 160×90 см', text)
        self.assertIn('Столешница: Стекло', text)

    def test_r32_drawer_fragment_shows_variant(self):
        resp = self.client.post(reverse('cart_add', args=[self.table.id]), {'variant': self.glass.id}, **HX)
        self.assertEqual(resp.status_code, 200)
        text = norm_space(parse(resp).text)
        self.assertIn('Размер: 160×90 см', text)
        self.assertIn('54900', squash(text))

    def test_r32_checkout_page_shows_variant(self):
        self.add(self.table, self.glass)
        text = norm_space(parse(self.client.get(reverse('checkout'))).text)
        self.assertIn('Размер: 160×90 см', text)
        self.assertIn('Столешница: Стекло', text)


class E3CartChangesTests(VariantCartTestCase):
    def test_r32_changed_variant_price_shows_in_cart(self):
        self.add(self.table, self.glass)
        self.glass.price = 60000
        self.glass.save()
        line, resp = self.only_line()
        self.assertEqual(line['unit_price'], 60000)
        self.assertIn('60000', squash(parse(resp).text))

    def test_r32_deleted_variant_line_disappears_from_total_and_counter(self):
        self.add(self.table, self.glass)
        self.add(self.chair)
        self.glass.delete()
        lines, resp = self.lines()
        self.assertEqual([l['product'].id for l in lines], [self.chair.id])
        self.assertEqual(resp.context['cart'].count, 1)
        self.assertEqual(resp.context['cart'].total_price, 42000)
        self.assertNotIn('Столешница', parse(resp).text)

    def test_r32_cart_with_only_deleted_variant_is_empty(self):
        self.add(self.table, self.glass)
        self.glass.delete()
        lines, resp = self.lines()
        self.assertEqual(lines, [])
        self.assertTrue(resp.context['cart'].is_empty)

    def test_r32_remove_and_undo_restores_variant_and_quantity(self):
        self.add(self.table, self.glass, quantity=2)
        line_id = next(iter(self.client.session['cart']))
        self.client.post(reverse('cart_remove'), {'line_id': line_id})
        self.assertEqual(self.lines()[0], [])
        self.client.post('/cart/undo/')
        line, _ = self.only_line()
        self.assertEqual(line['quantity'], 2)
        self.assertEqual(line['unit_price'], 54900)
        self.assertEqual(line['colors_display'][:2], [('Размер', '160×90 см'), ('Столешница', 'Стекло')])

    def test_r32_legacy_line_without_variant_still_works(self):
        session = self.client.session
        session['cart'] = {f'{self.chair.id}:': {'product_id': self.chair.id, 'quantity': 2, 'colors': {}}}
        session.save()
        line, resp = self.only_line()
        self.assertEqual((line['quantity'], line['unit_price'], line['line_total']), (2, 42000, 84000))
        self.assertIn('84000', squash(parse(resp).text))

    def test_r32_legacy_line_of_product_that_gained_variants_uses_from_price_without_size(self):
        session = self.client.session
        session['cart'] = {f'{self.table.id}:': {'product_id': self.table.id, 'quantity': 1, 'colors': {}}}
        session.save()
        line, _ = self.only_line()
        self.assertEqual(line['unit_price'], 29900)
        self.assertEqual(line['colors_display'], [])

    def test_r32_update_quantity_keeps_variant(self):
        self.add(self.table, self.glass)
        line_id = next(iter(self.client.session['cart']))
        self.client.post(reverse('cart_update'), {'line_id': line_id, 'quantity': 3})
        line, _ = self.only_line()
        self.assertEqual((line['quantity'], line['line_total']), (3, 164700))


class E3DataLayerTests(VariantCartTestCase):
    def product_event(self, product, **post):
        resp = self.client.post(reverse('cart_add', args=[product.id]), post, **HX)
        self.assertEqual(resp.status_code, 200)
        return json.loads(resp['HX-Trigger'])['ecommerce:add']['products'][0]

    def test_r32_add_event_carries_variant_label_and_price(self):
        event = self.product_event(self.table, variant=self.glass.id)
        self.assertEqual(event['variant'], '160×90 см, Стекло')
        self.assertEqual(int(event['price']), 54900)
        self.assertEqual(event['id'], self.table.id)

    def test_r32_add_event_without_variant_field_uses_first_variant(self):
        event = self.product_event(self.table)
        self.assertEqual(event['variant'], '80×80 см, HPL compact')
        self.assertEqual(int(event['price']), 29900)

    def test_r32_add_event_of_product_without_variants_has_no_variant(self):
        event = self.product_event(self.chair, variant=self.glass.id)
        self.assertFalse(event.get('variant'))
        self.assertEqual(int(event['price']), 42000)
