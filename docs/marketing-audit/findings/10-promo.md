# 10 - /promo landing page audit (Agent 10, Promotional Landing Page Specialist)

Audit date: 2026-10-20 (off-season). Live Tilda site only. No form was submitted. I did not click the cookie banner's "ХОРОШО".
Confidence labels: **Confirmed** (I observed it), **Well-supported hypothesis**, **Preliminary assumption**.

---

## 1. What I inspected

**Corpus/crawl:** `corpus/promo.txt`, `crawl_results.jsonl` (promo record plus a search of every crawled page's links for `/promo`), `page_promo.html`, `page_.html` (home HTML), `page_sitemap_xml.html`, and the corpus pages home, dostavka, vozvrat, kontakty, b2b, salerotang, saleroup, divan, divanroup, kresloroup, komplektyroup, uglovyedivany (+2 products), aksessuary (+ Укрывной чехол), the Вольтерра Люкс sofa and armchair pages, the 11 rotang sets that contain Вольтерра, and offer.

**Live Playwright (real Chrome):**
- `a10/promo_desk.py` at 1440x900: dumped every Tilda record (text, links, sliders, video attributes), stepped through every slider with its arrows, opened the `#popup:myform` CTA, checked the map, captured Metrika/Maps network calls, and took a full-page screenshot.
- `a10/promo2.py`:
  - Read the Tilda store API JSON for /komplektyroup, /uglovyedivany and /divanroup to get set contents and per-size prices.
  - Clicked play on a review video and listed the review slides and the project gallery.
  - Measured the header overlap.
  - Ran an **iPhone 13 emulation** (Playwright device profile, not a real phone): first screen at 3 s and 9 s, fixed elements, small tap targets, a full-page shot and the burger menu.
- `a10/vk.py`: opened one VK Video embed directly.

**Screenshots:** `shots/promo_d_first.png`, `promo_d_slider{0,2,4,6,8}_{s0,after}.png`, `promo_d_popup.png`, `promo_d_map.png`, `promo_d_full.png`, `promo_d_video_click.png`, `promo_vk_embed.png`, `promo_m_first_t3.png`, `promo_m_first_t9.png`, `promo_m_full.png`, `promo_m_menu.png`.

**Could not access:**
- Yandex Direct, VK Ads and Metrika data, so the real traffic source and conversion rate are unknown.
- Whether `mc.yandex.ru/metrika/tag.js` loads for real visitors. It failed from this machine both times (ERR_CONNECTION_CLOSED, then TIMED_OUT), which is more likely this network than the site.
- How the Telegram/CRM side treats promo leads.
- A web search for the promo returned nothing relevant (the search tool is US-only).

---

## 2. Page anatomy (as rendered, top to bottom, desktop)

| # | Section (Tilda rec) | Verbatim content | CTA → destination |
|---|---|---|---|
| 0 | Header (rec1031209021, fixed) | anchors "Акция месяца / Акция недели / Популярные позиции / Отзывы / Наши проекты / Контакты"; button "ОСНОВНОЙ САЙТ"; burger on the left opens a catalogue menu with 16 category links ("Кашпо" goes to a **Google Drive file**) | "ОСНОВНОЙ САЙТ" → `https://estivo63.ru`; "Наши проекты" → `#guarantees` |
| 0b | Typewriter toast, bottom right (rec1069452251) | "УВАЖАЕМЫЕ КЛИЕНТЫ! Отправим образец за свой счёт, чтобы вы смогли убедиться в качестве нашей продукции!" | "УЗНАТЬ ПОДРОБНЕЕ" → `#popup:myform` |
| 1 | Hero slider, 2 slides (rec1068348951 desktop, rec1060205601 mobile) | Slide 1, shown first: "АКЦИЯ МЕСЯЦА - трехместный диван на всю компанию - 2 больших просторных кресла - 3 стандартных кресла - стол из HPL Compact". Slide 2: "ЗАКАЖИТЕ МИЛАН 3XL в этом месяце и получите крутые подарки: - фирменную подставку под горячее - 2 стильные и функциональные разделочные доски - укрывной чехол на весь комплект". No product name on slide 1, no price on either slide. No autoplay: still on slide 1 after 9 s. | "УЗНАТЬ ПОДРОБНЕЕ" / "ХОЧУ МИЛАН С ПОДАРКАМИ" → `#popup:myform` |
| 2 | Marquee ticker (×3 on the page) | "Акция: кофейный столик для всех новых клиентов" | → `#popup:myform` |
| 3 | "Акция недели" slider, 2 slides (rec1066639701) | Slide 1, shown first: "АКЦИЯ НЕДЕЛИ 345.300 ₽ [struck through] 245.300₽ Ваша выгода - 30%!". Slide 2: "Угловая Зона ВОЛЬТЕРРА ЛЮКС 220х340 СМ на 12 персон". **The price and the product name are on different slides.** | → `#popup:myform` |
| 4 | "Популярные позиции из ротанга", 5 visible slides | Every slide has the same caption and only a photo: no product name, price or set number | → `/komplekty` (all slides) |
| 5 | "Популярные позиции из роупа (веревки)", 3 visible slides | Same: caption and photo only | → `/komplektyroup` (all slides) |
| 6 | "ОТЗЫВЫ О НАС" slider (13 items incl. loop clones) | 3 VK Video embeds (2 distinct videos, `vk.com/video-219037647_456239120/121`, titled "Видео от ESTIVO") plus WhatsApp/Instagram-style chat screenshots. `IMG_1218.jpg` appears twice. No names, dates, cities or links to Yandex/Avito reviews. | none |
| 7 | Black block | "СПЕЦИАЛЬНОЕ ПРЕДЛОЖЕНИЕ ДЛЯ ВАС - ЛЕТНИЕ ПРИВИЛЕГИИ · Акции для новых клиентов - кофейный стол в подарок каждому новому клиенту · Разделочная доска за отзыв - Дарим фирменную разделочную доску ESTIVO с HPL покрытием" | "ПОСМОТРЕТЬ КАТАЛОГ" → `/rotang`; "УЗНАТЬ ПОДРОБНЕЕ" → popup |
| 8 | "ПОЧЕМУ ВЫБИРАЮТ ИМЕННО НАС" | "ОТПРАВИМ ОБРАЗЕЦ ЗА СВОЙ СЧЁТ / ДОСТАВКА в любую точку мира / ГАРАНТИЯ 5 ЛЕТ на все изделия / РАССРОЧКА ПЛАТЕЖА без переплат / ОБМЕН И ВОЗВРАТ в течение 14 дней / СЕРВИСНОЕ ОБСЛУЖИВАНИЕ на протяжении всего срока эксплуатации" | none |
| 9 | "НАШИ ПРОЕКТЫ" (rec1072530291) | 8 zoomable photos, all with empty `alt`. No captions (city, set, materials) and no links to products. | lightbox only |
| 10 | "ВАШ ПУТЬ К ИДЕАЛЬНОМУ ДОМУ" | "ВИДЕО-КОНСУЛЬТАЦИЯ ДИЗАЙНЕРА с подбором лучшего решения / СОЗДАНИЕ ПРОЕКТА разработка 3D-визуализации вашего интерьера / ИНДИВИДУАЛЬНЫЙ ДИЗАЙН / ПРОИЗВОДСТВО … -фото отчет на каждом этапе … / ТОЧНАЯ ДОСТАВКА -прямо до двери -в удобное для вас время -максимально выгодно" | none |
| 11 | Final CTA | "ДЕЙСТВУЙТЕ ПРЯМО СЕЙЧАС - ОСТАВЬТЕ ЗАЯВКУ ИЛИ ПОЗВОНИТЕ НАМ, ЧТОБЫ: Получить консультацию специалиста / Узнать актуальные цены / Заказать дизайн-проект" | `/rotang`; popup |
| 12 | Contacts + Yandex map | "Телефон: +7(917)824-67-22 … Адрес: г. Тольятти, б-р Туполева 12А. Офис 2-4"; hours. **The map renders despite the console warning "Invalid API key"** (promo_d_map.png). | `tel:+7(917)824-67-22` |
| 13 | Footer | "ООО “Эстиво” ОГРН: 1146320022089 ИНН: 6321368220 Юр. адрес: 445042, г.Тольятти … ул. Луначарского, б-р 17-31"; privacy popup "утверждено Костриковым Н. В. ООО «ЭСТИВО»" | `/policy` |
| fixed | Floating widget (t898) | VK `vk.com/estivo_tlt`, WhatsApp `wa.me/79178246722`, `tel:+79178246722`; on mobile a full-width sticky "ПОЗВОНИТЬ" bar (390x60) → `tel:+79178246722` | |

**Popup `#popup:myform`** (Confirmed, promo_d_popup.png): "КОНСУЛЬТАЦИЯ. Оставьте свои контактные данные, мы свяжемся с вами в ближайшее время". Fields: Имя*, Телефон*, consent checkbox*, plus a hidden `form-spec-comments` field. Button "Отправить заявку". Every offer CTA (9 links in the crawl's link list, all with `href="#popup:myform"`) opens this same form, and no hidden field records which offer was clicked.

**Technical:**
- Title "Плетёная мебель ручной работы", empty meta description, **no H1**, canonical points to itself, no robots meta, 8/8 images without alt.
- Metrika counter **93915751**, the same as the home page. No `reachGoal` calls in the page HTML.
- Tilda page id 68967643. Sitemap `lastmod` 2026-08-28.
- Desktop document height 9781 px; mobile 7762 px. No horizontal overflow (scrollWidth 390 = innerWidth).

---

## 3. Findings

### F1. The campaign's headline promises contradict the main site and the legal pages
- **Problem:** The trust block makes stronger promises than the rest of the site, and two of them conflict with /vozvrat.
- **Location:** /promo section 8 (and the toast), compared with /, /vozvrat, /dostavka and /b2b.
- **Evidence (Confirmed):**
  - **Warranty.** /promo: "ГАРАНТИЯ 5 ЛЕТ на все изделия". Home and /b2b: "Гарантия 3 года". /vozvrat: "24 МЕСЯЦА".
  - **Delivery.** /promo: "ДОСТАВКА в любую точку мира". Home: "Доставка по всей России от 3 дней". /dostavka: GTA "в любой населенный пункт", Russia only.
  - **Returns.** /promo: "ОБМЕН И ВОЗВРАТ в течение 14 дней" with no conditions. /vozvrat: "Возврат возможен в момент принятия заказа или в течение 14 дней после. Но это не распространяется на мебель, выполненную по индивидуальным размерам … возврату не подлежит". It says nothing about exchange. The same /promo page sells "ИНДИВИДУАЛЬНЫЙ ДИЗАЙН", which is exactly the furniture excluded from returns.
  - **Samples.** "ОТПРАВИМ ОБРАЗЕЦ ЗА СВОЙ СЧЁТ" appears only on /promo, in the corpus of 152 pages. Its terms (what sample, to where) are not stated anywhere.
  - **Instalments.** "РАССРОЧКА ПЛАТЕЖА без переплат" is consistent with /dostavka ("Беспроцентная рассрочка до 12 месяцев"), but /promo does not state the 12-month term or the bank.
  - **Service.** "СЕРВИСНОЕ ОБСЛУЖИВАНИЕ на протяжении всего срока эксплуатации" appears nowhere else.
- **Customer impact:** A buyer who compares tabs, or reads the contract, finds 5 / 3 / 2 years. That damages trust exactly at the decision step on a purchase of 150–400k ₽.
- **Commercial impact:** Risk of disputes ("you promised 5 years") and of FAS/consumer-protection complaints about unreliable advertising. The legal assessment is a Preliminary assumption and needs a lawyer.
- **Confidence:** Confirmed (the texts). The legal risk is a Preliminary assumption.
- **Recommendation:** Pick one warranty value that matches the contract and use it everywhere. Change the delivery line to "по всей России, ТК ГТА до двери, страховка". Write "Возврат 14 дней для стандартных моделей" and link to /vozvrat. Either define the sample offer (for example "образцы роупа/ротанга и ткани по почте бесплатно") or remove it.
- **Validation:** Compare with the contract template. Re-crawl and grep for "гарант".
- **Effort:** S

### F2. Offer prices cannot be checked against the catalogue, and the discount maths is wrong
- **Location:** "Акция недели" slider; /uglovyedivany; rotang sets.
- **Evidence (Confirmed):**
  - "345.300 ₽ → 245.300₽ Ваша выгода - 30%!". 100 000 / 345 300 = **28.96 %**, so the claim rounds up to 30 %. Under Russian advertising practice the stated benefit should not exceed the real one (Preliminary assumption).
  - Neither 345 300 nor 245 300 appears anywhere in the corpus or the store API.
  - The catalogue sells "Угловые диваны «Вольтера Люкс»" in the 220х340 (2х4) size for **159 000 ₽** (store API: 129 000 / 139 000 / 159 000 for 220х220 / 220х280 / 220х340). Its description says "для одновременного размещения 4-5 персон". The promo calls the "Угловая Зона … 220х340 СМ" one for "12 персон".
  - The photo shows a table and about 6 chairs, so the 345 300 bundle presumably adds a table and chairs, but the composition is not listed. The comparable catalogue sets list their parts with prices (e.g. set №61 "Диван угловой Вольтерра Люкс 280х220 … =139.000, Стол Палермо Люкс … =66.900 …", 247 500 ₽).
  - The brand's own spelling differs: "Вольтера" vs "Вольтерра".
  - The price (slide 1) and the product name (slide 2) are on separate slides, so a visitor who sees one slide does not get both.
- **Customer impact:** The "old price" cannot be checked, and a shopper who looks it up finds the 220х340 sofa at 159 000, which makes "345 300" look inflated.
- **Commercial impact:** Credibility loss on the page's strongest offer. Possible advertising-law exposure for an unverifiable reference price (Preliminary assumption).
- **Confidence:** Confirmed (numbers); legal risk Preliminary.
- **Recommendation:** Show one card with name, photo, an itemized composition ("диван 220х340 159 000 + стол … + 6 кресел …"), the real total, the promo price, the true percentage (or the rouble saving "−100 000 ₽") and an end date. Link it to a real product or set page.
- **Validation:** Check every number against the store API. Get the owner to sign off on the old price.
- **Effort:** S

### F3. "Милан 3XL" exists, but the promo hides the product, the price and the gift value
- **Location:** Hero slides 1–2; /divanroup; /komplektyroup set №8; /aksessuary.
- **Evidence (Confirmed, store API):**
  - "Диван Милан 3XL (роуп)" costs **96 200 ₽** (/divanroup/tproduct/491338626712-divan-milan-3xl-roup).
  - The "АКЦИЯ МЕСЯЦА" bullet list (3-seat sofa + 2 large + 3 standard armchairs + HPL table) matches **"Комплект мебели из роупа 8" — 397 200 ₽**: "Диван Милан 3XL … 96.200, Кресло Милан … 26.400х3=79.200, Кресло Милан XL … 36.400х2=72.800, Стол Милан из HPL 220х100 см - 149.000".
  - The two hero slides are therefore probably the same offer split across two slides, but the page never names the set, its price or a link to it.
  - Gift value from the catalogue: "Укрывной Чехол" 15 000 ₽, "Разделочная доска из HPL" 2 500 ₽ each, so about 20 000 ₽ plus the trivet. That is about 5 % of 397 200 and is never stated.
  - Catalogue data in the same family is inconsistent:
    - Кресло Милан XL costs 36.400 in set 8 but 34 900 on /kresloroup and in set 17.
    - Set 17 lists "Диван Милан 3XL - 96.900".
    - Set 9 says "Итого: 417.200", but its price is 413 700.
  - "в этом месяце" has no month, and the page was last modified on 2026-08-28.
- **Customer impact:** The visitor has to submit a phone number just to learn what the offer costs. Mobile users see only "АКЦИЯ МЕСЯЦА" plus bullets.
- **Commercial impact:** Low-intent "сколько стоит?" leads, or bounces from price-sensitive paid traffic.
- **Confidence:** The exact match to set 8 is a Well-supported hypothesis. The prices are Confirmed.
- **Recommendation:** Merge the two slides into one offer card: "Комплект Милан 3XL на 6 персон — 397 200 ₽ + подарки на ~20 000 ₽ (чехол, 2 доски, подставка) до 30.11", with "Смотреть комплект" linking to the set page and "Забронировать" opening the form. Fix the Milan price inconsistencies in the catalogue.
- **Validation:** Track clicks on the card and form submits by offer (see F5).
- **Effort:** S

### F4. Stale, conflicting and undated promotions in October
- **Evidence (Confirmed):**
  - "ЛЕТНИЕ ПРИВИЛЕГИИ" is shown on 2026-10-20.
  - "Акция месяца", "Акция недели" and "в этом месяце" carry no dates.
  - The free coffee table appears in three different forms:
    - "кофейный столик для всех новых клиентов" (the ticker, repeated 7 times per row, 3 rows);
    - "кофейный стол в подарок каждому новому клиенту";
    - the hero gifts offer, which does not mention it.
  - None of these says which table, whether there is a minimum order, or whether it combines with the other offers.
  - The site's real discount section (home "СКИДКИ ДО 70%" → /salerotang; e.g. "Кресло из Роупа «Милан Лаунж» 9 900р. / 34 900р.") is not mentioned on /promo at all. The −29 % "акция недели" looks weaker than the sale the main site advertises.
- **Customer and commercial impact:**
  - Undated "акция недели" and summer copy in autumn read as an abandoned page.
  - A promise of a gift "каждому новому клиенту" with no terms invites disputes.
- **Confidence:** Confirmed.
- **Recommendation:**
  - Give every offer an end date and a short "Условия акции" line, plus a terms popup (which table, minimum order, whether offers combine).
  - Change the season copy to off-season: pre-order for the 2027 season, a winter storage service and the covers.
  - Add a block for the clearance stock ("Остатки со скидкой до 70%") that links to /salerotang and /saleroup.
- **Effort:** S

### F5. One generic form for every offer; offer attribution is lost
- **Evidence (Confirmed):**
  - All offer CTAs, the toast and the tickers open `#popup:myform`, titled "КОНСУЛЬТАЦИЯ".
  - The form does not mention the chosen offer, and there is no hidden field or per-CTA popup.
  - No `reachGoal` calls in the HTML. Tilda can send form goals itself; whether it does is not verified.
  - "Популярные позиции" buttons go to whole category pages (/komplekty, /komplektyroup) rather than to the set in the photo.
- **Impact:**
  - The manager calls back without knowing whether the lead wanted Milan, Вольтерра or the free table.
  - The owner cannot see which offer converts, so the page cannot be optimized.
  - The visitor who clicked "ХОЧУ МИЛАН С ПОДАРКАМИ" sees a generic "КОНСУЛЬТАЦИЯ" form, a mismatch in the message.
- **Confidence:** Confirmed (behaviour). The analytics gap is a Well-supported hypothesis; check it in Metrika.
- **Recommendation:**
  - Duplicate the popup per offer with its own heading (e.g. "Забронировать Милан 3XL с подарками") and a hidden `offer` field.
  - Add a "Удобнее написать: Telegram/MAX/VK" choice.
  - Set up a Metrika goal per popup.
  - Link each popular-position slide to its exact set.
- **Validation:** Leads by offer in Tilda Leads and Metrika over 4 weeks.
- **Effort:** S–M

### F6. Contact and legal identity differ from the rest of the site
- **Evidence (Confirmed):**
  - **Phone.** /promo uses +7(917)824-67-22 everywhere: contacts, the sticky "ПОЗВОНИТЬ" bar and WhatsApp. Every other page uses +7 927 200 43 03.
  - **Legal entity.** The /promo footer shows ООО “Эстиво” (ОГРН 1146320022089), and its privacy text is "утверждено Костриковым Н. В. ООО «ЭСТИВО»". The /dostavka and /vozvrat footers show "ИП МЕЛИХОВА МИРОСЛАВА СЕРГЕЕВНА, ИНН 632147606449". /kontakty also names the ООО.
  - **E-mail.** "Esti-vo@mail.ru" on /promo vs "esti-vo@mail.ru" elsewhere (cosmetic).
- **Interpretation:** The 917 number may be a deliberate call-tracking number or a single manager's line for the campaign (Preliminary assumption). If it is call tracking, it is a good practice, but it should then be dynamic (a call-tracking service) rather than hard-coded. Two legal entities on one site confuse a buyer who checks the seller before paying 245 000 ₽.
- **Recommendation:**
  - Confirm who answers the 917 number and whether calls to it reach the CRM.
  - Name one seller per order and keep the requisites consistent.
  - Show the same contract party in the promo footer as on the main site, or explain the relationship ("производство — ООО, продажи — ИП").
- **Effort:** S

### F7. The mobile first screen does not say what is offered or what it costs, and its CTA is covered
- **Evidence (Confirmed, iPhone 13 emulation; screenshots promo_m_first_t3/_t9, promo_mobile_first.png):**
  - The viewport is 390x664. A 100 px header holds the logo and burger; there is no phone number and no offer in it.
  - The hero shows "АКЦИЯ МЕСЯЦА" plus four bullets, with no product name, no price, no deadline and no gift.
  - The main CTA "УЗНАТЬ ПОДРОБНЕЕ" sits at y=609–669 and **is overlapped by the fixed "ПОЗВОНИТЬ" bar** (y=604–664, 390x60). Until the user dismisses it, the cookie bar (y=538–664) covers both.
  - The Milan gift slide exists but is slide 2 and does not autoplay.
  - Slider arrows are 10x18 px and the dots 10x10 px, well below 44 px.
  - The section headings render in a fallback serif on mobile (Times-like), unlike desktop. The cause is not determined; this is a Preliminary observation.
  - The "Акция недели" price only appears at about y=1112, below the first screen.
- **Impact:** A paid-traffic visitor gets about 2 seconds to see a reason to stay and sees an anonymous list. The single visible action is a call, which many people avoid during the working day.
- **Confidence:** Confirmed (emulation, not a real device).
- **Recommendation:** Use a compact hero:
  - an H1 with the offer and its price ("Комплект Милан 3XL на 6 персон — 397 200 ₽ + подарки до 30.11");
  - one line of proof (for example the Yandex rating, if it is good);
  - a primary "Забронировать цену" button and a secondary "Написать в Telegram/MAX".
  - Keep the sticky bar but make it two buttons ("Позвонить | Написать") and keep the hero CTA above it.
  - Replace the slider with a static hero.
- **Effort:** M

### F8. Navigation, popups and widgets compete with the offer
- **Evidence (Confirmed):**
  - **Desktop header.**
    - The "ОСНОВНОЙ САЙТ" button (x 1294–1420) overlaps the "Контакты" anchor (x 1281–1350); "Контакты" is visibly cut off as "Ко" at 1440 px.
    - The burger opens a 16-link catalogue menu, which is an exit to the whole catalogue. Its "Кашпо" item goes to a Google Drive file.
    - The "Наши проекты" anchor points to `#guarantees`.
  - **Overlays on the first screen.** Three overlays sit on the hero at once: the cookie banner (bottom left), the typewriter "УВАЖАЕМЫЕ КЛИЕНТЫ!" toast (bottom right, 360x120 on desktop) and the chat widget. The toast's own heading "ВНИМ|" is mid-typing in the crawl text.
  - **Tickers.** Three marquee tickers repeat "Акция: кофейный столик для всех новых клиентов" 21 times.
  - **Exits.** "ПОСМОТРЕТЬ КАТАЛОГ" appears twice and sends the user to /rotang, the general catalogue.
- **Impact:** Attention and exit leakage. A landing page for a paid click usually removes the full catalogue menu. Here the catalogue is one click away in two places, plus Google Drive.
- **Confidence:** Confirmed. The conversion effect is a Well-supported hypothesis (standard landing-page practice); measure it.
- **Recommendation:**
  - Keep only the in-page anchors (Акции / Отзывы / Проекты / Контакты), the phone number and one messenger link.
  - Remove the burger catalogue and the "ОСНОВНОЙ САЙТ" button, or move them to the footer.
  - Remove the toast; fold "образец" into the trust block if it is real.
  - Keep a single slim ticker or none.
- **Effort:** S

### F9. Social proof is unverifiable and the projects carry no information
- **Evidence (Confirmed):**
  - **Reviews.**
    - "ОТЗЫВЫ О НАС" is a slider of chat screenshots (WhatsApp-style bubbles, one Instagram-style post) plus VK videos titled "Видео от ESTIVO".
    - There are no names, cities, dates or purchased sets, and no link to Yandex Maps or Avito ratings.
    - One screenshot is duplicated (IMG_1218 at slides 0 and 11).
  - **Videos.** The videos are VK Video embeds. Clicking play inserts `vkvideo.ru/video_ext.php?oid=-219037647&id=456239121&…autoplay=1`. In the page the frame was still black after 8 s (promo_d_video_click.png). Opened directly, the embed loaded and showed video content (promo_vk_embed.png). The videos work, but slowly, and they are vertical phone clips of a gazebo with no testimonial framing.
  - **Projects.** "НАШИ ПРОЕКТЫ" has 8 zoomable photos with no captions, no `alt`, no set name, no city and no link to buy "такой же комплект".
  - **Process claims.** "СОЗДАНИЕ ПРОЕКТА разработка 3D-визуализации" and "фото отчет на каждом этапе" appear only here and on an unlinked draft page, /page69400427.html, titled "Copy of …". There are no examples of a 3D render or a photo report.
- **Impact:** Premium buyers look for proof. Anonymous chat screenshots read as unverifiable, and the strongest assets (real installations) are not tied to products.
- **Confidence:** Confirmed. The video playback finding is a Well-supported hypothesis; check it on a real phone.
- **Recommendation:**
  - Show the 3 best reviews with name, city, date, set and photo.
  - Add a "Рейтинг на Яндекс Картах X,X" badge linking to the card, if the rating is good.
  - Caption each project ("Тольятти, терраса, комплект Вольтерра Люкс 220х340") and link it to the set.
  - Show one real 3D render and one photo report as evidence.
- **Effort:** M

### F10. The page's role and traffic source are undefined; it is indexable but orphaned
- **Evidence (Confirmed):**
  - /promo is in sitemap.xml (lastmod 2026-08-28), has no `noindex`, and its canonical points to itself.
  - It has a generic title "Плетёная мебель ручной работы", an empty description and no H1.
  - **No crawled page links to /promo** (0 of the crawled pages). The home banner "СКИДКИ ДО 70% / ПЕРЕЙТИ НА СТРАНИЦУ СПЕЦПРЕДЛОЖЕНИЙ" goes to /salerotang instead.
  - The page has its own header, phone and legal footer, and the same Metrika counter as the main site.
  - No UTM handling is visible in the HTML; Tilda forms capture UTMs automatically, but that is not verified here.
- **Interpretation (Well-supported hypothesis):** It is a paid-traffic or direct-link landing page (Yandex Direct, VK ads, or a link sent by managers in messengers/Avito), built in summer 2026 and not maintained since. Because it is indexable, it can also compete with the home page in search for "плетёная мебель ручной работы", and it shows stale offers to organic visitors (Preliminary assumption).
- **Recommendation:**
  - If it is used for ads, set `noindex` and remove it from the sitemap, or give it a proper offer title/H1/description.
  - Tag every ad and QR link with UTMs and record the source in the lead.
  - Decide one owner and one update cadence: offers expire on the last day of the month.
- **Validation:** Metrika → Отчёты → Источники for URL /promo over 90 days; Direct/VK campaign landing URLs.
- **Effort:** S

---

## 4. Scenario evaluation (channel not established)

| Scenario | Fit today | Main gap | What the page needs |
|---|---|---|---|
| **Yandex Direct search** ("плетеная мебель купить", "мебель из роупа", "угловой диван ротанг") | Weak. The query intent is a product or category; the page shows anonymous bullet lists, and the first screen has no price. | Search users compare prices across 3–5 tabs; no price means a bounce. The 5-year/14-day promises conflict with the site they will check. | One offer per ad group (a Milan landing page for "роуп", a Вольтерра one for "угловой диван ротанг"), with price, composition and a deadline. Alternatively send search traffic straight to category/set pages and keep /promo for retargeting. |
| **RSYA / VK targeting** (cold, visual) | Medium. The photos are strong and the gift hook suits impulse attention. | Cold users need a low-commitment step; the only step is a phone form or a call. | A lead magnet: "Подборка комплектов + цены 2027 в PDF/Telegram", or "образцы материалов бесплатно" (if real). A quiz is optional. A messenger CTA. |
| **Offline QR** (showroom, fairs, flyers, delivery boxes) | Medium. A visitor who already knows the brand wants the current deal. | Stale summer offers; the phone differs from the flyer/main site. | A date-stamped "Акции месяца" page with a working phone and an "Записаться в шоурум" CTA (visits are by appointment). |
| **Avito / social / manager-sent link** | Good, if a manager explains it. | Undated; reviews unverifiable. | Keep it short: the offer card, terms, reviews with names, a messenger button. |

---

## 5. Recommendation: **Redesign as a monthly offer landing page and stop it competing with the site** (not delete)

**Why not delete:** The page has a separate tracked phone, its own Metrika context and a working lead form. The building blocks (offer, gifts, trust, projects, process) are right for a lead-generation business with no online payment.

**Why not keep as is:**
- Its promises contradict the legal pages (F1).
- Its prices cannot be verified (F2, F3).
- Its offers are stale (F4).
- Leads cannot be attributed (F5).
- The mobile first screen is anonymous and its CTA is covered (F7).

**Why not merge into /salerotang:** The sale pages are catalogue grids of clearance stock. /promo sells made-to-order sets with gifts and design services, a different job. Link the two to each other instead.

**Proposed structure (mobile first):**
1. **Hero.** H1 with one offer, price and deadline, e.g. "Комплект Милан 3XL на 6 персон — 397 200 ₽ + подарки на 20 000 ₽ до 30 ноября". Photo of that set. Primary CTA "Забронировать цену" (form with the hidden offer). Secondary "Написать в Telegram/MAX". One proof line: years in business, rating, warranty as in the contract.
2. **Offer cards (2–3 max)**, each showing photo, name, composition with prices, old/new price, real % or ₽ saving, deadline, "Подробнее о комплекте" (link to the set page) and "Забронировать" (offer-specific popup). Example: Вольтерра Люкс 220х340 zone, with its composition itemized.
3. **Gift and new-client terms.** Which coffee table, minimum order, whether offers combine.
4. **Clearance strip.** "Остатки со скидкой до 70%" linking to /salerotang and /saleroup.
5. **Proof.** 3 named reviews with photos, a Yandex rating badge, 1–2 short videos (with poster frames) and captioned projects linked to their sets.
6. **How we work.** Video consultation → 3D project (with a real example) → production with photo reports → delivery by ТК ГТА with insurance across Russia → warranty and returns, linking to /vozvrat and /dostavka. Show "Рассрочка 0% до 12 мес." with an example monthly payment.
7. **Final CTA + contacts.** One phone that matches the main site (or dynamic call tracking), messenger links, a showroom booking, and the one legal entity that will sign the contract.

**Remove or move:**
- the burger catalogue and the "ОСНОВНОЙ САЙТ" button (move to the footer);
- the typewriter toast;
- two of the three tickers;
- the "ЛЕТНИЕ ПРИВИЛЕГИИ" copy;
- the Google Drive link.

Then set `noindex` (if it is ad-only) or SEO meta, add UTMs, and add Metrika goals per offer.

---

## 6. Top 5 priorities (promo-specialist view)
1. **Align the promises with the contract and /vozvrat** (warranty 5 / 3 / 2 years; "в любую точку мира"; "обмен и возврат 14 дней" vs the exclusion for custom furniture; the undefined sample offer). Effort S, F1.
2. **Make each offer concrete:** product, itemized price, honest discount (−29 %, not −30 %), deadline. Milan 3XL = set №8, 397 200 ₽; Вольтерра 220х340 sofa alone is 159 000 ₽. Effort S, F2/F3.
3. **Rebuild the mobile first screen:** an offer H1 with price, and a CTA not covered by the sticky call bar or the cookie bar. Effort M, F7.
4. **One popup per offer with a hidden offer field, plus Metrika goals and UTMs.** Without this the page cannot be judged or improved. Effort S–M, F5/F10.
5. **Remove stale and duplicated offers and the exits;** unify phone and legal entity with the main site (or document deliberate call tracking). Effort S, F4/F6/F8.

## 7. Open questions and the data needed
- What traffic reaches /promo? Need Metrika (counter 93915751): sources, UTMs, conversion rate for /promo vs /, and the Direct/VK campaign landing URLs.
- Is +7 917 824-67-22 a call-tracking or manager line, and do its calls reach the CRM?
- Which entity signs the contract (ООО “Эстиво” or ИП Мелихова), and what warranty term is written in it?
- What is the itemized composition behind 345 300 / 245 300 ₽, and was 345 300 ever the actual selling price?
- Which coffee table is the "подарок каждому новому клиенту", with what minimum order, and does it combine with the Milan gifts?
- Is "отправим образец за свой счёт" a real, operational offer? What is sent, and to which regions?
- Do the VK videos play quickly on a real iPhone or Android device on mobile data? This audit used emulation only.
- Does Tilda already send form-submit goals to Metrika for this page (Tilda settings → Analytics)?
