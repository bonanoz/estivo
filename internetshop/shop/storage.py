"""Хранилища media, которые при сохранении ужимают фото в WebP и кладут рядом уменьшенные копии (THUMB_SIDES).

Сжатие стоит на уровне storage, а не модели: так его проходят все пути записи — админка,
``FieldFile.save()`` (импорт с Tilda), ``ContentFile`` в ``objects.create`` и ``compress_media``.
Не-картинки (.glb), SVG и анимированные GIF сохраняются как есть.

Инвариант для шаблонов: у каждого ``*.webp`` есть копии ``thumb_name(name, side)`` всех размеров — поэтому фильтр
``thumb_url`` строит их адреса без обращения к хранилищу. Новый размер появляется у старых фото после
``compress_media`` (её запускает build.sh до переключения трафика на новую версию).
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
THUMB_SIDE = 640  # карточка ≤ 275 CSS px на десктопе (×2 ретина); ~40 КБ
# 400 — карточка в две колонки на телефоне; 1200 — главное фото товара (до 840 CSS px) вместо оригинала 2000
THUMB_SIDES = (400, THUMB_SIDE, 1200)
WEBP_QUALITY = 80
MAX_PIXELS = 50_000_000  # ~150 МБ в памяти при декодировании; больше — сохраняем как есть, не пережимая


def thumb_name(name, side=THUMB_SIDE):
    return f'{os.path.splitext(name)[0]}.w{side}.webp'


def _open(content):
    """Открытая картинка или None (не картинка, битый файл, анимация)."""
    content.seek(0)
    try:
        img = Image.open(content)
        if img.width * img.height > MAX_PIXELS:
            return None
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


def make_thumbs(content):
    """{сторона: байты WebP} для всех THUMB_SIDES; пусто, если файл не картинка."""
    img = _open(content)
    return {} if img is None else {side: _to_webp(img, side) for side in THUMB_SIDES}


class CompressImagesMixin:
    def save(self, name, content, max_length=None):
        data = compress_image(content)
        if data is not None:
            name = os.path.splitext(name)[0] + '.webp'
            content = ContentFile(data)
        thumbs = make_thumbs(content)  # до записи: FileSystemStorage перемещает временный файл загрузки
        name = super().save(name, content, max_length=max_length)
        if name.endswith('.webp'):
            for side, data in thumbs.items():
                self.save_thumb(name, data, side)
        return name

    def save_thumb(self, name, data, side=THUMB_SIDE):
        """Записать копию `name` в обход сжатия (иначе появилась бы миниатюра миниатюры)."""
        self.delete(thumb_name(name, side))  # иначе при совпадении имени storage подставил бы суффикс
        super().save(thumb_name(name, side), ContentFile(data))


class CompressedFileSystemStorage(CompressImagesMixin, FileSystemStorage):
    pass


class CompressedS3Storage(CompressImagesMixin, S3Storage):
    pass
