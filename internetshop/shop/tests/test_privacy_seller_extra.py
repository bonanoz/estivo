from django.test import TestCase
from django.urls import reverse


class RequisitesRenderTests(TestCase):
    def test_no_empty_requisites_and_no_ip_ogrnip(self):
        for name in ('privacy_page', 'home'):
            html = self.client.get(reverse(name)).content.decode()
            for bad in ('ОГРН ,', 'ОГРН  ·', 'адрес: .', '323632700013220'):
                self.assertNotIn(bad, html, name)
            self.assertIn('ОГРН 1146320022089', html, name)
