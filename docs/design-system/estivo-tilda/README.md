Плетёная мебель ручной работы — для дома, дачи и бизнеса. ESTIVO pages are quiet, light and editorial: a near-white ground, dark-brown text, big uppercase serif headings, one rust colour for small signals and one terracotta for the request button and sales.

Captured from estivo63.ru (Tilda) on 2026-10-20, then corrected against `MARKETING_AUDIT.md` (2026-10-22): where the source site and the audit disagree, the audit wins and the rule cites its ID (R04, R13…).

## Content fundamentals

- Write in Russian, addressing the reader as «вы» (lower case), speaking as «мы» for the workshop: «Мы создаём мебель, которая становится частью…».
- Headings are short claims, stored in sentence case and uppercased by CSS: «Комфорт, в котором исчезает время», «Мебель, которая…», «Отвечаем на вопросы».
- Every section heading gets a 1–3 word eyebrow naming the topic: «Философия бренда», «Преимущества компании», «Отзывы», «FAQ», «Форма заявки».
- Facts, not superlatives. The voice is calm and premium, and earns it with checkable numbers: «Своё производство в Тольятти: 3 цеха, сварка и покраска алюминия», «Рассрочка 0% до 12 месяцев». No «Rolls-Royce среди мебели», «Эверест мастерства» or other unprovable claims (audit §14).
- Promises appear in one wording only, taken from the contract: guarantee, lead time, prepayment, delivery. Until the owner confirms them, write «Гарантия [уточнить]», never a number copied from an old page (R04, R05). Same for company age: no «10+ лет» while the seller is a 2023 sole proprietor.
- Materials are named honestly: «искусственный ротанг (ПЭ), ручное плетение», frame alloy per product (R11).
- The site takes requests, not payments: say «заявка» and «расчёт», never «заказ» or «оплатить» (R07). Buttons are verbs in sentence case: «Получить расчёт», «Перейти к заявке», «Узнать цену» (products without a price, R08), «Подобрать комплект», «Обсудить дизайн-проект». Promo and banner buttons go uppercase.
- Every offer carries a price, a composition and an end date; drop it when the date has passed (R17, R26).
- No emoji. Swipe hints are a single asterisked word in `eyebrow` style: «Листайте*».

## Colour

- Ground: `surface` on the main site, `surface-white` on promo and in popups, `surface-muted` for review and FAQ tiles.
- Text: `ink` (dark brown, not black) for all headings and body on the main site; `ink-black` for promo headings; `ink-soft` for secondary paragraphs; `muted` only for labels.
- `brand` (logo rust) is a signal, never a fill: eyebrows, the phone number, material names («РОУП», «РОТАНГ»), the outline call button, error states.
- `accent` (terracotta) marks the request button («Получить расчёт») and the sale strip. The sale strip is never the first screen (R13): the home page opens with product, promise and proof. Button labels on accent use `on-accent` (dark brown, 5.4:1); white `on-dark` (3.1:1) only for 40px+ banner type.
- Dark actions are `graphite` with `on-dark` text. Overlays use `scrim`.
- There is no dark theme on the source site; the system has one theme.

## Type

- Two families: `display` (Cormorant, Google Fonts, Cyrillic) for headings, `body` (Gilroy) for everything else.
- Home headings: `hero` and `section-title` at weight 400, uppercase, `ink`. Promo headings: `promo-title` and `promo-cover` at 600.
- Readable on a phone (R22): body copy is `body` 16/24; nothing on the site is set below 14px — `nav`, `eyebrow`, `caption` and button labels are 14px. The source site's 10–13px text is not carried over.
- Display sizes are desktop values. Below 768px, `es-title` and the banner line scale down with `clamp()` in `components/bundle.css`; there is no separate mobile token set.
- The sale strip is the one place Gilroy goes huge: `banner` uppercase.
- Gilroy is a commercial font served by Tilda; no files are bundled here. Load licensed `.woff2` files yourself, otherwise the stack falls back to Helvetica Neue / Arial.

## Layout and spacing

- Content sits in a 1160px `container` built from five 224px `module` columns with a 10px `gutter`. Cards, photos and text columns span 1, 2 or 3 modules (224 / 458 / 692px). Below 768px, columns stack to full width with a 16px side gutter.
- The first two screens of the home page show real products with prices (R13); the sale strip comes after them.
- Sections are separated by generous white space, not rules or colour bands; the only full-bleed colour block is the `accent` sale strip.
- Photos are rectangular, unframed, often cut-out furniture on white; text sits beside photos, not over them (except the promo cover).

## Shape, borders, depth

- Square: `radius-none` for photos, cards and tiles. Only controls round: `radius-md` (5px) for buttons and inputs, `radius-sm` (4px) on promo buttons, `radius-pill` for the cookie button.
- Outlined cards use a 1px `ink` hairline. Inputs use a 1px `border-input` line.
- No shadows, no gradients.
- Every tap target is at least `tap-min` (44px) in both directions: header icons, slider arrows, small buttons (R22).

## Navigation

- From 1024px the header shows a horizontal menu by category (сеты, кресла, диваны, столы…), with material as a filter, and one «Акции» item (R20). The burger is for narrower screens only.
- Header icon buttons (wishlist, cart, menu) are 44px round `es-icon-btn`.
- After «В корзину», the notice links straight to the request: «Добавлено в заявку · Открыть» (R01).

## Motion and states

- Hover on buttons and links: opacity to 0.85, 0.2s ease-in-out. No other motion system.
- Focus: 2px `brand` outline, 2px offset (added here; the source shows browser defaults).

## Iconography

- Thin single-stroke line icons (about 1.5px at 30px) in `brand` on advantage cards; round icon buttons in the header for wishlist, cart and menu. The source draws them as Tilda vectors; none are exported here, so use any matching 1.5px line set and flag it.

## Logo

- `Logos/estivo-logo.svg`: wordmark in near-black with `brand` details, on light grounds only. See the group's README.

## Components

- Button, SectionHeading, TextField, Card, FactStrip, PromoBanner, ContactBlock: plain CSS classes in `components/bundle.css` (prefix `es-`), no script. Wrap a page in `.es` to get the body font and `ink` colour.
- Not covered yet (the audit asks for them; design them before building): product card with price and «Узнать цену» state, promo offer card (price, composition, end date, its own form), cart/checkout panel.
