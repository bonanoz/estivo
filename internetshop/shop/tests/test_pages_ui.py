"""E6: home section order, hero CTA, content pages (single h1 + breadcrumbs), lead forms, 404, static 500."""
from unittest import mock

from django.template.loader import get_template
from django.test import TestCase
from django.urls import reverse

from shop.models import Category, Collection, Lead, Material, Review

from .helpers import make_product, parse, product_card_for

HOME_SECTIONS = ['hero', 'categories', 'collections', 'services', 'reviews', 'story', 'seo']
CONTENT_PAGES = ['about_page', 'b2b_page', 'designers_page', 'delivery_payment_page',
                 'warranty_page', 'faq_page', 'contacts_page']


class E6HomeTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        material = Material.objects.create(name='Ротанг', slug='rotang')
        category = Category.objects.create(name='Кресла', slug='kresla')
        collection = Collection.objects.create(name='Терраса', slug='terrasa', is_featured=True)
        product = make_product(name='Кресло Главное', material=material, category=category,
                               collection=collection, is_featured=True)
        Review.objects.create(product=product, author='Мария', rating=5, text='Чудесно', is_published=True)

    def setUp(self):
        resp = self.client.get(reverse('home'))
        self.assertEqual(resp.status_code, 200)
        self.root = parse(resp)

    def test_sections_in_order(self):
        order = [n.get('data-section') for n in self.root.find_all(attrs={'data-section': True})
                 if n.get('data-section') in HOME_SECTIONS]
        self.assertEqual(order, HOME_SECTIONS)

    def test_hero_has_h1_and_single_primary_cta(self):
        hero = self.root.find(attrs={'data-section': 'hero'})
        self.assertIsNotNone(hero)
        self.assertIsNotNone(hero.find('h1'))
        self.assertEqual(len(hero.find_all(cls='btn-primary')), 1)

    def test_single_h1(self):
        self.assertEqual(len(self.root.find_all('h1')), 1)


class E6ContentPagesTests(TestCase):
    def test_single_h1_and_breadcrumbs(self):
        for name in CONTENT_PAGES:
            resp = self.client.get(reverse(name))
            self.assertEqual(resp.status_code, 200, name)
            self.assertEqual(len(parse(resp).find_all('h1')), 1, name)
            self.assertTemplateUsed(resp, 'partials/_breadcrumbs.html', name)


class E6LeadFormsTests(TestCase):
    DATA = {'name': 'Иван', 'phone': '+7 900 123-45-67', 'email': '', 'message': 'Хочу проект'}

    def post(self, url_name, lead_type):
        with mock.patch('shop.views.notify_telegram', return_value=True):
            resp = self.client.post(reverse(url_name), dict(self.DATA, lead_type=lead_type))
        self.assertEqual(resp.status_code, 302, url_name)
        return Lead.objects.get()

    def test_designers_form_saves_lead(self):
        lead = self.post('designers_page', 'designer')
        self.assertEqual(lead.lead_type, 'designer')
        self.assertTrue(lead.telegram_notified)

    def test_contacts_form_saves_lead(self):
        lead = self.post('contacts_page', 'private')
        self.assertEqual(lead.lead_type, 'private')

    def test_lead_saved_even_if_telegram_fails(self):
        with mock.patch('shop.views.notify_telegram', return_value=False):
            self.client.post(reverse('b2b_page'), dict(self.DATA, lead_type='b2b'))
        self.assertFalse(Lead.objects.get().telegram_notified)


class E6NotFoundPageTests(TestCase):
    URL = '/takoy-stranicy-net/'

    def test_heading_and_catalog_link(self):
        resp = self.client.get(self.URL)
        self.assertEqual(resp.status_code, 404)
        root = parse(resp)
        self.assertEqual(len(root.find_all('h1')), 1)
        self.assertIsNotNone(root.find('main').find('a', attrs={'href': reverse('catalog_list')}))

    def test_bestseller_cards(self):
        hit = make_product(name='Кресло Хит 404', is_bestseller=True)
        root = parse(self.client.get(self.URL))
        self.assertIsNotNone(product_card_for(root, hit), 'bestsellers must render as product cards')


class E6ServerErrorTemplateTests(TestCase):
    def test_500_is_static(self):
        template = get_template('500.html')
        source = template.template.source
        for forbidden in ('{% extends', 'site_info', 'site_settings', '{{ cart', '{{ wishlist', 'request.'):
            self.assertNotIn(forbidden, source, f'500.html must not use {forbidden!r}')
        with self.assertNumQueries(0):
            html = template.render({})
        root = parse(html)
        self.assertEqual(root.find('html').get('lang'), 'ru')
        self.assertEqual(len(root.find_all('h1')), 1)
