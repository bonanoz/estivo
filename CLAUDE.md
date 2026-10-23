# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
общайся только на русском языке, несмотря на английский язык в этом файле!!

## Project overview

Django site for ESTIVO — a handmade premium woven-furniture brand (rope/rattan/veneer/HPL), migrated
from a Tilda site (estivo63.ru) to a custom Django build. Single `shop` app. The business model is
still lead-generation (no online payment): a visitor builds a **session cart**, submits it as one
multi-item request, and a manager follows up manually; Telegram gets a best-effort notification.
Consultation/B2B leads use the separate `Lead` path. Orders and leads are always persisted to Postgres
first; Telegram delivery is never allowed to block or lose data.

## Setup and commands

Project root for Django commands is `internetshop/` (the inner directory containing `manage.py`), not the repo root.
Stack: Django **5.2.18** (LTS, pinned in `requirements.txt`; django-htmx needs >=5.2), Tailwind CSS v4 + htmx +
Alpine.js + TypeScript built with Vite (`internetshop/frontend/`), django-vite in templates.

```bash
cd internetshop
python -m venv venv && venv\Scripts\activate   # Windows
pip install -r ../requirements.txt
cd frontend && npm ci && npm run build && cd ..   # Vite build -> shop/static/dist/ (before collectstatic!)
python manage.py migrate
python manage.py seed_demo        # demo Material/Category/Collection/Product/Review data
python manage.py createsuperuser
python manage.py collectstatic --noinput   # required once — ManifestStaticFilesStorage fails template
                                   # rendering (missing manifest entry) if static isn't collected
python manage.py runserver
```

- Run all tests: `python manage.py test` (from `internetshop/`; 179 tests in `shop/tests/`, one file per area,
  needs the Postgres from `.env`; `django_vite` runs in dev mode under `test`, so no built `dist/` is needed).
- Run a single test: `python manage.py test shop.tests.test_smoke.<Class>.<test_method>`
- No Python linter/formatter is configured. Frontend: `npm run build` runs `tsc --noEmit` + `vite build`.
- Frontend dev: `VITE_DEV_MODE=1` makes django-vite load the Vite dev server (`npm run dev`, port 5173) with HMR
  instead of reading the manifest. Without it (production-like) templates need `npm run build` first.
- Static changes (CSS/JS/TS/fonts) need `npm run build` (for `frontend/src`) and
  `python manage.py collectstatic --noinput` before they show up under `CompressedManifestStaticFilesStorage` —
  templates reference the manifest, not raw files.
- `CompressedManifestStaticFilesStorage` **fails collectstatic hard** if a CSS `url()` points at a
  missing file (e.g. a font). `shop/static/fonts/gilroy/` holds the real `Gilroy-{Light,Regular,Medium,SemiBold,Bold,ExtraBold}.woff2`
  referenced by `@font-face` — don't delete or rename them.
- Design QA gates before merging UI work: `node ~/.claude/skills/design-taste-frontend/scripts/lint.mjs
  internetshop/shop/templates internetshop/frontend/src` must show no FAIL outside the allow-list
  (palette-claude/terracotta/cream, card-rows, few-pictures, no-real-pictures, no-footage, still-page; stored in
  `.taste-skill/direction.json`, see `docs/design-system.md` §7), plus the ui-ux-pro-max pre-delivery checklist;
  `shop/tests/test_design_tokens.py` guards the tokens and bans (shadows, gradients, <14px, Gilroy weights outside 300–800).
  Design source of truth: `docs/design-system/estivo-tilda/` (owner decision 2026-10-22; read-only except
  `MAPPING.md`, which maps its tokens/`es-*` components onto the project), applied in `docs/design-system.md`.

### Required environment (`.env` in `internetshop/`, never committed)

- `BOT_TOKEN` — Telegram bot token from @BotFather
- `CHAT_ID` — Telegram chat/user id that receives order/lead notifications (the recipient must have
  sent `/start` to the bot first, or the Telegram API returns "chat not found")
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` — PostgreSQL connection (PostgreSQL >=12 is required
  by Django 5.2; set `DB_PORT` to your server's port, e.g. 5433 if a second PostgreSQL already uses 5432)
- `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS` — standard Django settings, read via `os.environ` with dev-friendly defaults
- `VITE_DEV_MODE=1` — optional, use the Vite dev server instead of the built manifest
- `SITE_URL` — public domain, used for sitemap/canonical/OG absolute URLs (defaults to `https://estivo63.ru`)

The project uses PostgreSQL (`psycopg2-binary`), not SQLite, despite a stray `db.sqlite3` in the tree.
`settings.py` forces `PGCLIENTENCODING=UTF8` before connecting — Windows locales (e.g. `Russian_Russia.1251`)
otherwise cause `UnicodeDecodeError` in psycopg2. `LANGUAGE_CODE='ru'`, `TIME_ZONE='Europe/Samara'`.

