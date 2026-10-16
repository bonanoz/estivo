# UX.md — E-commerce UX patterns (reference: castlery.com, US store)

Scope: structure, content hierarchy and interaction behavior only. Visual styling (colors, type, spacing, radii) comes from DESIGN.md and must not be taken from this file. Do not copy Castlery brand names, copy, imagery or promo text; reuse the patterns.

Observed on castlery.com/us in October 2026 at a ~800px-wide viewport (tablet-like layout: hamburger nav, 3-column grid). Desktop layout may differ. Items marked "not verified" were not seen.

## 1. Global shell

- **Top promo bar**: one-line sale message with promo code, a countdown on the right, a dismiss (X) button.
- **Header**: hamburger menu + search icon on the left, centered wordmark, account icon + cart icon (with item-count badge) on the right.
- **Secondary strip** under the header on the home page: horizontally scrollable promo links (newsletter gift offer, free-shipping threshold) with arrows.
- **Floating "Chat" button** pinned to the right edge on every page, including checkout (checkout also offers WhatsApp support in the footer).
- **Breadcrumbs** on category and product pages (Category > Subcategory / Product type).
- **Region gate**: the root domain shows a country picker (US, SG, AU, CA, UK) before the store; each country has its own path prefix (`/us/...`) and prices.
- **404 page**: short message ("page can't be found, may have been moved") followed by a "Browse our bestsellers" product carousel and the normal footer, so the visitor is never at a dead end.
- **Footer**: "What's popular" SEO category links, About, "Shopping with us" (delivery, returns/refunds, warranty, help center, free swatches, AR view), average rating with review count, legal links. A newsletter signup band ("Sign up for exclusive access") sits directly above the footer.

## 2. Home page

Order of sections, top to bottom:
1. Full-bleed campaign hero (seasonal/sale) with a single main CTA.
2. Quick category CTAs ("Shop sofas / dining / accessories / chairs") tied to the current collection feature.
3. Collection/editorial block with "View all".
4. Service blocks: customization service, in-person showroom, free interior styling — each with a "Learn more" link.
5. User-generated content carousel from Instagram ("See our designs in real homes").
6. Brand story block with "Read our story".
7. Long SEO text with answers to shipping, returns, warranty and financing, ending the page above the footer.

Promotion is layered: sale bar, free-shipping threshold and gift-for-signup all appear before the first scroll.

## 3. Category / listing page

**Structure**
- Breadcrumb, then a short hero banner with H1 and a one-to-two sentence description.
- A bar with "Filters" on the left and "Sort by" on the right. It becomes sticky at the top while scrolling.
- Below it, a "QuickShip to [ZIP]" toggle. The ZIP is prefilled (from location) and is a link that can be edited. When on, it shows only items that ship quickly.
- Product grid: 3 columns at this width, 24 products per page.
- **Numbered pagination** ("1 2 3 … 19"), not infinite scroll. Total result count is 433 for "All sofas".
- SEO copy and an FAQ below the grid (materials, stain resistance, when to buy, sizing, delivery area, warranty).

**Product card**
- Badge in the top-left corner: New, Bestseller, Set Price, Sale, Clearance, Sitewide Sale.
- Product image with a 2-dot gallery indicator (second image is a lifestyle/alternate view).
- Name, then a one-line feature descriptor (e.g. "Removable covers, machine washable"; long ones are truncated with an ellipsis).
- Color/material swatches under the descriptor; the selected one has a dark outline. A "+N" label appears when more swatches exist than fit.
- Price. When discounted, the sale price is in the accent color followed by the struck-through original price.
- Optional small labels such as "2 sizes available".
- Carousel cards (bestsellers, recommendations) additionally show two round icon buttons under the price: quick add-to-cart and wishlist heart. These were not visible on the grid cards in the listing.

**Sort options**: Recommendation (default), Price low to high, Price high to low. A small dropdown anchored under the button; chevron flips when open.

**Filters panel**
- Opens as a full-screen panel at this width (title "Filters", close X at top right).
- Collapsible groups with chevrons: Category, Material (checkboxes, "View more"), Length (range slider), Color (round swatches), Price (range slider), Featured (New arrival, Sale, Clearance), Fabric feature (machine-washable, spill-resistant, stain-resistant & pet-friendly), Seat depth, Seat softness, Seat comfort, Seat height, Fabric type, Sustainability feature.
- Notable pattern: product-specific comfort attributes (depth, softness, height) are filters, not just spec-sheet text.
- Sticky footer inside the panel: live "N results available" text, a secondary RESET button and a primary APPLY button. Filters apply only on APPLY.

## 4. Product detail page (PDP)

**Above the fold**
- Large hero image first, then a thumbnail strip with a mix of: lifestyle photo, short video (play icon), room scene, studio shots from several angles. A thin progress bar under the strip shows horizontal scroll position.
- Breadcrumb, badge (e.g. New), product name, wishlist heart on the right, star rating with review count as a link (jumps to reviews).
- Price directly under the rating.
- Option groups, each as "Label: *current value*" with swatches:
  - Material/fabric: label "Stocked fabrics", swatch with a check mark on the selected one, links "View fabric details" and "Get free swatches".
  - Leg/frame finish (or other product-specific option): same swatch pattern.
