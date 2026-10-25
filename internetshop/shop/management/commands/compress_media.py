"""Пережимает в WebP фото, загруженные до появления сжатия (shop/storage.py), и дорисовывает миниатюры
карточек тем .webp, у которых их ещё нет.

Запуск: `python manage.py compress_media` (повторный запуск безопасен — готовое пропускается).
Оригиналы в хранилище не удаляются: модель просто начинает ссылаться на новый файл.
"""
import os

from django.apps import apps
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import models

from shop.storage import compress_image, make_thumb, thumb_name


class Command(BaseCommand):
    help = 'Пережать в WebP уже загруженные фото (оригиналы остаются в хранилище)'

    def handle(self, *args, **opts):
        done = thumbs = skipped = failed = before = after = 0
        for model in apps.get_app_config('shop').get_models():
            for field in model._meta.fields:
                if not isinstance(field, models.ImageField):
                    continue
                qs = (model.objects.exclude(**{f'{field.name}__isnull': True})
                      .exclude(**{field.name: ''}))
                for obj in qs.iterator():
                    f = getattr(obj, field.name)
                    try:
                        if f.name.endswith('.webp'):
                            if not f.storage.exists(thumb_name(f.name)):
                                with f.open('rb'):
                                    f.storage.save_thumb(f.name, make_thumb(ContentFile(f.read())))
                                thumbs += 1
                            continue
                        with f.open('rb'):
                            content = ContentFile(f.read())
                        data = compress_image(content)
                        if data is None:
                            skipped += 1
                            continue
                        old = f.name
                        # storage уже готовый WebP не трогает, поэтому расширение меняем сами
                        f.save(os.path.splitext(os.path.basename(old))[0] + '.webp', ContentFile(data), save=False)
                        obj.save(update_fields=[field.name])
                    except Exception as e:  # битый или пропавший файл не должен ронять остальные
                        failed += 1
                        self.stderr.write(f'{model.__name__}#{obj.pk}.{field.name}: {e}')
                        continue
                    done += 1
                    before += content.size
                    after += len(data)
                    self.stdout.write(f'{old} → {f.name}: {content.size // 1024} → {len(data) // 1024} КБ')
        self.stdout.write(self.style.SUCCESS(
            f'Пережато {done}, миниатюр дорисовано {thumbs}, пропущено {skipped}, ошибок {failed}; '
            f'{before / 1048576:.1f} → {after / 1048576:.1f} МБ'))
