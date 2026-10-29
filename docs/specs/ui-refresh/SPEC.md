# SPEC: Новая сетка, ритм и компоненты сайта

- **slug:** `ui-refresh`
- **ветка:** `feat/ui-refresh`
- **создано:** 2026-10-29
- **режим:** полный `/pipeline`, по волнам в одном чате; после каждой волны оркестратор останавливается и показывает результат
- **команда тестов:** `cd internetshop && python manage.py test` (в worktree воркера: `DB_TEST_NAME=test_internetshop_<epic>`)
- **источник:** `docs/design-system/proposals/2026-10-28-ui-refresh.md` (одобрено владельцем 29.10.2026),
  наглядно — `docs/design-system/proposals/2026-10-28-ui-refresh.html`

## Задача

«владелец одобрил всё, по поводу тильды я тебе развязываю руки, не нужно ориентироваться на нее, но дизайн систему
оставляй 100%. построй план по переделке через пайплайн»

## Цель и границы

Перевести весь сайт на новую сетку (контейнер 1360px, 12 колонок), единую шкалу заголовков без прописных, правило
«терракотовая кнопка — только заявка» и облегчённые компоненты из предложения. Цвета, шрифты, запреты и правила
доступности из `docs/design-system.md` не меняются. Ориентир на Tilda снимается: `docs/design-system/estivo-tilda/`
уходит в архив, единственный источник правды — `docs/design-system.md`. Охват — все публичные страницы.

## Решения (из опроса)

| Вопрос | Решение |
|---|---|
| Что значит «дизайн-систему оставлять 100%»? | Не меняются: цвета, шрифты (Cormorant Garamond, Gilroy 300–800), запреты (тени, градиенты, `transform` на hover/active, тёмные секции, текст < 14px), фокус, §4 доступность, §5 тексты. Меняются по предложению: сетка, шкала заголовков, компоненты; `design-system.md` обновляется |
| Папка `estivo-tilda` | В архив: остаётся справкой, тесты больше не сверяют с ней размеры; логотип берётся оттуда, как сейчас |
| Какие страницы | Все: главная, каталог, товар, корзина и оформление — по черновику; остальные (о нас, B2B, дизайнерам, контакты, FAQ, доставка, гарантия, политика, 404/410/500, избранное, «заявка принята») — новая сетка, подписи над заголовками, одна серая секция, правило кнопок |
| «Почему ESTIVO» | Полный блок только на главной. В каталоге и на странице товара — строка фактов |
| «В корзину» на странице товара | Графитовая (предложение одобрено целиком) |
| Основной текст | Gilroy 400 вместо 300 (одобрено) |
| Фото во всю ширину | Да: первый экран главной и «Кто мы» (одобрено) |
| Незакоммиченные правки | Закоммичены в master двумя коммитами до ветки (bce20d5, 725eae4) |
| Как вести пайплайн | По волнам в этом чате, остановка после каждой волны |
| Модели и уровень усилий | Воркеры sonnet: E1 — high, E2–E7 — medium. Автор тестов — sonnet, high. Ревьюер — opus, high |

## Целевые значения

| Что | Было | Стало |
|---|---|---|
| `--container` | 1160px | 1360px |
| `--module`, `--gutter` | 224px, 10px | удалить; промежутки сетки — `--space-4` (24px), ниже 768px `--space-3` (16px) |
| Поля страницы | 16 / 24px | новый токен `--page-pad: clamp(16px, 4vw, 48px)`, один для `.page-container`, шапки, футера, промо-полосы |
| `--control-height` | 60px | 52px |
| `--weight-body-regular` | 300 | 400 (`--weight-body-bold` 800 остаётся для цен) |
| Вес кнопок и подписей | 300 / 800 | новый токен `--weight-ui: 600`; `.btn-primary` тоже 600 |
| Заголовки `h1`, `h2` | прописные, 400 и 500 в разных местах, две шкалы | строчные, вес 400, одна шкала: display `clamp(44px, 6vw, 76px)`/1.02, h2 `clamp(32px, 3.6vw, 48px)`/1.05, h3 24px/1.2 |
| Подпись над заголовком | нет | `.eyebrow`: Gilroy 500, 14px, прописные, `letter-spacing: 0.08em`, `ink-muted` |
| Ритм секций | всем 64/96px | `.page-section` 64/96, `--tight` 40/64, `--loose` 64/128 (мобильный/≥768) |
| Серые секции | через одну | не больше одной `.page-section--alt` на шаблон; `.page-section--dark` удалить |

