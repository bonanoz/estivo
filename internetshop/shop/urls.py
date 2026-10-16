from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),

    path('catalog/', views.catalog_list, name='catalog_list'),
    # Должен идти ДО catalog/<slug:material_slug>/, иначе slug-маршрут перехватит "count".
    path('catalog/count/', views.catalog_count, name='catalog_count'),
    path('catalog/<slug:material_slug>/', views.catalog_by_material, name='catalog_by_material'),
    path('catalog/<slug:material_slug>/<slug:category_slug>/', views.catalog_by_category, name='catalog_by_category'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('product/<slug:slug>/review/', views.review_create, name='review_create'),
    path('search/suggest/', views.search_suggest, name='search_suggest'),

    path('wishlist/', views.wishlist_page, name='wishlist'),
    path('wishlist/toggle/<int:product_id>/', views.wishlist_toggle, name='wishlist_toggle'),

    path('b2b/', views.b2b_page, name='b2b_page'),
    path('for-designers/', views.designers_page, name='designers_page'),
    path('o-nas/', views.about_page, name='about_page'),
    path('dostavka-i-oplata/', views.delivery_payment_page, name='delivery_payment_page'),
    path('garantiya/', views.warranty_page, name='warranty_page'),
    path('faq/', views.faq_page, name='faq_page'),
    path('kontakty/', views.contacts_page, name='contacts_page'),

    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/update/', views.cart_update, name='cart_update'),
    path('cart/remove/', views.cart_remove, name='cart_remove'),
    path('cart/undo/', views.cart_undo, name='cart_undo'),
    path('cart/checkout/', views.checkout, name='checkout'),
    path('order/success/', views.order_success, name='order_success'),
    path('lead/', views.lead_create, name='lead_create'),
]
