"""Избранное на сессии (без аккаунтов): список id товаров в ``request.session``."""

from .models import Product

WISHLIST_SESSION_ID = 'wishlist'


class Wishlist:
    def __init__(self, request):
        self.session = request.session
        ids = self.session.get(WISHLIST_SESSION_ID)
        if not isinstance(ids, list):
            ids = []
        self._ids = [i for i in ids if isinstance(i, int)]

    def __contains__(self, product_id):
        try:
            return int(product_id) in self._ids
        except (TypeError, ValueError):
            return False

    def __len__(self):
        return len(self._ids)

    @property
    def count(self):
        return len(self._ids)

    @property
    def ids(self):
        return set(self._ids)

    def add(self, product_id):
        if product_id not in self._ids:
            self._ids.append(product_id)
            self.save()

    def remove(self, product_id):
        if product_id in self._ids:
            self._ids.remove(product_id)
            self.save()

    def toggle(self, product_id):
        """Переключить товар. Возвращает True, если он теперь в избранном."""
        if product_id in self._ids:
            self.remove(product_id)
            return False
        self.add(product_id)
        return True

    def save(self):
        self.session[WISHLIST_SESSION_ID] = list(self._ids)
        self.session.modified = True

    def products(self):
        """Доступные товары из избранного (удалённые и снятые отфильтрованы),
        в порядке добавления."""
        found = Product.objects.filter(id__in=self._ids, is_available=True).select_related('material', 'category')
        by_id = {p.id: p for p in found}
        return [by_id[i] for i in self._ids if i in by_id]
