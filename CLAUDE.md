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

- Run all tests: `python manage.py test` (from `internetshop/`; ~600 tests in `shop/tests/`, one file per area,
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
  The design is described in `docs/design-system.md` alone (owner approved the grid/typography/button refresh
  2026-10-29, `docs/design-system/proposals/2026-10-28-ui-refresh.md`): content width `--container` 1360px on 12
  columns, side padding `--page-pad` outside it (`.page-container`), one sentence-case heading scale, `.btn-primary`
  only for the request action. `docs/design-system/estivo-tilda/` is an archive of the Tilda look (colors and fonts
  came from there); its sizes and components no longer apply.
- Overrides the global "UI references" rule: here only **Lucide** applies (copy the SVG inline, `stroke-width="1.5"`,
  no npm package) plus **React Aria / Radix UI** as an a11y/behaviour reference only. Don't pull shadcn/ui, Magic UI,
  Aceternity, Motion/Motion Primitives, GSAP, Anime.js, Uiverse, mapcn, Spline — React stack or banned
  shadows/gradients/hover transforms (`docs/design-system.md` §3).

### Required environment (`.env` in `internetshop/`, never committed)

- `BOT_TOKEN` — Telegram bot token from @BotFather
- `CHAT_ID` — Telegram chat/user id that receives order/lead notifications (the recipient must have
  sent `/start` to the bot first, or the Telegram API returns "chat not found")
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` — PostgreSQL connection (PostgreSQL >=12 is required
  by Django 5.2; set `DB_PORT` to your server's port, e.g. 5433 if a second PostgreSQL already uses 5432)
- `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS` — standard Django settings, read via `os.environ` with dev-friendly defaults
- `VITE_DEV_MODE=1` — optional, use the Vite dev server instead of the built manifest
- `SITE_URL` — public domain, used for sitemap/canonical/OG absolute URLs (defaults to `https://estivo63.ru`)
- `SEO_NOINDEX=True` — demo stand only (set in `render.yaml` for estivo.onrender.com): every response gets
  `X-Robots-Tag: noindex, nofollow` (`shop.middleware.noindex_header`) so the demo isn't indexed as a duplicate of
  the live site; robots.txt stays crawlable so bots can see the header. Remove when the real domain moves here.

The project uses PostgreSQL (`psycopg2-binary`), not SQLite, despite a stray `db.sqlite3` in the tree.
`settings.py` forces `PGCLIENTENCODING=UTF8` before connecting — Windows locales (e.g. `Russian_Russia.1251`)
otherwise cause `UnicodeDecodeError` in psycopg2. `LANGUAGE_CODE='ru'`, `TIME_ZONE='Europe/Samara'`.

## Architecture

- `internetshop/internetshop/` — Django project config (`settings.py`, `urls.py`, `wsgi.py`/`asgi.py`).
  `urls.py` wires `handler404`, `sitemap.xml` (`shop/sitemaps.py`), `robots.txt`, `llms.txt` (company summary for AI
  assistants: facts, catalog sections, FAQ — keep its facts in sync with the pages) and `/favicon.ico` (302 to
  `static/img/favicon.svg`).
- `internetshop/shop/` — the only app, flat structure (no sub-apps, no DRF). Models, views, forms,
  templates, and static assets all live here.

### Data model (`shop/models.py`)

`Material` (роуп/ротанг/шпон/HPL) and `Category` (кресла/диваны/…) are independent lookup tables —
a `Category` is not tied to one `Material` (tables come in HPL, veneer, etc.), so `Product` carries
both FKs separately.

Collections (Милан/Бари/Асти…) group products for `/kollekcii/` and `/kollekcii/<slug>/`: `Product.collections` is M2M
(one table can sit in several collections), `Product.zone` is an FK to the `Zone` lookup (Обеденная группа, Лаунж-зона,
editable in the admin) — a collection page renders one section per zone, products without a zone go last under
«Ещё в коллекции»; collections without shown products are hidden and 404. `Collection.is_featured` is unused.
Migration `0018_collections_data` seeded the zones, `TabletopType` and the three collections from product names.

`ProductVariant` (size text + optional `TabletopType` + price) is the per-product price variant (tables: size ×
tabletop). With variants, `Product.price` is the cheapest variant, kept in sync by `Product.sync_price_from_variants()`
from `ProductVariant.save()/delete()` and `ProductAdmin.save_related` (a manual price is overwritten); «Включить
скидку» skips products with variants.

`Product` uses a `slug` (auto-generated via `shop.utils.ru_slugify`, **not** Django's stock `slugify`
with `allow_unicode` — URLs must stay ASCII like the old Tilda site's `/kreslo`, `/divan`; the admin has no
`prepopulated_fields`, its `SlugFromNameForm` fills an empty slug with `ru_slugify(name)` before the uniqueness check) and
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
  `selected_colors` JSON snapshot like `{"Размер": "160×90 см", "Столешница": "Стекло", "Плетение": "Графит"}`;
  `OrderItem.from_db` restores that key order because Postgres jsonb sorts keys). `Order.total_price` is set by
  `recalc_total()` (sum of line totals) after items are created — snapshots so historical orders don't
  drift when prices change.
