# SPEC: ESTIVO storefront redesign (visuals, page structure, navigation, shopping UX)

- **slug:** `furniture-store-redesign`
- **branch:** `feat/furniture-store-redesign` (from `feat/session-cart-checkout-3d` @ `0143b33`)
- **created:** 2026-10-16
- **test command:** from `internetshop/`: `python manage.py test` + from `internetshop/frontend/`: `npm run build` (includes `tsc --noEmit`)
- **spec status:** draft, awaiting user approval. No code is written before approval.

## Task

Redesign the visual identity, layout, page structure, navigation and UX of the ESTIVO store according to `DESIGN.md`
and `UX.md` (repo root), preserving business logic, models, routes and integrations. Evaluate Vite + TS, Tailwind v4,
HTMX + django-htmx, Alpine.js. Full wording is in the session's first message.

## Sources of truth and their precedence

| Document | What we take from it |
|---|---|
| `UX.md` | page structure, block order, user journeys, behavior (section 8 "Cross-cutting rules" is mandatory) |
| `DESIGN.md` | **rules, not the palette**: WCAG 2.2 AA, required component states (default/hover/focus-visible/active/disabled/loading/error), pill controls ≥ 44px, "no shadows by default", motion duration scale, writing tone, Do/Don't |
| `docs/design-system.md` + `shop/static/css/variables.css` | ESTIVO brand **visual values**: colors (warm background, terracotta accent, incl. the corrected 🆕 tokens `accent-text`, `line-strong`, `error`), fonts Cormorant Garamond + Gilroy (300/800 only), spacing, radii |

Conflicts found during the audit and how they are resolved (user decisions below):

1. **DESIGN.md (Muuto palette/font: Inter, neutral grays, no accent) ↔ ESTIVO brand.** Resolved: ESTIVO brand.
   From DESIGN.md we do not take `color.*`, `font.family.*`, or the Muuto type scale; we do take the rules,
   `radius.pill` and `motion.duration.*`.
2. **docs/design-system.md and CLAUDE.md say "no Bootstrap/Tailwind, no bundler" ↔ chosen stack Vite + Tailwind.**
   Resolved: the user's stack. E7 updates the stack line in `docs/design-system.md` §1 and the "Templates and
   static"/"Setup" sections of `CLAUDE.md` (token values and rules in design-system.md stay unchanged).
   DESIGN.md/UX.md are not touched.
3. **UX.md relies on accounts, payment, ZIP logistics, promo codes** — ESTIVO's business model is lead generation.
   What is in and out — see "Decisions" and "Non-goals".

## Goal and scope

The storefront gets the new structure and behavior from UX.md in ESTIVO's visual language, built on Tailwind v4
(ESTIVO tokens via `@theme`), HTMX (server fragments: filters, search suggestions, cart drawer, wishlist) and Alpine.js
(local UI state: menu, panels, overlays). Backend stays Django templates; models, URLs and order/lead persistence
(Postgres → Telegram best-effort) are preserved. Only agreed features are added: session wishlist, promo bar, contact
button, moderated review form, New/Bestseller badges, filters/sorting, search with suggestions.

## Decisions (from the interview)

| Question | Decision |
|---|---|
| Visual source of truth | ESTIVO brand (colors/fonts from design-system.md); from DESIGN.md — rules, a11y, states, pill, no shadows; structure — from UX.md |
| Extra UX.md features | Wishlist (session, no accounts); promo bar (text from admin, dismissible, no promo codes/countdown); floating contact button (Telegram/WhatsApp/phone from `site_info`); review form on PDP (saved with `is_published=False`) |
| Product model | Add `is_new`, `is_bestseller` (migration + admin + seed_demo); badges New / Bestseller / Sale (Sale = `old_price > price`) |
| Frontend stack | HTMX + django-htmx + Alpine.js **and** Vite + TypeScript + Tailwind v4 (via `django-vite`) |
| Uncommitted work | Committed to `feat/session-cart-checkout-3d` (`0143b33`); `feat/furniture-store-redesign` branched from it |
| Test DB | User fixes `DB_PASSWORD` in `internetshop/.env` before the test phase (Postgres currently rejects password auth for user `postgres`) |
| Checkout | Single page: existing `OrderForm` + cart summary; reduced header (logo only) and "Need help?" footer (phone, messengers); URL `/cart/checkout/` unchanged |
| Search | Header icon → overlay with HTMX suggestions (up to 6 products, debounced), Enter → `/catalog/?search=…`; empty result shows recommendations |

## Assumptions (made without asking)

- **Frontend build.** Sources in `internetshop/frontend/` (`package.json`, `vite.config.ts`, `src/main.ts`,
  `src/styles/main.css`). Build → `internetshop/shop/static/dist/` with `manifest.json`; `dist/` is in `.gitignore`.
  `django-vite`: `dev_mode = True` when `VITE_DEV_MODE=1` **or when running tests** (`'test' in sys.argv`), otherwise
  the manifest is read. So `python manage.py test` doesn't need Node. Deploy / local run without the dev server:
  `npm ci && npm run build` → `collectstatic`.
- htmx and Alpine are installed via npm and bundled by Vite (no CDN). `model-viewer` stays a vendored ES module loaded
  only on PDPs with `model_3d` (as today). Fonts: Google Fonts for Cormorant stays; Gilroy via `@font-face` with the
  current files/placeholders.
