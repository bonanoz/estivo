"""E2: страницы коллекций /kollekcii/, пункт меню, SEO и sitemap (R2.1-R2.4)."""
from django.conf import settings
from django.test import TestCase
from django.urls import reverse


from .helpers import norm_space, parse
from .helpers_collections import card_paths, category, collection, material, product_in, zone

LIST_URL = '/kollekcii/'


def link_hrefs(root):
    return [a.get('href') for a in root.find_all('a', attrs={'href': True})]


def sections(root):
    """{заголовок раздела: [пути карточек]} по порядку документа."""
    return card_paths(root)


def find_section(root, title):
    for name, paths in sections(root):
        if name.startswith(title):
            return paths
    return None


class CollectionsTestCase(TestCase):
    def setUp(self):
        self.mat = material('Роуп')
        self.chairs = category('Кресла', order=1)
        self.tables = category('Столы обеденные', order=2)
        self.sofas = category('Диваны', order=3)
        self.dining = zone('Обеденная группа', order=1)
        self.lounge = zone('Лаунж-зона', order=2)
        self.milan = collection('Милан', order=1, description='Линейка из роупа ручной работы.')
        self.bari = collection('Бари', order=2)

    def prod(self, name, cat, collections, zone_obj=None, price=10000, **kw):
        return product_in(collections=collections, zone_obj=zone_obj, name=name, category=cat,
                          material=self.mat, price=price, **kw)

    def page(self, url=LIST_URL, status=200):
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status)
        return parse(resp)


class E2UrlsTests(TestCase):
    def test_r21_route_names(self):
        self.assertEqual(reverse('collection_list'), '/kollekcii/')
        self.assertEqual(reverse('collection_detail', args=['milan']), '/kollekcii/milan/')


class E2ListTests(CollectionsTestCase):
    def test_r21_list_shows_collections_with_links_and_heading(self):
        for i in range(3):
            self.prod(f'Кресло Милан {i}', self.chairs, [self.milan], self.dining)
        self.prod('Стол Бари', self.tables, [self.bari], self.dining)
        root = self.page()
        hrefs = link_hrefs(root)
        self.assertIn('/kollekcii/milan/', hrefs)
        self.assertIn('/kollekcii/bari/', hrefs)
        self.assertEqual(norm_space(root.find('h1').text), 'Коллекции')
        self.assertIn('Милан', root.text)
        self.assertIn('Бари', root.text)

    def test_r21_breadcrumbs(self):
        self.prod('Кресло Милан', self.chairs, [self.milan])
        crumbs = self.page().find(cls='breadcrumbs')
        self.assertIsNotNone(crumbs)
        items = [norm_space(li.text) for li in crumbs.find_all('li') if norm_space(li.text) != '/']
        self.assertEqual(items, ['Главная', 'Коллекции'])

    def test_r21_collections_follow_order_field(self):
        self.milan.order, self.bari.order = 2, 1
        self.milan.save()
        self.bari.save()
        self.prod('Кресло Милан', self.chairs, [self.milan])
        self.prod('Стол Бари', self.tables, [self.bari])
        hrefs = link_hrefs(self.page())
        self.assertLess(hrefs.index('/kollekcii/bari/'), hrefs.index('/kollekcii/milan/'))

    def test_r21_collection_without_products_is_hidden(self):
        como = collection('Комо', order=5)
        self.prod('Кресло Милан', self.chairs, [self.milan])
        root = self.page()
        self.assertNotIn(f'/kollekcii/{como.slug}/', link_hrefs(root))
        self.assertNotIn('Комо', root.find('main').text if root.find('main') else root.text)

    def test_r21_collection_with_only_hidden_products_is_hidden(self):
        asti = collection('Асти', order=3)
        self.prod('Кресло Асти', self.chairs, [asti], is_available=False)
        self.prod('Кресло Милан', self.chairs, [self.milan])
        self.assertNotIn('/kollekcii/asti/', link_hrefs(self.page()))

    def test_r21_nothing_to_show_message_and_catalog_link(self):
        root = self.page()
        message = [n for n in root.iter() if 'Коллекции скоро появятся' in n.text]
        self.assertTrue(message)
        node = message[-1]
        scopes = [node] + [a for a in node.ancestors() if a.tag not in ('body', 'html', '#root')][:3]
        self.assertTrue(any(s.find('a', attrs={'href': '/catalog/'}) for s in scopes),
                        'рядом с сообщением нет ссылки на /catalog/')
        self.assertNotIn('/kollekcii/milan/', link_hrefs(root))

    def test_r21_message_absent_when_collections_exist(self):
        self.prod('Кресло Милан', self.chairs, [self.milan])
        self.assertNotIn('Коллекции скоро появятся', self.page().text)