Правило кнопок. `.btn-primary` (терракота) — только «отправить заявку / перейти к заявке», не больше одной в видимой
группе действий. `.btn-dark` — остальные главные действия («В корзину», «Применить», «Отправить отзыв»).
`.btn-outline` и текстовые ссылки — второстепенные. Разрешённые места `.btn-primary`: hero главной (одна), товар
«Оформить заявку» (в том числе липкая панель), `_cart_lines.html`/`_cart_drawer.html` «Перейти к заявке»,
`checkout.html` «Получить расчёт», `_cta_section.html` «Оставить заявку», пустой каталог «Оставить заявку»,
`b2b.html`, `designers.html`, `_lead_form.html` (отправка формы), `_offer_card.html`.

## Допущения (принято без вопроса)

- Раскладки делаются утилитами Tailwind, которые уже есть в шаблонах (`grid-cols-1 lg:grid-cols-12`, `lg:col-span-7`,
  `gap-4 md:gap-6`), без своего грид-фреймворка.
- Порядок секций главной не меняется (`HOME_SECTIONS` в `test_pages_ui.py`).
- H1 главной: «Плетёная мебель из ротанга и роупа», над ним подпись «Своё производство · Тольятти»; «Тольятти»
  остаётся в `<title>` и meta description.
- На телефоне в hero фото идёт над текстом во всю ширину.
- Подпись над заголовком ставится только там, где она добавляет сведения, которых нет в заголовке. Тексты подписей
  на главной, в каталоге и на товаре — по черновику (`2026-10-28-ui-refresh.html`); на остальных страницах воркер
  предлагает сам, оркестратор проверяет все новые тексты скиллом `site-copy-check`.
- Строка фактов — общий партиал `partials/_facts_strip.html` (гарантия `site_info.warranty`, изготовление
  `site_info.production_term`, «Доставка ТК по России», «Работаем по договору»).
- Кнопка чата: где она закрывает форму или кнопку заявки на телефоне, страница получает класс `chat-inline`
  (механизм уже есть в `_chat_button.html`). Сам партиал не меняется.
- Шапка и футер не перерисовываются: только новый контейнер и поля `--page-pad`.
- `prefers-reduced-motion`, View Transitions и появление при скролле (`site-motion`) не трогаем.
- Тесты гоняются на PostgreSQL из `.env`; в worktree воркер копирует `internetshop/.env` из основной копии
  (файл не в git) и задаёт свой `DB_TEST_NAME`. Под это в `settings.py` добавлен `DATABASES['default']['TEST']['NAME']`.

## Чего не трогаем

- Модели, миграции, вьюхи, URL, формы, корзину и логику заявок (только шаблоны и CSS).
- Цвета `--color-*`, шрифты и файлы Gilroy, логотип.
- Запреты в `test_design_tokens.py` (тени, градиенты, `transform` на hover, Gilroy вне 300–800, < 14px, линия иконок 1,5)
  не ослабляются.
- `docs/design-system/estivo-tilda/` кроме `MAPPING.md`; `frontend/src/motion/`, `frontend/src/lib/`.
- Админку и SEO-разметку (canonical, OG, JSON-LD).

## Эпики

