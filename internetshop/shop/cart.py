"""Корзина на сессии.

Регистрации/логина на сайте нет, поэтому корзина живёт в ``request.session``.
Позиция уникальна по комбинации товара и выбранных цветов отделки — один и
тот же товар с разными цветами попадает в корзину как две отдельные позиции.
"""

from .models import ColorOption, Product

CART_SESSION_ID = 'cart'
CART_UNDO_SESSION_ID = 'cart_undo'
# Предел на позицию: огромное число переполняет integer-колонки и роняет checkout.
MAX_QUANTITY = 99


def _clamp(quantity):
    return min(quantity, MAX_QUANTITY)


def _line_id(product_id, colors):
    """Детерминированный ключ позиции: товар + выбранные цвета.

    Один товар с одинаковым набором цветов всегда даёт один ключ (повторное
    добавление увеличивает количество), а другой набор цветов — новую позицию.
    """
    parts = [f'{ft}={cid}' for ft, cid in sorted(colors.items())]
    return f'{product_id}:' + '-'.join(parts)


class Cart:
    def __init__(self, request):
        self.session = request.session
        # Только чтение: запись в сессию здесь создавала бы строку django_session на каждый визит (и бота).
        self._cart = self.session.get(CART_SESSION_ID, {})
        self._lines = None

    def add(self, product, colors=None, quantity=1):
        """Добавить товар с выбранными цветами (``{finish_type: color_id}``)."""
        colors = colors or {}
        line_id = _line_id(product.id, colors)
        if line_id in self._cart:
            self._cart[line_id]['quantity'] = _clamp(self._cart[line_id]['quantity'] + quantity)
        else:
            self._cart[line_id] = {
                'product_id': product.id,
                'quantity': _clamp(quantity),
                'colors': colors,
            }
        self.save()
        return line_id

    def set_quantity(self, line_id, quantity):
        if line_id in self._cart:
            if quantity > 0:
                self._cart[line_id]['quantity'] = _clamp(quantity)
            else:
                del self._cart[line_id]
            self.save()

    def remove(self, line_id):
        if line_id in self._cart:
            del self._cart[line_id]
            self.save()

    def stash_removed(self, line_id):
        """Запомнить позицию перед удалением, чтобы её можно было вернуть (undo)."""
        item = self._cart.get(line_id)
        if item is not None:
            self.session[CART_UNDO_SESSION_ID] = {'line_id': line_id, 'item': dict(item)}
            self.session.modified = True

    def undo_remove(self):
        """Вернуть последнюю удалённую позицию. Возвращает line_id или None."""
        stashed = self.session.pop(CART_UNDO_SESSION_ID, None)
        if not stashed:
            return None
        line_id, item = stashed['line_id'], stashed['item']
        if line_id in self._cart:
            self._cart[line_id]['quantity'] = _clamp(self._cart[line_id]['quantity'] + item['quantity'])
        else:
            self._cart[line_id] = item
        self.save()
        return line_id

    def clear(self):
        self._cart = {}
        self.session.pop(CART_UNDO_SESSION_ID, None)
        self.save()

    def save(self):
        self.session[CART_SESSION_ID] = self._cart
        self.session.modified = True
        self._lines = None

    def __iter__(self):
        # Шаблон обходит корзину несколько раз (строки, итог, счётчик) — запросы делаем один раз.
        if self._lines is None:
            self._lines = list(self._load_lines())
        return iter(self._lines)

    def _load_lines(self):
        """Позиции корзины с подгруженными товарами и названиями цветов.

        Позиции с удалённым или снятым с продажи товаром молча пропускаются.
        """
        product_ids = [item['product_id'] for item in self._cart.values()]
        products = Product.objects.in_bulk(product_ids)

        color_ids = set()
        for item in self._cart.values():
            color_ids.update(item.get('colors', {}).values())
        colors = ColorOption.objects.in_bulk(list(color_ids)) if color_ids else {}

        for line_id, item in self._cart.items():
            product = products.get(item['product_id'])
            if product is None or not product.is_available:
                continue
            colors_map = item.get('colors', {})
            colors_display = []
            for finish_type, label in ColorOption.FINISH_TYPE_CHOICES:
                color_id = colors_map.get(finish_type)
                color = colors.get(color_id)
                if color is not None:
                    colors_display.append((label, color.name))
            quantity = item['quantity']
            yield {
                'line_id': line_id,
                'product': product,
                'quantity': quantity,
                'colors': colors_map,
                'colors_display': colors_display,
                'unit_price': product.price,
                'line_total': product.price * quantity,
            }

    def __len__(self):
        # По загруженным строкам: снятые с продажи товары не должны попадать в счётчик шапки.
        return sum(item['quantity'] for item in self)

    @property
    def count(self):
        return len(self)

    @property
    def total_price(self):
        return sum(item['line_total'] for item in self)

    @property
    def is_empty(self):
        return not list(self)
