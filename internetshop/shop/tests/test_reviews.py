"""E2: moderated review form — POST /product/<slug>/review/ (ReviewForm + honeypot).

Form field names (chosen, see report): author, rating, usage_duration (optional), text;
honeypot field: website (must stay empty).
"""
from unittest import mock

from django.test import TestCase

from shop.models import Review

from .helpers import make_product

HX = {'HTTP_HX_REQUEST': 'true'}


def review_url(product):
    return f'/product/{product.slug}/review/'


VALID = {
    'author': 'Ольга',
    'rating': '5',
    'usage_duration': '2 месяца',
    'text': 'Уникальный текст отзыва для проверки модерации',
    'website': '',
}


class E2ReviewSubmitTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.product = make_product(name='Кресло Отзывное', slug='kreslo-otzyvnoe')

    def post(self, data, **extra):
        with mock.patch('shop.views.notify_telegram', return_value=True) as views_notify, \
                mock.patch('shop.utils.notify_telegram', return_value=True) as utils_notify:
            resp = self.client.post(review_url(self.product), data, **extra)
        self.views_notify, self.utils_notify = views_notify, utils_notify
        return resp

    def test_valid_review_saved_unpublished(self):
        resp = self.post(VALID, **HX)
        self.assertEqual(resp.status_code, 200)
        review = Review.objects.get()
        self.assertEqual(review.product, self.product)
        self.assertFalse(review.is_published)
        self.assertEqual(review.author, 'Ольга')
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.usage_duration, '2 месяца')

    def test_htmx_success_returns_moderation_message(self):
        resp = self.post(VALID, **HX)
        self.assertIn('модерац', resp.content.decode().lower())

    def test_usage_duration_optional(self):
        data = dict(VALID, usage_duration='')
        self.post(data, **HX)
        self.assertEqual(Review.objects.count(), 1)

    def test_unpublished_review_not_shown_on_pdp(self):
        self.post(VALID, **HX)
        resp = self.client.get(self.product.get_absolute_url())
        self.assertNotContains(resp, VALID['text'])

    def test_honeypot_filled_creates_nothing(self):
        resp = self.post(dict(VALID, website='http://spam.example'), **HX)
        self.assertLess(resp.status_code, 500)
        self.assertEqual(Review.objects.count(), 0)

    def test_rating_out_of_range_is_form_error(self):
        for rating in ('0', '6', 'abc'):
            resp = self.post(dict(VALID, rating=rating), **HX)
            self.assertIn(resp.status_code, (200, 400, 422), rating)
            self.assertContains(resp, 'name="rating"', status_code=resp.status_code)
        self.assertEqual(Review.objects.count(), 0)

    def test_required_fields(self):
        self.post(dict(VALID, author='', text=''), **HX)
        self.assertEqual(Review.objects.count(), 0)

    def test_no_telegram_notification(self):
        self.post(VALID, **HX)
        self.views_notify.assert_not_called()
        self.utils_notify.assert_not_called()

    def test_unknown_product_404(self):
        resp = self.client.post('/product/net-takogo-tovara/review/', VALID, **HX)
        self.assertEqual(resp.status_code, 404)

    def test_non_htmx_post_also_saves(self):
        resp = self.post(VALID)
        self.assertIn(resp.status_code, (200, 302))
        self.assertEqual(Review.objects.filter(is_published=False).count(), 1)
