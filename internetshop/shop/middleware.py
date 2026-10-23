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
