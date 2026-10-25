import csv
import re
from functools import lru_cache

from django.conf import settings
from django.http import HttpResponsePermanentRedirect
from django.shortcuts import render

from .models import Product


def _key(path):
    return path.rstrip('/') or '/'


@lru_cache(maxsize=1)
def _load_map():
    """Карта редиректов Tilda -> Django: {old_path без слэша: (действие, new_path)}."""
    with open(settings.BASE_DIR / 'shop' / 'data' / 'redirect_map.csv', encoding='utf-8-sig', newline='') as f:
        rows = list(csv.reader(f, delimiter=';'))[1:]
    return {_key(r[0]): (r[4], r[5]) for r in rows if len(r) > 5}


def _section_url(path):
    """Раздел каталога для /<раздел>/tproduct/…: куда карта ведёт /<раздел>, без query; иначе /catalog/."""
    action, new_path = _load_map().get('/' + path.strip('/').split('/')[0], (None, ''))
    new_path = new_path.split('?')[0]
    return new_path if action == '301' and new_path.startswith('/catalog/') else '/catalog/'


ATTRIBUTION_KEYS = {'utm_source': 255, 'utm_medium': 255, 'utm_campaign': 255, 'utm_content': 255,
                    'utm_term': 255, 'yclid': 64}
SKIP_PREFIXES = ('/static/', '/media/', '/admin/', '/robots.txt', '/sitemap.xml')


class AttributionMiddleware:
    """First-touch: первый HTML-заход сессии запоминает utm_*, yclid и страницу входа, дальше не перезаписывает."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if (request.method == 'GET' and 'attribution' not in request.session
                and not request.headers.get('HX-Request')
                and not request.path.startswith(SKIP_PREFIXES)):
            data = {k: request.GET.get(k, '')[:n] for k, n in ATTRIBUTION_KEYS.items()}
            # Анонимный заход без меток сессию не создаёт (иначе падает test_anonymous_visit_does_not_create_session).
            if request.session.session_key or any(data.values()):
                data['landing_page'] = request.get_full_path()[:500]
                request.session['attribution'] = data
        return self.get_response(request)


class TildaRedirectMiddleware:
    """Старые адреса Tilda: на 404 отдаёт 301/410 по карте (стоит после CommonMiddleware, чтобы
    видеть исходный 404 раньше APPEND_SLASH и не плодить цепочки)."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if response.status_code != 404:
            return response
        path = _key(request.path)
        if path.startswith('/news/tpost/'):
            return HttpResponsePermanentRedirect('/')
        if '/tproduct/' in path + '/' and (m := re.match(r'(\d+)-', path.rsplit('/', 1)[-1])):
            product = Product.objects.filter(tilda_id=int(m.group(1))).first()
            if product:
                return HttpResponsePermanentRedirect(product.get_absolute_url())
        action, new_path = _load_map().get(path, (None, None))
        if action == '301' and new_path.startswith('/product/') \
                and not Product.objects.filter(slug=new_path.split('/')[2]).exists():
            # товар не импортирован (ручная проверка) — в раздел каталога, а не в 404
            new_path = _section_url(path)
        if action == '301':
            return HttpResponsePermanentRedirect(new_path)
        if action == '410':
            return render(request, '410.html', status=410)
        return response


def clear_prefetch_on_post(get_response):
    """После POST (корзина, избранное, формы) сбрасывает страницы, заранее скачанные по speculationrules
    в base.html: иначе переход показал бы старый счётчик корзины. Браузеры без поддержки заголовок игнорируют."""
    def middleware(request):
        response = get_response(request)
        if request.method == 'POST':
            response['Clear-Site-Data'] = '"prefetchCache"'
        return response
    return middleware
