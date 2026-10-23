#!/usr/bin/env bash
# Сборка для хостинга (Render/Koyeb и т.п.): зависимости -> Vite -> collectstatic -> миграции.
set -o errexit
pip install -r requirements.txt
(cd internetshop/frontend && npm ci && npm run build)
cd internetshop
python manage.py collectstatic --noinput
python manage.py migrate --noinput
python manage.py clearsessions