- `Lead` — the shared model behind every contact form (`lead_type`: private/designer/b2b),
  used by the B2B page, designer page, and general contact page via the shared `_lead_page()` view helper.

Both have a `telegram_notified` flag that is only set `True` when the Telegram send actually succeeds
(`shop.utils.notify_telegram` returns a bool, never raises) — the DB write always happens regardless
of Telegram outcome, so a bad token/blocked chat never loses a submission. The bot is created with
`validate_token=False`, so an empty or malformed `BOT_TOKEN` doesn't break imports or `migrate`; a failed send is
logged as WARNING to the `shop` logger with a label like «заявка №N» and a scrubbed traceback (no message text,
token or URL — they carry personal data). `LOGGING` sends `django` and `shop` WARNING+ to the console.
`throttle_post` (5 POST / 10 min per IP) counts only successful responses: 3xx or `response.throttle_success = True`.
The admin login is wrapped with `throttle_post(count_failures=True)` in `shop/admin.py`: 5 failed logins per IP per
10 min, then 429.

`Review` requires `is_published=True` to surface anywhere; nothing filters/moderates them automatically.

### Request flow (`shop/views.py` + `shop/urls.py`)

Catalog browsing nests by material then category: `catalog_list` → `catalog_by_material` →
`catalog_by_category`, all rendering the same `catalog_list.html` with different queryset filters and
`meta_title`/`meta_description` context (SEO copy follows the `"{Категория} из {материал}"` pattern
scraped from the original Tilda site). `product_detail` is slug-based.

Cart flow (`shop/cart.py` + cart views): the `Cart` class wraps `request.session['cart']`. A line is
keyed by product **plus variant plus chosen colors**, so the same product in different colors or sizes are separate
lines (`shop/cart.py:_line_id`; lines without a variant keep the old `<pid>:<colors>` key). The line price is read
from the DB variant on every render, never from the client; a deleted variant drops its line. Views: `cart_add`
(validates colors against `available_colors` via `_valid_colors` and the `variant` field via `_pick_variant` — a
foreign/missing id falls back to the first variant — then HTMX drawer fragment or redirect to a safe `next`), `cart_update`, `cart_remove`, `cart_detail`, and
`checkout` (creates `Order` + `OrderItem`s, `recalc_total`, Telegram, clears cart → `order_success`).
The product page's "В корзину" button posts via htmx and opens the cart drawer; removing a line without JS stores a
session notice so `cart_detail` still offers «Вернуть» (`cart_undo`); "Оформить заявку" posts with `name=checkout` and
`data-no-ajax` so the server redirects straight to checkout. There is no more `order_create`.

`FAQ_ITEMS` (views.py) feeds /faq/ in full (plus `FAQPage` JSON-LD) but the catalog shows only the first
`CATALOG_FAQ_COUNT`, so 24 catalog pages don't repeat one text. `materials_compare_page` (/roup-ili-rotang/) is a
roup-vs-rattan comparison table; its facts, like the extra FAQ answers, were confirmed by the owner on 05.11.2026.