| ID | Эпик | Волна | Зависит от | Зона файлов | Модель / усилия | Статус | Ветка |
|---|---|---|---|---|---|---|---|
| E1 | Фундамент: токены, типографика, общие компоненты | 1 | — | `frontend/src/styles/main.css`, `frontend/src/styles/pages.css`, новый `frontend/src/styles/home.css` (пустой + импорт), `templates/base.html`, `partials/_header.html`, `partials/_footer.html`, `partials/_promo_bar.html`, новый `partials/_facts_strip.html`; в `templates/home.html` и `templates/about.html` — только снять класс `page-section--dark` | sonnet / high | done | merge 05b4a33 |
| E2 | Главная | 2 | E1 | `templates/home.html`, `partials/_why_estivo.html`, `frontend/src/styles/home.css` | sonnet / medium | in_progress | |
| E3 | Каталог и избранное | 2 | E1 | `templates/catalog_list.html`, `templates/wishlist.html`, `partials/_product_card.html`, `partials/_pagination.html`, `frontend/src/styles/catalog.css` | sonnet / medium | done | merge 8e5e9a6 |
| E4 | Страница товара | 2 | E1 | `templates/product_detail.html`, `partials/_reviews.html`, `partials/htmx/_review_form.html`, `frontend/src/styles/product.css`, `frontend/src/product/*` | sonnet / medium | in_progress | |
| E5 | Корзина и оформление | 2 | E1 | `templates/cart.html`, `templates/checkout.html`, `partials/htmx/_cart_*.html`, `frontend/src/styles/cart.css`, `frontend/src/styles/request.css` | sonnet / medium | in_progress | |
| E6 | Остальные страницы | 2 | E1 | `templates/{about,b2b,designers,contacts,faq,delivery_payment,warranty,privacy,404,410,500,order_success}.html`, `partials/_cta_section.html`, `partials/_lead_form.html`, `partials/_breadcrumbs.html`, `frontend/src/styles/pages.css` | sonnet / medium | in_progress | |
| E7 | Документация | 3 | E2–E6 | `docs/design-system.md`, `docs/design-system/estivo-tilda/MAPPING.md`, `CLAUDE.md`, `.taste-skill/direction.json` | sonnet / medium | todo | |

Статусы: `todo` → `in_progress` → `review` → `done` (или `blocked` + причина в журнале).

`pages.css`: в волне 1 его общие части (`.page-container`, `.page-section*`, `.page-h1/2/3`) правит E1, в волне 2
файл целиком у E6. Стили главной в волне 2 живут в `home.css` (E2), чтобы не делить `pages.css`.

### E1. Фундамент: токены, типографика, общие компоненты

- **Что сделать:** токены из «Целевых значений» в `@theme`; базовые `h1`/`h2` без `text-transform`, одна шкала, вес
  400; `.page-h1/2/3` в `pages.css` приведены к той же шкале (вторая шкала исчезает); класс `.eyebrow`; `.btn` и
  `.btn-primary` с `--weight-ui`; поля форм и большие кнопки от `--control-height`; `.page-container` с `--page-pad`,
  модификаторы `.page-section--tight`/`--loose`, удалён `.page-section--dark`; шапка, футер, промо-полоса на
  `--page-pad`; партиал `_facts_strip.html` + его стиль; пустой `home.css` с импортом в `main.css`.
- **Критерии готовности:**
  - [ ] `@theme`: `--container: 1360px`, `--control-height: 52px`, `--weight-body-regular: 400`, `--weight-ui: 600`, `--page-pad: clamp(16px, 4vw, 48px)`; `--module` и `--gutter` отсутствуют в CSS и шаблонах
  - [ ] ни одно правило для `h1`, `h2`, `.page-h1`, `.page-h2` не содержит `text-transform: uppercase`; вес заголовков 400
  - [ ] `.eyebrow` есть в `main.css`: 14px, вес 500, `uppercase`, `letter-spacing: 0.08em`, цвет `--color-ink-muted`
  - [ ] `.btn` и `.btn-primary` используют `var(--weight-ui)`; `body` — `var(--weight-body-regular)`
  - [ ] `.page-section--tight`, `.page-section--loose` есть; `.page-section--dark` нет ни в CSS, ни в шаблонах
  - [ ] `render_to_string('partials/_facts_strip.html')` с `site_info` содержит `data-facts-strip`, гарантию и срок изготовления из `site_info`
  - [ ] `.page-container`, шапка, футер и промо-полоса используют `var(--page-pad)`
  - [ ] все запреты `test_design_tokens.py` проходят
