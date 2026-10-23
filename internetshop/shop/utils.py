import os
import re
from functools import wraps

import telebot
from django.core.cache import cache
from django.http import HttpResponse
from django.utils.text import slugify

bot = telebot.TeleBot(os.environ.get('BOT_TOKEN'))
CHAT_ID = os.environ.get('CHAT_ID')
# Отправка идёт внутри запроса: по умолчанию 15+30 с, а gunicorn убивает воркер через 30 с.
telebot.apihelper.CONNECT_TIMEOUT = 3
telebot.apihelper.READ_TIMEOUT = 5
TELEGRAM_MAX_LEN = 4096

PHONE_RE = re.compile(r'^\+?[78][\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}$')

# Транслитерация кириллицы в латиницу для человекочитаемых ASCII-slug
# (URL вида /product/kreslo-kokon/, как на estivo63.ru — /kreslo, /divan).
_TRANSLIT = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e',
    'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
    'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
    'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
    'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
}


def ru_slugify(value):
    """Транслитерирует кириллицу и возвращает ASCII-slug."""
    value = (value or '').lower()
    transliterated = ''.join(_TRANSLIT.get(ch, ch) for ch in value)
    return slugify(transliterated)


def notify_telegram(text):
    """Отправляет сообщение в Telegram-чат менеджера. Не бросает исключений —
    заявка должна сохраняться в БД независимо от доступности Telegram API.
    """
    if len(text) > TELEGRAM_MAX_LEN:  # длиннее Telegram отклоняет целиком; полный текст есть в админке
        text = text[:TELEGRAM_MAX_LEN - 1] + '…'
    try:
        bot.send_message(CHAT_ID, text)
        return True
    except Exception:
        return False


def clean_phone_number(value):
    """Простая проверка на российский номер телефона. Возвращает исходную
    строку без изменений (валидация, не нормализация форматов ввода).
    """
    value = (value or '').strip()
    if not PHONE_RE.match(value):
        raise ValueError('Введите номер телефона в формате +7 XXX XXX-XX-XX')
    return value


def throttle_post(limit=5, window=600):
    """Не больше ``limit`` POST с одного IP за ``window`` секунд; GET не считается.

    shortcut: кэш LocMem — счётчик отдельный у каждого воркера gunicorn; для общего лимита нужен Redis/DB-кэш.
    """
    def decorator(view):
        @wraps(view)
        def wrapper(request, *args, **kwargs):
            if request.method == 'POST':
                # За прокси (Render) настоящий адрес клиента — последний в X-Forwarded-For; первый подделывается.
                ip = (request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[-1].strip()
                      or request.META.get('REMOTE_ADDR', ''))
                key = f'throttle:{view.__name__}:{ip}'
                cache.add(key, 0, window)
                try:
                    count = cache.incr(key)
                except ValueError:
                    count = 1
                if count > limit:
                    return HttpResponse('Слишком много запросов, попробуйте позже.', status=429)
            return view(request, *args, **kwargs)
        return wrapper
    return decorator
