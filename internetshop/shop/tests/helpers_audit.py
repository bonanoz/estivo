"""Общие помощники тестов-контракта audit-fixes (не тестовый модуль)."""
import importlib
import os
import re
from contextlib import contextmanager
from unittest import mock

import shop.utils

# «0 ₽» как отдельная цена: перед нулём нет цифры (иначе это хвост «10 000 ₽»), после — пробелы/nbsp и ₽.
ZERO_PRICE_RE = re.compile(r'(?<!\d)0[\s  ]*₽')

VALID_TOKEN = '123456:TEST-token-for-unit-tests'


def has_zero_price(text):
    """Есть ли в тексте цена «0 ₽» (но не «10 000 ₽»)."""
    return ZERO_PRICE_RE.search(text) is not None


def without_total(text):
    """Текст без фраз «Итого … ₽»: итог заявки из одних позиций «по запросу» может быть 0."""
    return re.sub(r'Итого[\s  ]*[\d\s  ]*₽', '', text)


@contextmanager
def telegram_env(**env):
    """Подменяет BOT_TOKEN/CHAT_ID (None — убрать переменную) и перезагружает ``shop.utils``.

    views импортирует ``notify_telegram`` по имени, но у старого объекта функции те же globals,
    что у модуля, поэтому после reload он видит новую конфигурацию. На выходе переменные
    возвращаются и модуль перезагружается с исходными, чтобы не влиять на остальные тесты.
    """
    try:
        with mock.patch.dict(os.environ):
            for key, value in env.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value
            importlib.reload(shop.utils)
            yield
    finally:
        importlib.reload(shop.utils)


def add_to_cart(client, product, **post):
    from django.urls import reverse
    return client.post(reverse('cart_add', args=[product.id]), post)
