## ESTIVO storefront redesign

Redesigns the storefront's layout, navigation and shopping UX following `UX.md`, the rules in `DESIGN.md`, and the ESTIVO brand values in `docs/design-system.md`. Business logic, models, URLs and the order/lead flow (Postgres first, Telegram best-effort) are unchanged. Full spec and decision log: `docs/specs/furniture-store-redesign/SPEC.md`.

### Stack
- **Vite + TypeScript + Tailwind v4** in `internetshop/frontend/`, served through `django-vite`. Brand tokens live in `@theme`, components in `@layer components`.
- **htmx + django-htmx** for server fragments: filter count, search suggestions, cart drawer, wishlist toggle, undo.
- **Alpine.js** for UI state: menu, overlays, filter panel, drawer, focus traps, shared scroll lock.
- Legacy hand-written CSS/JS removed. `model-viewer` stays vendored.
- **Django pin bumped 5.0.6 → 5.2.18 (LTS)**, required by django-htmx 1.29. All tests ran on 5.2.18.

### What changed for visitors
- **Shell:** new header (search overlay with live suggestions, wishlist and cart counters, Alpine mobile menu), promo bar editable in admin, floating contact button, new footer with popular categories and review rating.
- **Catalog:** sticky Filters/Sort bar. The filter panel only applies on «Применить», shows a live count and «Сбросить», and covers category, material, colour, price, length and new/bestseller/sale. Also: sorting, numbered pagination (24 per page) that keeps filters, SEO text and FAQ, and an empty state with bestsellers. Everything still works without JS.
- **Product page:** larger gallery with thumbnails (3D recolor unchanged), swatch choice stored in the URL (`?weave=&cushion=&frame=`), «В корзину — price» button, trust block, sticky mobile buy bar, accordions, related products, reviews with average rating, a moderated review form, and JSON-LD.
- **Cart:** a side drawer opens after adding an item (focus trap, Esc). `/cart/` page has a quantity stepper and «Вернуть» undo after removal (with and without JS). Empty cart shows recommendations.
- **Checkout:** one page with a reduced header and a «Нужна помощь?» footer. The `Order`/`OrderItem` flow is unchanged.
- **Wishlist:** stored in the session (no accounts), heart on cards and product pages, `/wishlist/` page.
- **Home and content pages:** home sections reordered per UX.md, with a new hero H1 «Мебель для мест, куда хочется возвращаться». Copy on content pages is unchanged. 404 page shows bestsellers.

### Backend
- **Migrations (additive, reversible):**
  - `0006`: `Product.is_new`, `Product.is_bestseller`, `SiteSettings.promo_*`.
  - `0007`: validator on `promo_url`.
- **New modules:** `shop/catalog_filters.py`, `shop/wishlist.py`, `shop/templatetags/shop_tags.py`.
- **Accessibility:** form errors set `aria-invalid` and `aria-describedby`.
- **Security:** safe redirects (`url_has_allowed_host_and_scheme`) in `cart_add`, `wishlist_toggle` and `lead_create`. This also fixes an existing open redirect and a 500 in `lead_create`.

### Verification
- `python manage.py test`: **179/179 on PostgreSQL 18** (16 existing + 163 new tests, written before the code).
- `npm run build` (includes `tsc --noEmit`), `collectstatic`, `makemigrations --check`: all clean.
- Ran the app in a browser:
  - all public pages return 200 with exactly one `<h1>`; no server errors;
  - swatch → URL;
  - add to cart → drawer → Esc;
  - wishlist toggle;
  - search suggestions (Cyrillic);
  - filter panel with live count;
  - remove → undo.
- Design gates: tasteskill `lint.mjs` and `inspect.mjs` (1440/768/390), plus the ui-ux-pro-max checklist. The remaining warnings are listed and justified in SPEC.md.

### Not checked
- Submitting checkout and lead forms in the browser, because that would send a real Telegram message (covered by tests).
- Real devices.
- Favicon (the site has never had one).

### Deploy notes
- Deploy now needs Node: run `npm ci && npm run build` in `internetshop/frontend/` before `collectstatic`.
- Install the new Python dependencies (`django-htmx`, `django-vite`, Django 5.2.18) and run `migrate`.
- This branch is based on `feat/session-cart-checkout-3d`, so it also carries 2 commits not yet in master: `5d34429` (a11y/typography polish) and `0143b33` (SiteSettings page photos, design/UX docs).

🤖 Generated with [Claude Code](https://claude.com/claude-code)