- **Тесты:** `shop/tests/test_design_tokens.py` (обновлённый контракт), `shop/tests/test_ui_refresh.py::FoundationTests`
- **Ручная проверка:** на 1440 контент занимает ≥ 1340px; на 390 поля 16px, нет горизонтальной прокрутки

### E2. Главная

- **Что сделать:** hero по черновику (текст на 6 колонок слева, фото до правого края экрана; на телефоне фото сверху),
  одна `.btn-primary` и две текстовые ссылки на каталоги ротанга и роупа; подписи над заголовками; ритм (факты
  `--tight`, «Почему ESTIVO» `--loose`); «Почему ESTIVO» — заголовок на 4 колонки, пункты списком без рамок с линией
  `border-input`; «Кто мы» — фото во всю ширину; серая секция одна (отзывы).
- **Критерии готовности:**
  - [ ] GET `/` → в `[data-section=hero]` ровно одна `.btn-primary`, ни одной `.btn-outline`, есть ссылки на `catalog_by_material` для `rotang` и `roup`
  - [ ] H1 главной — «Плетёная мебель из ротанга и роупа»; над ним `.eyebrow` «Своё производство · Тольятти»
  - [ ] в шаблоне `home.html` не больше одного `page-section--alt`, ноль `page-section--dark`
  - [ ] `_why_estivo.html` не использует `page-card`; партиал включается только из `home.html`
  - [ ] порядок `data-section` совпадает с `HOME_SECTIONS`
- **Тесты:** `shop/tests/test_ui_refresh.py::HomeTests`, `shop/tests/test_pages_ui.py`
- **Ручная проверка:** 1440 и 390 — фото hero до края, заголовок в 2 строки на 1440

### E3. Каталог и избранное

- **Что сделать:** баннер раздела на 12 колонок (заголовок 7, описание 5), подпись «{Материал} · N моделей»; сетка
  карточек в новом контейнере (4 в ряд на ≥1024); вместо `_why_estivo.html` — `_facts_strip.html`; пустой каталог —
  «Оставить заявку» `.btn-primary`; избранное на той же сетке. Панель фильтров не меняется.
- **Критерии готовности:**
  - [ ] GET `/catalog/rotang/kresla/` → нет `data-section="why-estivo"` и класса `page-card`, есть `data-facts-strip`
  - [ ] у баннера раздела есть `.eyebrow` с числом товаров
  - [ ] пустая выдача → ссылка «Оставить заявку» с классом `btn-primary`
  - [ ] тесты фильтров, сортировки и htmx-счётчика (`test_catalog_*`) зелёные без правок
- **Тесты:** `shop/tests/test_ui_refresh.py::CatalogTests`, `shop/tests/test_catalog_ui.py`, `shop/tests/test_catalog_filters.py`
- **Ручная проверка:** 1440 — 4 карточки в ряд шириной около 322px; 390 — 2 в ряд

### E4. Страница товара

- **Что сделать:** раскладка 7+5 на 12 колонках; над названием `.eyebrow` «{категория} · {материал}»; «Оформить
  заявку» — `.btn-primary` (в основной группе и в липкой панели), «В корзину» — `.btn-dark`; вместо `_why_estivo.html`
  — `_facts_strip.html`; отзывы и «Вам может подойти» на новой сетке.
