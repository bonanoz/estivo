"""E3: catalog page UI — filter form, live count, sort control, pagination nav, empty state, SEO text, search fragments."""
from django.test import TestCase
from django.urls import reverse

from shop.models import Category, ColorOption, Material, Product

from .helpers import has_number, make_product, parse, path_of, product_hrefs, query, squash

COUNT_URL = '/catalog/count/'
SUGGEST_URL = '/search/suggest/'
HX = {'HTTP_HX_REQUEST': 'true'}


def filter_form(root):
    """The GET form of the filter panel (the one carrying price_min)."""
    for form in root.find_all('form'):
        if form.get('method', '').lower() == 'get' and form.find('input', attrs={'name': 'price_min'}):
            return form
    return None


def is_checked(root, name, value):
    for inp in root.find_all('input', attrs={'name': name, 'value': str(value)}):
        if inp.has_attr('checked'):
            return True
    return False


class E3FilterPanelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.rotang = Material.objects.create(name='Ротанг', slug='rotang',
                                             description='Эко-ротанг выдерживает десятилетия.')
        cls.kresla = Category.objects.create(name='Кресла', slug='kresla')
        cls.divany = Category.objects.create(name='Диваны', slug='divany')
        cls.graphite = ColorOption.objects.create(name='Графит', finish_type=ColorOption.WEAVE, hex='#3b3a36')
        make_product(name='Кресло Каталог', price=20000, old_price=30000, material=cls.rotang,
                     category=cls.kresla, colors=[cls.graphite])
        make_product(name='Диван Каталог', price=90000, material=cls.rotang, category=cls.divany)

    def get(self, url):
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        return parse(resp)

    def test_filter_form_is_get_with_submit_and_reset(self):
        root = self.get(reverse('catalog_list'))
        form = filter_form(root)
        self.assertIsNotNone(form, 'expected <form method="get"> with filter inputs (price_min, …)')
        self.assertIn(form.get('action'), (None, '', reverse('catalog_list')),
                      'without JS the form must GET the current catalog path')
        submit = form.find(pred=lambda n: n.tag in ('button', 'input') and n.get('type') == 'submit'
                           or (n.tag == 'button' and not n.has_attr('type')))
        self.assertIsNotNone(submit, 'filter form needs an "Apply" submit')
        resets = [a for a in root.find_all('a', attrs={'href': reverse('catalog_list')})
                  if a.closest('form') is form]
        self.assertTrue(resets, '"Reset" must be a link to the path without params inside the filter form')

    def test_reset_link_on_material_page_keeps_path(self):
        url = reverse('catalog_by_material', args=['rotang'])
        root = self.get(url + '?price_min=1000')
        form = filter_form(root)
        self.assertIsNotNone(form)
        self.assertTrue([a for a in form.find_all('a', attrs={'href': url})])

    def test_live_count_element(self):
        root = self.get(reverse('catalog_list'))
        triggers = root.find_all(pred=lambda n: n.get('hx-get', '').startswith(COUNT_URL))
        self.assertTrue(triggers, 'expected an element with hx-get to /catalog/count/')
        live_ok = False
        for trig in triggers:
            target_sel = trig.get('hx-target', '')
            candidates = [trig] + list(trig.iter())
            if target_sel.startswith('#'):
                target = root.get_by_id(target_sel[1:])
                if target is not None:
                    candidates.append(target)
            if any(c.get('aria-live') == 'polite' for c in candidates):
                live_ok = True
        self.assertTrue(live_ok, 'the count element (or its hx-target) must have aria-live="polite"')

    def test_active_filters_reflected(self):
        root = self.get(reverse('catalog_list')
                        + f'?category=kresla&color={self.graphite.id}&flag=sale&price_min=1000&price_max=50000')
        self.assertTrue(is_checked(root, 'category', 'kresla'))
        self.assertFalse(is_checked(root, 'category', 'divany'))
        self.assertTrue(is_checked(root, 'color', self.graphite.id))
        self.assertTrue(is_checked(root, 'flag', 'sale'))
        self.assertEqual(root.find('input', attrs={'name': 'price_min'}).get('value'), '1000')
        self.assertEqual(root.find('input', attrs={'name': 'price_max'}).get('value'), '50000')

    def test_filter_groups_present(self):
        form = filter_form(self.get(reverse('catalog_list')))
        self.assertIsNotNone(form, 'expected the filter <form method="get">')
        for name in ('category', 'material', 'color', 'price_min', 'price_max', 'length_min', 'length_max', 'flag'):
            self.assertIsNotNone(form.find('input', attrs={'name': name}), name)

    def test_sort_control_reflects_current_value(self):
        root = self.get(reverse('catalog_list') + '?sort=price_asc')
        select = root.find('select', attrs={'name': 'sort'})
        if select is not None:
            selected = [o.get('value') for o in select.find_all('option') if o.has_attr('selected')]
            self.assertEqual(selected, ['price_asc'])
            self.assertEqual(select.closest('form').get('method', '').lower(), 'get')
        else:
            self.assertIsNotNone(root.find('button', attrs={'aria-haspopup': 'listbox'}),
                                 'sort must be <select name="sort"> or a button with aria-haspopup="listbox"')
            inputs = root.find_all('input', attrs={'name': 'sort'})
            current = [i.get('value') for i in inputs
                       if i.get('type') == 'hidden' or i.has_attr('checked')]
            self.assertIn('price_asc', current, 'no-JS fallback needs input name="sort" with the current value')

    def test_seo_text_and_faq_under_grid(self):
        root = self.get(reverse('catalog_by_material', args=['rotang']))
        self.assertIn('Эко-ротанг выдерживает десятилетия.', root.text)
        self.assertIn('Как сделать заказ?', root.text)