- Tailwind v4 `@theme` mirrors the tokens in `variables.css` (colors incl. 🆕 tokens, fonts, spacing, radii,
  durations). Repeated components (`btn`, `pill`, `swatch`, `form-input`, `badge`, `product-card`) are classes in
  `@layer components`, not copy-pasted utilities. Body font weights — 300/800 only (design-system.md rule).
- While pages migrate, `base.html` loads **both** the Vite bundle and the legacy CSS; legacy `css/*.css` and
  `js/*.js` are removed in E7 once all templates are converted.
- Catalog: 24 products per page, numbered pagination with ellipsis, all filter GET params preserved.
  Filters are GET params on top of the existing `/catalog/…/…/` routes (routes unchanged):
  `material` (multi, slug; only on `/catalog/`), `category` (multi, slug), `color` (multi, `ColorOption` id),
  `price_min`/`price_max`, `length_min`/`length_max` (cm), `flag` (multi: `new`, `bestseller`, `sale`), `sort`
  (`recommended` default = current model ordering, `price_asc`, `price_desc`, `new`), `search`, `page`.
  Invalid values are silently ignored (no 500).
- The filter panel applies only on "Apply" (UX.md §3, §8.9), shows a live "N found" count via an HTMX endpoint and a
  "Reset" button. Full-screen on mobile, side panel on desktop.
- PDP color variants are written to the URL (`?weave=<id>&cushion=<id>&frame=<id>`, `history.replaceState`) and read
  by the server to preselect swatches; invalid/foreign ids are ignored.
- The PDP buy button shows the price: «В корзину — 45 000 ₽». Next to it, a trust block from real fields:
  `warranty_years`, delivery across Russia from 3 days, handmade (UX.md §8.1). Sticky mobile bar with name, price and
  a compact button.
- "Add to cart" → HTMX request, button in loading state, then a right-side drawer "Item added" slides in with lines,
  total, "Checkout" and "Continue shopping" + "You may also like" (up to 4 products from the same category).
  The header cart icon goes to the full `/cart/` page (UX.md §8.4). Without JS the old POST-redirect still works.
- Removing a line on `/cart/` shows a toast "… removed" with an "Undo" link (last removed line kept in the session).
  Empty cart: message, "Continue shopping", trust blocks, bestseller picks.
- Wishlist — `request.session['wishlist']` (list of product ids), a class modeled on `Cart`. Heart on card and PDP
  (HTMX toggle, `aria-pressed`), header counter, `/wishlist/` page. Unavailable/deleted products are filtered out.
- Review: name, rating 1–5, usage duration (optional), text; honeypot field against bots; after submit —
  "Review sent for moderation". No Telegram notification for reviews (not in requirements).
- Promo bar: fields `SiteSettings.promo_enabled`, `promo_text`, `promo_url`; dismissal remembered in `localStorage`
  keyed by a hash of the text (new text shows again).
- Home page in UX.md §2 order: hero (photo from `SiteSettings.hero_image`) with one CTA → quick category/material
  CTAs → featured collections with "View all" → service blocks (current `HOME_SEGMENTS`: home / business / custom
  project) → reviews (instead of an Instagram UGC feed — no data) → brand story block "About us" → SEO text + FAQ.
- Footer (UX.md §1): popular categories (SEO links to `/catalog/<material>/<category>/`), about, "For customers"
  (delivery, warranty, FAQ, contacts), average rating and count of published reviews, legal details. Instead of a
  newsletter — the existing `_cta_section` (lead form); the business has no newsletter.
- 404: short message + bestseller carousel (`is_bestseller`, else `is_featured`) + footer (UX.md §1, §8.6).
- SEO text under the catalog grid — `Material.description` (on material/category pages) + shared FAQ.
- Tests: existing `shop/tests.py` moves into a `shop/tests/` package (`test_smoke.py` etc.) without changing test
  logic; new tests — one file per epic.
- Workers: `.env` is not in git — copy `internetshop/.env` from the main checkout into the worktree before running
  tests; run `npm ci` in the worktree.
- Site copy (UI labels, headings, messages) stays in Russian.

## Non-goals

Region/country picker, accounts and login (checkout "account" step), ZIP/shipping and tax calculation, free-shipping
progress, promo codes and coupons, installments, online payment (`payment_status` stays an extension point),
Instagram UGC feed, AR, video in the gallery, review "Top mentions"/sorting/country filter, newsletter, React/Next.js,
changing existing URLs or the `Order`/`OrderItem`/`Lead` schema, rewriting `DESIGN.md`/`UX.md`.

## Do not touch

- `Cart` logic (line key = product + colors), `_parse_colors`, `Order`/`OrderItem` creation/`recalc_total`,
  `notify_telegram` and the `telegram_notified` flag, `_lead_page`/`lead_create`. Adding HTMX response branches is fine.
- Existing URL names and paths, `sitemap.xml`, `robots.txt`, canonical/OG/meta blocks of `base.html` (carried over 1:1).
- `ru_slugify`, `STORAGES` (both keys), `PGCLIENTENCODING`, `CompressedManifestStaticFilesStorage`, Gilroy placeholders.
- `DESIGN.md`, `UX.md` — read only.

## Audit findings (current state)

- Django 5.0.6, single `shop` app, function views, Postgres, whitenoise + `CompressedManifestStaticFilesStorage`.
  Frontend: 5 hand-written CSS files (~710 lines), 5 vanilla JS files, templates ~1300 lines. No bundler, no npm.
- Hook `.claude/hooks/collectstatic_hook.py` runs `collectstatic` after every edit — with Vite it must not fail when
  `dist/` is missing (checked in E1).
