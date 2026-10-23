"""E2: session wishlist — POST /wishlist/toggle/<id>/, GET /wishlist/, header counter."""
from django.test import TestCase
from django.urls import reverse

from .helpers import make_product, parse, product_card_for, product_hrefs

WISHLIST_URL = '/wishlist/'
HX = {'HTTP_HX_REQUEST': 'true'}


def toggle_url(product_id):
    return f'/wishlist/toggle/{product_id}/'


def oob_counter_texts(root):
    """Texts of data-wishlist-count elements delivered out-of-band (hx-swap-oob)."""
    texts = []
    for oob in root.find_all(attrs={'hx-swap-oob': True}):
        for node in oob.iter_self():
            if node.has_attr('data-wishlist-count'):
                texts.append(node.text.strip())
    return texts


class E2WishlistToggleTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.product = make_product(name='Кресло Избранное')

    def test_toggle_adds_then_removes(self):
        resp = self.client.post(toggle_url(self.product.id), **HX)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(self.product.id, self.client.session['wishlist'])
        self.assertIsNotNone(parse(resp).find(attrs={'aria-pressed': 'true'}))

        resp = self.client.post(toggle_url(self.product.id), **HX)
        self.assertEqual(resp.status_code, 200)
        self.assertNotIn(self.product.id, self.client.session.get('wishlist', []))
        self.assertIsNotNone(parse(resp).find(attrs={'aria-pressed': 'false'}))

    def test_toggle_updates_counter_out_of_band(self):
        resp = self.client.post(toggle_url(self.product.id), **HX)
        texts = oob_counter_texts(parse(resp))
        self.assertTrue(texts, 'expected an hx-swap-oob element with data-wishlist-count')
        self.assertTrue(any('1' in t for t in texts), texts)

        resp = self.client.post(toggle_url(self.product.id), **HX)
        texts = oob_counter_texts(parse(resp))
        self.assertTrue(texts)
        self.assertFalse(any('1' in t for t in texts), texts)

    def test_unknown_product_404(self):
        resp = self.client.post(toggle_url(999999), **HX)
        self.assertEqual(resp.status_code, 404)

    def test_get_not_allowed(self):
        self.assertEqual(self.client.get(toggle_url(self.product.id)).status_code, 405)

    def test_header_counter_reflects_session(self):
        self.client.post(toggle_url(self.product.id), **HX)
        root = parse(self.client.get(reverse('home')))
        counters = root.find_all(attrs={'data-wishlist-count': True})
        self.assertTrue(counters)
        self.assertTrue(any(c.text.strip() == '1' for c in counters), [c.text for c in counters])

    def test_card_heart_pressed_for_wishlisted_product(self):
        self.client.post(toggle_url(self.product.id), **HX)
        card = product_card_for(parse(self.client.get(reverse('catalog_list'))), self.product)
        self.assertIsNotNone(card)
        heart = card.find('button', attrs={'aria-pressed': True})
        self.assertIsNotNone(heart)
        self.assertEqual(heart.get('aria-pressed'), 'true')


class E2WishlistPageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.kept = make_product(name='Кресло Оставленное')
        cls.unavailable = make_product(name='Кресло Снятое')
        cls.deleted = make_product(name='Кресло Удалённое')
        cls.not_added = make_product(name='Кресло Не Добавленное')

    def main(self, resp):
        main = parse(resp).find('main')
        self.assertIsNotNone(main)
        return main

    def test_shows_only_added_available_products(self):
        for p in (self.kept, self.unavailable, self.deleted):
            self.client.post(toggle_url(p.id), **HX)
        self.unavailable.is_available = False
        self.unavailable.save()
        deleted_url = self.deleted.get_absolute_url()
        self.deleted.delete()

        resp = self.client.get(WISHLIST_URL)
        self.assertEqual(resp.status_code, 200)
        links = product_hrefs(self.main(resp))
        self.assertIn(self.kept.get_absolute_url(), links)
        self.assertNotIn(self.unavailable.get_absolute_url(), links)
        self.assertNotIn(deleted_url, links)
        self.assertNotIn(self.not_added.get_absolute_url(), links)

    def test_empty_wishlist_message_and_catalog_link(self):
        resp = self.client.get(WISHLIST_URL)
        self.assertEqual(resp.status_code, 200)
        main = self.main(resp)
        self.assertIsNotNone(main.find('a', attrs={'href': reverse('catalog_list')}))
