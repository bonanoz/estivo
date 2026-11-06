"""E3: вариант в заявке, снимок, Telegram, админка (R3.3)."""
from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from shop.models import ColorOption, Order, OrderItem

from .helpers import make_product, squash
from .helpers_collections import TABLE_VARIANTS, product_in

ORDER_DATA = {
    'customer_name': 'Иван', 'customer_phone': '+7 900 123-45-67', 'customer_email': '',
    'delivery_address': 'Тольятти', 'comment': '',
}


class VariantCheckoutTestCase(TestCase):
    def setUp(self):
        self.weave = ColorOption.objects.create(name='Графит', finish_type=ColorOption.WEAVE, hex='#3b3a36')
        self.table = product_in(name='Стол Новара', slug='stol-novara', price=1000, variants=TABLE_VARIANTS)
        self.table.available_colors.set([self.weave])
        self.small, self.glass, self.hpl = list(self.table.variants.all())
        self.chair = make_product(name='Кресло Милан', slug='kreslo-milan', price=42000)

    def add(self, product, variant=None, **extra):
        data = dict(extra)
        if variant is not None:
            data['variant'] = variant.id
        self.client.post(reverse('cart_add', args=[product.id]), data)

    def checkout(self):
        with mock.patch('shop.views.notify_telegram', return_value=False) as notify:
            resp = self.client.post(reverse('checkout'), ORDER_DATA)
        return resp, notify

    def telegram_text(self, notify):
        notify.assert_called_once()
        return notify.call_args[0][0]


class E3OrderSnapshotTests(VariantCheckoutTestCase):
    def test_r33_item_has_variant_price_and_choice_snapshot(self):
        self.add(self.table, self.glass)
        resp, _ = self.checkout()
        self.assertEqual(resp.status_code, 302)
        order = Order.objects.get()
        item = order.items.get()
        self.assertEqual(item.unit_price, 54900)
        self.assertEqual(item.selected_colors, {'Размер': '160×90 см', 'Столешница': 'Стекло'})
        self.assertEqual(order.total_price, 54900)

    def test_r33_snapshot_includes_colors_after_size_and_tabletop(self):
        self.add(self.table, self.glass, color_weave=self.weave.id)
        self.checkout()
        item = OrderItem.objects.get()
        self.assertEqual(list(item.selected_colors.items()),
                         [('Размер', '160×90 см'), ('Столешница', 'Стекло'), ('Плетение', 'Графит')])

    def test_r33_two_variants_make_two_items_and_sum(self):
        self.add(self.table, self.glass)
        self.add(self.table, self.small)
        self.checkout()
        order = Order.objects.get()
        self.assertEqual(sorted(i.unit_price for i in order.items.all()), [29900, 54900])
        self.assertEqual(order.total_price, 84800)

    def test_r33_quantity_multiplies_variant_price(self):
        self.add(self.table, self.glass, quantity=2)
        self.checkout()
        order = Order.objects.get()
        self.assertEqual((order.items.get().quantity, order.total_price), (2, 109800))

    def test_r33_item_without_variants_keeps_old_snapshot(self):
        self.add(self.chair)
        self.checkout()
        item = OrderItem.objects.get()
        self.assertEqual((item.unit_price, item.selected_colors), (42000, {}))

    def test_r33_legacy_cart_line_checks_out_as_before(self):
        session = self.client.session
        session['cart'] = {f'{self.chair.id}:': {'product_id': self.chair.id, 'quantity': 1, 'colors': {}}}
        session.save()
        resp, _ = self.checkout()
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(OrderItem.objects.get().unit_price, 42000)

    def test_r33_snapshot_survives_price_change_after_order(self):
        self.add(self.table, self.glass)
        self.checkout()
        self.glass.price = 60000
        self.glass.save()
        item = OrderItem.objects.get()
        self.assertEqual(item.unit_price, 54900)
        self.assertEqual(Order.objects.get().total_price, 54900)
        self.assertEqual(item.selected_colors['Размер'], '160×90 см')

    def test_r33_snapshot_survives_variant_deletion_after_order(self):
        self.add(self.table, self.glass)
        self.checkout()
        self.glass.delete()
        item = OrderItem.objects.get()
        self.assertEqual(item.unit_price, 54900)
        self.assertEqual(item.selected_colors, {'Размер': '160×90 см', 'Столешница': 'Стекло'})

    def test_r33_variant_deleted_before_checkout_leaves_no_empty_order(self):
        self.add(self.table, self.glass)
        self.glass.delete()
        resp = self.client.post(reverse('checkout'), ORDER_DATA)
        self.assertRedirects(resp, reverse('cart_detail'), fetch_redirect_response=False)
        self.assertEqual(Order.objects.count(), 0)


class E3TelegramTests(VariantCheckoutTestCase):
    def test_r33_message_has_size_tabletop_and_line_total(self):
        self.add(self.table, self.glass)
        _, notify = self.checkout()
        text = self.telegram_text(notify)
        self.assertIn('Размер: 160×90 см', text)
        self.assertIn('Столешница: Стекло', text)
        self.assertIn('54900', text)
        self.assertIn('Итого: 54900', text)

    def test_r33_message_lists_each_variant_line(self):
        self.add(self.table, self.glass)
        self.add(self.table, self.small)
        _, notify = self.checkout()
        text = self.telegram_text(notify)
        self.assertIn('160×90 см', text)
        self.assertIn('80×80 см', text)
        self.assertIn('Итого: 84800', text)

    def test_r33_order_saved_when_telegram_fails(self):
        self.add(self.table, self.glass)
        self.checkout()
        order = Order.objects.get()
        self.assertFalse(order.telegram_notified)
        self.assertEqual(order.items.count(), 1)


class E3AdminOrderTests(VariantCheckoutTestCase):
    def setUp(self):
        super().setUp()
        self.client.force_login(get_user_model().objects.create_superuser('boss', 'b@example.com', 'pw-for-tests-123'))

    def order_page(self):
        order = Order.objects.get()
        resp = self.client.get(reverse('admin:shop_order_change', args=[order.pk]))
        self.assertEqual(resp.status_code, 200)
        return resp.content.decode()

    def test_r33_admin_shows_price_choice_and_total(self):
        self.add(self.table, self.glass)
        self.checkout()
        html = self.order_page()
        self.assertIn('54900', squash(html))
        for text in ('Выбор покупателя', 'Размер', '160×90 см', 'Столешница', 'Стекло'):
            self.assertIn(text, html)

    def test_r33_admin_keeps_old_price_after_variant_price_change(self):
        self.add(self.table, self.glass)
        self.checkout()
        self.glass.price = 60000
        self.glass.save()
        html = self.order_page()
        self.assertIn('54900', squash(html))
        self.assertNotIn('60000', squash(html))

    def test_r33_admin_opens_after_variant_deleted(self):
        self.add(self.table, self.glass)
        self.checkout()
        self.glass.delete()
        html = self.order_page()
        self.assertIn('160×90 см', html)
