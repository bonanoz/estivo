# OfferCard
One dated sale offer on `surface-white`: photo, promo heading, composition, price with the real old price, saving, end date and the request button.

- Provide: name (`es-title--promo`, `ink-black`), composition in one line, price, old price (`muted`, struck through), saving in roubles or an exact percentage that adds up (R12), end date in `brand` («Акция до 30 ноября 2026»).
- No end date — the card is not rendered; after the date it disappears by itself (R17, R26). Data: `Product.old_price > price` and `Product.offer_ends_at`.
- The button is the one `es-btn--accent` on the card: «Узнать цену [название]», opening the lead form with a hidden source field (R16).
- Used in the catalogue with `?flag=sale` and under the sale strip on the home page, never on the first screen (R13).
- Two columns from 768px, stacked below; nothing below 14px.
