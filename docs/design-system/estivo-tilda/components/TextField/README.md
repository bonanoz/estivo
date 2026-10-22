# TextField
A 60px transparent input with a 1px light-grey border and 5px corners, used in every lead form.

- Provide: `placeholder` naming what to type («Ваше имя», «Телефон»), `name`, error text.
- Stack fields with a 12px gap, the full width of a two-module column (458px); the submit is the accent «Получить расчёт» (request form) or a dark button (other forms) in `button-lg`, same height.
- `border-input` is only 1.7:1 on `surface` (source value): pair each field with a visible label or placeholder, and rely on the `graphite` focus border.
- Errors: `brand` border plus a 14px `brand` message under the field.
- Radio buttons and the consent checkbox use `es-choice`: label in the body font, 44px row. The source fell back to a browser serif here (audit 4.5).
- The request form also gets a comment field («Цвет плетения и подушек, размеры, удобное время для звонка») and, above the submit, one line on what happens next: «Оплаты на сайте нет: менеджер перезвонит и уточнит цвет, сроки и доставку» (audit R07).
- Each form carries a hidden field naming its source (`offer`, form name) so requests can be told apart (audit R16).
