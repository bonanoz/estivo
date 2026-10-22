# ESTIVO

Django-сайт бренда плетёной мебели ручной работы (лидогенерация: корзина-заявка, формы для B2B и дизайнеров,
уведомления в Telegram). Подробности архитектуры и правил: `CLAUDE.md`, дизайн: `docs/design-system/estivo-tilda/`,
`docs/design-system.md`.

## Стек

Django 5.2 (LTS) + PostgreSQL, Tailwind CSS v4 + htmx + Alpine.js + TypeScript (сборка Vite в
`internetshop/frontend/`), whitenoise.

## Запуск

```bash
cd internetshop
python -m venv venv && venv\Scripts\activate     # Windows
pip install -r ../requirements.txt
# создайте internetshop/.env (BOT_TOKEN, CHAT_ID, DB_*, SECRET_KEY, ...) — см. CLAUDE.md
cd frontend && npm ci && npm run build && cd ..
python manage.py migrate
python manage.py seed_demo
python manage.py collectstatic --noinput
python manage.py runserver
```

Для разработки фронтенда: `npm run dev` в `internetshop/frontend/` и `VITE_DEV_MODE=1` для Django.

## Тесты

```bash
cd internetshop
python manage.py test
```
