from django.db import migrations


def fk_to_m2m(apps, schema_editor):
    Product = apps.get_model('shop', 'Product')
    Through = Product.collections.through
    Through.objects.bulk_create(
        [Through(product_id=pk, collection_id=cid)
         for pk, cid in Product.objects.filter(collection__isnull=False).values_list('pk', 'collection_id')],
        ignore_conflicts=True,
    )


def m2m_to_fk(apps, schema_editor):
    """Обратно у товара остаётся одна коллекция, первая по порядку."""
    Product = apps.get_model('shop', 'Product')
    for product in Product.objects.filter(collections__isnull=False).distinct():
        product.collection = product.collections.order_by('order', 'name').first()
        product.save(update_fields=['collection'])


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0015_zone_tabletop_variant'),
    ]

    operations = [
        migrations.RunPython(fk_to_m2m, m2m_to_fk),
    ]
