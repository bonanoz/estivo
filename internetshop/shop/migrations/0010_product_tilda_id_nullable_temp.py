from django.db import migrations, models


def fill_temp_forward(apps, schema_editor):
    # Диапазон -50/+50 известен только для ротанга; остальным температура не задана.
    Product = apps.get_model('shop', 'Product')
    Product.objects.filter(material__slug='rotang').update(temp_min_c=-50, temp_max_c=50)
    Product.objects.exclude(material__slug='rotang').update(temp_min_c=None, temp_max_c=None)


def fill_temp_reverse(apps, schema_editor):
    # Возврат к прежним значениям по умолчанию перед возвратом NOT NULL.
    Product = apps.get_model('shop', 'Product')
    Product.objects.filter(temp_min_c__isnull=True).update(temp_min_c=-70)
    Product.objects.filter(temp_max_c__isnull=True).update(temp_max_c=70)


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0009_product_offer_ends_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='tilda_id',
            field=models.BigIntegerField(blank=True, null=True, unique=True, verbose_name='ID товара в Tilda'),
        ),
        migrations.AlterField(
            model_name='product',
            name='temp_min_c',
            field=models.IntegerField(blank=True, null=True, verbose_name='Мин. температура эксплуатации, °C'),
        ),
        migrations.AlterField(
            model_name='product',
            name='temp_max_c',
            field=models.IntegerField(blank=True, null=True, verbose_name='Макс. температура эксплуатации, °C'),
        ),
        # После AlterField: при откате выполнится до возврата NOT NULL.
        migrations.RunPython(fill_temp_forward, fill_temp_reverse),
    ]
