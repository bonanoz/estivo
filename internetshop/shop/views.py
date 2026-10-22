from django.contrib import messages
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import F, Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_GET, require_POST

from .cart import Cart
from .catalog_filters import SORT_CHOICES, apply_filters, apply_sort
from .forms import LeadForm, OrderForm, ReviewForm
from .models import Category, Collection, ColorOption, Material, OrderItem, Product, Review
from .utils import notify_telegram
from .wishlist import Wishlist

CATALOG_PAGE_SIZE = 24
SUGGEST_LIMIT = 6
# Карточка товара читает цвета и галерею: без prefetch это по запросу на карточку.
CARD_PREFETCH = ('available_colors', 'gallery')
REMOVED_NOTICE_KEY = 'cart_removed_notice'


def _bestsellers(limit=8):
    """Хиты продаж; если не отмечено ни одного — избранные товары."""
    available = Product.objects.filter(is_available=True).prefetch_related(*CARD_PREFETCH)
    products = list(available.filter(is_bestseller=True)[:limit])
    if not products:
        products = list(available.filter(is_featured=True)[:limit])
    return products


def _crumbs(*trail):
    """Хлебные крошки: последняя — текущая страница (без ссылки)."""
    return [(label, None) for label in trail]


def _safe_redirect_target(request, candidate, default):
    """Вернуть ``candidate``, только если это путь этого сайта (``/…``) или http(s)-URL на этот же хост.

    Голые строки вроде ``foo`` отбрасываются: ``redirect()`` принял бы их за имя view.
    Результат всегда путь или абсолютный URL, поэтому вызывающие используют ``HttpResponseRedirect``.
    """
    if candidate:
        is_path = candidate.startswith('/') and not candidate.startswith(('//', '/\\'))
        is_absolute = candidate.startswith(('http://', 'https://'))
        if (is_path or is_absolute) and url_has_allowed_host_and_scheme(
            candidate, allowed_hosts={request.get_host()}, require_https=request.is_secure()
        ):
            return candidate
    return default

PRODUCTION_STEPS = [
    ('Заявка и консультация', 'Обсуждаем задачу, бюджет и сроки — по телефону или на встрече.'),
    ('Поиск или конструирование', 'Подбираем готовое изделие в наличии или проектируем индивидуальный вариант.'),
    ('Плетение мебели', 'Мастера вручную плетут корпус из выбранного материала.'),
    ('Сварка и порошковая окраска', 'Каркас сваривается и окрашивается порошковым методом для равномерного покрытия.'),
    ('Контроль качества', 'Каждое изделие проверяется перед отправкой клиенту.'),
    ('Согласование с клиентом', 'Присылаем фото и видео готового изделия на согласование.'),
    ('Упаковка и брендирование', 'Аккуратно упаковываем изделие для транспортировки.'),
    ('Логистика и доставка', 'Рассчитываем маршрут и доставляем по всей России от 3 дней.'),
]

FAQ_ITEMS = [
    ('Как сделать заказ?', 'Оставьте заявку на сайте или позвоните нам — менеджер уточнит детали и поможет выбрать модель.'),
    ('Какой вес выдерживает плетёная мебель?', 'Конструкция выдерживает нагрузку до 120 кг на одно посадочное место.'),
    ('Для какого климата подходит мебель?', 'Материалы устойчивы к перепадам температур от -70 до +70°C, не боятся влаги и солнца.'),
    ('Из чего изготавливаются каркасы?', 'Каркасы производятся по выбору клиента из тонкостенной стали или алюминия.'),
    ('Как происходит покраска каркасов?', 'Каркасы красятся порошковым методом — это обеспечивает плотное и равномерное покрытие.'),
    ('Из чего изготавливаются мягкие элементы?', 'Используются влагостойкие материалы, безопасные для взрослых и детей, гипоаллергенные.'),
]

HOME_SEGMENTS = [
    {
        'title': 'Для дома',
        'description': 'Мебель для квартиры, частного дома, дачи и летней террасы.',
        'cta_text': 'Смотреть каталог',
        'cta_url_name': 'catalog_list',
    },
    {
        'title': 'Для ресторанов и отелей',
        'description': 'Комплексное оснащение террас, зон отдыха и общественных пространств.',
        'cta_text': 'Условия для бизнеса',
        'cta_url_name': 'b2b_page',
    },
    {
        'title': 'Индивидуальный проект',
        'description': 'Разработаем мебель по вашему эскизу вместе с дизайнером.',
        'cta_text': 'Обсудить проект',
        'cta_url_name': 'designers_page',
    },
]


