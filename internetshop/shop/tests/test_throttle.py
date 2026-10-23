from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse


@override_settings(CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}})
class ThrottleTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_post_forms_limited_per_ip(self):
        url = reverse('contacts_page')
        codes = [self.client.post(url, {}).status_code for _ in range(7)]
        self.assertEqual(codes[-1], 429)
        self.assertNotIn(429, codes[:5])

    def test_get_not_limited(self):
        url = reverse('contacts_page')
        self.assertTrue(all(self.client.get(url).status_code == 200 for _ in range(8)))
