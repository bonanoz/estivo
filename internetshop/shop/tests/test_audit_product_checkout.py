"""E3 (audit-fixes): карточка, корзина, заявка — снятый товар, разметка, цена 0, отзыв в лимите, FAQ, canonical, редиректы."""
from unittest import mock

from django.test import TestCase, override_settings
from django.urls import reverse

from shop.models import Category, Material, Order, Product, Review
from shop.tests.helpers import json_ld_objects, make_product, norm_space, parse, path_of, product_hrefs, squash
from shop.tests.helpers_audit import has_zero_price, without_total
from shop.views import CATALOG_PAGE_SIZE

HX = {'HTTP_HX_REQUEST': 'true'}
ORDER_DATA = {
    'customer_name': 'Иван', 'customer_phone': '+7 900 123-45-67', 'customer_email': '',
    'delivery_address': 'Тольятти', 'comment': '',
}
REVIEW = {'author': 'Ольга', 'rating': '5', 'usage_duration': '', 'text': 'Хорошее кресло, всем советую', 'website': ''}


def refs_to(root, url):
    """Элементы, у которых любой атрибут (action, hx-post, href, formaction...) равен ``url``."""
    return [n for n in root.iter() if url in n.attrs.values()]


def main_text(resp):
    root = parse(resp)
    return norm_space((root.find('main') or root).text)


