import re

from django.db import migrations

from shop.utils import ru_slugify

ZONES = [('Обеденная группа', 10), ('Лаунж-зона', 20)]
TABLETOPS = [('Стекло', 10), ('HPL compact', 20), ('HPL', 30), ('Шпон', 40), ('ДПК', 50)]
COLLECTIONS = [('Милан', 10), ('Бари', 20), ('Асти', 30)]
DEMO_SLUGS = ['terrasa', 'launzh', 'sad']

DINING, LOUNGE = 'Обеденная группа', 'Лаунж-зона'


def zone_name(category_name, name_words):
    if category_name in ('Столы кофейные', 'Диваны'):
        return LOUNGE
    if category_name == 'Столы обеденные':
        return DINING
    if category_name == 'Кресла':
        if 'барное' in name_words:
            return None
        return LOUNGE if 'лаунж' in name_words else DINING
    return None


def seed_collections(apps, schema_editor):
    Zone = apps.get_model('shop', 'Zone')
    TabletopType = apps.get_model('shop', 'TabletopType')
    Collection = apps.get_model('shop', 'Collection')
    Product = apps.get_model('shop', 'Product')

    zones = {n: Zone.objects.get_or_create(name=n, defaults={'slug': ru_slugify(n), 'order': o})[0]
             for n, o in ZONES}
    for n, o in TABLETOPS:
        TabletopType.objects.get_or_create(name=n, defaults={'order': o})
    collections = {n: Collection.objects.get_or_create(slug=ru_slugify(n), defaults={'name': n, 'order': o})[0]
                   for n, o in COLLECTIONS}
    Collection.objects.filter(slug__in=DEMO_SLUGS).delete()

    # Ротанг — другая линейка, его раскладывает владелец
    for product in Product.objects.select_related('category').exclude(material__name__iexact='Ротанг'):
        name_words = {w.lower() for w in re.findall(r'\w+', product.name)}
        for series, coll in collections.items():
            if series.lower() in name_words:
                product.collections.add(coll)
        if product.zone_id is None and product.category_id:
            zone = zone_name(product.category.name, name_words)
            if zone:
                product.zone = zones[zone]
                product.save(update_fields=['zone'])


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0017_remove_product_collection'),
    ]

    operations = [
        migrations.RunPython(seed_collections, migrations.RunPython.noop),
    ]
