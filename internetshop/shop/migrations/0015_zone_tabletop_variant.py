import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0014_slug_blank'),
    ]

    operations = [
        migrations.CreateModel(
            name='Zone',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, verbose_name='Название')),
                ('slug', models.SlugField(blank=True, max_length=64, unique=True)),
                ('order', models.IntegerField(default=0, verbose_name='Порядок')),
            ],
            options={
                'verbose_name': 'Зона',
                'verbose_name_plural': 'Зоны',
                'ordering': ['order', 'name'],
            },
        ),
        migrations.CreateModel(
            name='TabletopType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, verbose_name='Название')),
                ('order', models.IntegerField(default=0, verbose_name='Порядок')),
            ],
            options={
                'verbose_name': 'Вид столешницы',
                'verbose_name_plural': 'Виды столешниц',
                'ordering': ['order', 'name'],
            },
        ),
        migrations.AddField(
            model_name='product',
            name='zone',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='products', to='shop.zone', verbose_name='Зона'),
        ),
        # Временный related_name: старое поле collection ещё занимает 'products' у Collection.
        migrations.AddField(
            model_name='product',
            name='collections',
            field=models.ManyToManyField(blank=True, related_name='products_m2m', to='shop.collection', verbose_name='Коллекции'),
        ),
        migrations.CreateModel(
            name='ProductVariant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('size', models.CharField(help_text='Например: 160×90 см или Ø 55 см', max_length=64, verbose_name='Размер')),
                ('price', models.IntegerField(validators=[django.core.validators.MinValueValidator(1)], verbose_name='Цена, ₽')),
                ('order', models.IntegerField(default=0, verbose_name='Порядок')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='variants', to='shop.product')),
                ('tabletop', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='variants', to='shop.tabletoptype', verbose_name='Столешница')),
            ],
            options={
                'verbose_name': 'Вариант',
                'verbose_name_plural': 'Варианты',
                'ordering': ['order', 'price'],
                'constraints': [
                    models.UniqueConstraint(fields=('product', 'size', 'tabletop'), name='uniq_variant_product_size_top'),
                    models.UniqueConstraint(condition=models.Q(('tabletop__isnull', True)), fields=('product', 'size'), name='uniq_variant_product_size_no_top'),
                ],
            },
        ),
    ]