- Catalog: filtering only by material/category via path and `?search=` on name/description; 12 per page,
  "Prev/Next" pagination. No sorting, no color/price/size filters, no badges except old_price.
- PDP: gallery, grouped swatches, 3D, reviews (read-only), related products. Variants are not written to the URL.
- Cart: AJAX `cart.js` with JSON, no drawer, no undo. Checkout has the full header/footer.
- Missing: header search, wishlist, promo bar, contact button, bestsellers on 404.
- Tests: 15 tests in `shop/tests.py` (smoke, cart, configurator). **Currently not runnable** — Postgres
  authentication error (see Decisions).

## Architecture and stack (rationale)

- **Django templates + HTMX** cover every UX.md requirement (filters with live count, suggestions, drawer, wishlist
  toggle, undo) with server fragments and no duplicated client logic; SEO preserved (full SSR). `django-htmx` provides
  `request.htmx` to choose "fragment vs full page" in the same views.
- **Alpine.js** — UI state with no server logic: mobile menu, search overlay, filter panel, drawer, accordions,
  promo bar, sticky bar.
- **Vite + TypeScript** — one bundle (htmx, Alpine, own modules: gallery, 3D recolor, phone mask, variant URL state),
  typing, hashed filenames. **Tailwind v4** (`@tailwindcss/vite`) — brand tokens in `@theme`.
- **React/Next.js not needed**: no requirement that SSR + HTMX/Alpine can't meet; a migration would break the SEO path
  and double the stack.
- New dependencies — Python: `django-htmx`, `django-vite`; npm: `vite`, `typescript`, `tailwindcss`,
  `@tailwindcss/vite`, `htmx.org`, `alpinejs`, `@types/alpinejs`. Nothing else.

## Epics

| ID | Epic | Wave | Depends on | File zone | Model | Status | Branch |
|---|---|---|---|---|---|---|---|
| E1 | Foundation: build, tokens, shell | 1 | — | `internetshop/frontend/**`, `settings.py`, `requirements.txt`, `.gitignore`, `.claude/hooks/*`, `templates/base.html`, `templates/partials/_header.html`, `_footer.html`, `_promo_bar.html`, `_chat_button.html`, `_breadcrumbs.html`, `_product_card.html`, `_cta_section.html`, `_lead_form.html` | sonnet | done | worktree-agent-aacaa7b5c7c9cd86e (merged) |
| E2 | Backend: fields, filters, wishlist, reviews, search, HTMX responses | 1 | — | `shop/*.py` (except `settings.py`), `shop/migrations/**`, `shop/management/**`, new minimal fragment templates in `templates/partials/htmx/**` and `templates/wishlist.html` | sonnet | done | worktree-agent-a570bbdce35667b83 (merged 6ed60ad) |
| E3 | Catalog and search (UI) | 2 | E1, E2 | `templates/catalog_list.html`, `partials/_filters.html`, `partials/_pagination.html`, `partials/htmx/_search_*.html`, `partials/htmx/_catalog_count.html`, `frontend/src/catalog/**`, `frontend/src/styles/catalog.css` | sonnet | done | worktree-agent-a6bdc2e52ddaebcf3 (merged) |
| E4 | Product page (UI) | 2 | E1, E2 | `templates/product_detail.html`, `partials/_reviews.html`, `partials/htmx/_review_*.html`, `frontend/src/product/**`, `frontend/src/styles/product.css` | sonnet | done | worktree-agent-a672aec6e993946b8 (merged) |
| E5 | Cart, drawer, checkout, wishlist (UI) | 2 | E1, E2 | `templates/cart.html`, `checkout.html`, `order_success.html`, `wishlist.html`, `partials/htmx/_cart_*.html`, `partials/htmx/_wishlist_*.html`, `frontend/src/cart/**`, `frontend/src/styles/cart.css` | sonnet | done | worktree-agent-a9765df5472278797 (merged) |
| E6 | Home, content pages, 404/500 | 2 | E1, E2 | `templates/home.html`, `about.html`, `b2b.html`, `designers.html`, `delivery_payment.html`, `warranty.html`, `faq.html`, `contacts.html`, `404.html`, `500.html`, `frontend/src/styles/pages.css` | haiku | done | worktree-agent-a621404613a76c507 (merged) |
| E7 | Cleanup, docs, cross-cutting a11y/SEO | 3 | E3–E6 | delete `shop/static/css/*.css`, `shop/static/js/{main,forms,cart,product-gallery,product-3d}.js`, `base.html` (legacy static links only), `CLAUDE.md`, `docs/design-system.md` §1 and §7, `README.md` | sonnet | done | |

Statuses: `todo` → `in_progress` → `review` → `done` (or `blocked` + reason in the log).

Wave 1 has no file overlap: E1 is the shell and infrastructure, E2 is all Python. In wave 2 each epic has its own
templates, its own folder in `frontend/src/` and its own CSS file; E1 makes the shared `frontend/src/main.ts` a
**registry with auto-import** (`import.meta.glob('./*/index.ts', { eager: true })`), and `main.css` `@import`s every
`styles/*.css` file, which E1 creates as empty stubs — so wave-2 workers never edit a shared file. Minimal fragments
created by E2 are restyled by wave 2 (different waves, no conflict).

### E1. Foundation: build, tokens, shell

