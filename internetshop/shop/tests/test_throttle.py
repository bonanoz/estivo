"""E1 (audit-fixes): лимит POST считает только успешные отправки (редирект 3xx или ответ с ``throttle_success``)."""
from unittest import mock

from django.core.cache import cache
from django.http import HttpResponse
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse

from shop.models import Lead
from shop.utils import throttle_post

VALID_LEAD = {'name': 'Анна', 'phone': '+7 900 123-45-67', 'email': '', 'lead_type': 'private', 'message': ''}


@override_settings(CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}})
class ThrottleTests(TestCase):
    def setUp(self):
        cache.clear()
        patcher = mock.patch('shop.views.notify_telegram', return_value=True)
        patcher.start()
        self.addCleanup(patcher.stop)

    def post_valid(self, **extra):
        return self.client.post(reverse('contacts_page'), VALID_LEAD, **extra)

    def test_e1_invalid_posts_are_not_counted(self):
        url = reverse('contacts_page')
        codes = [self.client.post(url, {}).status_code for _ in range(7)]
        self.assertEqual(codes, [200] * 7)
        self.assertEqual(Lead.objects.count(), 0)

    def test_e1_wrong_phone_five_times_then_valid_still_accepted(self):
        url = reverse('contacts_page')
        for _ in range(5):
            self.assertEqual(self.client.post(url, {**VALID_LEAD, 'phone': '123'}).status_code, 200)
        self.assertEqual(self.client.post(url, VALID_LEAD).status_code, 302)
        self.assertEqual(Lead.objects.count(), 1)

    def test_e1_sixth_successful_post_is_limited(self):
        codes = [self.post_valid().status_code for _ in range(5)]
        self.assertEqual(codes, [302] * 5)
        self.assertEqual(self.post_valid().status_code, 429)
        self.assertEqual(Lead.objects.count(), 5)

    def test_e1_after_five_successes_even_invalid_post_gets_429(self):
        for _ in range(5):
            self.post_valid()
        self.assertEqual(self.client.post(reverse('contacts_page'), {}).status_code, 429)

    def test_e1_errors_between_successes_do_not_eat_the_budget(self):
        url = reverse('contacts_page')
        for _ in range(4):
            self.assertEqual(self.client.post(url, VALID_LEAD).status_code, 302)
            self.assertEqual(self.client.post(url, {}).status_code, 200)
        self.assertEqual(self.client.post(url, VALID_LEAD).status_code, 302)
        self.assertEqual(self.client.post(url, VALID_LEAD).status_code, 429)

    def test_e1_honeypot_redirect_counts_as_success(self):
        url = reverse('contacts_page')
        spam = {**VALID_LEAD, 'website': 'http://spam.example'}
        self.assertEqual([self.client.post(url, spam).status_code for _ in range(5)], [302] * 5)
        self.assertEqual(self.client.post(url, spam).status_code, 429)
        self.assertEqual(Lead.objects.count(), 0)

    def test_e1_get_not_limited(self):
        url = reverse('contacts_page')
        self.assertTrue(all(self.client.get(url).status_code == 200 for _ in range(8)))

    def test_e1_get_does_not_use_up_post_budget(self):
        url = reverse('contacts_page')
        for _ in range(8):
            self.client.get(url)
        self.assertEqual([self.post_valid().status_code for _ in range(5)], [302] * 5)

    def test_e1_clients_with_different_ips_do_not_share_budget(self):
        for _ in range(5):
            self.post_valid(HTTP_X_FORWARDED_FOR='1.1.1.1')
        self.assertEqual(self.post_valid(HTTP_X_FORWARDED_FOR='1.1.1.1').status_code, 429)
        self.assertEqual(self.post_valid(HTTP_X_FORWARDED_FOR='2.2.2.2').status_code, 302)

    def test_e1_ip_is_last_forwarded_address(self):
        for i in range(5):
            self.post_valid(HTTP_X_FORWARDED_FOR=f'10.0.0.{i}, 9.9.9.9')
        self.assertEqual(self.post_valid(HTTP_X_FORWARDED_FOR='10.0.0.99, 9.9.9.9').status_code, 429)


@override_settings(CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}})
class ThrottleSuccessMarkerTests(TestCase):
    """Контракт декоратора: успех — 300 <= status < 400 или у ответа истинный ``throttle_success``."""

    def setUp(self):
        cache.clear()
        self.factory = RequestFactory()

    def hammer(self, view, times):
        wrapped = throttle_post(limit=2, window=60)(view)
        return [wrapped(self.factory.post('/x/')).status_code for _ in range(times)]

    def test_e1_marked_200_response_is_counted(self):
        def marked_view(request):
            response = HttpResponse('ok')
            response.throttle_success = True
            return response
        self.assertEqual(self.hammer(marked_view, 4), [200, 200, 429, 429])

    def test_e1_plain_200_response_is_not_counted(self):
        def plain_view(request):
            return HttpResponse('форма с ошибками')
        self.assertEqual(self.hammer(plain_view, 6), [200] * 6)

    def test_e1_explicitly_false_marker_is_not_counted(self):
        def false_view(request):
            response = HttpResponse('ошибка')
            response.throttle_success = False
            return response
        self.assertEqual(self.hammer(false_view, 5), [200] * 5)

    def test_e1_redirect_is_counted_without_marker(self):
        def redirect_view(request):
            return HttpResponse(status=302, headers={'Location': '/ok/'})
        self.assertEqual(self.hammer(redirect_view, 4), [302, 302, 429, 429])

    def test_e1_client_and_server_errors_are_not_counted(self):
        def broken_view(request):
            return HttpResponse(status=400)
        self.assertEqual(self.hammer(broken_view, 5), [400] * 5)

    def test_e1_mixed_results_count_only_successes(self):
        calls = []

        def view(request):
            calls.append(1)
            if len(calls) % 2:
                return HttpResponse('ошибка')
            return HttpResponse(status=302, headers={'Location': '/ok/'})
        # ошибка, успех, ошибка, успех, ошибка -> лимит 2 исчерпан двумя успехами
        self.assertEqual(self.hammer(view, 5), [200, 302, 200, 302, 429])

    def test_e1_get_never_limited_even_for_successful_view(self):
        def marked_view(request):
            response = HttpResponse('ok')
            response.throttle_success = True
            return response
        wrapped = throttle_post(limit=2, window=60)(marked_view)
        self.assertEqual([wrapped(self.factory.get('/x/')).status_code for _ in range(6)], [200] * 6)
