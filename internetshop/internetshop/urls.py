"""
URL configuration for internetshop project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import os

from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.templatetags.static import static as static_url
from django.views.generic import TemplateView

from shop.sitemaps import CatalogSitemap, ProductSitemap, StaticViewSitemap
from shop.views import FAQ_ITEMS

sitemaps = {
    'products': ProductSitemap,
    'catalog': CatalogSitemap,
    'static': StaticViewSitemap,
}

urlpatterns = [
    path('', include('shop.urls')),
    path((os.environ.get('ADMIN_URL') or 'admin/'), admin.site.urls),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
    # Боты и старые браузеры спрашивают /favicon.ico, не читая <link rel="icon">; 302 — имя файла хешируется при collectstatic.
    path('favicon.ico', lambda request: redirect(static_url('img/favicon.svg'))),
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    # Выжимка о компании для ИИ-ассистентов (llmstxt.org)
    path('llms.txt', TemplateView.as_view(template_name='llms.txt', content_type='text/plain; charset=utf-8',
                                          extra_context={'faq_items': FAQ_ITEMS})),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) \
  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'shop.views.handler404'
