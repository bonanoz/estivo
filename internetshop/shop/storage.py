"""Хранилища media, которые при сохранении ужимают фото в WebP и кладут рядом миниатюру для карточек.

Сжатие стоит на уровне storage, а не модели: так его проходят все пути записи — админка,
``FieldFile.save()`` (импорт с Tilda), ``ContentFile`` в ``objects.create`` и ``compress_media``.
Не-картинки (.glb), SVG и анимированные GIF сохраняются как есть.

Инвариант для шаблонов: у каждого ``*.webp`` есть миниатюра ``thumb_name(name)`` — поэтому фильтр
``thumb_url`` строит её адрес без обращения к хранилищу.
"""
import io
import mimetypes
import os

from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from PIL import Image, ImageOps, UnidentifiedImageError
from storages.backends.s3 import S3Storage

# Без этого на части систем (Windows) guess_type('.webp') → None, и S3 сохраняет фото как octet-stream.
mimetypes.add_type('image/webp', '.webp')

MAX_SIDE = 2000  # hero на всю ширину ретина-экрана
THUMB_SIDE = 640  # карточка ≤ 275 CSS px на десктопе (×2 ретина) и ~170 px на телефоне (×3); ~40 КБ
WEBP_QUALITY = 80


def thumb_name(name):
    return f'{os.path.splitext(name)[0]}.w{THUMB_SIDE}.webp'


def _open(content):
    """Открытая картинка или None (не картинка, битый файл, анимация)."""
    content.seek(0)
    try:
        img = Image.open(content)
        img.load()
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError):
        return None
    finally:
        content.seek(0)
    return None if getattr(img, 'is_animated', False) else img


def _to_webp(img, side):
    icc = img.info.get('icc_profile')
    has_alpha = img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info)
    img = ImageOps.exif_transpose(img).convert('RGBA' if has_alpha else 'RGB')  # фото с телефона не лягут на бок
    img.thumbnail((side, side), Image.LANCZOS)
    out = io.BytesIO()
    img.save(out, 'WEBP', quality=WEBP_QUALITY, method=6, icc_profile=icc)
    return out.getvalue()


def compress_image(content):
    """Байты WebP (длинная сторона ≤ MAX_SIDE) или None, если файл не картинка или сжимать незачем."""
    img = _open(content)
    if img is None or (img.format == 'WEBP' and max(img.size) <= MAX_SIDE):
        return None
    data = _to_webp(img, MAX_SIDE)
    return data if len(data) < content.size else None  # мелкая иконка в WebP может выйти тяжелее


def make_thumb(content):
    img = _open(content)
    return None if img is None else _to_webp(img, THUMB_SIDE)


class CompressImagesMixin:
    def save(self, name, content, max_length=None):
        data = compress_image(content)
        if data is not None:
            name = os.path.splitext(name)[0] + '.webp'
            content = ContentFile(data)
        thumb = make_thumb(content)  # до записи: FileSystemStorage перемещает временный файл загрузки
        name = super().save(name, content, max_length=max_length)
        if name.endswith('.webp') and thumb is not None:
            self.save_thumb(name, thumb)
        return name

    def save_thumb(self, name, data):
        """Записать миниатюру для `name` в обход сжатия (иначе появилась бы миниатюра миниатюры)."""
        self.delete(thumb_name(name))  # иначе при совпадении имени storage подставил бы суффикс
        super().save(thumb_name(name), ContentFile(data))


class CompressedFileSystemStorage(CompressImagesMixin, FileSystemStorage):
    pass


class CompressedS3Storage(CompressImagesMixin, S3Storage):
    pass
