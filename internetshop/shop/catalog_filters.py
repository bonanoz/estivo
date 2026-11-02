"""Фильтры и сортировка каталога по GET-параметрам.

Всё чистые функции над queryset: невалидные значения молча игнорируются
(страница никогда не падает из-за мусора в URL).
"""

from django.db.models import Case, F, IntegerField, Q, Value, When

from .models import Category, ColorOption, Material

FLAGS = ('new', 'bestseller', 'sale')

SORT_RECOMMENDED = 'recommended'
# Товары «по запросу» (price=0) уходят в конец при сортировке по цене в обе стороны.
_PRICE_ON_REQUEST_LAST = Case(When(price=0, then=Value(1)), default=Value(0), output_field=IntegerField())
SORT_ORDERINGS = {
    'price_asc': (_PRICE_ON_REQUEST_LAST, 'price', 'id'),
    'price_desc': (_PRICE_ON_REQUEST_LAST, '-price', 'id'),
    'new': ('-is_new', '-id'),
}
SORT_CHOICES = [
    (SORT_RECOMMENDED, 'Рекомендуемые'),
    ('price_asc', 'Сначала дешевле'),
    ('price_desc', 'Сначала дороже'),
    ('new', 'Новинки'),
]


def _int(value):
    try:
        number = int(str(value).strip())
    except (TypeError, ValueError):
        return None
    return number if number >= 0 else None


def _int_list(values):
    result = []
    for value in values:
        number = _int(value)
        if number is not None and number not in result:
            result.append(number)
    return result


def apply_filters(queryset, params, skip=()):
    """Применить фильтры из ``params`` (QueryDict) к ``queryset``.

    Возвращает ``(queryset, active_filters)``, где ``active_filters`` — словарь
    только реально применённых значений (для подсветки в форме фильтров).
    ``skip`` — имена параметров, которые не применять (например ``material``
    на странице, где материал уже задан путём URL).
    Несколько значений одного параметра объединяются через OR.
    """
    active = {}

    if 'material' not in skip:
        slugs = [s for s in params.getlist('material') if s]
        valid = list(Material.objects.filter(slug__in=slugs).values_list('slug', flat=True))
        if valid:
            queryset = queryset.filter(material__slug__in=valid)
            active['material'] = valid

    if 'category' not in skip:
        slugs = [s for s in params.getlist('category') if s]
        valid = list(Category.objects.filter(slug__in=slugs).values_list('slug', flat=True))
        if valid:
            queryset = queryset.filter(category__slug__in=valid)
            active['category'] = valid

    color_ids = _int_list(params.getlist('color'))
    if color_ids:
        valid_ids = list(ColorOption.objects.filter(id__in=color_ids).values_list('id', flat=True))
        if valid_ids:
            queryset = queryset.filter(available_colors__id__in=valid_ids).distinct()
            active['color'] = valid_ids

    for field, column in (('price', 'price'), ('length', 'length_cm')):
        low = _int(params.get(f'{field}_min'))
        high = _int(params.get(f'{field}_max'))
        if field == 'price' and (low is not None or high is not None):
            queryset = queryset.filter(price__gt=0)  # «по запросу» не попадает ни в какие границы цены
        if low is not None:
            queryset = queryset.filter(**{f'{column}__gte': low})
            active[f'{field}_min'] = low
        if high is not None:
            queryset = queryset.filter(**{f'{column}__lte': high})
            active[f'{field}_max'] = high

    flags = []
    for flag in params.getlist('flag'):
        if flag in FLAGS and flag not in flags:
            flags.append(flag)
    if flags:
        condition = Q()
        if 'new' in flags:
            condition |= Q(is_new=True)
        if 'bestseller' in flags:
            condition |= Q(is_bestseller=True)
        if 'sale' in flags:
            condition |= Q(old_price__gt=F('price'))
        queryset = queryset.filter(condition)
        active['flag'] = flags

    return queryset, active


def apply_sort(queryset, params):
    """Сортировка по ``?sort=``; неизвестное значение — порядок модели по умолчанию.

    Возвращает ``(queryset, current_sort)``.
    """
    sort = params.get('sort', '')
    ordering = SORT_ORDERINGS.get(sort)
    if ordering:
        return queryset.order_by(*ordering), sort
    return queryset, SORT_RECOMMENDED