def _home_catalog_links():
    """Материалы и их категории — только реально существующие сочетания с доступными товарами."""
    pairs = (
        Product.objects.filter(is_available=True, material__isnull=False, category__isnull=False)
        .values_list('material', 'category').distinct()
    )
    by_material = {}
    for material_id, category_id in pairs:
        by_material.setdefault(material_id, set()).add(category_id)
    category_ids = {c for ids in by_material.values() for c in ids}
    categories = {c.id: c for c in Category.objects.filter(id__in=category_ids)}
    return [
        {
            'material': material,
            'categories': sorted((categories[c] for c in by_material[material.id]), key=lambda c: c.name),
        }
        for material in Material.objects.filter(id__in=by_material)
    ]


def home(request):
    collections = Collection.objects.filter(is_featured=True)[:6]
    featured_products = Product.objects.filter(is_featured=True, is_available=True).select_related('material').prefetch_related(*CARD_PREFETCH)[:8]
    reviews = Review.objects.filter(is_published=True).select_related('product')[:6]
    return render(request, 'home.html', {
        'segments': HOME_SEGMENTS,
        'collections': collections,
        'featured_products': featured_products,
        'catalog_links': _home_catalog_links(),
        'faq_items': FAQ_ITEMS,
        'reviews': reviews,
    })


def _paginate_products(request, products):
    paginator = Paginator(products, CATALOG_PAGE_SIZE)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def _catalog_context(request, products, skip=()):
    """Общая часть каталога: фильтры, сортировка, пагинация 24/стр.

    ``querystring`` — GET-параметры без ``page`` (для ссылок пагинации:
    ``?{{ querystring }}&page=N``), чтобы фильтры не терялись при перелистывании.
    """
    products, active_filters = apply_filters(products, request.GET, skip=skip)
    products, current_sort = apply_sort(products, request.GET)
    params = request.GET.copy()
    params.pop('page', None)
    page_obj = _paginate_products(request, products)
    offers = []
    if 'sale' in request.GET.getlist('flag'):
        # Промо-карточки: только скидка с датой окончания не раньше сегодня.
        offers = Product.objects.filter(
            is_available=True, old_price__gt=F('price'), offer_ends_at__gte=timezone.localdate(),
        ).order_by('offer_ends_at')[:3]
    return {
        'offers': offers,
        'page_obj': page_obj,
        'active_filters': active_filters,
        'current_sort': current_sort,
        'sort_choices': SORT_CHOICES,
        'faq_items': FAQ_ITEMS,
        'querystring': params.urlencode(),
        'total_count': page_obj.paginator.count,
        'color_options': ColorOption.objects.all(),
        'bestsellers': _bestsellers(4) if page_obj.paginator.count == 0 else [],
    }


def _search_products(products, search):
    return products.filter(Q(name__icontains=search) | Q(description__icontains=search))


def catalog_list(request):
    products = Product.objects.filter(is_available=True).select_related('material', 'category').prefetch_related(*CARD_PREFETCH)
    search = request.GET.get('search')
    if search:
        products = _search_products(products, search)
    context = _catalog_context(request, products)
    context.update({
        'materials': Material.objects.all(),
        'categories': Category.objects.all(),
        'search': search or '',
        'current_material': None,
        'breadcrumbs': _crumbs('Каталог'),
    })
    return render(request, 'catalog_list.html', context)


@require_GET
def catalog_count(request):
    """Фрагмент с числом товаров под текущие фильтры (живой счётчик панели фильтров)."""
    products = Product.objects.filter(is_available=True)
    search = request.GET.get('search')
    if search:
        products = _search_products(products, search)
    products, _active = apply_filters(products, request.GET)
    return render(request, 'partials/htmx/_catalog_count.html', {'count': products.count()})


@require_GET
def search_suggest(request):
    """Подсказки поиска в шапке: до 6 доступных товаров по названию/артикулу/описанию."""
    q = (request.GET.get('q') or '').strip()
    if len(q) < 2:
        return HttpResponse('')
    products = list(
        Product.objects.filter(is_available=True)
        .filter(Q(name__icontains=q) | Q(sku__icontains=q) | Q(description__icontains=q))
        .select_related('material', 'category')[:SUGGEST_LIMIT]
    )
    context = {'query': q, 'products': products}
    if not products:
        context['recommendations'] = _bestsellers(4)
    return render(request, 'partials/htmx/_search_suggestions.html', context)


