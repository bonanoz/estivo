# 03 — CRO and the purchase funnel (Agent 3)

Live site estivo63.ru (Tilda) and /promo, checked 2026-10-20. Tools: Python Playwright with system Chrome, at desktop 1440×900 and with Playwright's "iPhone 13" emulation (emulation only, not a real device), plus the shared corpus and crawl_results.jsonl. No form or order was submitted. I typed into fields only to check the input mask.
Scripts: `scratchpad/a03/s2.py … s7.py`. Screenshots: `shots/cro_*.png`.

## 1. What I inspected

| Path | Desktop | iPhone 13 emu | What I tested |
|---|---|---|---|
| /komplekty catalogue → card "В корзину" (priced item «Рета», 205 800 р.) | yes | yes | Feedback after adding, header counter, `tcart` in localStorage |
| /komplekty → card "В корзину" on a "Цена по запросу" item (Комплект мебели из стропы) | yes | yes | What the drawer, sum and checkout show |
| /komplekty → "Подробнее" (opens as an overlay, URL pushState to /tproduct/…) → "В корзину" | yes | — | Feedback, header and cart access |
| Product by direct URL /komplekty/tproduct/500328850442-…-reta → "В корзину" → "Назад"/✕ | yes | yes | Feedback, cart access, where the exit goes |
| Header cart icon → drawer "Ваш заказ" → "Оформить заказ" → checkout | yes | yes | Fields, required flags, phone mask, delivery radio, what's promised. **Stopped before "Оформить заказ" (submit).** |
| / home: first screen, cookie banner, 30 s wait for timed popups, every CTA/href, "Получить персональную консультацию дизайнера" popup | yes | yes | CTA map, popup form fields |
| /promo: CTA→href map, "ХОЧУ МИЛАН С ПОДАРКАМИ" popup, 30 s wait | yes | yes | CTA map, popup form |
| Corpus scan: 234 product pages, /salerotang, /saleroup | — | — | Products with no price, discount depth, "Error get alias" |