class E2DetailTests(CollectionsTestCase):
    def fill_milan(self):
        self.dining_items = [self.prod('Стол Новара', self.tables, [self.milan], self.dining, price=50000),
                             self.prod('Кресло Милан', self.chairs, [self.milan], self.dining, price=20000)]
        self.lounge_items = [self.prod(f'Диван Милан {i}', self.sofas, [self.milan], self.lounge, price=80000 + i)
                             for i in range(3)]

    def test_r22_heading_description_and_breadcrumbs(self):
        self.fill_milan()
        root = self.page('/kollekcii/milan/')
        self.assertEqual(norm_space(root.find('h1').text), 'Коллекция «Милан»')
        self.assertIn('Линейка из роупа ручной работы.', root.text)
        crumbs = root.find(cls='breadcrumbs')
        items = [norm_space(li.text) for li in crumbs.find_all('li') if norm_space(li.text) != '/']
        self.assertEqual(items, ['Главная', 'Коллекции', 'Милан'])
        self.assertIsNotNone(crumbs.find('a', attrs={'href': '/kollekcii/'}))

    def test_r22_no_description_block_when_empty(self):
        self.milan.description = ''
        self.milan.save()
        self.fill_milan()
        self.assertEqual(self.page('/kollekcii/milan/').find('h1').tag, 'h1')

    def test_r22_two_zones_in_order_with_cards(self):
        self.fill_milan()
        root = self.page('/kollekcii/milan/')
        titles = [name for name, _ in sections(root) if name.startswith(('Обеденная', 'Лаунж'))]
        self.assertEqual([t.split()[0] for t in titles], ['Обеденная', 'Лаунж-зона'])
        self.assertEqual(len(find_section(root, 'Обеденная группа')), 2)
        self.assertEqual(len(find_section(root, 'Лаунж-зона')), 3)

    def test_r22_zones_follow_zone_order_field(self):
        self.dining.order, self.lounge.order = 9, 3
        self.dining.save()
        self.lounge.save()
        self.fill_milan()
        names = [n for n, _ in sections(self.page('/kollekcii/milan/')) if n.startswith(('Обеденная', 'Лаунж'))]
        self.assertTrue(names[0].startswith('Лаунж'))

    def test_r22_anchor_links_point_to_zone_sections(self):
        self.fill_milan()
        root = self.page('/kollekcii/milan/')
        for title in ('Обеденная группа', 'Лаунж-зона'):
            with self.subTest(zone=title):
                anchors = [a for a in root.find_all('a', attrs={'href': True})
                           if a.get('href').startswith('#') and norm_space(a.text) == title]
                self.assertEqual(len(anchors), 1)
                target = root.get_by_id(anchors[0].get('href')[1:])
                self.assertIsNotNone(target, 'у якоря нет цели')
                heading = target if target.tag in ('h2', 'h3') else target.find(pred=lambda n: n.tag in ('h2', 'h3'))
                self.assertTrue(norm_space(heading.text).startswith(title))

    def test_r22_product_without_zone_goes_last_under_more(self):
        self.fill_milan()
        loose = self.prod('Пуф Милан', self.chairs, [self.milan], None)
        root = self.page('/kollekcii/milan/')
        titles = [n for n, _ in sections(root) if n.startswith(('Обеденная', 'Лаунж', 'Ещё в коллекции'))]
        self.assertEqual(titles[-1], 'Ещё в коллекции')
        self.assertEqual(find_section(root, 'Ещё в коллекции'), [loose.get_absolute_url()])

    def test_r22_no_more_section_when_all_have_zone(self):
        self.fill_milan()
        self.assertIsNone(find_section(self.page('/kollekcii/milan/'), 'Ещё в коллекции'))

    def test_r22_empty_zone_has_no_section_and_no_anchor(self):
        bar = zone('Барная зона', order=3)
        self.fill_milan()
        self.prod('Барное кресло Бари', self.chairs, [self.bari], bar)  # зона занята, но в другой коллекции
        root = self.page('/kollekcii/milan/')
        self.assertIsNone(find_section(root, 'Барная зона'))
        self.assertFalse([a for a in root.find_all('a') if norm_space(a.text) == 'Барная зона'])

    def test_r22_shared_table_on_both_pages(self):
        table = self.prod('Стол Новара', self.tables, [self.milan, self.bari], self.dining)
        for url in ('/kollekcii/milan/', '/kollekcii/bari/'):
            with self.subTest(url=url):
                self.assertIn(table.get_absolute_url(), find_section(self.page(url), 'Обеденная группа'))

    def test_r22_hidden_product_has_no_card_and_hidden_only_zone_has_no_section(self):
        self.fill_milan()
        hidden = self.prod('Диван Снят', self.sofas, [self.milan], zone('Барная зона', order=3), is_available=False)
        root = self.page('/kollekcii/milan/')
        self.assertNotIn(hidden.get_absolute_url(), link_hrefs(root))
        self.assertIsNone(find_section(root, 'Барная зона'))

    def test_r22_unknown_slug_is_404(self):
        self.fill_milan()
        self.page('/kollekcii/milan/')  # страница работает, значит 404 ниже не из-за отсутствия маршрута
        self.assertEqual(self.client.get('/kollekcii/net-takoy/').status_code, 404)

    def test_r22_collection_without_products_is_404_by_direct_link(self):
        como = collection('Комо', order=5)
        self.prod('Кресло Милан', self.chairs, [self.milan])
        self.page('/kollekcii/milan/')
        self.assertEqual(self.client.get(f'/kollekcii/{como.slug}/').status_code, 404)

    def test_r22_collection_with_only_hidden_products_is_404(self):
        asti = collection('Асти', order=3)
        self.prod('Кресло Асти', self.chairs, [asti], is_available=False)
        self.prod('Кресло Милан', self.chairs, [self.milan])
        self.page('/kollekcii/milan/')
        self.assertEqual(self.client.get('/kollekcii/asti/').status_code, 404)

    def test_r22_within_zone_category_order_then_price(self):
        table = self.prod('Стол Новара', self.tables, [self.milan], self.dining, price=10000)
        dear_chair = self.prod('Кресло Дорогое', self.chairs, [self.milan], self.dining, price=90000)
        cheap_chair = self.prod('Кресло Дешёвое', self.chairs, [self.milan], self.dining, price=20000)
        paths = find_section(self.page('/kollekcii/milan/'), 'Обеденная группа')
        self.assertEqual(paths, [cheap_chair.get_absolute_url(), dear_chair.get_absolute_url(),
                                 table.get_absolute_url()])


