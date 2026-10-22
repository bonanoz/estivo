# estivo-tilda → Django: сопоставление

**Дата:** 22.10.2026. **Источник стиля:** эта папка (`README.md`, `tokens.css`, `components/bundle.css`). По решению владельца от 22.10.2026 она заменяет `DESIGN.md`, `UX.md` и `docs/design-system.md` (см. `docs/specs/tilda-migration/SPEC.md`, «Решения владельца»).
**Куда переносим:** блок `@theme` и `@layer base/components` в `internetshop/frontend/src/styles/main.css` и страничные файлы `styles/{catalog,product,cart,pages}.css`. `bundle.css` целиком не подключаем: классы `es-*` переписываются в существующие классы проекта (`.btn`, `.form-input`…), чтобы не держать две системы.

Контраст считан по WCAG 2.x для пар этой системы.

## 1. Токены

| estivo-tilda | Сейчас в `main.css` (`@theme`) | Предложение |
|---|---|---|
| `surface` `#fdfdfd` | `--color-bg` `#faf8f5` | `--color-bg: #fdfdfd` |
| `surface-white` `#ffffff` | `--color-surface` `#ffffff` | без изменений |
| `surface-muted` `#f4f4f4` | `--color-surface-alt` `#f2ede6` | `--color-surface-alt: #f4f4f4` |
| `ink` `#281913` | `--color-ink` `#1c1a17` | `--color-ink: #281913` (16,7:1 на `bg`) |
| `ink-black` `#141414` | — | добавить `--color-ink-black` (заголовки промо-карточки) |
| `ink-soft` `#3c3c3c` | `--color-ink-soft` `#55504a` | `--color-ink-soft: #3c3c3c` (10,8:1) |
| `muted` `#6d6d6d` | `--color-ink-muted` `#6e675e` | `--color-ink-muted: #6d6d6d` (5,1:1 на `bg`, 4,7:1 на `surface-alt`) — только подписи |
| `graphite` `#333333` | `--color-dark` `#23201c` | добавить `--color-graphite: #333333` (тёмные кнопки, 12,6:1 с белым); `--color-dark` удалить после переноса футера (см. пробел П4) |
| `brand` `#b83400` | — (роль играет `--color-accent-text` `#a1592e`) | добавить `--color-brand: #b83400` (5,85:1 на `bg`): eyebrow, телефон, названия материалов, фокус, ошибки. `--color-accent-text` удалить |
| `accent` `#d9783e` | `--color-accent` `rgb(217,120,62)` | без изменений по значению; только кнопка заявки и полоса распродажи |
| `on-accent` = `ink` | — (`.btn-primary` сейчас белый текст) | добавить `--color-on-accent: var(--color-ink)` (5,4:1) |
| `on-dark` `#ffffff` | `--color-white`, `--color-dark-ink` `#f4efe8` | `--color-on-dark: #ffffff`; `--color-dark-ink` удалить |
| `border-input` `#c9c9c9` | `--color-line-strong` `#948f88` | `--color-border-input: #c9c9c9`. **Риск:** 1,6:1 против 3:1 WCAG 1.4.11 — README системы это признаёт и требует видимую подпись у поля и фокус `graphite`. См. П1 |
| `scrim` `rgba(0,0,0,.6)` | — | добавить `--color-scrim` (подложка панели корзины, меню) |
| — (линии в системе — 1px `ink`) | `--color-line` `#e4ddd3` | удалить; разделители — 1px `--color-ink` (как в `es-facts`, `es-card`) |
| ошибки = `brand` | `--color-error` `#b3261e` | удалить, ошибки — `--color-brand` |
| — | `--color-accent-dark`, `--color-accent-soft` | удалить: hover в системе — только opacity 0,85 |
| `font-display` Cormorant Garamond | `--font-display` то же | без изменений |
| `font-body` Gilroy, Helvetica Neue, Arial | `--font-body` Gilroy, -apple-system… | fallback привести к `"Helvetica Neue", Arial, sans-serif` |
| Gilroy 300 / 800 | `--weight-body-regular: 300`, `--weight-body-bold: 800` | без изменений (решение владельца) |
| `body` 16/24 | `body` 17px / 1.65 | 16px / 24px |
| `hero` 51/61, 400; `section-title` 50/60, 400, uppercase | `h1` clamp(2.6–5rem), `h2` clamp(2–3.2rem), weight 500 | `h1`/`h2` разделов — `clamp(32px, 6vw, 50px)/1.2`, weight 400, `text-transform: uppercase` (как `es-title`); hero — 51/61 на десктопе |
| `material-title` 22/26, `promo-title` 30/47 (600), `modal-title` 35/42 (500), `promo-note` 18/27,9 | `h3` clamp(1.4–1.9rem), `h4` 1.2rem | `h3` = `material-title`; `promo-title`/`modal-title` — только в промо-карточке и модалке «Узнать цену» |
| `lead` 20/31; `step-title` 20/27 (800); `button-lg` 16/22,4 (800); `nav`/`eyebrow`/`caption`/`button` 14/17 (300) | `.lead` clamp(1.1–1.35rem); мелкий текст 0,8–0,85rem (12,8–13,6px) | `.lead` 20/31; всё «мелкое» — не меньше 14px. `.badge` 0,8rem и `.count-dot` 0,8rem → 14px (нарушают правило «не мельче 14 px») |
| `banner` 100/120 Gilroy 300 | — | только в полосе распродажи (`es-banner__title`, clamp 40–100px) |
| `container` 1160 | `--container` 1240px, `--container-narrow` 820px | `--container: 1160px`; `--container-narrow` → 692px (3 модуля) |
| `module` 224, `gutter` 10 | — | добавить `--module: 224px`, `--gutter: 10px`; колонки 224 / 458 / 692 |
| `control-height` 60 | поля `min-height: 44px` | добавить `--control-height: 60px` (поля, кнопка формы, кнопка звонка) |
| `tap-min` 44 | 44px константой в `.icon-btn`, `.btn`, `.pill`, `.swatch` | добавить `--tap-min: 44px`, заменить константы |
| `radius-none` 0 | — (карточки 12px) | добавить `--radius-none: 0`; фото, карточки, плитки — квадратные |
| `radius-sm` 4 | `--radius-sm` 6px | `4px` |
| `radius-md` 5 | `--radius-md` 12px | `5px` (кнопки, поля) |
| — | `--radius-lg` 20px | удалить |
| `radius-pill` 30 | `--radius-pill` 50px | `30px` — только кнопка cookie; `.btn`, `.pill`, `.badge` уходят на `radius-md` |
| без теней | `--shadow-md` | удалить токен и все использования |
| hover: opacity 0,85, 0,2s ease-in-out | `--dur-*` (4 шт.), `--duration-*` (5 шт.), `--ease`, `--ease-out`; `scale(.97)` на нажатие, подъём карточки, zoom фото | оставить `--dur-fast: 200ms` и `--ease: ease-in-out`; остальные шкалы, `transform` на `.btn:active` и `.product-card:hover` удалить |
| фокус: 2px `brand`, offset 2px | 2px `--color-accent-text` | 2px `--color-brand`, offset 2px |
| — | `--space-1…8` (4–128px) | оставить: в системе нет шкалы отступов (П2) |
| — | `--z-*` | оставить (в системе нет) |
| брейкпоинты: < 768 — одна колонка, ≥ 1024 — горизонтальное меню | Tailwind по умолчанию (`md` 768, `lg` 1024) | совпадает, без изменений |

