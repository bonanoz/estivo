from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0016_collection_fk_to_m2m'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='collection',
        ),
        migrations.AlterField(
            model_name='product',
            name='collections',
            field=models.ManyToManyField(blank=True, related_name='products', to='shop.collection', verbose_name='Коллекции'),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='selected_colors',
            field=models.JSONField(blank=True, default=dict, help_text='Снимок вида {"Размер": "160×90 см", "Столешница": "Стекло", "Плетение": "Графит"}', verbose_name='Выбор покупателя'),
        ),
    ]