class E3PaginationNavTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        Product.objects.bulk_create([
            Product(name=f'Товар {i:03d}', slug=f'tovar-{i:03d}', description='d', price=1000 + i)
            for i in range(24 * 12)
        ])

    def nav(self, params=''):
        root = parse(self.client.get(reverse('catalog_list') + params))
        nav = root.find('nav', attrs={'aria-label': 'Страницы'})
        self.assertIsNotNone(nav, 'expected <nav aria-label="Страницы">')
        return nav

    def test_current_page_marked(self):
        nav = self.nav('?page=2')
        current = nav.find_all(attrs={'aria-current': 'page'})
        self.assertEqual(len(current), 1)
        self.assertTrue(has_number(current[0].text, 2), current[0].text)

    def test_numbered_links(self):
        nav = self.nav('?page=2')
        pages = {}
        for a in nav.find_all('a', attrs={'href': True}):
            pages.setdefault(query(a.get('href')).get('page', ['1'])[0], []).append(a.text)
        self.assertTrue(any(has_number(t, 1) for t in pages.get('1', [])), pages)
        self.assertTrue(any(has_number(t, 3) for t in pages.get('3', [])), pages)

    def test_ellipsis_and_last_page(self):
        nav = self.nav()
        self.assertIn('…', nav.text)
        last = [a for a in nav.find_all('a', attrs={'href': True}) if query(a.get('href')).get('page') == ['12']]
        self.assertTrue(last, 'last page must be reachable from page 1')


class E3EmptyResultTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.hit = make_product(name='Кресло Бестселлер', is_bestseller=True)

    def test_empty_result_message_and_bestsellers(self):
        resp = self.client.get(reverse('catalog_list') + '?search=qqqzzzxxx')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context['page_obj'].object_list), 0)
        self.assertContains(resp, 'Ничего не найдено')
        self.assertIn(self.hit.get_absolute_url(), product_hrefs(parse(resp)))


class E3SearchFragmentTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.product = make_product(name='Кресло Суджест', price=45000)

    def test_suggestion_rows_and_all_results_link(self):
        resp = self.client.get(SUGGEST_URL, {'q': 'Суджест'}, **HX)
        root = parse(resp)
        self.assertIn(self.product.get_absolute_url(), product_hrefs(root))
        self.assertIn('Кресло Суджест', root.text)
        self.assertIn('45000', squash(root.text))
        all_results = [a for a in root.find_all('a', attrs={'href': True})
                       if path_of(a.get('href')) == reverse('catalog_list')
                       and query(a.get('href')).get('search') == ['Суджест']]
        self.assertTrue(all_results, 'expected "All results" link to /catalog/?search=<q>')