Not covered: the actual submit and what follows it (thank-you page, CRM/Telegram, the manager's response time). Metrika goals and the funnel setup (no access). Messenger reply speed. Quiz: none exists on the live site (no quiz forms in the crawl, and no quiz CTA). Real iOS Safari.

## 2. Findings

### F1. "Цена по запросу" items can be added to the cart, and they then disappear from the total without any notice
- **Problem:** Items without a price have a normal "В корзину" button. In the cart they show **no price at all** (a blank cell), and "Сумма"/"Итого" silently counts them as 0. The buyer can't tell whether that line is free, unpriced, or a bug. Nothing explains that a manager will quote it.
- **Location:** /komplekty cards 1–2 ("Комплект мебели из стропы", "Комплект мебели из ротанга"), /komplektyroup, and the drawer and checkout.
- **Evidence (Confirmed):** After adding «Рета» and «Комплект мебели из стропы», `tcart` = `«Рета» x1 205800`, `стропы x1 0`. Drawer: "Комплект мебели из стропы 1 [empty] … Сумма 205 800р." (shots/cro_desktop_cart_drawer.png, cro_mobile_cart_drawer.png, cro_desktop_checkout_filled.png). The direct product page for that item shows only the title and "В корзину", with no price, description or "request a price" text (corpus/komplekty_tproduct_827181619422…txt). The corpus scan found 21 of 234 product pages with no price: 11 are rattan colour swatches (/cvetrotanga, with an English "BUY NOW" button), 5 are /onas "Комплект из ротанга" items, and the rest include «Вольтерра Люкс» П-образные (see F6). On /aksessuary («Укрывной Чехол») and /hranenie («Сундук Позитано») the card shows **both** "Цена по запросу" and a price (15 000р. / 28 500р.). The phrase comes from the product description and contradicts the price field.
- **Customer impact:** A ~205 000 р. order ends in a checkout whose total is plainly incomplete. That reads as carelessness on a premium purchase, or it hides the real cost.
- **Commercial impact:** The highest-ticket bespoke sets are exactly the ones without prices. Those leads arrive as orders with a wrong total, and the manager starts by correcting the customer's expectation.
- **Confidence:** Confirmed (behaviour). The commercial effect is a well-supported hypothesis.
- **Recommendation:** For price-on-request products, replace "В корзину" with "Запросить цену" and open a short form prefilled with the product name. Alternatively, set the Tilda price field to empty and use the Tilda "price on request" label so the cart shows "по запросу" and the total reads "от 205 800 р. + позиции по запросу". Remove the stray "Цена по запросу" from descriptions of priced items. Unpublish or hide the colour-swatch "products" from the store.
- **Validation:** Metrika: the share of carts holding a 0-price line and their submit rate before and after. Manager log: how often the first call starts with re-quoting.
- **Effort:** S

### F2. The "order" is really a request, but nothing on the way says so, and the checkout promises nothing about payment, delivery cost or timing
- **Problem:** The submit button says "Оформить заказ" (place the order), and the drawer heading is "Ваш заказ". Yet the footer says the site "не является публичной офертой", and the business model is a manager call-back. The checkout gives no next step ("менеджер перезвонит в течение … и подтвердит стоимость доставки"). It says nothing about payment (cash/SBP/invoice/0% instalments, all of which exist on /dostavka), prepayment, delivery price or lead time, production time for made-to-order items, or the warranty.
- **Location:** Cart drawer and checkout (t706), every catalogue page.
- **Evidence (Confirmed):** Full visible checkout text: "Ваш заказ · [Ваше имя] · +7 · Доставка транспортной компанией · Самовывоз · Я согласен с политикой конфиденциальности · Оформить заказ · [items] · Итого 205 800р.". That is all of it (s4.py output). There is no email field (it exists in the consultation forms) and no comment field visible (only a hidden spam trap `form-spec-comments`). The delivery radio has no cost, carrier name or pickup address next to it.
- **Customer impact:** At 100–300 k р. a buyer wants to know "what happens when I press this, do I pay now, what does delivery to my city cost". Without answers they phone, leave for a competitor who states it, or don't press.
- **Commercial impact:** This is the biggest drop-off risk at the final step of the main money path (Well-supported hypothesis; no funnel data available).
- **Confidence:** Behaviour Confirmed. Impact is a hypothesis.
- **Recommendation:** Rename the submit button to "Отправить заявку на заказ" or "Получить расчёт с доставкой". Add a 3-line block above it: "Оплаты сейчас нет. Менеджер позвонит в течение 30 минут в рабочее время, уточнит цвет и размеры и посчитает доставку ГТА до вашего города. Оплата: наличные/СБП/счёт с НДС, рассрочка 0% до 12 мес." Use an optional city field instead of the bare TK/pickup radio, and show the pickup address next to "Самовывоз". Show the same two lines in the drawer under "Сумма".
- **Validation:** A/B test of button copy plus the reassurance block (Tilda + Metrika goal on submit). Primary metric: checkout submit rate.
- **Effort:** S

### F3. Adding to cart gives feedback, but there is no way to reach the cart from it, and a product page opened by direct URL has no cart or header at all
- **Problem:** On the catalogue, the product overlay and a product page opened by direct URL, "В корзину" shows a black toast ("… добавлено в корзину") for a few seconds. The toast has no "Перейти в корзину" link, and no drawer opens. On a product page opened by direct URL (how search, ads and shared links arrive) the page has **no header, no cart icon, no menu** and one phone link in the footer. The only ways out are "Назад" or ✕, which go to /komplekty. To check out, the buyer must guess that the cart lives on a category page.
- **Location:** All /…/tproduct/… pages (234) and the catalogue overlay.
- **Evidence (Confirmed):** Toast present on desktop and mobile, direct URL and overlay (cro_desktop_pdp_direct_after_add.png, cro_mobile_pdp_direct_after_add.png, cro_desktop_after_popup_add.png). This **corrects the brief**, which said there was "NO visible feedback": the toast appears about 1–2 s after the click and fades. `a[href="#opencart"]` visible on direct PDP = 0. "Назад" → https://estivo63.ru/komplekty (desktop); ✕ → /komplekty (mobile). Every product page also prints raw "Error get alias" (234/234 in the corpus) and the «№1» set is labelled "Тип: Места для хранения" (cro_desktop_product_popup.png).
- **Customer impact:** A visitor from search adds a 200 k set, sees a toast, and then has nowhere obvious to go. Many will assume it worked and leave, or think the site is broken.
- **Commercial impact:** Product URLs are the SEO and ad landing pages, so this hits cold traffic at its highest intent. The size of the loss is unknown without Metrika.
- **Confidence:** Confirmed (behaviour). Impact is a well-supported hypothesis.
- **Recommendation:** Turn on Tilda's "open cart after adding" option, or add a "Оформить" link in the toast. Put the header with cart icon and phone on product pages (Tilda store product-page header setting). Remove the "Error get alias" block. Fix the "Тип" field.
- **Validation:** Metrika: sessions landing on /tproduct/ → cart open → checkout. Webvisor recordings.
- **Effort:** S–M

### F4. Too many competing conversion mechanisms, with no hierarchy and different numbers
- **Problem:** A visitor meets 7 different ways to convert, most with identical forms, and the phone number changes between the main site and /promo.
- **Evidence (Confirmed, live CTA→href maps, s6/s7 output):**
  | Mechanism | Main site | /promo |
  |---|---|---|
  | Cart → checkout ("Оформить заказ": name, phone, delivery radio, consent) | every catalogue page | **absent** (no cart, no product prices except the Вольтерра banner) |
  | "Консультация" popup (#popup:myform: Имя, phone, consent) | home "Получить персональную консультацию дизайнера" | **all** 15 offer "УЗНАТЬ ПОДРОБНЕЕ", 4 "ХОЧУ МИЛАН С ПОДАРКАМИ", 21 "Акция: кофейный столик…" |
  | "Обсудить дизайн-проект" popup (#popup:myform20, same fields) | home | — |
  | Inline "НУЖНА ПОМОЩЬ В ПОДБОРЕ…" form (Имя, phone, consent) and a second form with E-mail | every page | — |
  | Phone | +7 927 200 43 03 (header desktop only, footer, "Позвонить" in menu) | **+7 (917) 824-67-22** |
  | WhatsApp | wa.me/79272004303 | wa.me/**79178246722** |
  | Telegram | t.me/+7zVfVsf1abszODYy (an **invite link to a group/channel**, not a chat with a manager) | — |
  | VK | vk.com/estivo_tlt | same |
  | Avito reviews widget (26 "Отзыв Avito" links) | home | — |
  Every form has the same fields and a generic title, and none says what you get (a price, a 3D, a call within X minutes). Three different forms on the same home page all promise "мы свяжемся с вами в ближайшее время".
- **Customer impact:** The choice is unclear: buy (cart) or ask (form)? A visitor who calls the /promo number and later the main number reaches what may be different people.
- **Commercial impact:** Leads are split across 2 phones, 2 WhatsApps and ≥4 near-identical form types. That makes attribution impossible (which channel sells?) and makes double-handling likely (Well-supported hypothesis).
- **Recommendation:** One primary action per page type. On catalogue and product pages: "Запросить расчёт" / cart. On content pages: one "Подбор мебели" form. One phone and one WhatsApp site-wide (or a deliberate call-tracking number, labelled and documented). Change the Telegram link to a direct manager chat (t.me/username) or a bot. Give each form a distinct name in Tilda (`tildaspec-formname`) so Metrika and the CRM can tell them apart.
- **Validation:** Count leads by form name and channel for 4 weeks after consolidation.
- **Effort:** M

### F5. /promo: every offer leads to the same anonymous form, the offer product doesn't match its own product page, and the promo is not linked from the main site
- **Problem (beyond the brief):** (a) 40 offer buttons on /promo all point to `#popup:myform` "КОНСУЛЬТАЦИЯ", whose only addition over the home version is "Убедитесь в правильности введенного вами номера!". No hidden field records which offer was clicked, so the manager doesn't know whether the lead wants Милан 3XL, Вольтерра or the coffee-table gift. (b) The "Популярные позиции" buttons (24×) say "УЗНАТЬ ПОДРОБНЕЕ" but drop the visitor at the top of a whole category (/komplekty 14×, /komplektyroup 10×), not at the product shown. (c) The menu item "Кашпо" links to a **Google Drive file** (drive.google.com/file/d/1T1e8K3…). (d) The "АКЦИЯ НЕДЕЛИ" offer is "Угловая Зона ВОЛЬТЕРРА ЛЮКС 220х340 СМ", 345.300 → 245.300 ₽. Its product page (/uglovyedivany/tproduct/425279570482-…) has **no price** and lists sizes "2200х3000х2200" / "2800х3000х2800", so 220×340 isn't one of them. (e) The main-site hero "СКИДКИ ДО 70% → ПЕРЕЙТИ НА СТРАНИЦУ СПЕЦПРЕДЛОЖЕНИЙ" goes to /salerotang, not /promo. The two promo systems don't know about each other.
- **Evidence (Confirmed):** s7 desktop href map. Popup text in cro_mobile_promo_popup_form.png. Corpus product page text.
- **Customer impact:** A visitor who clicks "ХОЧУ МИЛАН С ПОДАРКАМИ" gets a form titled "КОНСУЛЬТАЦИЯ". The intent they expressed is lost, and the follow-up call starts from zero. A visitor who checks the Вольтерра offer on the main site finds no price and different dimensions.
- **Commercial impact:** Paid or social traffic to /promo (purpose unknown) converts into untagged leads. The offer's ROI can't be measured.
- **Confidence:** Confirmed (a–e). Impact is a hypothesis.
- **Recommendation:** One popup per offer, or one popup with a hidden `offer` field filled from the button (Tilda: "Передать данные в форму" / UTM-like hidden field). Title it with the offer ("Милан 3XL с подарками — оставьте телефон, пришлём расчёт"). Point "Популярные позиции" at the product URL. Replace the Drive link with /kashpo or remove it. Sync the Вольтерра dimensions and price with its product page and add an end date. Decide whether /promo is an ads landing page (then noindex and a single phone) or part of the site (then link it from the hero).
- **Validation:** Hidden-field counts by offer. Metrika goal per popup.
- **Effort:** S

### F6. The consultation and checkout forms are short (good), but consent is an unchecked required box and labels fall back to a serif system font
- **Problem:** Each form needs 3–4 inputs: name*, phone (masked), delivery radio* (checkout only) and the consent checkbox*, which starts **unchecked**. On checkout the radio and consent labels render in a Times-like fallback font while the rest is Gilroy, so this one step looks broken or unstyled.
- **Evidence (Confirmed):** Fields from DOM: `Name req=1`, `tildaspec-phone-part[] tel`, `Delivery radio req=1 ×2`, `Checkbox req=1 checked=false`. The phone mask works well: typing "abc89271112233" gives "(927) 111-22-33" (letters and the leading 8 dropped). "12345" leaves "(123) 45" and isn't flagged until submit, which I did not test. Font: cro_desktop_checkout_filled.png, cro_mobile_checkout_form.png.
- **Click count, path (a), desktop:** home → "Каталог ротанга" (1) → category tile (1) → card "В корзину" (1) → cart icon (1) → "Оформить заказ" (1) → name + phone + radio + consent (4) → submit (1) = **6 clicks + 4 inputs**. Through "Подробнее" add 1 click and 1 close. Mobile: burger (1) → "Каталог ротанга" (1) → submenu/tile (1) → same as above = **8 clicks + 4 inputs**. Consultation popup: 1 click + 3 inputs + submit.
- **Recommendation:** Keep the form short. Under 152-FZ the consent checkbox can't be pre-ticked, but it can be replaced by the line "Нажимая кнопку, вы соглашаетесь с политикой…" where the legal reviewer accepts that (Preliminary assumption; check with a lawyer). Fix the label font (set it in the t706 form style). Make the delivery radio optional, or default it to "Доставка", since the manager confirms it anyway.
- **Confidence:** Confirmed (fields, mask, font). The 152-FZ point is a preliminary assumption.
- **Effort:** S

### F7. Cookie banner and floating mobile icons cover content and CTAs; there is no phone on the mobile header
- **Evidence (Confirmed):** Mobile home: the cookie banner ("Мы используем файлы cookie… ХОРОШО") takes the bottom ~20% of the first screen (cro_mobile_home_first.png). On desktop it sits bottom-left over the "Гарантия и возврат" menu link (cro_desktop_home_after30s.png). On the mobile catalogue, the fixed round wishlist, cart and burger icons float over the product buttons while scrolling (cro_mobile_catalog_after_add.png: they overlap a "В корзину" button). The mobile header shows logo, wishlist, cart and burger, but **no phone or call icon**, while desktop shows the number. No timed or exit popups fired within 30 s on home or /promo (good).
- **Recommendation:** Make the cookie notice a slim one-line bar. Give the header a solid background on scroll or move the icons into a real bar. Add a call/WhatsApp icon to the mobile header (furniture buyers on mobile call).
- **Effort:** S

### F8. The home first screen sells discounts, not the product
- **Evidence (Confirmed):** Desktop and mobile first screen = "СКИДКИ ДО 70%" plus "ПЕРЕЙТИ НА СТРАНИЦУ СПЕЦПРЕДЛОЖЕНИЙ" (→ /salerotang). The value proposition "ПЛЕТЁНАЯ МЕБЕЛЬ РУЧНОЙ РАБОТЫ" comes below the fold. Discount depth from the corpus: /salerotang has 36 discounted items, 21–87% off; 6 are over 70% ("Кокон «Комо Люкс 2х»" 79 900 → 10 000 р., −87%, which looks like a data error). /saleroup has 17 items, 33–78% off. "До 70%" is therefore inaccurate in both directions, and some items exceed it.
- **Customer impact:** A "Rolls-Royce" positioning (home copy) opens with a clearance banner. The −87% looks like a pricing error and invites "is the full price real?" doubts (cross-check findings/02 F6).
- **Recommendation:** Lead with the product and proof (photo of a real terrace set, "ручная работа, Тольятти, гарантия X лет", "Подобрать комплект" CTA). Move the sale to a secondary strip. Audit sale prices above 70% for typos.
- **Confidence:** Confirmed (layout, numbers). Impact is a hypothesis.
- **Effort:** S

### F9. Analytics: Metrika is loaded, so the funnel can be measured, but form identity is not
- **Evidence:** `ym` = function on /, /komplekty and /promo (crawl `trackers`). tag.js was requested on all three. The brief's ERR_CONNECTION_CLOSED was not reproduced in the crawl, so it was likely a transient or local error (Well-supported hypothesis). No gtag, VK pixel or Top.Mail.ru. Forms carry no distinguishing hidden field, except the cart form's `tildaspec-formname`.
- **Recommendation:** Set Metrika goals for: add-to-cart, cart open, checkout open, checkout submit, each popup submit (by form name), tel:/wa.me/t.me clicks. Add the VK pixel if VK ads are used.
- **Effort:** S

## 3. Top 5 priorities (CRO view)
1. **Checkout reassurance and honest wording (F2):** rename "Оформить заказ" to a request, add the "what happens next / no payment now / delivery quoted / instalments" block. S effort, last step of the main money path.
2. **Price-on-request handling (F1):** stop "В корзину" for unpriced items, show "по запросу" in the cart, hide the swatch products.
3. **Product pages reachable to checkout (F3):** header and cart on product pages, "open cart after add", remove "Error get alias".
4. **One channel set and tagged forms (F4 + F5 + F9):** one phone and WhatsApp, a direct Telegram chat, an offer name passed into the /promo popup, Metrika goals per form.
5. **Mobile first screen (F7 + F8):** slim cookie bar, call icon in the header, value proposition before "СКИДКИ ДО 70%".

## 4. Open questions and data needed
- Metrika access: the add-to-cart → checkout → submit funnel, form submits by type, phone/WA click share, and traffic to /tproduct/ landings and /promo (and its source: ads or VK?).
- What happens after submit: thank-you text, response SLA, and where leads land (Tilda leads, email, CRM, Telegram). Who answers +7 917 824-67-22, and is it call tracking?
- The share of orders that arrive via the cart vs a call or messenger (manager log). This decides whether the cart should stay at all, or become a "подборка для расчёта".
- Whether the unpriced bespoke sets (стропа, /onas items, Вольтерра П-образная) are meant to be orderable online.
- Actual prepayment and production-time terms, so they can be stated in checkout.

*Skipped: did not test the submit itself or server-side validation. Did not test the quantity +/- for 0-price lines. Mobile results come from emulation, not a real iPhone.*
