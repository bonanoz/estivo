# RequestPanel
The cart as a request, not an order: a right drawer on `surface-white` over `scrim`, the same content on the cart page and at checkout.

- Heading «Ваша заявка» (`modal-title`). Never «заказ», «Оформить заказ», «Купить», «Оплатить» (R07); «под заказ» as a lead time is fine.
- Lines: square photo, name, chosen colours by group, quantity (44px buttons), line price. Products with `price = 0` never get here (R08).
- Sum, then the note «Это предварительный расчёт. Оплаты на сайте нет: менеджер перезвонит в течение [уточнить: время], уточнит цвет, сроки и стоимость доставки» (R07).
- `es-facts`: срок · доставка · гарантия 3 года (link to /garantiya/) · договор 50/50 после фото- и видеоотчёта (R06).
- One `es-btn--accent`: «Перейти к заявке» in the drawer and on the cart page, «Получить расчёт» on checkout.
- After adding a product: a `graphite` toast «Добавлено в заявку · Открыть», the link at least 44px tall (R01).
- Full width below 420px; no sideways scroll.