## 2. Компоненты

| `es-*` | Чем заменится в `shop/templates/` | Что поменять |
|---|---|---|
| `.es` (обёртка страницы) | `body` в `@layer base` (`main.css`), `base.html` | шрифт `body` 16/24, цвет `ink`, фон `bg` |
| `es-btn es-btn--dark` | `.btn` (сейчас без варианта) + новый `.btn-dark` | по умолчанию CTA — `graphite`, текст `on-dark`, 14/16,8 weight 300, `radius-md`, `min-height` 45 |
| `es-btn--outline` | `.btn-outline` | граница и текст `graphite`, без hover-заливки |
| `es-btn--accent` | `.btn-primary` | фон `accent`, текст `on-accent` (не белый), 16/22,4 weight 800. Только «Перейти к заявке» (`partials/htmx/_cart_drawer.html`, `cart.html`) и «Получить расчёт» (`checkout.html`). Остальные `.btn-primary` (`404.html`, `b2b.html`, `catalog_list.html`, `designers.html`, `home.html`, `order_success.html`, `product_detail.html`, `wishlist.html`, `partials/_header.html`, `partials/_lead_form.html`, `partials/htmx/_cart_lines.html`, `partials/htmx/_review_form.html`) → `.btn-dark` |
| `es-btn--call` | ссылка на телефон в `partials/_header.html`, `contacts.html` | новая `.btn-call`: высота 60, обводка и текст `brand`, 800 |
| `es-btn--promo` | — | не нужен: /promo уходит 301 на каталог (решение владельца). Не переносить |
| `es-btn--pill` | — (cookie-уведомления нет) | новая `.btn-pill` в cookie-полосе эпика (g) |
| `.btn-light` | `partials/_cta_section.html`, `partials/_footer.html` | удалить; на полосе распродажи — `.btn-dark` с обводкой `accent` (как `es-banner .es-btn--dark`) |
| `es-icon-btn` | `.icon-btn`: `_header.html` (избранное, корзина, меню), сердце `_product_card.html`, стрелки галереи `product_detail.html` | 44×44, круг, 1px `ink`, прозрачный фон, hover opacity. Сейчас hover красит фон `surface-alt` — убрать. Расхождение со скриншотом — П3 |
| `es-eyebrow` + `es-title` | заголовки секций `home.html`, `about.html`, `b2b.html`, `designers.html`, `delivery_payment.html`, `warranty.html`, `faq.html` | eyebrow 14px `brand` над каждым H2 секции; H2 — `es-title` |
| `es-title--promo` | промо-карточка (эпик b) | `promo-title`, `ink-black` |
| `es-text` | абзацы страниц | 16/24, `ink`/`ink-soft`, ширина ≤ 458px |
| `es-input`, `es-field-error` | `.form-input`, `.form-errors`/`.form-error` в `_lead_form.html`, `checkout.html`, `partials/htmx/_review_form.html` | высота 60, `radius-md`, граница `border-input`, фокус `graphite`, ошибка — граница и текст `brand` 14px. Видимая подпись у каждого поля (риск П1) |
| `es-choice` | радио доставки и чекбокс согласия в `checkout.html`, `_lead_form.html` | строка 44px, подпись шрифтом `body` 16/24 |
| `es-card` (+ `__icon`) | карточки преимуществ: «Почему ESTIVO» в `home.html`, `b2b.html`, `designers.html` | 1px `ink`, без фона и скругления, 20px; иконка 30px `brand`, линия 1,5px |
| `es-tile` (+ `__author`) | `.review-item` в `partials/_reviews.html`, `.faq-item` в `faq.html` | фон `surface-alt`, без границы; автор отзыва — имя, город, дата, площадка (R14) |
| `es-facts` | `.pdp-trust` в `product_detail.html`; итог в `partials/htmx/_cart_drawer.html`, `cart.html`, `checkout.html` | `ul` с `b`-подписью `muted` и значением `ink`, линии сверху и снизу 1px `ink`; срок · доставка · гарантия · оплата (R06). Иконки из `.pdp-trust` убрать |
| `es-banner` (+ `__title`) | новый блок в `home.html` после товаров | полоса `accent`, строка `banner` в `on-dark`, одна на страницу, не первый экран (R13). `partials/_promo_bar.html` — см. П5 |
| `es-contact__label/__value` | `partials/_footer.html`, `contacts.html`, `partials/_chat_button.html` | подпись 14px `muted`, значение 16/24; телефон — `brand`; порядок мессенджеров: Telegram (диалог) → MAX → WhatsApp (R18) |
| Cover (`components/Cover/preview.html`, без README) | первый экран `home.html` | продукт, обещание, доказательство, «Подобрать комплект» (R13); hero 51/61 |
| Логотип `assets/Logos/estivo-logo.svg` | `partials/_header.html`, `partials/_footer.html` | скопировать в `shop/static/img/`, ширина ≥ 120px, только на светлом фоне |