def catalog_by_material(request, material_slug):
    material = get_object_or_404(Material, slug=material_slug)
    products = Product.objects.filter(is_available=True, material=material).select_related('material', 'category').prefetch_related(*CARD_PREFETCH)
    context = _catalog_context(request, products, skip=('material',))
    context.update({
        'materials': Material.objects.all(),
        'categories': Category.objects.filter(products__material=material).distinct(),
        'search': '',
        'current_material': material,
        'breadcrumbs': [('Каталог', reverse('catalog_list')), (material.name, None)],
        'meta_title': f'{material.name} — каталог | ESTIVO',
    })
    return render(request, 'catalog_list.html', context)


def catalog_by_category(request, material_slug, category_slug):
    material = get_object_or_404(Material, slug=material_slug)
    category = get_object_or_404(Category, slug=category_slug)
    products = Product.objects.filter(is_available=True, material=material, category=category).select_related('material', 'category').prefetch_related(*CARD_PREFETCH)
    context = _catalog_context(request, products, skip=('material', 'category'))
    context.update({
        'materials': Material.objects.all(),
        'categories': Category.objects.filter(products__material=material).distinct(),
        'search': '',
        'current_material': material,
        'current_category': category,
        'breadcrumbs': [
            ('Каталог', reverse('catalog_list')),
            (material.name, reverse('catalog_by_material', args=[material.slug])),
            (category.name, None),
        ],
        'meta_title': f'{category.name} из {material.name.lower()} | ESTIVO',
        'meta_description': f'{category.name} из {material.name.lower()} ручной работы — ESTIVO. Гарантия 3 года, доставка по России от 3 дней.',
    })
    return render(request, 'catalog_list.html', context)


def _selected_colors(request, product):
    """Предвыбор цветов из ``?weave=&cushion=&frame=`` — только реально доступные
    товару цвета нужного типа отделки; всё остальное молча игнорируется."""
    available = {c.id: c for c in product.available_colors.all()}
    selected = {}
    for finish_type, _label in ColorOption.FINISH_TYPE_CHOICES:
        try:
            color_id = int(request.GET.get(finish_type))
        except (TypeError, ValueError):
            continue
        color = available.get(color_id)
        if color is not None and color.finish_type == finish_type:
            selected[finish_type] = color_id
    return selected


def _product_context(request, product, review_form=None):
    related_products = (
        Product.objects.filter(is_available=True, category=product.category)
        .exclude(pk=product.pk).prefetch_related(*CARD_PREFETCH)[:4]
    )
    reviews = product.reviews.filter(is_published=True)
    crumbs = [('Каталог', reverse('catalog_list'))]
    if product.material:
        crumbs.append((product.material.name, reverse('catalog_by_material', args=[product.material.slug])))
    crumbs.append((product.name, None))
    return {
        'product': product,
        'related_products': related_products,
        'reviews': reviews,
        'breadcrumbs': crumbs,
        'selected_colors': _selected_colors(request, product),
        'review_form': review_form or ReviewForm(),
    }


def product_detail(request, slug):
    product = get_object_or_404(Product.objects.select_related('material', 'category'), slug=slug)
    return render(request, 'product_detail.html', _product_context(request, product))


@require_POST
def review_create(request, slug):
    """Отзыв с PDP: сохраняется неопубликованным, без Telegram-уведомления."""
    product = get_object_or_404(Product.objects.select_related('material', 'category'), slug=slug)
    form = ReviewForm(request.POST)
    if form.is_valid():
        if not form.is_spam:
            review = form.save(commit=False)
            review.product = product
            review.is_published = False
            review.save()
        # Бот с заполненным honeypot получает тот же ответ, что и человек.
        if request.htmx:
            return render(request, 'partials/htmx/_review_success.html', {'product': product})
        messages.success(request, 'Спасибо! Отзыв отправлен на модерацию.')
        return redirect(product.get_absolute_url())
    if request.htmx:
        return render(request, 'partials/htmx/_review_form.html', {'product': product, 'review_form': form})
    return render(request, 'product_detail.html', _product_context(request, product, review_form=form))