class E2MenuTests(CollectionsTestCase):
    def nav_labels(self, root, nav):
        links = nav.find_all('a')
        return [(norm_space(a.text), a.get('href')) for a in links]

    def check(self, url):
        root = self.page(url)
        desktop = root.find('nav', attrs={'aria-label': 'Основная навигация'})
        mobile = root.find('nav', attrs={'id': 'mobile-menu'})
        for name, nav in (('шапка', desktop), ('мобильное меню', mobile)):
            with self.subTest(menu=name, url=url):
                self.assertIsNotNone(nav)
                labels = self.nav_labels(root, nav)
                texts = [t for t, _ in labels]
                self.assertEqual(texts.index('Коллекции'), texts.index('Каталог') + 1)
                self.assertEqual(labels[texts.index('Коллекции')][1], '/kollekcii/')
        self.assertEqual([t for t, _ in self.nav_labels(root, mobile)][:2], ['Каталог', 'Коллекции'])

    def test_r23_menu_item_on_home(self):
        self.check('/')

    def test_r23_menu_item_on_other_pages(self):
        self.check('/cart/')
        self.check('/faq/')


class E2SeoTests(CollectionsTestCase):
    def setUp(self):
        super().setUp()
        self.prod('Кресло Милан', self.chairs, [self.milan], self.dining)

    def meta(self, root, name):
        node = root.find('meta', attrs={'name': name})
        return node.get('content') if node else None

    def test_r24_title(self):
        root = self.page('/kollekcii/milan/')
        self.assertEqual(norm_space(root.find('title').text), 'Коллекция «Милан» — уличная мебель ESTIVO')

    def test_r24_description_is_first_160_chars(self):
        self.milan.description = ' '.join(['Слово'] * 60)
        self.milan.save()
        content = self.meta(self.page('/kollekcii/milan/'), 'description')
        self.assertLessEqual(len(content), 160)
        self.assertEqual(content.strip(), self.milan.description[:160].strip())

    def test_r24_short_description_used_as_is(self):
        content = self.meta(self.page('/kollekcii/milan/'), 'description')
        self.assertEqual(content, 'Линейка из роупа ручной работы.')

    def test_r24_empty_description_uses_template_with_name(self):
        self.milan.description = ''
        self.milan.save()
        content = self.meta(self.page('/kollekcii/milan/'), 'description')
        self.assertEqual(content, 'Коллекция «Милан» от ESTIVO: обеденная группа и лаунж-зона из роупа ручной работы. '
                                  'Гарантия 3 года.')

    def test_r24_canonical_on_main_domain(self):
        root = self.page('/kollekcii/milan/')
        canonical = root.find('link', attrs={'rel': 'canonical'}).get('href')
        self.assertEqual(canonical, settings.SITE_URL.rstrip('/') + '/kollekcii/milan/')

    def test_r24_sitemap_has_list_and_populated_collections_only(self):
        collection('Комо', order=5)
        asti = collection('Асти', order=3)
        self.prod('Кресло Асти', self.chairs, [asti], is_available=False)
        xml = self.client.get('/sitemap.xml').content.decode()
        self.assertIn('/kollekcii/</loc>', xml)
        self.assertIn('/kollekcii/milan/</loc>', xml)
        self.assertNotIn('/kollekcii/komo/', xml)
        self.assertNotIn('/kollekcii/asti/', xml)
        self.assertIn(settings.SITE_URL.rstrip('/') + '/kollekcii/milan/', xml)
