SITE_INFO = {
    'brand_name': 'ESTIVO',
    'phone': '+7 927 268-94-04',
    'phone_href': '+79272689404',
    'callback_note': 'Перезваниваем или пишем в течение 5 минут',
    'email': 'esti-vo@mail.ru',
    'address': 'г. Тольятти, б-р Туполева, 12А, офис 2-4',
    # долгота,широта дома для метки Яндекс Карт: поиск по тексту с «офис 2-4» ставит метку не туда
    'map_ll': '49.302885,53.521736',
    'work_hours': [
        ('Пн-Пт', '10:00–19:00'),
        ('Сб', '10:00–18:00'),
        ('Вс', '10:00–17:00'),
    ],
    'work_hours_note': 'Работаем по предварительной записи',
    'social_links': {
        'instagram': 'https://www.instagram.com/estivo.tlt',
        'whatsapp': 'https://wa.me/79272689404',
        'telegram': 'https://t.me/estivo63',
        'max': 'https://max.ru/+79272004303',
        'vk': 'https://vk.com/estivo_tlt',
        'pinterest': 'https://pin.it/4AWL8Yise',
    },
    'legal_name': 'ООО «Эстиво»',
    'inn': '6321368220',
    'ogrn': '1146320022089',
    'legal_address': '445042, Самарская обл., г. Тольятти, б-р Луначарского, д. 17, 31',
}


def site_info(request):
    """Контакты, соцсети и реквизиты компании — доступны в любом шаблоне
    без передачи вручную из каждого view (шапка/подвал сайта)."""
    return {'site_info': SITE_INFO}


def cart(request):
    """Корзина — доступна в любом шаблоне (счётчик в шапке на всех страницах)."""
    from .cart import Cart
    return {'cart': Cart(request)}


def wishlist(request):
    """Избранное — счётчик в шапке и состояние сердечек на карточках.

    ``wishlist`` поддерживает ``{% if product.id in wishlist %}``,
    ``wishlist.count`` и ``wishlist.ids``.
    """
    from .wishlist import Wishlist
    wl = Wishlist(request)
    return {'wishlist': wl, 'wishlist_ids': wl.ids}


def site_settings(request):
    """Редактируемые из админки фото страниц (hero, B2B, дизайнерам) —
    доступны в любом шаблоне без передачи из каждого view."""
    from .models import SiteSettings
    return {'site_settings': SiteSettings.get_cached()}


def analytics(request):
    """Согласие на cookie (полоса, счётчик Метрики) и цели, ждущие показа на этой странице."""
    consent = request.COOKIES.get('cookie_consent')
    context = {
        'analytics_consent': consent == 'analytics',
        'show_cookie_banner': consent not in ('analytics', 'necessary') or bool(request.GET.get('cookie_settings')),
    }
    if not request.headers.get('HX-Request'):  # htmx-фрагмент не должен «съесть» цели
        goals = request.session.pop('pending_goals', None)
        if goals:
            context['pending_goals'] = goals
    return context
