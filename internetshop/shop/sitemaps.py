from urllib.parse import urlsplit

from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Product


class SiteUrlSitemap(Sitemap):
    """<loc> на основном домене (SITE_URL), а не на хосте запроса (например *.onrender.com)."""

    protocol = urlsplit(settings.SITE_URL).scheme

    def get_domain(self, site=None):
        return urlsplit(settings.SITE_URL).netloc


class ProductSitemap(SiteUrlSitemap):
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return Product.objects.filter(is_available=True)

    def location(self, item):
        return item.get_absolute_url()

    def lastmod(self, item):
        return item.updated_at


class CatalogSitemap(SiteUrlSitemap):
    """Разделы каталога «материал» и «материал + категория» — только с доступными товарами."""

    changefreq = 'weekly'
    priority = 0.7

    def items(self):
        pairs = list(
            Product.objects.filter(is_available=True, material__isnull=False)
            .order_by('material__slug', 'category__slug')
            .values_list('material__slug', 'category__slug').distinct()
        )
        materials = sorted({m for m, _ in pairs})
        return [(m,) for m in materials] + [(m, c) for m, c in pairs if c]

    def location(self, item):
        name = 'catalog_by_material' if len(item) == 1 else 'catalog_by_category'
        return reverse(name, args=item)


class StaticViewSitemap(SiteUrlSitemap):
    changefreq = 'monthly'
    priority = 0.5

    def items(self):
        return [
            'home', 'catalog_list', 'b2b_page', 'designers_page', 'about_page',
            'delivery_payment_page', 'warranty_page', 'faq_page', 'contacts_page', 'privacy_page',
        ]

    def location(self, item):
        return reverse(item)
