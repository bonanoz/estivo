"""Помощники тестов коллекций и вариантов (не тестовый модуль).

Новые модели берутся через ``shop.models`` в момент вызова, а не при импорте:
пока реализации нет, падает каждый тест по отдельности (AttributeError), а не весь файл.
Справочники — get_or_create: data-миграция уже создала Милан/Бари/Асти и зоны в тестовой базе.
"""
from shop import models as m
from shop.models import Category, Material

from .helpers import make_product

# (размер, столешница или None, цена) — порядок как в схеме владельца
TABLE_VARIANTS = [
    ('80×80 см', 'HPL compact', 29900),
    ('160×90 см', 'Стекло', 54900),
    ('160×90 см', 'HPL compact', 44900),
]


def collection(name, order=0, **kw):
    obj, _ = m.Collection.objects.get_or_create(name=name)
    obj.order = order
    for key, value in kw.items():
        setattr(obj, key, value)
    obj.save()
    return obj


def zone(name, order=0):
    obj, _ = m.Zone.objects.get_or_create(name=name)
    obj.order = order
    obj.save()
    return obj


def tabletop(name):
    obj, _ = m.TabletopType.objects.get_or_create(name=name)
    return obj


def category(name, order=0):
    obj, _ = Category.objects.get_or_create(name=name)
    obj.order = order
    obj.save()
    return obj


def material(name='Роуп'):
    obj, _ = Material.objects.get_or_create(name=name)
    return obj


def add_variants(product, variants=TABLE_VARIANTS):
    """Создаёт варианты с order = индекс в списке; возвращает их в том же порядке."""
    result = []
    for i, (size, top, price) in enumerate(variants):
        result.append(m.ProductVariant.objects.create(
            product=product, size=size, tabletop=tabletop(top) if top else None, price=price, order=i))
    return result


def product_in(collections=(), zone_obj=None, variants=None, **kw):
    """Товар в коллекциях/зоне, при необходимости с вариантами."""
    if zone_obj is not None:
        kw['zone'] = zone_obj
    product = make_product(**kw)
    if collections:
        product.collections.set(collections)
    if variants:
        add_variants(product, variants)
        product.refresh_from_db()
    return product


def card_paths(root):
    """Пути товаров по порядку карточек на странице: [(заголовок раздела или None, [пути])]."""
    from .helpers import norm_space, product_hrefs
    result = []
    for node in root.iter():
        if node.tag in ('h2', 'h3'):
            result.append((norm_space(node.text), []))
        elif node.has_class('product-card') and result:
            result[-1][1].extend(sorted(product_hrefs(node)))
    return result
