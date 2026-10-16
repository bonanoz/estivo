"""Template tags для общего каркаса (подвал): данные, которые нельзя достать из текущего контекста."""
from django import template
from django.db.models import Avg, Count

from shop.models import Product, Review

register = template.Library()

FOOTER_CATEGORY_LIMIT = 12


@register.simple_tag
def footer_data():
    """Популярные разделы каталога (SEO-ссылки) и сводка по опубликованным отзывам."""
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
            'label': f'{category_name} из {material_name.lower()}',
        })
        if len(categories) >= FOOTER_CATEGORY_LIMIT:
            break

    stats = Review.objects.filter(is_published=True).aggregate(avg=Avg('rating'), count=Count('id'))
    reviews = {'avg': stats['avg'], 'count': stats['count']} if stats['count'] else None
    return {'categories': categories, 'reviews': reviews}