def _lead_page(request, template_name, lead_type, extra_context=None):
    # «Узнать цену»: слаг товара приходит скрытым полем (POST) или ?product= (GET-предзаполнение).
    price_slug = request.POST.get('price_request_for') or request.GET.get('product')
    price_product = Product.objects.filter(slug=price_slug).first() if price_slug else None
    if request.method == 'POST':
        form = LeadForm(request.POST)
        if form.is_valid() and form.is_spam:
            messages.success(request, 'Заявка отправлена! Мы свяжемся с вами в ближайшее время.')
            return redirect(request.path)
        if form.is_valid():
            lead = form.save(commit=False)
            lead.source_page = template_name
            if price_product:
                lead.source_page = f'price-request:{price_product.slug}'
                lead.message = f'Узнать цену: {price_product.name}\n{lead.message}'.strip()
            lead.save()
            sent = notify_telegram(
                f'📩 Новая заявка ({lead.get_lead_type_display()})\n'
                f'Имя: {lead.name}\nТелефон: {lead.phone}\nEmail: {lead.email}\n'
                f'Сообщение: {lead.message}'
            )
            if sent:
                lead.telegram_notified = True
                lead.save(update_fields=['telegram_notified'])
            messages.success(request, 'Заявка отправлена! Мы свяжемся с вами в ближайшее время.')
            return redirect(request.path)
    else:
        initial = {'lead_type': lead_type}
        if price_product:
            initial['message'] = f'Узнать цену: {price_product.name}'
        form = LeadForm(initial=initial)

    context = {'form': form, 'price_product': price_product}
    if extra_context:
        context.update(extra_context)
    return render(request, template_name, context)


def b2b_page(request):
    return _lead_page(request, 'b2b.html', 'b2b', {'breadcrumbs': _crumbs('Для бизнеса')})


def designers_page(request):
    return _lead_page(request, 'designers.html', 'designer', {'breadcrumbs': _crumbs('Дизайнерам')})


def about_page(request):
    return render(request, 'about.html', {
        'breadcrumbs': _crumbs('О нас'),
        'materials': Material.objects.all(),
        'production_steps': PRODUCTION_STEPS,
    })


def delivery_payment_page(request):
    return render(request, 'delivery_payment.html', {'breadcrumbs': _crumbs('Доставка и оплата')})


def warranty_page(request):
    return render(request, 'warranty.html', {'breadcrumbs': _crumbs('Гарантия')})


def faq_page(request):
    return render(request, 'faq.html', {'faq_items': FAQ_ITEMS, 'breadcrumbs': _crumbs('Вопросы и ответы')})


def contacts_page(request):
    return _lead_page(request, 'contacts.html', 'private', {'breadcrumbs': _crumbs('Контакты')})


def _parse_colors(request, product):
    """Считать выбранные цвета из POST и провалидировать по available_colors.

    Возвращает ``{finish_type: color_id}`` только для цветов, реально
    привязанных к товару, — подмену чужого color_id из формы отсекаем.
    """
    available = {c.id: c for c in product.available_colors.all()}
    colors = {}
    for finish_type, _label in ColorOption.FINISH_TYPE_CHOICES:
        raw = request.POST.get(f'color_{finish_type}')
        if not raw:
            continue
        try:
            color_id = int(raw)
        except (TypeError, ValueError):
            continue
        color = available.get(color_id)
        if color is not None and color.finish_type == finish_type:
            colors[finish_type] = color_id
    return colors


@require_POST
def cart_add(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_available=True)
    if not product.price:
        # Цена по запросу: в заявку не кладём, ведём на форму «Узнать цену».
        url = f"{reverse('contacts_page')}?product={product.slug}"
        if request.htmx:
            response = HttpResponse(status=204)
            response['HX-Redirect'] = url
            return response
        return redirect(url)
    colors = _parse_colors(request, product)
    try:
        quantity = max(1, int(request.POST.get('quantity', 1)))
    except (TypeError, ValueError):
        quantity = 1
    cart = Cart(request)
    cart.add(product, colors=colors, quantity=quantity)
    if request.htmx and 'checkout' not in request.POST:
        recommendations = (
            Product.objects.filter(is_available=True, category=product.category)
            .exclude(pk=product.pk)[:4]
            if product.category_id else []
        )
        return render(request, 'partials/htmx/_cart_drawer.html', {
            'added_product': product,
            'recommendations': recommendations,
        })
    if 'checkout' in request.POST:
        if request.htmx:
            response = HttpResponse(status=204)
            response['HX-Redirect'] = reverse('checkout')
            return response
        return redirect('checkout')
    return HttpResponseRedirect(_safe_redirect_target(request, request.POST.get('next'), reverse('cart_detail')))


def _cart_lines_response(request, removed=None):
    """HTMX-ответ для cart_update/cart_remove: свежие строки корзины и итог."""
    return render(request, 'partials/htmx/_cart_lines.html', {'removed': removed})


