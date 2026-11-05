"""Template tags для общего каркаса (подвал, JSON-LD): данные, которые нельзя достать из текущего контекста."""
import json

from django import template
from django.conf import settings
from django.core.cache import cache
from django.db.models import Avg, Count
from django.urls import reverse
from django.utils.safestring import mark_safe

from shop.context_processors import ADDRESS_CITY, ADDRESS_STREET, SITE_INFO
from shop.models import Product, Review
from shop.storage import THUMB_SIDE, thumb_name

register = template.Library()

FOOTER_CATEGORY_LIMIT = 12
FOOTER_CACHE_SECONDS = 300  # каждый запрос к БД на проде ~25 мс, а подвал есть на каждой странице
# shortcut: родительный падеж материалов — словарь, а не поле модели; новый материал вне словаря даст lower() без склонения.
MATERIAL_GENITIVE = {'ротанг': 'ротанга', 'роуп': 'роупа', 'шпон': 'шпона', 'hpl': 'HPL'}


@register.filter
def material_genitive(name):
    """«Ротанг» -> «ротанга» (для «Кресла из ротанга»)."""
    return MATERIAL_GENITIVE.get(name.lower(), name.lower())


@register.filter
def thumb_url(image, side=THUMB_SIDE):
    """Уменьшенная копия (shop/storage.py кладёт её рядом с каждым .webp); у прочих файлов — сам файл.

    ``{{ img|thumb_url:1200 }}`` — копия с длинной стороной 1200 px (размеры — storage.THUMB_SIDES).
    """
    return image.storage.url(thumb_name(image.name, side)) if image.name.endswith('.webp') else image.url


@register.filter
def absolute(url):
    """Абсолютный URL на основном домене (SITE_URL), а не на том хосте, с которого пришёл запрос.

    Уже абсолютные ссылки (медиа в S3/R2) возвращаются как есть.
    """
    url = str(url)
    return url if url.startswith(('http://', 'https://')) else settings.SITE_URL.rstrip('/') + url


@register.simple_tag
def media_origin():
    """https://<хост бакета> для preconnect: фото (hero — элемент LCP) идут с другого домена."""
    domain = getattr(settings, 'AWS_S3_CUSTOM_DOMAIN', None)
    return f'https://{domain.split("/")[0]}' if domain else ''


@register.simple_tag
def footer_data():
    """Популярные разделы каталога (SEO-ссылки) и сводка по опубликованным отзывам.

    shortcut: кэш на 5 минут без сброса — новый раздел или отзыв появится в подвале с задержкой;
    если станет мешать, чистить ключ в save() Product/Review.
    """
    return cache.get_or_set('footer_data', _footer_data, FOOTER_CACHE_SECONDS)


def _footer_data():
    stats = Review.objects.filter(is_published=True).aggregate(avg=Avg('rating'), count=Count('id'))
    reviews = {'avg': stats['avg'], 'count': stats['count']} if stats['count'] else None
    return {'categories': catalog_sections(FOOTER_CATEGORY_LIMIT), 'reviews': reviews}


@register.simple_tag
def catalog_sections(limit=None):
    """Разделы «категория из материала» с доступными товарами, в порядке меню."""
    seen = set()
    categories = []
    rows = (
        Product.objects.filter(is_available=True, material__isnull=False, category__isnull=False)
        .order_by('material__order', 'material__name', 'category__order', 'category__name')
        .values_list('material__slug', 'material__name', 'category__slug', 'category__name')
        .distinct()
    )
    for material_slug, material_name, category_slug, category_name in rows:
        key = (material_slug, category_slug)
        if key in seen:
            continue
        seen.add(key)
        categories.append({
            'material_slug': material_slug,
            'category_slug': category_slug,
            'label': f'{category_name} из {material_genitive(material_name)}',
        })
        if len(categories) == limit:
            break
    return categories


