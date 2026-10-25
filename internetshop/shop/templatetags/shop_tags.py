"""Template tags для общего каркаса (подвал): данные, которые нельзя достать из текущего контекста."""
from django import template
from django.conf import settings
from django.core.cache import cache
from django.db.models import Avg, Count

from shop.models import Product, Review
from shop.storage import thumb_name

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
def thumb_url(image):
    """Миниатюра для карточек (shop/storage.py кладёт её рядом с каждым .webp); у прочих файлов — сам файл."""
    return image.storage.url(thumb_name(image.name)) if image.name.endswith('.webp') else image.url


@register.filter
def absolute(url):
    """Абсолютный URL на основном домене (SITE_URL), а не на том хосте, с которого пришёл запрос.

    Уже абсолютные ссылки (медиа в S3/R2) возвращаются как есть.
    """
    url = str(url)
    return url if url.startswith(('http://', 'https://')) else settings.SITE_URL.rstrip('/') + url


@register.simple_tag
def footer_data():
    """Популярные разделы каталога (SEO-ссылки) и сводка по опубликованным отзывам.

    shortcut: кэш на 5 минут без сброса — новый раздел или отзыв появится в подвале с задержкой;
    если станет мешать, чистить ключ в save() Product/Review.
    """
    return cache.get_or_set('footer_data', _footer_data, FOOTER_CACHE_SECONDS)


def _footer_data():
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
        if len(categories) >= FOOTER_CATEGORY_LIMIT:
            break

    stats = Review.objects.filter(is_published=True).aggregate(avg=Avg('rating'), count=Count('id'))
    reviews = {'avg': stats['avg'], 'count': stats['count']} if stats['count'] else None
    return {'categories': categories, 'reviews': reviews}


@register.simple_tag
def review_stats(reviews):
    """Средняя оценка и число отзывов из queryset опубликованных отзывов (PDP). None, если отзывов нет."""
    stats = reviews.aggregate(avg=Avg('rating'), count=Count('id'))
    return {'avg': stats['avg'], 'count': stats['count']} if stats['count'] else None