## Architecture

- `internetshop/internetshop/` — Django project config (`settings.py`, `urls.py`, `wsgi.py`/`asgi.py`).
  `urls.py` wires `handler404`, `sitemap.xml` (`shop/sitemaps.py`), and `robots.txt`.
- `internetshop/shop/` — the only app, flat structure (no sub-apps, no DRF). Models, views, forms,
  templates, and static assets all live here.

### Data model (`shop/models.py`)

`Material` (роуп/ротанг/шпон/HPL) and `Category` (кресла/диваны/…) are independent lookup tables —
a `Category` is not tied to one `Material` (tables come in HPL, veneer, etc.), so `Product` carries
both FKs separately. `Collection` groups products for homepage/showcase curation (`is_featured`).

`Product` uses a `slug` (auto-generated via `shop.utils.ru_slugify`, **not** Django's stock `slugify`
with `allow_unicode` — URLs must stay ASCII like the old Tilda site's `/kreslo`, `/divan`) and
`main_image`/`ProductImage` gallery (`ImageField`, not the old `image_url` string). Price fields:
`price` ("от"), `old_price` (for sales), plus spec fields (`max_load_kg`, `warranty_years`,
`temp_min_c`/`temp_max_c`, `length_cm`/`width_cm`/`height_cm`/`weight_kg` dimensions) used directly in
templates — no separate "specs" model. `model_3d` (`.glb` FileField) + `model_3d_poster` drive the
3D configurator (see Templates), falling back to the 2D gallery when absent.

`ColorOption` is a single site-wide palette of finish colors keyed by `finish_type`
(`weave`/`cushion`/`frame`). A product opts into colors via M2M `Product.available_colors`;
`Product.colors_by_type()` groups them (Плетение/Подушки/Каркас) and **skips empty groups** — a rattan
piece with no separate frame simply shows no "Каркас" group. Colors never affect price.

`Order`/`OrderItem` and `Lead` are the write paths from the public site:
- `Order` is a multi-item request built at `checkout` from the session cart. Its `product` FK is now
  nullable/legacy; new orders keep items in `OrderItem` (product + quantity + `unit_price` snapshot +
  `selected_colors` JSON snapshot like `{"Плетение": "Графит"}`). `Order.total_price` is set by
  `recalc_total()` (sum of line totals) after items are created — snapshots so historical orders don't
  drift when prices change.
- `Lead` — the shared model behind every contact form (`lead_type`: private/designer/b2b),
  used by the B2B page, designer page, and general contact page via the shared `_lead_page()` view helper.

Both have a `telegram_notified` flag that is only set `True` when the Telegram send actually succeeds
(`shop.utils.notify_telegram` returns a bool, never raises) — the DB write always happens regardless
of Telegram outcome, so a bad token/blocked chat never loses a submission.

`Review` requires `is_published=True` to surface anywhere; nothing filters/moderates them automatically.

### Request flow (`shop/views.py` + `shop/urls.py`)

Catalog browsing nests by material then category: `catalog_list` → `catalog_by_material` →
`catalog_by_category`, all rendering the same `catalog_list.html` with different queryset filters and
`meta_title`/`meta_description` context (SEO copy follows the `"{Категория} из {материал}"` pattern
scraped from the original Tilda site). `product_detail` is slug-based.

Cart flow (`shop/cart.py` + cart views): the `Cart` class wraps `request.session['cart']`. A line is
keyed by product **plus chosen colors**, so the same product in different colors are separate lines
(`shop/cart.py:_line_id`). Views: `cart_add` (validates colors against `available_colors` via
`_valid_colors`, then HTMX drawer fragment, legacy AJAX-JSON, or redirect to a safe `next`), `cart_update`, `cart_remove`, `cart_detail`, and
`checkout` (creates `Order` + `OrderItem`s, `recalc_total`, Telegram, clears cart → `order_success`).
The product page's "В корзину" button posts via htmx and opens the cart drawer; removing a line without JS stores a
session notice so `cart_detail` still offers «Вернуть» (`cart_undo`); "Оформить заявку" posts with `name=checkout` and
`data-no-ajax` so the server redirects straight to checkout. There is no more `order_create`.

Lead-capturing pages (`b2b_page`, `designers_page`, `contacts_page`) all funnel through
`_lead_page(request, template_name, lead_type)` — same POST/validate/save/notify logic, differing
only in template and default `lead_type`. `lead_create` is a separate POST-only endpoint for forms
embedded on pages that don't render their own `LeadForm` context (e.g. a hero CTA elsewhere).

`shop/context_processors.py` injects `site_info` (brand contact/socials/legal) **and** `cart` into
every template — that's why `_header.html` shows the cart counter and `base.html`/`_footer.html`
reference `site_info.*` without any view passing them explicitly.

### Templates and static

`base.html` + `partials/_header.html` / `_footer.html` / `_product_card.html` / `_lead_form.html` /
`_cta_section.html` / `_breadcrumbs.html` / `_promo_bar.html` / `_chat_button.html` / `_pagination.html` are the
shared building blocks; HTMX fragments live in `partials/htmx/`. Page templates extend `base.html` and override
`meta_title`/`meta_description`/`og_*` blocks (defaults carry the real ESTIVO SEO copy from Tilda). Content pages
get `breadcrumbs` (list of `(label, url|None)`) from their views and render `partials/_breadcrumbs.html`.
`base.html` sets the `html.js` flag and the promo-dismissed class in `<head>` before first paint.

`shop/templatetags/shop_tags.py` provides `footer_data` and `review_stats`; context processors inject
`site_info`, `site_settings` (singleton `SiteSettings`: hero/about images, promo bar with validated `promo_url`),
`cart` and `wishlist` into every template.

**Frontend (`internetshop/frontend/`)**: Vite entry `src/main.ts` imports `styles/main.css` (Tailwind v4: `@theme`
tokens, `@layer base/components`; page CSS in `styles/{catalog,product,cart,pages}.css`), registers htmx and
Alpine, and auto-imports every `src/<feature>/index.ts` (`cart` drawer, `catalog` filter panel/focus-trap,
`product` gallery/variants/sticky bar, `forms` phone mask + `form[data-once]` double-submit guard, `lib`
`$scrollLock` helper shared by overlays). Output goes to `shop/static/dist/` (gitignored build artefact, read via
the Vite manifest). The legacy hand-written CSS/JS were removed; only `shop/static/js/vendor/model-viewer.min.js`
remains, loaded as an ES module on PDPs that have a `model_3d`.

Interactions are progressive enhancement: filters/sort/cart/wishlist/undo work as plain GET/POST+redirect
without JS; htmx and Alpine upgrade them (cart drawer, live filter count, search suggestions, wishlist heart).

Catalog filters/sorting live in `shop/catalog_filters.py` (`apply_filters`, `apply_sort`, `SORT_CHOICES`; query
params `category`, `material`, `color`, `price_min/max`, `length_min/max`, `flag`, `sort`); the wishlist is a
session-backed `shop/wishlist.py::Wishlist` with `wishlist_toggle` (HTMX fragment or safe redirect).

The 3D configurator uses Google's `<model-viewer>`, vendored at `shop/static/js/vendor/model-viewer.min.js`.
The color swatch handling in `frontend/src/product/variants.ts` maps swatches to `.glb` materials **by name** —
materials must be named `weave` / `cushion` / `frame` (same strings as `finish_type`). When re-vendoring
model-viewer, strip its trailing `//# sourceMappingURL=` comment or `collectstatic` fails on the missing `.map`.

Typography: headings use **Cormorant Garamond** (Google Fonts). Body/UI text uses **Gilroy**, which
is a paid font; the owner has a license for weights 300–800 (confirmed 23.10.2026, files from their Tilda
account). Defaults stay `--weight-body-regular` (300) / `--weight-body-bold` (800); 400–700 are available
when the estivo-tilda design calls for them (the live Tilda site uses 400/500). The `.woff2` files live in
`shop/static/fonts/gilroy/`; if they fail to load, `--font-body` falls back to `"Helvetica Neue", Arial`.

Product/collection images are placeholders (`shop/static/img/placeholders/*.svg`) until real photos
are uploaded through the admin — `main_image`/`cover_image` are `blank=True`, and templates always
check `{% if product.main_image %}` before falling back to the placeholder.

### Admin and demo data

`shop/admin.py` registers every model with `list_display`/`list_filter`/`search_fields` — this is the
intended day-to-day content tool for the site owner (uploading photos, adjusting prices, working
Order/Lead queues), not just a debug view. `ProductAdmin` uses `filter_horizontal` for
`available_colors`; `OrderAdmin` shows read-only `OrderItem` inlines. `shop/management/commands/seed_demo.py`
seeds Material/Category/Collection/Product/Review/`ColorOption` rows (plus dimensions and per-product
color bindings) for local development; safe to rerun (`get_or_create`, colors/dimensions re-applied
each run).

Media (uploaded photos, `.glb` models) lives under `MEDIA_ROOT` (`media/`). `settings.STORAGES` must
define **both** `default` (FileSystemStorage) and `staticfiles` — omitting `default` makes any
`<file>.url` raise `InvalidStorageError` (surfaces only once a real image/model is uploaded).

### Payment

There is intentionally no online payment integration. `Order.payment_status` exists as a future
extension point (see the `# TODO` comment above it in `models.py`) but wiring a real provider
(YooKassa/etc.) requires the site owner's own merchant account — don't add SDKs or webhook views for
this speculatively.