- **What:** `frontend/` with Vite + TS + Tailwind v4 + htmx + Alpine; `django-vite` and `django-htmx` in settings and
  requirements (`django_htmx.middleware.HtmxMiddleware`); `@theme` with ESTIVO tokens; `@layer components` for
  btn/pill/swatch/form/badge/product-card with every DESIGN.md state; new `base.html` (meta/OG/canonical 1:1, skip
  link, `header`/`footer` blocks for the reduced checkout, `{% vite_hmr_client %}`/`{% vite_asset %}`, CSRF for htmx
  via `hx-headers` on `<body>`); header per UX.md §1 (hamburger + search on the left on mobile, centered logo,
  wishlist and cart with counters on the right; horizontal menu on desktop), search overlay (markup + Alpine,
  `hx-get` to the E2 endpoint), promo bar, footer, contact button, product card (badges, 2-image indicator when a
  gallery exists, truncated descriptor, swatches + "+N", price/old price, heart). Collectstatic hook doesn't fail
  without `dist/`.
- **Acceptance criteria:**
  - [ ] `npm ci && npm run build` in `internetshop/frontend/` exits 0, produces `shop/static/dist/.vite/manifest.json` (or `manifest.json` depending on Vite version), and `tsc --noEmit` reports no errors.
  - [ ] `python manage.py test` renders any page without a built `dist/` (dev_mode in tests).
  - [ ] GET `/` → HTML has `<a class="skip-link" href="#main">`, `<main id="main">`, `<link rel="canonical">`, `og:title`, the Vite bundle script tag.
  - [ ] Header: search button with `aria-label="Поиск"` and `aria-expanded`, cart link with `data-cart-count`, link to `/wishlist/` with `data-wishlist-count`, hamburger with `aria-controls`.
  - [ ] Promo bar renders only when `SiteSettings.promo_enabled=True` and text is non-empty; has a close button with `aria-label`.
  - [ ] Contact button is present on every page (incl. `/cart/checkout/`) and contains Telegram, WhatsApp and `tel:` links from `site_info`.
  - [ ] Product card: badge «Новинка»/«Хит»/«Скидка» from `is_new`/`is_bestseller`/`old_price>price`; with `old_price` there's an `<s>` with the old price; with >4 colors a "+N" is shown; the heart has `aria-pressed`.
  - [ ] Footer contains catalog category links, average rating and count of published reviews (block hidden when there are no reviews).
  - [ ] Existing smoke tests (home, static pages, PDP, 404) are green.
- **Tests:** `shop/tests/test_shell.py`, `shop/tests/test_smoke.py`
- **Manual check:** header/menu/search overlay at 375 / 768 / 1280 px; focus visible on all controls; promo bar closes and stays closed after reload.

### E2. Backend: fields, filters, wishlist, reviews, search, HTMX responses

- **What:** migration for `Product.is_new`, `is_bestseller`, `SiteSettings.promo_enabled/promo_text/promo_url`;
  admin (list_filter/list_editable) and `seed_demo`; module `shop/catalog_filters.py` (pure function
  `apply_filters(queryset, params) -> (queryset, active_filters)` + sorting); 24-per-page pagination preserving
  params; count endpoint `GET /catalog/count/`; `GET /search/suggest/?q=`; `shop/wishlist.py` +
  `POST /wishlist/toggle/<id>/`, `GET /wishlist/`; `wishlist` context processor; `POST /product/<slug>/review/`
  (`ReviewForm` + honeypot); `cart_add` returns the drawer fragment for HTMX; `POST /cart/undo/`; PDP color
  preselection from GET; 404 context with bestsellers; `Product.badges` (list of codes). Minimal unstyled templates
  for the new fragments/pages.
- **Acceptance criteria:**
  - [ ] Migration applies on a clean DB; `seed_demo` runs twice in a row without errors; demo data has at least 1 `is_new` and 1 `is_bestseller` product.
  - [ ] `/catalog/?color=<id>` → only products with that color; `?price_min=10000&price_max=50000` → prices in range; `?flag=sale` → only `old_price > price`; `?flag=new` → only `is_new`; `?category=a&category=b` → union of categories; `?price_min=abc` → 200 and the filter is ignored.
  - [ ] `?sort=price_asc` / `price_desc` → ordered by `price`; unknown `sort` → default ordering.
  - [ ] 30 products → page 1 has 24, `?page=2` has 6; pagination links preserve the other GET params.
  - [ ] `/catalog/<material>/<category>/` works as before (smoke), filters apply on top.
  - [ ] `GET /catalog/count/?…` (HTMX) → fragment with the number of matches for those params.
  - [ ] `GET /search/suggest/?q=крес` → at most 6 products, matching on name/sku/description; `q` shorter than 2 chars → empty fragment; only `is_available=True`.
  - [ ] `POST /wishlist/toggle/<id>/` twice → product added, then removed; HTMX response contains `aria-pressed="true"`/`"false"` and an updated counter (OOB); unknown id → 404; GET on toggle → 405.
  - [ ] `/wishlist/` shows only added and available products; empty wishlist → message + link to the catalog.
  - [ ] `POST /product/<slug>/review/` with valid data → `Review` with `is_published=False`, not shown on the PDP; with the honeypot filled → no review created; rating outside 1..5 → form error.
  - [ ] HTMX `POST /cart/add/<id>/` → 200 with a drawer fragment containing the product name and total; without HTMX/AJAX — the old redirect; the old AJAX-JSON format is preserved.
  - [ ] `POST /cart/remove/` then `POST /cart/undo/` → line restored with the same quantity and colors.
  - [ ] `/product/<slug>/?weave=<id>` with an available color → that swatch is marked `checked`; a foreign id is ignored.
  - [ ] Unknown URL → 404 with bestsellers in context (up to 8).
  - [ ] All existing cart/checkout/lead tests are green (order and Telegram contract unchanged).