- **Критерии готовности:**
  - [ ] GET товара с ценой → кнопка `name=checkout` имеет класс `btn-primary`, кнопка `data-add-to-cart` — `btn-dark`
  - [ ] над `h1` есть `.eyebrow` с названием категории и материалом
  - [ ] нет `data-section="why-estivo"`, есть `data-facts-strip`
  - [ ] товар без цены → «Узнать цену» без `btn-primary` (это не заявка из корзины), как сейчас ведёт на контакты
  - [ ] `test_product_ui.py`, `test_cart_htmx.py`, `test_reviews.py` зелёные
- **Тесты:** `shop/tests/test_ui_refresh.py::ProductTests`, `shop/tests/test_product_ui.py`
- **Ручная проверка:** липкая панель на 390 не перекрывается кнопкой чата

### E5. Корзина и оформление

- **Что сделать:** корзина и оформление на 12 колонках (строки 8, итог 4, итог закреплён при прокрутке); итог без
  серого фона, отделён линией `ink`; «Продолжить покупки» — текстовая ссылка; на оформлении имя и телефон в одну
  строку от 768px; `cart.html` получает `chat-inline`.
- **Критерии готовности:**
  - [ ] GET `/cart/` с товаром → ровно одна `.btn-primary` «Перейти к заявке», «Продолжить покупки» без класса `btn`
  - [ ] у `cart.html` в `body_class` есть `chat-inline`
  - [ ] блок итога не использует `bg-surface-alt` / `--color-surface-alt`
  - [ ] сценарии заявки (`test_checkout_safety.py`, `test_cart_ui.py`, `test_cart_htmx.py`, `test_request_panel.py`) зелёные
- **Тесты:** `shop/tests/test_ui_refresh.py::CartTests`, существующие тесты корзины
- **Ручная проверка:** 390 — кнопка чата не закрывает кнопку заявки и поле телефона

### E6. Остальные страницы

- **Что сделать:** новая сетка и ритм на страницах из зоны; подписи над заголовками, где добавляют сведения; не больше
  одной серой секции; `_cta_section.html` «Оставить заявку», `_lead_form.html` и CTA на B2B/дизайнерам —
  `.btn-primary`; страницы с формой (контакты, B2B, дизайнерам) получают `chat-inline`; `.page-card` из `pages.css`
  удалить, если не используется; 404/410/500 и «заявка принята» оставляют графитовые кнопки (это не заявки).
- **Критерии готовности:**
  - [ ] в каждом шаблоне зоны не больше одного `page-section--alt` и ноль `page-section--dark`
  - [ ] кнопка отправки `_lead_form.html` и кнопка заявки `_cta_section.html` — `btn-primary`
  - [ ] `contacts.html`, `b2b.html`, `designers.html` имеют `chat-inline` в `body_class`
  - [ ] каждая страница зоны отвечает 200 (404/410/500 — своим кодом), один `h1`, уровни заголовков без пропусков
  - [ ] `test_pages_ui.py`, `test_seo_a11y.py`, `test_privacy_seller*.py`, `test_texts_f.py` зелёные
- **Тесты:** `shop/tests/test_ui_refresh.py::PagesTests`
- **Ручная проверка:** 390 и 1440 по каждой странице, тексты подписей через `site-copy-check`

### E7. Документация

- **Что сделать:** `design-system.md` описывает то, что смержено: §2 токены и сетка, §3 правило кнопок и
  компоненты (`.eyebrow`, строка фактов, «Почему ESTIVO» списком), источник правды — сам документ, `estivo-tilda`
  в архиве; пометка об архиве в начале `MAPPING.md`; в `CLAUDE.md` проекта поправить факты (Gilroy по умолчанию
  400/800, источник дизайна, сетка 1360/12); `.taste-skill/direction.json` — заметка про источник. Писать по правилам
  «Как писать» из глобального CLAUDE.md.
- **Критерии готовности:**
  - [ ] в `design-system.md` нет утверждений, что `estivo-tilda` — источник стиля, и нет значений 1160/224/60px/300 как текущих
  - [ ] `CLAUDE.md` проекта не утверждает «defaults stay 300/800» и «Design source of truth: estivo-tilda»
  - [ ] `aiw-ru scan docs/design-system.md` без находок P0–P1 (ручная проверка)
