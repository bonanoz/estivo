# SPEC: Анимации на весь сайт

- **slug:** `site-motion`
- **ветка:** `feat/site-motion`
- **создано:** 2026-10-23
- **режим:** `/pipeline lite` (код пишет оркестратор, без воркеров)
- **команда тестов:** `cd internetshop && python manage.py test` (+ `cd internetshop/frontend && npm run build`)

## Задача

«нужно добавить анимации на весь сайт»

## Цель и границы

Сдержанное движение по всему сайту: появление блоков при скролле, плавные переходы между страницами,
микро-анимации (счётчики корзины/избранного, сердечко, аккордеоны `details`). Всё — прогрессивное улучшение:
без JS, при `prefers-reduced-motion: reduce` и в браузерах без поддержки сайт выглядит как сейчас.

## Решения (из опроса)

| Вопрос | Решение |
|---|---|
| Какие анимации? | Появление при скролле, переходы между страницами, микро-анимации UI |
| Насколько заметно? | Сдержанно: 400–600ms, сдвиг 12–16px, без пружин |
| Hover-эффекты сильнее (zoom/подъём)? | Нет — запрет `transform` на `:hover`/`:active` остаётся |

## Допущения (принято без вопроса)

- Никаких новых зависимостей: CSS + один TS-модуль `frontend/src/motion/index.ts` (автоимпорт через `import.meta.glob`).
- Параметры движения — в `:root` вне `@theme` (`--motion-reveal: 500ms`, `--motion-ease`): `test_design_tokens`
  держит `@theme` без `--ease-out` и без `--dur-*` кроме `--dur-fast` (решение MAPPING).
- Скрываются только элементы ниже первого экрана — hero/первый экран не мигают.
- Переходы страниц — нативный cross-document View Transitions (`@view-transition { navigation: auto }`), только при
  `prefers-reduced-motion: no-preference`; шапка — `view-transition-name: site-header`.
- Аккордеоны — `::details-content` + `interpolate-size`; кнопку чата (`_chat_button.html`) не трогаем.

## Чего не трогаем

- `docs/design-system/estivo-tilda/` (read-only), модели/вьюхи/URL.
- Существующие тесты-запреты (`test_no_transform_in_hover_or_active` и др.) не ослабляем.

## Эпики

| ID | Эпик | Волна | Зависит от | Зона файлов | Модель | Статус | Ветка |
|---|---|---|---|---|---|---|---|
| E1 | Движение: CSS + motion-модуль + шапка | 1 | — | `frontend/src/styles/main.css`, `frontend/src/motion/index.ts`, `frontend/src/main.ts`, `shop/templates/partials/_header.html` | — (lite) | done | feat/site-motion |
| E2 | Документация | 1 | — | `docs/design-system.md` §2.5, `CLAUDE.md` | — (lite) | done | feat/site-motion |

### E1. Движение

- **Критерии готовности:**
  - [ ] `main.css` содержит `[data-reveal]` (opacity 0 + translateY) и `[data-reveal].is-in` (opacity 1, transform none)
  - [ ] `@view-transition { navigation: auto }` есть только внутри `@media (prefers-reduced-motion: no-preference)`
  - [ ] `.is-bumped` + `@keyframes count-bump` есть; `transform` не появляется в `:hover`/`:active` правилах
  - [ ] Аккордеоны `.faq-item/.pdp-acc/.filter-group/.review-write` имеют правило `::details-content`
  - [ ] `frontend/src/motion/index.ts` существует, проверяет `prefers-reduced-motion`, использует `IntersectionObserver`, слушает `htmx:load`
  - [ ] Обе `<header>` в `_header.html` имеют класс `site-header`
  - [ ] `@theme` не получил новых `--dur-*`/`--ease-out` (старые тесты зелёные)
  - [ ] `npm run build` (tsc + vite) без ошибок
- **Тесты:** `shop/tests/test_motion.py`
- **Ручная проверка:** главная — блоки появляются при скролле, первый экран не мигает; переход между страницами плавный;
  фильтр каталога (htmx) — новые карточки появляются; «В корзину» — счётчик подпрыгивает; сердечко; FAQ раскрывается
  плавно; reduced-motion — анимаций нет, контент виден; 390px без горизонтального скролла.

### E2. Документация

- **Критерии готовности:**
  - [ ] `docs/design-system.md` §2.5 описывает четыре вида движения и запрет transform на hover/active
  - [ ] `CLAUDE.md` упоминает `motion` среди фич фронтенда
- **Тесты:** `shop/tests/test_motion.py::MotionTests::test_design_system_documents_motion`

## Критерии готовности всей задачи

- [x] Полный набор тестов проекта зелёный
- [x] Линт design-taste без новых FAIL вне allow-list
- [x] Ручная проверка E1 пройдена в браузере

## Журнал

- 2026-10-23 spec создан (опрос проведён в plan mode)
- 2026-10-23 E1, E2 done (lite). Отклонение: htmx-проявление ограничено .product-card, иначе #cart-lines мигал при каждом изменении количества; live-фильтр каталога меняет только счётчик, карточки не подгружает.
