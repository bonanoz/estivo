"""Сжатие фото в WebP при сохранении в storage, миниатюры карточек и команда compress_media для уже загруженных."""
import io
import shutil
import tempfile

from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase, override_settings
from PIL import Image

from shop.models import Product
from shop.storage import MAX_SIDE, THUMB_SIDE, thumb_name
from shop.templatetags.shop_tags import thumb_url

from .helpers import make_product


def image_bytes(size=(2400, 1600), fmt='JPEG', mode='RGB', **save_kw):
    img = Image.effect_noise(size, 64).convert(mode)  # шум, чтобы файл был «тяжёлым», как фото
    if mode == 'RGBA':
        img.putalpha(128)  # полностью непрозрачный альфа-канал WebP выбросил бы
    out = io.BytesIO()
    img.save(out, fmt, **save_kw)
    return out.getvalue()


class MediaTestBase(TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        override = override_settings(MEDIA_ROOT=self.tmp)
        override.enable()
        self.addCleanup(override.disable)

    def open_main(self, product):
        product.refresh_from_db()
        product.main_image.open('rb')
        self.addCleanup(product.main_image.close)
        return Image.open(product.main_image)


class MediaCompressTests(MediaTestBase):
    def test_upload_becomes_resized_webp(self):
        p = make_product(main_image=SimpleUploadedFile('big.jpg', image_bytes()))
        self.assertTrue(p.main_image.name.endswith('.webp'), p.main_image.name)
        img = self.open_main(p)
        self.assertEqual(img.format, 'WEBP')
        self.assertEqual(max(img.size), MAX_SIDE)

    def test_webp_has_image_mime_type(self):
        import mimetypes  # S3Storage берёт Content-Type отсюда
        self.assertEqual(mimetypes.guess_type('x.webp')[0], 'image/webp')

    def test_exif_rotation_is_applied(self):
        exif = Image.Exif()
        exif[0x0112] = 6  # Orientation: повернуть на 90° — так пишут фото с телефона
        p = make_product(main_image=SimpleUploadedFile('phone.jpg', image_bytes((3000, 1500), exif=exif)))
        self.assertEqual(self.open_main(p).size, (MAX_SIDE // 2, MAX_SIDE))

    def test_png_keeps_transparency(self):
        p = make_product(main_image=SimpleUploadedFile('logo.png', image_bytes((800, 800), 'PNG', 'RGBA')))
        self.assertEqual(self.open_main(p).mode, 'RGBA')

    def test_non_image_saved_as_is(self):
        p = make_product(model_3d=SimpleUploadedFile('chair.glb', b'glTF' + b'\0' * 100))
        self.assertTrue(p.model_3d.name.endswith('.glb'))

    def test_import_path_file_save_is_compressed(self):
        p = make_product()
        p.main_image.save('tilda.jpg', ContentFile(image_bytes()))  # так пишет import_tilda
        self.assertTrue(p.main_image.name.endswith('.webp'))

    def test_command_recompresses_old_files_and_is_idempotent(self):
        name = FileSystemStorage().save('products/old.jpg', ContentFile(image_bytes()))  # «загружено до сжатия»
        p = make_product()
        Product.objects.filter(pk=p.pk).update(main_image=name)

        out = io.StringIO()
        call_command('compress_media', stdout=out, stderr=io.StringIO())
        self.assertIn('Пережато 1', out.getvalue())
        self.assertEqual(self.open_main(p).format, 'WEBP')
        self.assertTrue(p.main_image.name.startswith('products/'))
        self.assertTrue(FileSystemStorage().exists(name))  # оригинал не удалён

        out = io.StringIO()
        call_command('compress_media', stdout=out, stderr=io.StringIO())
        self.assertIn('Пережато 0', out.getvalue())


class ThumbTests(MediaTestBase):
    """Миниатюры карточек: лежат рядом с каждым .webp, шаблоны берут их через фильтр thumb_url."""

    def test_upload_creates_thumb(self):
        p = make_product(main_image=SimpleUploadedFile('big.jpg', image_bytes()))
        thumb = thumb_name(p.main_image.name)
        with p.main_image.storage.open(thumb) as f:
            self.assertEqual(max(Image.open(f).size), THUMB_SIDE)

    def test_thumb_url_falls_back_to_file_without_thumb(self):
        p = make_product(main_image=SimpleUploadedFile('big.jpg', image_bytes()))
        self.assertTrue(thumb_url(p.main_image).endswith(f'.w{THUMB_SIDE}.webp'))
        name = FileSystemStorage().save('products/old.jpg', ContentFile(b'x'))
        Product.objects.filter(pk=p.pk).update(main_image=name)
        p.refresh_from_db()
        self.assertEqual(thumb_url(p.main_image), p.main_image.url)

    def test_catalog_card_uses_thumb_srcset(self):
        make_product(main_image=SimpleUploadedFile('big.jpg', image_bytes()))
        html = self.client.get('/catalog/').content.decode()
        self.assertRegex(html, rf'srcset="[^"]+\.w{THUMB_SIDE}\.webp {THUMB_SIDE}w,[^"]+\.webp 2000w"')

    def test_command_adds_missing_thumbs_once(self):
        name = FileSystemStorage().save('products/ready.webp', ContentFile(image_bytes(fmt='WEBP')))
        p = make_product()
        Product.objects.filter(pk=p.pk).update(main_image=name)

        out = io.StringIO()
        call_command('compress_media', stdout=out, stderr=io.StringIO())
        self.assertIn('миниатюр дорисовано 1', out.getvalue())
        storage = FileSystemStorage()
        self.assertTrue(storage.exists(thumb_name(name)))
        self.assertFalse(storage.exists(thumb_name(thumb_name(name))))  # не миниатюра миниатюры

        out = io.StringIO()
        call_command('compress_media', stdout=out, stderr=io.StringIO())
        self.assertIn('миниатюр дорисовано 0', out.getvalue())