- **Тесты:** `shop/tests/test_ui_refresh.py::DocsTests` (проверки строк в документах)
- **Ручная проверка:** —

## Оставлено на сведение (делает оркестратор)

- `settings.py`: `DATABASES['default']['TEST']['NAME']` из `DB_TEST_NAME` (сделано до воркеров, в коммите спеки).
- Удаление мёртвых правил после волны 2 (например, `.page-card`, если E6 его не убрал).
- `npm run build` + `collectstatic`, скриншоты всех страниц на 1440 и 390, `site-copy-check` по новым текстам,
  линтер дизайна (`design-taste-frontend/scripts/lint.mjs`) и чек-лист ui-ux-pro-max.

## Критерии готовности всей задачи

- [ ] Полный набор тестов проекта зелёный
- [ ] `npm run build` (tsc + vite) без ошибок, `collectstatic` без ошибок (ручная проверка)
- [ ] Линтер дизайна без FAIL вне allow-list (ручная проверка)
- [ ] Все публичные страницы на 390 и 1440 без горизонтальной прокрутки (ручная проверка), с одним `h1` (тест `PagesTests`)
- [ ] `.btn-primary` встречается только в разрешённых местах из «Правила кнопок»
- [ ] Новые тексты сайта прошли `site-copy-check` (ручная проверка)

## Журнал

- 2026-10-29 spec создан; модели и усилия по ответу пользователя (ревьюер opus/high, E1 и тесты high); WIP и предложение закоммичены в master (bce20d5, 725eae4); в `settings.py` добавлено имя тестовой БД из `DB_TEST_NAME`
- 2026-10-29 тесты-контракт: новый `test_ui_refresh.py` (E1–E7); изменены существующие под спеку: `test_design_tokens.py` (размеры 1360/52, `--page-pad`/`--weight-ui`/400 литералами, убраны `--module`/`--gutter` и сверка размеров с `estivo-tilda`, в допустимых весах добавлен `var(--weight-ui)`; запреты не тронуты), `test_request_panel.py::EbAccentTests` (набор мест `.btn-primary` по «Правилу кнопок»), `test_texts_f.py` (h1 главной без «Тольятти»; «Почему ESTIVO» только на главной, в каталоге и товаре — строка фактов)
- 2026-10-29 зона E1 расширена: снять `page-section--dark` в `home.html:98` и `about.html:53` (иначе `FoundationTests.test_e1_section_dark_removed` не закрыть в волне 1); остальное в этих шаблонах — E2 и E6
- 2026-10-29 E1 done: 2 попытки (ревью: поле внутри 1360 съедало контент до 1264px → `.page-container` = `calc(var(--container) + 2 * var(--page-pad))`; строка фактов переделана по черновику на Gilroy 16px). Для волны 2: worktree может создаться от master — сверить базу с `feat/ui-refresh`; в worktree нужен `collectstatic`; перевести `max-w-[var(--container)] px-4 md:px-6` на `page-container`; свои `clamp`-размеры заголовков в catalog/product/cart/pages.css привести к шкале display/h2/h3
- 2026-10-29 волна 2: E3 done с первой попытки (merge 8e5e9a6). E2, E4, E5, E6 — CHANGES, вторая попытка: E2 — зона нажатия ссылок в hero < 44px, лишняя подпись «О нас»; E4 — «Узнать цену» должна быть btn-dark, липкая панель как в черновике (две кнопки без названия и цены); E5 — размеры вторичных заголовков вне шкалы; E6 — 500.html со старыми цветами и терракотовой кнопкой, h1 about в 5–6 строк из-за max-w-[64ch], серая плашка в _cta_section даёт вторую серую зону. На сведение: catalog.css `.filter-panel` без JS — max-width без полей; отступ `.catalog-banner__text` на телефоне; `.offer-card__title` в request.css вне шкалы; описание баннера каталога повторяет строку фактов (решить на site-copy-check)
