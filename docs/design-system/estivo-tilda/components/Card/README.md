# Card
Square-cornered content blocks sized to the 224px module: outlined in `ink` for advantages, filled `surface-muted` for reviews.

- Provide: body text (`body`, `ink`), an optional 30px line icon in `brand`, an optional caption.
- `es-card`: 1px `ink` outline, no fill, 20px padding («Почему ESTIVO», «Преимущества мебели»). One checkable fact per card («Своё производство в Тольятти: 3 цеха, сварка и покраска алюминия»), never an abstract promise. Guarantee and lead-time numbers only once the owner has confirmed them (audit R04).
- `es-tile`: `surface-muted` fill, no border (reviews, FAQ). A review always ends with `es-tile__author`: name, city, date and source («Ольга, Самара · май 2026 · Яндекс Карты»). No anonymous reviews, no links to dead profiles (audit R14).
- Widths are 1, 2 or 3 modules (224 / 458 / 692px) with the 10px `gutter`; full width below 768px. Never round the corners, never add shadows.