- The selected variant is written into the URL as query parameters (e.g. `?material=...&leg_color=...`), so variants are shareable and survive refresh.
- Promo banner with a tag icon, the offer rule and the promo code, placed immediately above the main button.
- Primary button includes the live price: "ADD TO CART — $499". Full width at this size.
- When the page first loads, a bottom bar with name, price and a compact ADD TO CART button is visible.

**Under the button (trust and logistics)**
- "Reaches your home: [date range]" estimated from the stored ZIP.
- Three one-line trust items: 30-day returns, pay later with monthly installments, up to 10-year warranty.
- "Where to get it": stock status ("In stock"), delivery cost note ("calculated per shipment"), ship-from location, editable ZIP, "Locate our showroom" with "check nearby stores for availability".

**Below**
- UGC strip ("Be inspired by real homes").
- Information sections: Dimensions & product details, Seat comfort, Materials & care, Delivery/warranty/returns, Assembly instructions.
- "What makes it special" bullet list, a link to the whole collection, then feature storytelling blocks ("Why everyone loves it"), each with a short heading and one paragraph.
- Three product carousels with the same card as the grid: "Ready to ship picks", "Shop the collection", "Bestselling picks".
- Reviews: overall score ("4.7/5 based on 886 reviews globally"), WRITE A REVIEW button, "Top mentions" topic chips (customer service, delivery, product, pricing...), sort control and location filter, then individual reviews with name, date, "Verified Purchase", country, title, text, and a line naming the related product when the review is for a sibling product.

## 5. Add to cart and mini-cart

1. Click on the main button: the button turns grey and shows a spinner while the request runs (about 2 seconds).
2. A right-side drawer slides in over a dimmed page (close X at top). Header: check icon + "1 item added to your cart".
3. Free-shipping progress bar: "You are $900 away from Free Shipping!" with a filled bar and cart icon at the end.
4. A dark strip with a truck icon: "Enter zip code to calculate shipping cost" (tapping it opens the ZIP entry).
5. Line item: thumbnail, name, option chips (material, leg), estimated delivery window, rating, "Remove" link with a trash icon, quantity stepper (− 1 +), line price.
6. Summary rows with thin separators: Items subtotal, Estimated shipping with the ZIP as an editable link (pencil icon), "Add coupon code" (expand with +; logged-out users see "Log in to view your coupons"), Sales tax, Total (incl. taxes & shipping) with an info icon.
7. Buttons: CHECKOUT (primary), CONTINUE SHOPPING (text button).
8. Below the buttons: "We think you'll love these" cross-sell carousel with quick add and wishlist on each card.

Taxes and shipping are estimated in the cart from the ZIP, so the user sees a close-to-final total before checkout.

## 6. Cart page

- The cart icon in the header opens a full page (`/cart`), not the drawer. The drawer appears only after adding an item.
- Same blocks as the drawer, laid out as a page: progress bar, line items, "Cart summary", checkout button.
- Removing an item shows a toast at the bottom: "[Item] has been removed" with an **Undo** link.
- **Empty state**: "You have no items in your shopping cart", CONTINUE SHOPPING, four trust cards (eco delivery, warranty, 30-day returns, 14-day price protection), a recommendations carousel, and "Add a finishing touch to your home" with accessories.

## 7. Checkout

- URL structure: `/checkout/account` is the first step.
- The header is reduced to the wordmark only (no navigation, search or cart), and the footer shows "Need any help on checkout?" with a WhatsApp number and "Secure Checkout".
- Step 1 is the account step: "Log in or sign up", email + password, "Forgot password", a "New to Castlery? Sign up" link, and quick login with Facebook, Apple and Google. A guest checkout option was not seen at this step (not verified).
- Later steps (address, delivery option, payment) were not viewed (not verified). The site mentions three delivery levels (Standard, Room of Choice, White Glove) and buy-now-pay-later options.

## 8. Cross-cutting rules to reuse

1. Put price, delivery date and returns near the main button, never only in a separate tab.
2. Keep all variant state in the URL.
3. Show the free-shipping threshold progress in the cart; it doubles as an upsell.
4. Use a drawer after "add to cart" but a full page when the user opens the cart deliberately.
5. Reduce checkout to the logo plus help and security notes.
6. Always give the user a next step on empty or error screens (bestsellers, recommendations).
7. Use real-home photos (UGC) and verified reviews, with product-specific comfort attributes in filters.
8. Use ZIP as the single location input for QuickShip, delivery date, shipping cost and tax; make it editable everywhere it appears.
9. Keep the filter panel apply-based, with a live result count and a reset action.
10. Use numbered pagination at 24 items per page and add SEO text with an FAQ below the grid.

## 9. Suggested screen build order

1. Shell (header, promo bar, footer, chat button, region/ZIP state)
2. Category page (grid, card, sticky filter/sort bar, filter panel, pagination)
3. PDP (gallery, options, URL state, buy box, info sections, reviews)
4. Mini-cart drawer and cart page
5. Checkout (account step, then the rest as designed by the project)
6. Home page
