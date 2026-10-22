# ProductCard
Catalogue card one module wide: square photo, stock line, name, price, swatches and one dark button.

- Provide: photo (square, no rounding, no shadow, no lift or zoom on hover), stock line «В наличии» / «Под заказ» (R06), name by composition, optional article («Арт. К-60») for sets instead of a number in the name (audit §14), price «от N ₽», optional swatches.
- Old price only when it really existed (R12): `muted`, struck through, after the price. No percentage badge.
- `price = 0`: the price line reads «Цена по запросу» and the button is «Узнать цену» (`es-btn--dark`), opening the lead form with the product name. «В корзину» is not shown and the server refuses to add such a product (R08).
- The heart is an `es-icon-btn` (44px) on `surface-white` over the photo corner.
- Nothing below 14px. At 390px the grid is two columns with no sideways scroll (R22).
- No `accent` on the card: the terracotta button belongs to the request panel and the offer card.