## 3. Компонентов нет в дизайн-системе — спроектировать в эпике (b)

Сначала макет в `components/<Имя>/preview.html` по образцу существующих (только классы `es-*` и токены, заглушки «[уточнить]»), потом шаблоны.

1. **Карточка товара с ценой и состоянием «Узнать цену»** → `partials/_product_card.html`, `.product-card`.
   - Фото квадратное по углам, без тени, без подъёма и zoom при наведении.
   - Название по составу; у комплекта артикул («Арт. К-60»), не номер в названии (аудит §14).
   - Цена «от N ₽»; старая цена — только реально существовавшая (R12).
   - `price = 0` → вместо цены «Цена по запросу», кнопка «Узнать цену» (`.btn-dark`), открывает форму с названием товара; «В корзину» не показывается, сервер такой товар в корзину не кладёт (R08).
   - Строка срока: «В наличии» / «Под заказ» (R06).
   - Сердце `icon-btn` 44px; образцы цвета, если есть.
   - Подписи не мельче 14px; на 390px две колонки без горизонтальной прокрутки (R22).
2. **Карточка промо-предложения** → новый `partials/_offer_card.html` (используется в каталоге с `?flag=sale` и в полосе распродажи на главной).
   - Название и состав, цена, реальная старая цена, выгода в рублях или точный процент (R12).
   - Дата окончания. Без даты карточка не показывается, после даты скрывается (R17, R26).
   - Своя кнопка «Узнать цену [название]» с формой, у которой скрытое поле-источник (R16).
   - Заголовок `es-title--promo`; `accent` — только на кнопке заявки.
   - Хранение данных: сейчас акция = `old_price` у товара, а поля даты окончания нет — нужна схема БД, см. SPEC (b), вопрос «[уточнить]».