@require_POST
def cart_update(request):
    line_id = request.POST.get('line_id')
    try:
        quantity = int(request.POST.get('quantity', 1))
    except (TypeError, ValueError):
        quantity = 1
    cart = Cart(request)
    removed = None
    if quantity <= 0:
        removed = _removed_info(cart, line_id)
        cart.stash_removed(line_id)
    cart.set_quantity(line_id, quantity)
    if request.htmx:
        return _cart_lines_response(request, removed)
    if removed:
        request.session[REMOVED_NOTICE_KEY] = removed['name']
    return redirect('cart_detail')


def _removed_info(cart, line_id):
    """Название товара удаляемой позиции — для тоста «… удалён · Вернуть»."""
    for item in cart:
        if item['line_id'] == line_id:
            return {'name': item['product'].name}
    return None


@require_POST
def cart_remove(request):
    cart = Cart(request)
    line_id = request.POST.get('line_id')
    removed = _removed_info(cart, line_id)
    cart.stash_removed(line_id)
    cart.remove(line_id)
    if request.htmx:
        return _cart_lines_response(request, removed)
    if removed:
        request.session[REMOVED_NOTICE_KEY] = removed['name']
    return redirect('cart_detail')


@require_POST
def cart_undo(request):
    """Вернуть последнюю удалённую из корзины позицию."""
    Cart(request).undo_remove()
    if request.htmx:
        return _cart_lines_response(request)
    return redirect('cart_detail')


@require_POST
def wishlist_toggle(request, product_id):
    wishlist = Wishlist(request)
    product = get_object_or_404(Product, id=product_id)
    if not product.is_available and product.id not in wishlist:
        return HttpResponse(status=404)
    wishlist.toggle(product.id)
    if request.htmx:
        return render(request, 'partials/htmx/_wishlist_toggle.html', {
            'product': product,
            'wishlist': wishlist,
            'in_wishlist': product.id in wishlist,
        })
    return HttpResponseRedirect(_safe_redirect_target(request, request.META.get('HTTP_REFERER'), reverse('wishlist')))


def wishlist_page(request):
    return render(request, 'wishlist.html', {'products': Wishlist(request).products(), 'breadcrumbs': _crumbs('Избранное')})


def cart_detail(request):
    # Для пустого состояния корзины: подборка хитов
    bestsellers = _bestsellers(4) if Cart(request).is_empty else []
    # Откат удаления без JS: имя удалённой позиции кладут в сессию cart_remove/cart_update.
    removed_name = request.session.pop(REMOVED_NOTICE_KEY, None)
    removed = {'name': removed_name} if removed_name else None
    return render(request, 'cart.html', {
        'bestsellers': bestsellers,
        'breadcrumbs': _crumbs('Корзина'),
        'removed': removed,
    })


def checkout(request):
    cart = Cart(request)
    if cart.is_empty:
        return redirect('cart_detail')

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            if form.is_spam:
                # Бот получает тот же ответ, что и человек, но заявка не создаётся.
                cart.clear()
                return redirect('order_success')
            items = list(cart)
            with transaction.atomic():
                order = form.save()
                for item in items:
                    OrderItem.objects.create(
                        order=order,
                        product=item['product'],
                        quantity=item['quantity'],
                        unit_price=item['unit_price'],
                        selected_colors=dict(item['colors_display']),
                    )
                order.recalc_total()
            # Чистим до Telegram: если отправка зависнет и воркер убьют, повторная отправка не создаст дубль.
            cart.clear()

            lines = []
            for item in items:
                colors_str = ', '.join(f'{label}: {name}' for label, name in item['colors_display'])
                suffix = f' ({colors_str})' if colors_str else ''
                lines.append(
                    f'• {item["product"].name} × {item["quantity"]} — {item["line_total"]} ₽{suffix}'
                )
            sent = notify_telegram(
                '🛒 Новая заявка из корзины\n'
                + '\n'.join(lines)
                + f'\n\nИтого: {order.total_price} ₽\n'
                + f'ФИО: {order.customer_name}\nТелефон: {order.customer_phone}\n'
                + f'Email: {order.customer_email}\nАдрес доставки: {order.delivery_address}\n'
                + f'Комментарий: {order.comment}'
            )
            if sent:
                order.telegram_notified = True
                order.save(update_fields=['telegram_notified'])
            return redirect('order_success')
    else:
        form = OrderForm()

    return render(request, 'checkout.html', {'form': form})


def order_success(request):
    return render(request, 'order_success.html')


def handler404(request, exception=None):
    return render(request, '404.html', {'bestsellers': _bestsellers(8)}, status=404)
