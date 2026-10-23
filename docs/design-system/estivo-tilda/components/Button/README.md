# Button
Rectangular 5px-radius buttons in Gilroy; graphite is the default, everything else is a named exception.

- Provide: the label (sentence case, a verb: «Подобрать комплект», «Обсудить дизайн-проект», «Получить консультацию») and an `href` or `type`.
- The site takes requests, not payments: never «Оформить заказ», «Купить», «Оплатить» (audit R07).
- `es-btn es-btn--dark` (graphite fill, on-dark text): the default for every CTA on the home page.
- `es-btn--outline`: the secondary next to a dark button («Посмотреть пример»). Never two dark buttons side by side.
- `es-btn--accent`: the request button only — «Перейти к заявке» in the cart panel, «Получить расчёт» on the form. Label in `on-accent` (dark brown, 5.4:1); never white on `accent` at button size.
- Products without a price get a dark «Узнать цену» that opens a form with the product name, not «В корзину» (audit R08).
- `es-btn--call`: 60px brand-outline phone button in the header and contacts.
- `es-btn--promo`: the small uppercase accent button in the promo header, 44px tall, 14px label.
- `es-btn--pill`: the cookie notice only.
- `es-icon-btn`: 44px round icon button for wishlist, cart, menu and slider arrows; give it an `aria-label`.
- Every button is at least 44px tall. Hover dims to 85% opacity; focus shows a 2px `brand` ring.