Lead-capturing pages (`b2b_page`, `designers_page`, `contacts_page`) all funnel through
`_lead_page(request, template_name, lead_type)` — same POST/validate/save/notify logic, differing
only in template and default `lead_type`. There is no separate `lead_create` endpoint.

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

`shop/templatetags/shop_tags.py` provides `footer_data`, `catalog_sections`, `review_stats` and the JSON-LD tags
`organization_ld` (home), `faq_ld` (/faq/), `breadcrumbs_ld` (inside `_breadcrumbs.html`) — `Product` JSON-LD stays
inline in `product_detail.html`. Product meta/og/JSON-LD description comes from the `seo_description` filter
(short_description or name + material + size, then price/warranty/term) — `description` often holds a Tilda price list. Cart, wishlist, checkout and catalog search results carry `noindex, follow`; context processors inject
`site_info`, `site_settings` (singleton `SiteSettings`: hero/about images, promo bar with validated `promo_url`),
`cart` and `wishlist` into every template.

**Frontend (`internetshop/frontend/`)**: Vite entry `src/main.ts` imports `styles/main.css` (Tailwind v4: `@theme`
tokens, `@layer base/components`; page CSS in `styles/{catalog,product,cart,pages,home,request}.css`), registers htmx and
Alpine, and auto-imports every `src/<feature>/index.ts` (`cart` drawer, `catalog` filter panel/focus-trap,
`product` gallery/variants/sticky bar, `forms` phone mask + `form[data-once]` double-submit guard, `lib`
`$scrollLock` helper shared by overlays, `motion` scroll reveal + counter/heart bump, `htmx-errors` toast for failed
htmx requests (429/403/network); page view transitions and
accordion easing are CSS-only at the end of `main.css`, all off under `prefers-reduced-motion`). Output goes to `shop/static/dist/` (gitignored build artefact, read via
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

Typography: headings use **Cormorant Garamond** (npm `@fontsource/cormorant-garamond`, cyrillic+latin 500/600
imported in `main.ts`, bundled by Vite — no Google Fonts request). Body/UI text uses **Gilroy**, which
is a paid font; the owner has a license for weights 300–800 (confirmed 23.10.2026, files from their Tilda
account). Tokens: `--weight-body-regular` 400 (body text), `--weight-ui` 600 (buttons, UI labels),
`--weight-body-bold` 800 (prices); 300 only in the sale banner line. The `.woff2` files live in
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

Media (uploaded photos, `.glb` models) lives under `MEDIA_ROOT` (`media/`), or in an S3 bucket when
`AWS_STORAGE_BUCKET_NAME` is set. Both default storages are `shop.storage.Compressed*`: every saved image is
converted to WebP (long side ≤2000 px, EXIF rotation applied) unless that would be larger; non-images pass through.
Every `*.webp` also gets smaller copies next to it for each `storage.THUMB_SIDES` (`x.w400/w640/w1200.webp`,
`shop.storage.thumb_name(name, side)`); templates use `thumb_url` / `thumb_url:1200` (falls back to the full file for
non-WebP) in `srcset` on cards, the PDP main photo and the home hero. Missing copies (older uploads, a newly added size)
are made by `python manage.py compress_media` (idempotent, keeps originals) — `build.sh` runs it before the new release
goes live, so templates never point at a copy that isn't in the bucket yet. `settings.STORAGES` must
define **both** `default` (FileSystemStorage) and `staticfiles` — omitting `default` makes any
`<file>.url` raise `InvalidStorageError` (surfaces only once a real image/model is uploaded).

### Payment

There is intentionally no online payment integration. `Order.payment_status` exists as a future
extension point (see the `# TODO` comment above it in `models.py`) but wiring a real provider
(YooKassa/etc.) requires the site owner's own merchant account — don't add SDKs or webhook views for
this speculatively.