- **Tests:** `shop/tests/test_catalog_filters.py`, `test_search.py`, `test_wishlist.py`, `test_reviews.py`, `test_cart_htmx.py`, `test_models.py`
- **Manual check:** —

### E3. Catalog and search (UI)

- **What:** `catalog_list.html` per UX.md §3: breadcrumbs → banner with H1 and 1–2 sentences → sticky "Filters" /
  "Sort" bar (dropdown, chevron) → grid (2 cols mobile, 3 tablet, 4 desktop) → numbered pagination → SEO text + FAQ
  accordion. Filter panel: accordion groups (Category, Material, Color swatches, Price, Length, Picks), sticky footer
  "N found" / "Reset" / "Apply". Empty result → message + bestsellers. Search suggestion fragments (row card: photo,
  name, price; "All results").
- **Acceptance criteria:**
  - [ ] Catalog HTML contains a `method="get"` filter form with "Apply" (submit) and "Reset" (link to the path without params), and a count element with `hx-get` to `/catalog/count/` and `aria-live="polite"`.
  - [ ] Active filters are reflected in markup (`checked` checkboxes, price field values) after applying.
  - [ ] Sorting is a `<select name="sort">` or a button with `aria-haspopup="listbox"`, current value selected.
  - [ ] Pagination is `<nav aria-label="Страницы">` with numbers; current page has `aria-current="page"`.
  - [ ] Empty result → «Ничего не найдено» message and a bestsellers block.
  - [ ] Without JS, filters and sorting work as a plain GET submit.
- **Tests:** `shop/tests/test_catalog_ui.py`
- **Manual check:** filter panel full-screen at 375 px, side panel at 1280 px; bar is sticky; focus is trapped in the panel and returns to the trigger on close (Esc closes); search suggestions appear after 2 characters.

### E4. Product page (UI)

- **What:** PDP per UX.md §4 within scope: gallery (main image + thumbnail strip with scroll progress, 3D as today),
  breadcrumbs, badge, name, heart, rating link to `#reviews`, price/old price, swatch groups «Плетение: *Графит*»,
  selection written to the URL, button «В корзину — <price> ₽» (loading state), «Оформить заявку», trust block,
  sticky mobile bar, accordions (Dimensions & specs, Materials & care, Delivery & warranty), "More from the
  collection"/related carousels with the same card, reviews (average score, list, "Write a review" button → HTMX form).
- **Acceptance criteria:**
  - [ ] The add button includes the product price in its text and `hx-post` to `cart_add`; the form also works without JS.
  - [ ] Swatches are radio groups with `<fieldset><legend>` per group; the «Плетение: <name>» label updates (markup check: element with `data-color-label`).
  - [ ] The rating link points to `#reviews`; section `id="reviews"` exists and shows the average score and number of published reviews.
  - [ ] Review form is present with name/rating/text fields and a hidden honeypot; a successful HTMX submit returns the moderation message.
  - [ ] Trust block next to the button shows the product's `warranty_years`.
  - [ ] With `model_3d`, `model-viewer` is loaded; without it — not (existing configurator tests green).
  - [ ] JSON-LD `Product` (name, offers.price, priceCurrency RUB, aggregateRating when reviews exist).
- **Tests:** `shop/tests/test_product_ui.py`, existing `ProductConfiguratorTests`
- **Manual check:** choosing a swatch changes the URL and survives reload; 3D recolors; sticky bar at 375 px; drawer after adding.

### E5. Cart, drawer, checkout, wishlist (UI)

- **What:** drawer (Alpine, dimmed backdrop, focus trap, Esc/X): «✓ Товар добавлен», lines (photo, name, color chips,
  "Remove", stepper − 1 +, line total), total, «Оформить заявку», «Продолжить покупки», «Вам может понравиться».
  `/cart/` page with the same blocks, toast with «Вернуть», empty state. `checkout.html`: reduced header (logo),
  order summary, form, "Need help?" footer, contact button. `order_success.html` with a next step (to the catalog).
  `wishlist.html` with a card grid.
- **Acceptance criteria:**
  - [ ] `/cart/checkout/` contains no main navigation (`nav[aria-label="Основная навигация"]`) and no search; contains the logo, phone and messenger links.
  - [ ] Drawer fragment: `role="dialog"`, `aria-modal="true"`, `aria-labelledby`, close button with `aria-label`.
  - [ ] Quantity stepper — buttons with `aria-label` «Уменьшить»/«Увеличить» and `hx-post` to `cart_update`; quantity 0 removes the line.
  - [ ] After removal on `/cart/` the response contains a toast with a `POST /cart/undo/` form («Вернуть»).
  - [ ] Empty cart → message, «Продолжить покупки» link to the catalog, recommendations block.
  - [ ] `/wishlist/` renders cards via the shared `_product_card.html`.
  - [ ] Existing checkout tests (Order + OrderItem creation, empty cart → redirect) are green.
- **Tests:** `shop/tests/test_cart_ui.py`, existing `CartTests`
- **Manual check:** drawer opens after "Add to cart", Tab stays inside, Esc closes, focus returns to the button; undo restores the line; checkout at 375 px.

### E6. Home, content pages, 404/500

- **What:** `home.html` in the order from "Assumptions"; content pages (about, B2B, designers, delivery, warranty,
  FAQ, contacts) moved to the new grid/components without changing copy or forms; 404 with bestsellers; 500 —
  static (no DB context).