class E3DiscontinuedProductTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.material = Material.objects.create(name='Ротанг', slug='rotang')
        cls.category = Category.objects.create(name='Кресла', slug='kresla')
        cls.old = make_product(name='Кресло Старое', slug='kreslo-staroe', price=15000, is_available=False,
                               material=cls.material, category=cls.category)
        cls.alive = make_product(name='Кресло Живое', slug='kreslo-zhivoe', price=18000,
                                 material=cls.material, category=cls.category)
        cls.other_old = make_product(name='Кресло Тоже Снятое', slug='kreslo-tozhe-snyatoe', price=9000,
                                     is_available=False, material=cls.material, category=cls.category)
        cls.url = reverse('product_detail', args=[cls.old.slug])

    def page(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        return resp, parse(resp)

    def test_e3_page_opens_with_discontinued_notice(self):
        resp, root = self.page()
        self.assertContains(resp, 'Снят с производства')
        self.assertContains(resp, 'Кресло Старое')

    def test_e3_no_add_to_cart_form(self):
        _, root = self.page()
        self.assertEqual(refs_to(root, reverse('cart_add', args=[self.old.id])), [])
        self.assertEqual(root.find_all('button', attrs={'data-add-to-cart': True}), [])

    def test_e3_no_wishlist_button_for_this_product(self):
        _, root = self.page()
        self.assertEqual(refs_to(root, reverse('wishlist_toggle', args=[self.old.id])), [])

    def test_e3_no_checkout_request_button(self):
        _, root = self.page()
        self.assertEqual(root.find_all('button', attrs={'name': 'checkout'}), [])

    def test_e3_find_analog_link_leads_to_price_request_form(self):
        _, root = self.page()
        href = f"{reverse('contacts_page')}?product={self.old.slug}"
        links = [a for a in root.find_all('a', attrs={'href': href}) if 'Подобрать аналог' in norm_space(a.text)]
        self.assertTrue(links, 'нет ссылки «Подобрать аналог» на ' + href)

    def test_e3_find_analog_is_secondary_button(self):
        _, root = self.page()
        href = f"{reverse('contacts_page')}?product={self.old.slug}"
        link = next(a for a in root.find_all('a', attrs={'href': href}) if 'Подобрать аналог' in norm_space(a.text))
        self.assertNotIn('btn-primary', link.classes())

    def test_e3_similar_products_are_available_ones_only(self):
        _, root = self.page()
        hrefs = product_hrefs(root)
        self.assertIn(self.alive.get_absolute_url(), hrefs)
        self.assertNotIn(self.other_old.get_absolute_url(), hrefs)

    def test_e3_discontinued_page_is_noindex(self):
        _, root = self.page()
        robots = [m for m in root.find_all('meta', attrs={'name': 'robots'}) if 'noindex' in m.get('content', '')]
        self.assertTrue(robots, 'нет <meta name="robots" content="noindex">')

    def test_e3_available_product_is_not_noindex(self):
        root = parse(self.client.get(self.alive.get_absolute_url()))
        self.assertEqual([m for m in root.find_all('meta', attrs={'name': 'robots'})
                          if 'noindex' in m.get('content', '')], [])

    def test_e3_discontinued_markup_says_discontinued_not_preorder(self):
        resp, root = self.page()
        product = next(o for o in json_ld_objects(root) if o.get('@type') == 'Product')
        self.assertTrue(product['offers']['availability'].endswith('Discontinued'), product['offers'])
        self.assertNotIn('PreOrder', resp.content.decode())

    def test_e3_available_product_markup_still_in_stock(self):
        root = parse(self.client.get(self.alive.get_absolute_url()))
        product = next(o for o in json_ld_objects(root) if o.get('@type') == 'Product')
        self.assertTrue(product['offers']['availability'].endswith('InStock'))

    def test_e3_available_product_page_keeps_cart_and_wishlist_controls(self):
        root = parse(self.client.get(self.alive.get_absolute_url()))
        self.assertTrue(refs_to(root, reverse('cart_add', args=[self.alive.id])))
        self.assertTrue(refs_to(root, reverse('wishlist_toggle', args=[self.alive.id])))
        self.assertNotIn('Снят с производства', root.text)

    def test_e3_post_to_cart_for_discontinued_is_404_and_cart_empty(self):
        resp = self.client.post(reverse('cart_add', args=[self.old.id]))
        self.assertEqual(resp.status_code, 404)
        self.assertFalse(self.client.session.get('cart'))

    def test_e3_unknown_slug_is_404(self):
        self.assertEqual(self.client.get(reverse('product_detail', args=['net-takogo'])).status_code, 404)

    def test_e3_discontinued_without_category_still_opens(self):
        lonely = make_product(name='Кресло Одинокое', slug='kreslo-odinokoe', price=7000, is_available=False)
        resp = self.client.get(lonely.get_absolute_url())
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Снят с производства')


class E3ProductMarkupPriceTests(TestCase):
    def test_e3_price_on_request_has_no_zero_price_in_markup(self):
        product = make_product(name='Кресло Запрос', slug='kreslo-zapros', price=0)
        resp = self.client.get(product.get_absolute_url())
        self.assertEqual(resp.status_code, 200)
        content = resp.content.decode()
        self.assertNotIn('"price": "0"', content)
        for obj in json_ld_objects(parse(resp)):  # разметка остаётся валидным JSON
            self.assertNotIn(obj.get('offers', {}).get('price'), ('0', 0))
        self.assertContains(resp, 'Цена по запросу')

    def test_e3_priced_product_has_price_in_markup(self):
        product = make_product(name='Кресло Цена', slug='kreslo-cena', price=15000)
        resp = self.client.get(product.get_absolute_url())
        self.assertIn('"price": "15000"', resp.content.decode())
        offer = next(o for o in json_ld_objects(parse(resp)) if o.get('@type') == 'Product')['offers']
        self.assertEqual(offer['price'], '15000')
        self.assertEqual(offer['priceCurrency'], 'RUB')


class E3ZeroPriceInCartTests(TestCase):
    """Товар лежит в корзине, цену обнулили: «Цена по запросу», итог без позиции, пометка в заявке."""

    @classmethod
    def setUpTestData(cls):
        cls.priced = make_product(name='Кресло С Ценой', slug='kreslo-s-cenoj', price=15000)
        cls.vanished = make_product(name='Диван Обнулённый', slug='divan-obnulyonnyj', price=20000)

    def fill_cart(self, *products):
        for product in products:
            self.client.post(reverse('cart_add', args=[product.id]))

    def zero(self, product):
        Product.objects.filter(pk=product.pk).update(price=0)

    def test_e3_cart_page_marks_line_and_totals_without_it(self):
        self.fill_cart(self.priced, self.vanished)
        self.zero(self.vanished)
        resp = self.client.get(reverse('cart_detail'))
        text = main_text(resp)
        self.assertIn('Цена по запросу', text)
        self.assertFalse(has_zero_price(text), text)
        self.assertEqual(resp.context['cart'].total_price, 15000)
        self.assertIn('15000₽', squash(text))
        self.assertIn('Диван Обнулённый', text)

    def test_e3_cart_drawer_marks_line(self):
        self.fill_cart(self.priced, self.vanished)
        self.zero(self.vanished)
        resp = self.client.post(reverse('cart_add', args=[self.priced.id]), **HX)
        text = norm_space(parse(resp).text)
        self.assertIn('Цена по запросу', text)
        self.assertFalse(has_zero_price(text), text)

    def test_e3_cart_update_fragment_marks_line(self):
        self.fill_cart(self.priced, self.vanished)
        self.zero(self.vanished)
        line_id = next(iter(self.client.session['cart']))
        resp = self.client.post(reverse('cart_update'), {'line_id': line_id, 'quantity': 2}, **HX)
        text = norm_space(parse(resp).text)
        self.assertIn('Цена по запросу', text)
        self.assertFalse(has_zero_price(text), text)

    def test_e3_priced_only_cart_has_no_marker(self):
        self.fill_cart(self.priced)
        text = main_text(self.client.get(reverse('cart_detail')))
        self.assertNotIn('Цена по запросу', text)

    def test_e3_checkout_page_marks_line(self):
        self.fill_cart(self.priced, self.vanished)
        self.zero(self.vanished)
        resp = self.client.get(reverse('checkout'))
        self.assertEqual(resp.status_code, 200)
        text = main_text(resp)
        self.assertIn('Цена по запросу', text)
        self.assertFalse(has_zero_price(text), text)

    def test_e3_checkout_saves_zero_item_total_without_it_and_marks_telegram(self):
        self.fill_cart(self.priced, self.vanished)
        self.zero(self.vanished)
        with mock.patch('shop.views.notify_telegram', return_value=True) as notify:
            resp = self.client.post(reverse('checkout'), ORDER_DATA)
        self.assertRedirects(resp, reverse('order_success'))
        order = Order.objects.get()
        prices = {i.product_id: i.unit_price for i in order.items.all()}
        self.assertEqual(prices, {self.priced.id: 15000, self.vanished.id: 0})
        self.assertEqual(order.total_price, 15000)
        text = notify.call_args[0][0]
        self.assertIn('цена по запросу', text)
        self.assertNotIn('— 0 ₽', text)
        self.assertFalse(has_zero_price(without_total(text)), text)
        self.assertIn('Диван Обнулённый', text)

    def test_e3_only_price_on_request_item_still_becomes_request(self):
        self.fill_cart(self.vanished)
        self.zero(self.vanished)
        page = self.client.get(reverse('checkout'))
        self.assertEqual(page.status_code, 200)
        text = main_text(page)
        self.assertIn('Цена по запросу', text)
        self.assertFalse(has_zero_price(without_total(text)), text)
        with mock.patch('shop.views.notify_telegram', return_value=True) as notify:
            resp = self.client.post(reverse('checkout'), ORDER_DATA)
        self.assertRedirects(resp, reverse('order_success'))
        order = Order.objects.get()
        self.assertEqual(order.total_price, 0)
        self.assertEqual(order.items.get().unit_price, 0)
        self.assertIn('цена по запросу', notify.call_args[0][0])
        self.assertNotIn('— 0 ₽', notify.call_args[0][0])

    def test_e3_priced_order_text_has_no_marker(self):
        self.fill_cart(self.priced)
        with mock.patch('shop.views.notify_telegram', return_value=True) as notify:
            self.client.post(reverse('checkout'), ORDER_DATA)
        self.assertNotIn('цена по запросу', notify.call_args[0][0])
        self.assertIn('15000 ₽', notify.call_args[0][0])


class E3VisibleLengthErrorTests(TestCase):
    """Ошибка длины комментария и адреса видна в HTML страницы оформления."""

    @classmethod
    def setUpTestData(cls):
        cls.product = make_product(name='Кресло Тест', price=42000)

    def post_too_long(self, field, length):
        self.client.post(reverse('cart_add', args=[self.product.id]))
        with mock.patch('shop.views.notify_telegram', return_value=True):
            resp = self.client.post(reverse('checkout'), {**ORDER_DATA, field: 'я' * length})
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(Order.objects.exists())
        return resp

    def test_e3_long_comment_error_text_is_rendered(self):
        resp = self.post_too_long('comment', 2001)
        message = resp.context['form'].errors['comment'][0]
        self.assertContains(resp, message)

    def test_e3_long_address_error_text_is_rendered(self):
        resp = self.post_too_long('delivery_address', 501)
        message = resp.context['form'].errors['delivery_address'][0]
        self.assertContains(resp, message)

    def test_e3_no_length_error_for_limit_values(self):
        self.client.post(reverse('cart_add', args=[self.product.id]))
        with mock.patch('shop.views.notify_telegram', return_value=True):
            resp = self.client.post(reverse('checkout'), {**ORDER_DATA, 'comment': 'я' * 2000,
                                                          'delivery_address': 'я' * 500})
        self.assertRedirects(resp, reverse('order_success'))


class E3ReviewThrottleMarkerTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.product = make_product(name='Кресло Отзывное', slug='kreslo-otzyvnoe')

    def post(self, data):
        return self.client.post(f'/product/{self.product.slug}/review/', data, **HX)

    def test_e3_htmx_success_is_marked(self):
        resp = self.post(REVIEW)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(getattr(resp, 'throttle_success', False))
        self.assertEqual(Review.objects.count(), 1)

    def test_e3_htmx_invalid_is_not_marked(self):
        resp = self.post({**REVIEW, 'text': ''})
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(getattr(resp, 'throttle_success', False))
        self.assertEqual(Review.objects.count(), 0)

    def test_e3_plain_post_success_is_redirect(self):
        resp = self.client.post(f'/product/{self.product.slug}/review/', REVIEW)
        self.assertEqual(resp.status_code, 302)


class E3FaqTests(TestCase):
    def test_e3_faq_page_asks_how_to_leave_request(self):
        content = self.client.get(reverse('faq_page')).content.decode()
        self.assertIn('Как оставить заявку?', content)
        self.assertNotIn('Как сделать заказ?', content)

    def test_e3_catalog_faq_block_uses_same_wording(self):
        Material.objects.create(name='Ротанг', slug='rotang')
        content = self.client.get(reverse('catalog_by_material', args=['rotang'])).content.decode()
        self.assertIn('Как оставить заявку?', content)
        self.assertNotIn('Как сделать заказ?', content)


@override_settings(SITE_URL='https://estivo63.ru')
class E3PaginationCanonicalTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        material = Material.objects.create(name='Ротанг', slug='rotang')
        Product.objects.bulk_create([
            Product(name=f'Товар {i:03d}', slug=f'tovar-{i:03d}', description='d', price=1000 + i, material=material)
            for i in range(CATALOG_PAGE_SIZE + 6)
        ])

    def canonical(self, path, **params):
        resp = self.client.get(path, params)
        self.assertEqual(resp.status_code, 200)
        links = parse(resp).find_all('link', attrs={'rel': 'canonical'})
        self.assertEqual(len(links), 1)
        return links[0].get('href')

    def test_e3_second_page_has_own_canonical(self):
        self.assertEqual(self.canonical('/catalog/', page=2), 'https://estivo63.ru/catalog/?page=2')

    def test_e3_first_page_canonical_has_no_page(self):
        self.assertEqual(self.canonical('/catalog/'), 'https://estivo63.ru/catalog/')
        self.assertEqual(self.canonical('/catalog/', page=1), 'https://estivo63.ru/catalog/')

    def test_e3_filters_and_sort_are_not_in_canonical(self):
        self.assertEqual(self.canonical('/catalog/', page=2, sort='price_asc', price_min=100),
                         'https://estivo63.ru/catalog/?page=2')
        self.assertEqual(self.canonical('/catalog/', sort='price_asc', price_min=100),
                         'https://estivo63.ru/catalog/')

    def test_e3_garbage_page_has_no_page_in_canonical(self):
        self.assertEqual(self.canonical('/catalog/', page='abc'), 'https://estivo63.ru/catalog/')

    def test_e3_material_catalog_second_page_canonical(self):
        self.assertEqual(self.canonical('/catalog/rotang/', page=2), 'https://estivo63.ru/catalog/rotang/?page=2')

    def test_e3_other_pages_canonical_unchanged(self):
        self.assertEqual(self.canonical('/faq/'), 'https://estivo63.ru/faq/')


class E3OpenRedirectTests(TestCase):
    """Регрессия: после добавления в корзину и переключения избранного возвращаем только на свой сайт."""

    @classmethod
    def setUpTestData(cls):
        cls.product = make_product(name='Кресло Тест', price=42000)

    def add(self, **data):
        return self.client.post(reverse('cart_add', args=[self.product.id]), data)

    def test_e3_external_next_goes_to_cart(self):
        self.assertRedirects(self.add(next='https://evil.example/'), reverse('cart_detail'), fetch_redirect_response=False)

    def test_e3_protocol_relative_next_is_not_followed(self):
        resp = self.add(next='//evil.example/')
        self.assertEqual(resp.status_code, 302)
        self.assertNotIn('evil', resp['Location'])
        self.assertEqual(resp['Location'], reverse('cart_detail'))

    def test_e3_javascript_next_is_not_followed(self):
        self.assertRedirects(self.add(next='javascript:alert(1)'), reverse('cart_detail'), fetch_redirect_response=False)

    def test_e3_backslash_next_is_not_followed(self):
        resp = self.add(next='/\\evil.example')
        self.assertEqual(resp['Location'], reverse('cart_detail'))

    def test_e3_own_next_is_followed(self):
        self.assertRedirects(self.add(next='/catalog/'), '/catalog/', fetch_redirect_response=False)

    def test_e3_missing_next_goes_to_cart(self):
        self.assertRedirects(self.add(), reverse('cart_detail'), fetch_redirect_response=False)

    def test_e3_wishlist_external_referer_goes_to_wishlist(self):
        resp = self.client.post(reverse('wishlist_toggle', args=[self.product.id]), HTTP_REFERER='https://evil.example/')
        self.assertRedirects(resp, reverse('wishlist'), fetch_redirect_response=False)

    def test_e3_wishlist_own_referer_goes_back(self):
        resp = self.client.post(reverse('wishlist_toggle', args=[self.product.id]),
                                HTTP_REFERER='http://testserver/catalog/')
        self.assertEqual(path_of(resp['Location']), '/catalog/')
        self.assertNotIn('evil', resp['Location'])

    def test_e3_wishlist_without_referer_goes_to_wishlist(self):
        resp = self.client.post(reverse('wishlist_toggle', args=[self.product.id]))
        self.assertRedirects(resp, reverse('wishlist'), fetch_redirect_response=False)