@register.simple_tag
def review_stats(reviews):
    """Средняя оценка и число отзывов из queryset опубликованных отзывов (PDP). None, если отзывов нет."""
    stats = reviews.aggregate(avg=Avg('rating'), count=Count('id'))
    return {'avg': stats['avg'], 'count': stats['count']} if stats['count'] else None


DAYS = dict(zip(('Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'),
                ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')))
# Профили бренда для sameAs; WhatsApp и MAX — ссылки на чат, а не страницы компании.
SAME_AS_KEYS = ('instagram', 'telegram', 'vk', 'pinterest')


def _ld(data):
    """<script type="application/ld+json">; «<» экранируется, чтобы текст из админки не закрыл тег."""
    body = json.dumps({'@context': 'https://schema.org', **data}, ensure_ascii=False).replace('<', '\\u003c')
    return mark_safe(f'<script type="application/ld+json">{body}</script>')


def _day_range(days):
    """«Пн-Пт» -> [Monday … Friday], «Сб» -> [Saturday]."""
    names = list(DAYS)
    first, _, last = days.partition('-')
    return [DAYS[d] for d in names[names.index(first):names.index(last or first) + 1]]


@register.simple_tag
def organization_ld(image=None):
    """Карточка компании (FurnitureStore) для поисковиков и ИИ-ответов: адрес, часы, телефон, соцсети."""
    lon, lat = SITE_INFO['map_ll'].split(',')
    data = {
        '@type': 'FurnitureStore',
        'name': SITE_INFO['brand_name'],
        'legalName': SITE_INFO['legal_name'],
        'taxID': SITE_INFO['inn'],
        'url': absolute('/'),
        'telephone': SITE_INFO['phone'],
        'email': SITE_INFO['email'],
        'address': {'@type': 'PostalAddress', 'streetAddress': ADDRESS_STREET, 'addressLocality': ADDRESS_CITY,
                    'addressRegion': 'Самарская область', 'addressCountry': 'RU'},
        'geo': {'@type': 'GeoCoordinates', 'latitude': lat, 'longitude': lon},
        'openingHoursSpecification': [
            {'@type': 'OpeningHoursSpecification', 'dayOfWeek': _day_range(days),
             'opens': hours.split('–')[0], 'closes': hours.split('–')[1]}
            for days, hours in SITE_INFO['work_hours']
        ],
        'areaServed': 'RU',
        'sameAs': [SITE_INFO['social_links'][k] for k in SAME_AS_KEYS],
    }
    if image:
        data['image'] = absolute(image.url)
    return _ld(data)


@register.simple_tag
def breadcrumbs_ld(crumbs):
    """BreadcrumbList из тех же крошек, что видит посетитель; у текущей страницы (url=None) нет item."""
    items = [('Главная', reverse('home'))] + list(crumbs)
    return _ld({'@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': i, 'name': str(label), **({'item': absolute(url)} if url else {})}
        for i, (label, url) in enumerate(items, 1)
    ]})


@register.simple_tag
def faq_ld(items):
    """FAQPage из пар (вопрос, ответ), которые показаны на странице."""
    return _ld({'@type': 'FAQPage', 'mainEntity': [
        {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in items
    ]})


@register.filter
def seo_description(product):
    """Описание для сниппета и JSON-LD из полей товара: в `description` часто прайс комплекта, импортированный с Tilda."""
    lead = product.short_description.strip().rstrip('.')
    if not lead:
        lead = product.name
        if product.material and product.material.name.lower() not in product.name.lower():
            lead += f' из {material_genitive(product.material.name)}'
        lead += ' ручной работы'
        if product.length_cm and product.width_cm and product.height_cm:
            lead += f', {product.length_cm}×{product.width_cm}×{product.height_cm} см'
    price = f'Цена от {product.price:,} ₽'.replace(',', ' ') if product.price else 'Цена по запросу'
    return (f'{lead}. {price}, гарантия {SITE_INFO["warranty"]}, '
            f'изготовление {SITE_INFO["production_term"]}, доставка по России.')