- **Acceptance criteria:**
  - [ ] Home sections in `data-section` order: `hero`, `categories`, `collections`, `services`, `reviews`, `story`, `seo` (checked by order of occurrence).
  - [ ] Hero contains exactly one primary CTA (`.btn-primary`) and an H1.
  - [ ] Each content page has exactly one `<h1>` and breadcrumbs (except home).
  - [ ] B2B/designers/contacts forms save leads as before (existing lead test green).
  - [ ] 404 contains a heading, a link to the catalog and bestseller cards when available.
  - [ ] 500.html uses no tags requiring the DB/context processors.
- **Tests:** `shop/tests/test_pages_ui.py`, `test_smoke.py`
- **Manual check:** visual match to the brand at 3 widths; images have `alt`, lazy-loading below the fold.

### E7. Cleanup, docs, cross-cutting a11y/SEO

- **What:** delete the legacy CSS/JS and their includes; ensure nothing references the deleted files; update
  `CLAUDE.md` (setup with npm, stack, static layout), `docs/design-system.md` §1 (stack) and §7 (migration),
  `README.md`; cross-cutting test for a single `<h1>`, `lang="ru"`, canonical and meta description on all public pages.
- **Acceptance criteria:**
  - [ ] `grep` over templates finds no `css/variables.css`, `css/base.css`, `js/main.js`, `js/cart.js`, etc.; files deleted.
  - [ ] `npm run build` + `collectstatic --noinput` succeed.
  - [ ] Test: every public page from the sitemap + cart/checkout/wishlist → 200, exactly one `<h1>`, has `meta name="description"` and `link rel="canonical"`.
  - [ ] `CLAUDE.md` and `docs/design-system.md` describe the new stack; `DESIGN.md`/`UX.md` unchanged (`git diff` empty).
- **Tests:** `shop/tests/test_seo_a11y.py` + full run
- **Manual check:** —

## Design QA skills (tasteskill + ui-ux-pro-max) — rules and checks only

Both skills are used as **checklists and gates**, never as a source of visual direction. Brand values
(docs/design-system.md, variables.css) and DESIGN.md/UX.md win every conflict.

| Skill | Used | Banned in this project |
|---|---|---|
| `ui-ux-pro-max:ui-ux-pro-max` | `references/quick-reference.md` (UX guidelines: a11y, touch, layout shift, forms, navigation, motion) and the pre-delivery checklist in `references/pro-rules.md` | `search.py` style/palette/font/product-type picks |
| `design-taste-frontend` (tasteskill) | house rules (no gradients, no shadows at rest, no glass, no emoji, no monospace outside code, no index numbering, no tiny tracked uppercase labels, no eyebrow labels above headings, no styled accent word in headings, headings ≤ 2 lines, ≤ 2 typefaces); `scripts/lint.mjs` (static scan); `scripts/inspect.mjs` (browser measurement at 1440/768/390 + screenshots); `references/critique.md` for the look-and-fix round | `draw.mjs` directions, its palettes/type systems/section blueprints, `assets.mjs` stock imagery, the mandatory 8+ moving-elements motion layer |