3. **Панель корзины и заявки** → `partials/htmx/_cart_drawer.html`, `cart.html`, `checkout.html`.
   - Заголовок «Ваша заявка».
   - Строки: фото, название, выбранные цвета, количество, цена. Товаров с ценой 0 нет (R08).
   - Сумма + «Это предварительный расчёт. Оплаты на сайте нет: менеджер перезвонит в течение [уточнить: время], уточнит цвет, сроки и стоимость доставки» (R07).
   - `es-facts`: срок · доставка · гарантия 3 года · договор 50/50 после фотоотчёта (R06).
   - Кнопка `.btn-primary` (accent) «Перейти к заявке» → «Получить расчёт».
   - Уведомление после добавления: «Добавлено в заявку · Открыть» (R01).
   - Подложка `scrim`, кнопки 44px.

## 4. Пробелы и расхождения

- **П1. Граница поля 1,6:1.** `border-input` `#c9c9c9` не проходит WCAG 1.4.11 (3:1). По решению «источник — estivo-tilda» берём его значение, компенсируем видимой подписью и фокусом. Если нужна AA без оговорок — владелец меняет значение в `tokens.json` (папку без разрешения не трогаем).
- **П2. Нет шкалы отступов, слоёв (`z-index`), длительностей кроме 0,2s.** Оставляем проектные `--space-*`, `--z-*`, `--dur-fast`.
- **П3. Кнопки-иконки в шапке.** Замер на живом сайте 22.10.2026 (390px, один запрос): кнопка меню — круг 48×48 с заливкой `#ebebeb` без обводки; иконки 19×19, линия `#b83400` (`brand`). В `es-icon-btn` — прозрачный круг 44px с обводкой `ink` и иконкой `ink`. Цвета `#ebebeb` в токенах нет. В переносе следуем `estivo-tilda`; поправить систему под оригинал — решение владельца.
- **П4. Нет футера и тёмных секций.** В системе нет компонента футера и тёмного фона (`graphite` — только кнопки). Футер переводим на `surface` с `es-contact` и hairline `ink`; `--color-dark`/`--color-dark-ink` удаляются.
- **П5. Нет тонкой промо-полосы.** `partials/_promo_bar.html` (`SiteSettings.promo_*`) в системе не описан. `accent` нельзя (только кнопка заявки и полоса распродажи) — полоса делается `surface-alt` + `ink` 14px.
- **П6. Нет компонентов:** горизонтальное меню ≥ 1024px и мобильное меню, хлебные крошки, пагинация, фильтры (`.pill`), образцы цвета (`.swatch`), бейджи, аккордеон FAQ, галерея карточки, оверлей поиска, cookie-полоса, модалка «Узнать цену», 404/500. Их **не проектируем заново**: эпик (a) переводит существующие классы на токены выше (квадратные углы → `radius-md` у контролов, без теней, 14px+, 44px+). Cookie-полоса — эпик (g) на `es-btn--pill`.
- **П7. Иконки.** В системе нет набора иконок — используем текущие inline SVG, приводим линию к 1,5px.
- **П8. Шрифт Gilroy.** В `shop/static/fonts/gilroy/` уже лежат `Gilroy-Light.woff2` и `Gilroy-ExtraBold.woff2` (по ~25 КБ, не пустые заглушки, хотя `CLAUDE.md` говорит обратное — поправить в эпике (a)). Читаемость Light 300 при 14px проверить на телефоне (чек-лист, раздел 0).