Allow-list for brand-mandated or e-commerce-inherent exceptions (stored in `.taste-skill/direction.json`, read
automatically by `inspect.mjs`; for `lint.mjs` the same findings are treated as allowed):
`palette-claude`, `palette-terracotta`, `palette-cream` (ESTIVO brand: warm ground + terracotta accent),
`card-rows` (product grids), `few-pictures`, `no-real-pictures` (placeholders until owner uploads photos),
`no-footage` (no video in scope), `still-page` (motion per DESIGN.md durations, not tasteskill's quota). Every other
FAIL must be fixed; each WARN is fixed or justified in one sentence in the worker report.
Note: the "no eyebrow" rule removes the current `.eyebrow` labels above headings — accepted deviation from the
existing look; `docs/design-system.md` §3 is updated in E7.

Where they run:
- **Workers on UI epics (E1, E3–E6):** read both references before building; before committing run
  `node ~/.claude/skills/design-taste-frontend/scripts/lint.mjs <own templates + own CSS/TS>` and walk the
  ui-ux-pro-max pre-delivery checklist for own pages; report results.
- **Reviewer:** reads `pro-rules.md` checklist + tasteskill house rules by path and checks the diff against them;
  reruns `lint.mjs` on the epic's files.
- **Orchestrator at integration:** `inspect.mjs` on the running app (home, catalog, PDP, cart, checkout, 404) at
  three widths, one critique round with `references/critique.md`, fix top issues (max 3 rounds).
- Added acceptance line for E1, E3, E4, E5, E6: "`lint.mjs` on the epic's files has no FAIL outside the allow-list;
  ui-ux-pro-max pre-delivery checklist walked and reported."

## Test contract interfaces (fixed by the tests, binding for workers)

Tests live in `internetshop/shop/tests/` (one file per epic, classes prefixed `E1…`–`E7…`); `helpers.py` has a
mini-DOM parser and `make_product()`. Run one epic: `python manage.py test shop.tests.test_<name>`.

- Markers: promo bar `data-promo-bar`; contact button container `data-contact-button`; footer rating block
  `data-reviews-summary`; wishlist toggle response includes an `hx-swap-oob` element carrying `data-wishlist-count`.
- Card swatches: first 4 shown, then `+N` where N = total − 4 (no `+N` at exactly 4).
- `Product.badges` → list of codes `'new'`, `'bestseller'`, `'sale'` (property or method).
- Review form fields `author`, `rating`, `usage_duration`, `text`; honeypot `name="website"`, hidden; success text
  contains «модерац».
- 404 context key `bestsellers` (≤ 8, falls back to `is_featured`).
- `apply_filters(params: QueryDict, …)` returns a 2-tuple; views keep `page_obj` in context.
- **`/catalog/count/` must be registered before `catalog/<slug:material_slug>/`** (otherwise the slug route catches it).
- Vite tag: `<script type="module">` whose src contains `main` (e.g. `{% vite_asset 'src/main.ts' %}`).
- Undo: element with `hx-post="/cart/undo/"` or a POST form to `/cart/undo/`, text «Вернуть».
- Count element: the `hx-get` element, a descendant, or its `hx-target` has `aria-live="polite"`.
- Empty `/search/suggest/` (q < 2 chars) returns an empty body.
- With `HX-Request`, `cart_update`/`cart_remove` return 200 HTML (not 302); PDP heart has
  `hx-post="/wishlist/toggle/<id>/"` and `aria-pressed`.
- Existing pieces relied on: nav `aria-label="Основная навигация"`, `partials/_breadcrumbs.html`, session key
  `wishlist` holding int ids.

Orchestrator decisions on ambiguities raised by the test writer:
- Multiple `color` values → union (OR), like `category`; no duplicate products.
- `sort=new` → `-is_new`, then newest first (`-id`).
- Price/length bounds are inclusive. Unknown `category`/`material` slugs in GET params are ignored.
- The review form is in the initial PDP HTML (may be visually collapsed with Alpine); the "Write a review" button reveals it.
- "Apply"/"Reset" are rendered in Russian («Применить» / «Сбросить»).
- Existing test count is 16, not 15.

## Left for integration (orchestrator)

- Resolve trivial merge conflicts, run `npm run build` + `collectstatic` in the main checkout.
- Final app launch and browser check (375 / 768 / 1280 px): navigation, search, filters, PDP, drawer, cart,
  checkout, wishlist, review, 404; no console errors; no 500s in server logs.
- Contrast and focus check on key pairs (axe/manual) — report with actual results.

## Risks and rollback

| Risk | Mitigation / rollback |
|---|---|
| Node toolchain becomes mandatory for deploy (previously Python only) | `dist/` built by a command documented in README/CLAUDE.md; rollback — revert the branch; legacy CSS/JS stay in history until E7 |
| Tailwind preflight breaks not-yet-migrated pages between waves | Acceptable inside the branch; final state verified at integration |
| Conflicts in wave-2 shared files (`main.ts`, styles) | E1 sets up auto-import by folder; each epic writes only its own files |
| `django-vite` in tests without a manifest | dev_mode in tests (E1 criterion) |
| `CompressedManifestStaticFilesStorage` fails on missing `url()` in built CSS | `collectstatic` in E1/E7 criteria |
| Tests can't run because of the Postgres password | Blocker before phase 3; user fixes it |
| E2 size (all Python in one epic) | Clear criteria; after 3 failed attempts — split into E2a (filters/search) and E2b (wishlist/reviews/HTMX cart) |
| Branch is based on `feat/session-cart-checkout-3d`, not fully merged into master (commits `5d34429`, `0143b33`) | A PR to master will include them; merge decision is the user's |

Full rollback: the branch is isolated, master is untouched; `git switch feat/session-cart-checkout-3d`. The E2
migration is reversible (`migrate shop 0005`).

## Definition of done (whole task)

- [ ] Full project test suite green (`python manage.py test`), `npm run build` without errors
- [ ] App launched, all scenarios from "Left for integration" verified in the browser at three widths
- [ ] No browser console errors, no 500s in the server log
- [ ] Cart orders and leads are still written to the DB; Telegram stays best-effort
- [ ] `DESIGN.md`, `UX.md` unchanged; master not touched without approval

## Log

- 2026-10-16 spec created (draft). Uncommitted work committed as `0143b33`, branch `feat/furniture-store-redesign`.
- 2026-10-16 spec rewritten in English at the user's request.
- 2026-10-16 test contract written: 179 tests (16 moved + 163 new). Diagnostic run on SQLite: 58 pass (all 16 existing), 113 red for missing fields/routes/markup. Real Postgres run pending PG upgrade (local server is 9.5; Django 5.0 needs 12+).
- 2026-10-16 Design QA skills section added (tasteskill + ui-ux-pro-max, rules/gates only, allow-list in .taste-skill/direction.json).
- 2026-10-16 E2 done: APPROVE on 1st attempt, merged 6ed60ad. Suite after merge (SQLite): 125/179. Red in E2 files only due to SQLite Cyrillic icontains (verify on PG) and templates owned by E3/E4.
- 2026-10-16 E1 worker done (1 attempt), in review. Orchestrator scope additions: E1 registers `shop.context_processors.wishlist` in settings and adds `shop/templatetags/shop_tags.py` (footer data).
- 2026-10-16 Reassigned from E1: card 2-image indicator → E3 (with `prefetch_related('gallery', 'available_colors')`); restyle `partials/htmx/_wishlist_toggle.html` to match the card heart (`icon-btn product-card__heart`, SVG) → E5. E4 must render PDP swatch `checked` from `selected_colors`; E3 must build pagination links from `querystring`. E7 also removes the `@layer legacy` imports in base.html.
- 2026-10-16 Local PostgreSQL 18 on port 5433 (9.5 left on 5432). Installed Django is 5.2.18 while requirements.txt pins 5.0.6 — flag for user.
- 2026-10-16 E1 done: APPROVE on 1st attempt, merged. Suite (SQLite) 144/179; all 35 red in wave 2/3 files. Django pin bumped 5.0.6 → 5.2.18 (LTS) by user decision: django-htmx 1.29 requires Django ≥ 5.2; 5.2.18 is what all tests ran on. Reviewer nits deferred: promo-bar flash on reload + promo_url scheme validator + lead-form aria-describedby → E7; search overlay focus trap and hx-vals js: eval → E3 (may edit the search-overlay part of _header.html only); per-card available_colors query → views prefetch in E3.
- 2026-10-16 Postgres 18.4 (port 5433) ready: migrate + seed_demo + collectstatic OK. Full suite on PG: 146/179; test_search 8/8 (Cyrillic OK). 33 red, all in wave 2/3 files. Workers from now on run tests on Postgres.
- 2026-10-16 E6 done: APPROVE on 1st attempt, merged. Suite on PG 150/179. E4 and E3 workers done (1 attempt each), in review. E4 added `review_stats` tag to shop_tags.py (accepted); E3 added `bestsellers` on empty catalog in views.py (pending review).
- Integration backlog (orchestrator): home "categories" section → pass materials/categories in `views.home` and link real CTAs (E6 used flag links); content-page `breadcrumbs` from views; 404 «Ошибка 404» eyebrow-like line; home hero H1 wording (ask user); trust facts (warranty/delivery) missing on home; unused `production_steps` in views.home; catalog FAQ duplicated in template vs FAQ_ITEMS; gallery prefetch on home/wishlist/PDP-related; `#cart-drawer-slot` placement (PDP form vs base.html) reconciled with E5.
- 2026-10-16 E3 done: APPROVE on 1st attempt, merged; suite on PG 162/179. Accepted out-of-grant `bestsellers` in `_catalog_context`. E4 review: CHANGES (mobile contact button covers sticky «В корзину»; + nested form for drawer slot, sendError, url tag, triple stats query) → attempt 2 in progress. E5 in review.
- Integration backlog additions: catalog FAQ hard-coded (pass `faq_items`); breadcrumbs from views everywhere (catalog builds its own nav); `_bestsellers()` should prefetch `available_colors`, `gallery`; `<noscript>` submit next to sort select; move `html.js` flag script to base.html; shared scroll-lock helper (filter panel / search overlay / drawer); E7 must port lead-form phone mask + double-submit guard from legacy forms.js to TS.
- 2026-10-16 E4 done: CHANGES on 1st review (mobile sticky bar covered by contact button + 4 minor), APPROVE on 2nd; merged. Suite on PG 173/179 (remaining: 4 E5, 2 E7). E5: APPROVE; worker fixing drawer close race + focus loss before merge. Backlog: sticky-bar bottom padding on body instead of [data-pdp]; non-JS undo via messages fallback.
- 2026-10-16 E5 done: APPROVE on 1st review; drawer close-race + focus-loss fixed in a follow-up commit (orchestrator checked the delta), merged. Suite on PG 177/179 (only E7 red). Wave 2 complete.
- 2026-10-16 E7 scope extended with the integration backlog (no parallel epics remain): views pass `breadcrumbs` + home materials/categories + catalog `faq_items`, drop unused `production_steps`; prefetch on `_bestsellers()`/home/wishlist/PDP-related; html.js flag in base.html; promo-bar flash + `promo_url` scheme validator; lead-form aria-describedby/aria-invalid; port legacy forms.js (phone mask, `data-once`) + main.js behaviour to the Vite bundle; 404 «Ошибка 404» line; `<noscript>` sort submit; sticky-bar padding on body; shared scroll-lock helper; non-JS undo via messages; safe referer redirect in wishlist_toggle/cart_add. Hero H1 copy waits for the user.
- 2026-10-16 E7 done after 3 attempts (1: CHANGES — BEL control char in CLAUDE.md/README; 2: orchestrator found next=foo → 500 in safe-redirect helper; 3: fixed, verified with test client). Merged. Full gates on feature branch: 179/179 on PG, npm build, collectstatic, makemigrations --check clean, DESIGN.md/UX.md unchanged. Granted exception: lead_create redirect uses the safe helper (open redirect + 500 fix).
- 2026-10-16 Integration (orchestrator): app run on PG18 via runserver. Found + fixed: (1) body typography/reset lost when legacy base.css was deleted (Times New Roman 400, body margin) → ported reset into `@layer base` (3679ca8); (2) PDP focal-point FAIL + eyebrow above title → portrait/square gallery, removed meta line (be610c8). Verified in browser: all public pages 200 with one h1, 404 page, no server errors; PDP swatch → URL `?weave=&cushion=` + label; add to cart → drawer (dialog, focus inside, main inert), Esc closes, focus returns, scroll unlocked; wishlist heart aria-pressed + header counter; search overlay suggestions (Cyrillic); filter panel full-screen modal at mobile with live count, Esc + focus return, unapplied changes discarded; cart remove → «Вернуть» → line restored with colors. tasteskill inspect.mjs: home/catalog/PDP/cart/contacts — remaining findings are defensible (covered-text = prices under sticky header at one scroll step; "eyebrow" = adjacency of last pill/accordion/label to next section heading; mixed-font headline = Cormorant price figures). Not done: checkout/lead form submission in browser (would send a real Telegram message — covered by tests), visual pass at exact 768/1280 in-pane (inspector screenshots at 1440/768/390 used instead), real-device check, favicon (none exists). Note: after `npm run build` the dev server must be restarted (django-vite caches the manifest).
