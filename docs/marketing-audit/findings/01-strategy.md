# 01 — Strategy, positioning, value proposition (Agent 1, Marketing Strategist)

Date: 2026-10-20. Source: the live Tilda site estivo63.ru, read through the Playwright corpus (`corpus/*.txt`, `crawl_results.jsonl`, `shots/`). I did not visit the site again. I did not submit any forms.
Confidence labels: **Confirmed** (seen in the corpus, location given), **Well-supported hypothesis**, **Preliminary assumption**.
Cross-checked against `findings/02-russian-market.md` (Agent 2) and `findings/07-competitors.md` (Agent 7). I don't repeat their findings on warranty, phones, delivery or messengers. I cite them only where they bear on positioning.

## 1. What I inspected

| Page | What I used it for |
|---|---|
| `/` (home.txt, shots/ux_home_mobile_first.png) | Hero, the claims (Rolls-Royce, 10+ years, handmade), segments, the production story, reviews, the SEO text, the legal entity |
| `/onas` | Team size, production facilities, the "bestsellers" block |
| `/b2b` | HoReCa offer, material explanation, products listed "for business" |
| `/roup`, `/rotang` | The two catalogue hubs: structure, copy, the claims for each material |
| `/price` | Price list (rattan pieces sold singly; rope "BUY NOW" pages) |
| `/salerotang`, `/saleroup` (+ shots/salerotang_desktop.png) | Discount depth and old/new prices |
| `/promo` | The ad landing page's offer stack |
| Category listings: komplekty, komplektyroup, kreslo, kresloroup, divan, divanroup, stol, stolroup, stolkofroup, shezlong, kreslopodves, uglovyedivany, hranenie, aksessuary | Card prices, "Цена по запросу" cards |
| Product pages (`*/tproduct/*`): see the coverage note in §3 | Price, set composition ("В комплект входит … Итого"), the material lines, template leftovers |

Scripts: `a01/prices.py` (product pages → price per section), `a01/cats.py` (listing cards), `a01/comps.py` (unit prices of set components compared with prices of the same pieces sold singly).

Not accessed: real lead and sales data, the CRM, Avito and Yandex accounts, Wordstat, margins. The B2B "Открыть презентацию" target is not visible in the crawl links, so I could not check it.

## 2. Business model as the site presents it (Confirmed unless marked)

- **The maker:** "ESTIVO – ПРОИЗВОДИТЕЛЬ ПЛЕТЁНОЙ МЕБЕЛИ РОДОМ ИЗ ТОЛЬЯТТИ", "более 20 профессионалов", "три цеха по сборке, отдельный цех по алюминиевой сварке и окраске металла и складские помещения 650 кв. м" (/onas). "10 + лет" (home).
- **Revenue model:** lead generation. A cart is turned into a request, and a manager quotes the price. The footer says the site "не является публичной офертой". There are two paths: catalogue items ("поиск по наличию на складах") and individual projects with a designer (home, the "Этапы производства" block).
- **Segments named:** "ДЛЯ ДОМА, ДАЧИ И БИЗНЕСА" (hero); "Для квартиры, частного дома, дачи и летних террас" and "Для отелей, ресторанов, кафе и гостевых домов" (home); /b2b lists restaurants, hotels, SPA, guest houses, terraces and tourist bases. **Designers/architects** are not addressed as a partner segment anywhere. There is no designer page, no trade discount and no specification kit. The "designers" on the site are ESTIVO's in-house designers.
- **Materials actually sold:** synthetic rattan ("Материал плетения: Искусственный эко-ротанг" on 29 rattan PDPs), rope, plus HPL, veneer, DPK, glass and metal tables. Listings also include "Комплект мебели из полипропилена" (205 800р.) and "Комплект мебели из стропы" (price on request). I found **no natural-rattan product**: none of the product pages mention "натуральн".
- **Legal entity on the main site:** "ИП МЕЛИХОВА МИРОСЛАВА СЕРГЕЕВНА … ОГРИП 323632700013220". The ОГРИП prefix 323 means a 2023 registration (**Well-supported hypothesis**). /promo shows ООО "Эстиво", ОГРН 1146320022089 (registered 2014). Agent 2 F2 covers the trust angle. For strategy, the "10+ лет" claim rests on the ООО, which the main site doesn't show.

## 3. Price positioning: actual ranges from the corpus (Confirmed)

Coverage: all 234 product pages from sitemap-store (crawl complete, 276/276 URLs), plus the category listing cards. I parsed them with `a01/prices.py` and `a01/cats.py`. Prices are the figures on the page. The prices the managers actually quote are unknown.

| Category | Material | Items with a price | Range, ₽ | Median, ₽ |
|---|---|---|---|---|
| Sets (/komplekty) | rattan | 51 of 53 | 59 500 – 397 000 | 230 500 |
| Sets (/komplektyroup) | rope (+1 polypropylene, +1 "стропа") | 23 of 24 | 78 600 – 498 400 | 225 400 |
| Armchairs/chairs/stools (/kreslo, /price) | rattan | 13 | 9 900 – 48 000 | 24 900 |
| Armchairs/chairs (/kresloroup listing) | rope | 12 | 17 900 – 45 600 | ~30 000 |
| Sofas (/divan) | rattan | 6 | 36 900 – 70 400 | 64 000 |
| Sofas (/divanroup) | rope | 3 | 64 900 – 228 000 (corner) | 96 200 |
| Corner/U-shaped sofas (/uglovyedivany) | rattan | 1 of 2 | 129 000 (the U-shaped one has no price) | — |
| Dining and coffee tables (/stol) | rattan | 16 | 9 900 – 46 900 | 26 900 |
| Dining tables (/stolroup) | rope base + HPL/veneer/DPK/glass | 7 | 26 900 – 64 900 | 29 900 |
| Coffee tables (/stolkofroup) | rope/HPL | 5 | 16 900 – 42 900 | 19 900 |
| Sun loungers (/shezlong) | rattan | 4 | 34 900 – 59 000 | 36 900 |
| Hanging cocoons (/kreslopodves) | rattan/metal | 5 (+2 cards) | 28 000 – 79 900 | 38 000 |
| Storage (/hranenie) | rattan/HPL/rope | 5 cards | 28 500 – 78 600 | 55 000 |
| Accessories (/aksessuary) | HPL board, planters, Christmas-tree skirts, cover | 5 | 2 500 – 18 000 | 7 000 |
| Sale (/salerotang p.1 + /saleroup) | both | 53 cards with old/new price | new 5 400 – 345 000 | discount: median 47 % (rattan), 43 % (rope); max 87 % |

**"Цена по запросу" and missing prices (Confirmed):**
- 5 listing cards carry the label "Цена по запросу":
  - «Комплект мебели из стропы» and «Комплект мебели из ротанга» on /komplekty;
  - «Комплект мебели из стропы» on /komplektyroup;
  - «Сундук «Позитано»» on /hranenie and «Укрывной Чехол» on /aksessuary. These two show "Цена по запросу" **and** a price (28 500р. / 15 000р.), which contradicts itself.
- 10 sellable product pages show no price at all:
  - the 3 sets above;
  - «П-образные диваны «Вольтерра Люкс»»;
  - 5 nameless "комплект из ротанга" pages that make up the whole /onas "НАШИ БЕСТСЕЛЛЕРЫ" block;
  - the stub "sale роуп" (/tproduct/175447806982).
- The 11 colour swatches in /cvetrotanga are stored as products with no price and an English "BUY NOW" button.

**Where this places ESTIVO (cross-check with 07-competitors §4):**
- ESTIVO's list prices sit in the band of the national makers: 4SIS (Лугано lounge 473 500), АртРотанг (dining group 315 000) and МарКо (22 000–308 000). It is 2–5× above the importers: Marite and Deamo sets at 18–126 k, Эко-Композит chairs at 11 440–18 040.
- The rope range tops out at 498 400 (set 19), above the 4SIS flagship.
- But the sale prices («Кресло из Роупа «Бари Лонг»» 5 400р., «Бари» 6 900р., «Кокон «Комо Люкс 2х»» 10 000р. instead of 79 900р.) go **below even the cheapest importer chairs**. **Confirmed.**
- ESTIVO therefore has no single price position. It is priced like a premium maker at list and like a clearance outlet on sale.

## 4. Answer to the core question

**Does the site give a customer a compelling reason to buy from ESTIVO rather than a competitor? Not yet.** (Well-supported hypothesis, based on the findings below.)

ESTIVO does have real, defensible advantages:
- it is the only local *maker* in Samara oblast that Agent 7 found;
- it has its own welding and powder-coating shop;
- it makes to custom size and colour;
- it offers 0 % instalments for 12 months;
- /promo adds a free sample shipment, photo reports during production, 3D visualisation and lifetime service.

The site does not turn these into a value proposition. The first thing a mobile visitor sees is a discount banner. The main pages talk in superlatives ("Rolls-Royce", "Эверест мастерства") and don't prove them. The strongest offer stack sits on an orphan landing page. Two catalogues are run in parallel with different quality standards, and the list prices are undermined by 40–87 % markdowns and by mismatches between set and single-item prices.

A shopper comparing ESTIVO with 4SIS or АртРотанг (similar prices, more proof) or with Marite/Deamo (much cheaper) gets no reason to pay ESTIVO's price.

## 5. Findings

### S1. The brand opens with "СКИДКИ ДО 70%", and its premium claims are contradicted on the same site
- **Problem:** The positioning is incoherent: "premium/Rolls-Royce" on one side, clearance-outlet pricing on the other.
- **Location:** The home hero (mobile first screen: shots/ux_home_mobile_first.png); the home copy; /salerotang and /saleroup; /b2b and home "по доступным ценам".
- **Evidence:**
  - The mobile first screen is entirely an orange block, "СКИДКИ ДО 70%" with "ПЕРЕЙТИ НА СТРАНИЦУ СПЕЦПРЕДЛОЖЕНИЙ". There is no product, material or brand promise above the fold.
  - Further down: "ESTIVO - это Rolls-Royce среди мебели для открытых пространств", "ДИЗАЙНЕРСКАЯ МЕБЕЛЬ ПРЕМИУМ-КЛАССА", "Партнёрство с ESTIVO - знак статуса".
  - Yet the same pages also say "комплекты плетеной мебели … по доступным ценам".
  - Sale cards: median discount 43–47 %; 23 of 53 cards are at ≥50 % off, and the maximum is 87 % («Кокон «Комо Люкс 2х»» 10 000р. / 79 900р.).
  - The PDP spec for cushions is "Ткань Оксфорд" (24 rattan PDPs), a utilitarian polyester and not a premium textile.
- **Customer impact:** A premium buyer reads the brand as a discounter. A price-led buyer anchors on 6 900р. chairs and treats every 30 000р. list price as inflated. The −70 % banner also makes the list prices look fictitious (compare the Avito review "по факту стоимость выше почти в два раза").
- **Commercial impact:** It erodes the price the brand can command and draws bargain-hunting leads that convert badly on made-to-order sets. "Old prices" that were never charged also carry a legal risk under the advertising law (Well-supported hypothesis; legal check needed).
- **Confidence:** Confirmed (copy and prices). The impact is a Well-supported hypothesis.
- **Recommendation:**
  - Pick one position: "a local maker of premium outdoor furniture, made to your size and colour".
  - Replace the hero with the product plus the promise plus proof (for example "Плетёная мебель на алюминиевом каркасе. Своё производство в Тольятти. Изготовим в вашем размере и цвете за N недель").
  - Move clearance into a quiet, explained "Шоурумные образцы / остатки склада" section with the reason for each discount (showroom sample, discontinued colour). The sale photos look like showroom and warehouse floors, which supports this framing.
  - Drop "Rolls-Royce" and "Эверест" unless they can be backed with proof (see S3).
- **Validation:** A/B test the hero on paid traffic. Measure the lead rate and the average lead value (set vs single item) for 4–6 weeks.
- **Effort:** S (hero/copy), M (restructuring the sale section).

### S2. The real differentiators are scattered, and the best offer stack lives on an orphan page
- **Problem:** ESTIVO's genuine reasons to buy are not assembled into a single value proposition on the main site.
- **Location:** /promo (not linked from any of the other 275 crawled pages; it links only to itself); home; /dostavka; /b2b.
- **Evidence:**
  - Only /promo has "ОТПРАВИМ ОБРАЗЕЦ ЗА СВОЙ СЧЁТ", "фото отчет на каждом этапе", "разработка 3D-визуализации вашего интерьера", "СЕРВИСНОЕ ОБСЛУЖИВАНИЕ на протяжении всего срока эксплуатации", "Акции для новых клиентов - кофейный стол в подарок".
  - The crawl link analysis (crawl_results.jsonl) shows no page except /promo itself that links to /promo.
  - "Беспроцентная рассрочка до 12 месяцев" appears only on /dostavka and /b2b.
  - "изготовим по индивидуальным размерам" appears only inside long SEO text blocks.
  - The home "ПОЧЕМУ ESTIVO" block contains only abstract lines ("Мы создаём мебель, которая становится частью вашего успеха").
- **Customer impact:** Organic and direct visitors never see the sample offer, the photo reports or the 3D project, which are exactly what reduces the risk of a 200–400 k remote purchase.
- **Commercial impact:** The main site converts with weaker arguments than the paid landing page. If /promo is the ad destination, its offers are also unverifiable from the main site (Preliminary assumption).
- **Confidence:** Confirmed.
- **Recommendation:**
  - Build one "Почему ESTIVO" block, used on the home page, both catalogue hubs and every PDP, with 5–6 concrete, provable points: own workshop in Tolyatti (show it); custom size and colour; lead time N weeks; one warranty figure (see Agent 2 F1); 0 % instalments for 12 months; photo report and sample before production.
  - Only include the /promo offers (the sample, the gift table) if they are real and current.
- **Validation:** Measure the PDP→request rate before and after. Ask managers which arguments close deals.
- **Effort:** S–M.

### S3. "Natural rattan" and "handmade/premium" claims are not substantiated, and some contradict the product data
- **Problem:** The copy promises natural rattan vine and craft processes that the product data doesn't support. There is no visual proof of the handmade production.
- **Location:** /rotang title; the home SEO text; /rotang SEO text; /b2b; the PDPs.
- **Evidence:**
  - /rotang `<title>`: "Купить мебель из натурального ротанга".
  - Home SEO text: "Мастер проводит с ротанговой лозой десятки часов: он проваривает её для эластичности", "лоза прошла правильную атмосферную сушку, а лаковое покрытие нанесено минимум в четыре слоя".
  - But 29 PDPs state "Материал плетения: Искусственный эко-ротанг", and no product page mentions "натуральн".
  - /b2b is candid: "Искусственный ротанг … Говоря простыми словами, — пластик".
  - Other claims contradict each other:
    - temperature range "от -70 до +70°С" (home, /roup, /b2b) vs "от -50 до +80°С" (/rotang);
    - "10 + лет" vs the main-site seller "ИП … ОГРИП 323…" (2023);
    - frame "Металл, порошковый окрас" (24 PDPs) vs "прочного алюминия" / "пайки алюминиевых труб в среде аргона" (copy).
  - "Тысячи часов ручной работы" and "десятки испытаний" are given with no figures, tests, photos or video of the workshop, masters or welding shop in the corpus pages I read. Social proof is an Avito widget, "5.0 из 5 На основе 36 оценок", and per Agent 2 the linked Avito profile is now "Пользователь не найден".
- **Customer impact:** A buyer who checks finds that "natural rattan" is plastic and the "aluminium" frame may be steel. Every other claim then loses credibility, the handmade one included (which is probably true).
- **Commercial impact:** Trust loss at the decision stage. There is a risk of complaints or FAS issues under misleading-advertising rules, and SEO for "натуральный ротанг" attracts the wrong demand.
- **Confidence:** Confirmed (contradictions). The legal risk is a Well-supported hypothesis.
- **Recommendation:**
  - Rewrite the rattan copy honestly: "искусственный ротанг (HDPE) ручного плетения — не гниёт, не выгорает, зимует на улице". Synthetic rattan is the right product for outdoor use, so this is a selling point, not a weakness.
  - State the frame alloy per product.
  - Unify the climate range.
  - Substantiate "handmade" with:
    - a "Производство" page (photo/video of the three workshops, a named master weaver, weaving hours per model, e.g. "кресло Бари — 14 часов плетения", only if measured);
    - certificates actually shown, not just "ВСЯ МЕБЕЛЬ ИМЕЕТ СЕРТИФИКАТЫ";
    - a dated portfolio of installed projects.
  - Remove the AI-sounding SEO essays that make unprovable claims.
- **Validation:** Content audit sign-off by the owner. Track time on page and requests from the "Производство" page.
- **Effort:** M.

### S4. Rope and rattan run as two parallel catalogues, not one brand
- **Problem:** The two material lines differ in navigation, naming, page quality and pricing logic. The site sells two catalogues instead of one ESTIVO range.
- **Location:** The global menu; /roup vs /rotang; /price; the PDPs.
- **Evidence:**
  - Menu: "Каталог роупа / Акции роупа / Каталог ротанга / Акции ротанга". There are separate hubs and separate sale pages, and the same sale items (Бари, Кокон «Комо», Стол HPL 220х100) are duplicated across both.
  - Naming: rattan items use Italian names in «» (Палермо, Терлаго, Кастельсардо) and sets numbered «№1…№90». Rope items have a "(роуп)" suffix and sets "Комплект мебели из роупа 1…22", and rope set numbers don't match the sale-page numbers. Some names are shared across materials and with 4SIS (Бари, Милан; 07-competitors F9).
  - Page quality: all 30 rope/HPL single items live under /price with an English "BUY NOW" button and **no spec lines** (0/30 have material, frame or dimensions). All 13 rattan chair PDPs have material/frame/cushion specs. Set PDPs in both lines (0/77) have no specs, only a component price list.
  - The only guide across materials is the "ЧТО ВЫБРАТЬ" block: two sentences per material. HPL, veneer, DPK, polypropylene and "стропа" appear as materials with no explanation.
  - /b2b "ПОПУЛЯРНЫЕ ПОЗИЦИИ ДЛЯ БИЗНЕСА" shows 16 items, all rattan, and no rope at all.
- **Customer impact:** A buyer who wants "a lounge set for a terrace" has to choose a material before seeing options. They can't compare rope and rattan versions of the same use, and the rope line looks less finished.
- **Commercial impact:** Fewer cross-material upsells (a rattan set with an HPL/veneer table). Duplicated SEO pages, and harder ad targeting for a brand that has no single story.
- **Confidence:** Confirmed.
- **Recommendation:**
  - Present one ESTIVO range organised by **use/room** (лаунж-зона, обеденная группа, кресла, подвесные, шезлонги, столы), with the material as a filter and a short comparison table (rope vs synthetic rattan: feel, care, outdoor wintering, price).
  - Group models into named collections across materials (e.g. "Милан": rope chair, rope sofa, HPL table).
  - Merge the two sale pages.
  - Give rope PDPs the same spec template as rattan.
- **Validation:** Track the share of sessions that view both materials, and the set-request rate. Run a card-sort or interview with 5 recent buyers about how they chose.
- **Effort:** M–L (catalogue restructure in Tilda).

### S5. Price integrity: set prices, single-item prices and "old prices" don't reconcile
- **Problem:** Set prices are the sum of component prices, but the same component costs different amounts in different places. Sale "old prices" don't match current list prices.
- **Location:** Set PDPs ("В комплект входит … Итого"); /price; /stolroup; /saleroup; /kresloroup.
- **Evidence (Confirmed):**
  - «Комплект мебели из роупа 2» lists "Стол Милан из HPL 180х110 см - 119.000". The same table sold singly, «Стол Милан с HPL 180х110 см (роуп)», is **38 100р.** (/price, /stolroup).
  - "Кресло Палермо" is 19 900 in set №25 and in one sale set, but 20 800 in other sets and on /price.
  - «Кресло Бари (роуп)» lists at 29 900р. (/kresloroup), but its sale card shows an old price of 28 900р.
  - Sets carry no bundle benefit. For example, set №30 = table 64 900 + 8 × Палермо 20 800 = 231 300, exactly the sum.
  - Base prices for size-variant items are shown without "от": «Обеденный стол «Овара»» 33 900р. with 12 sizes listed, while a set uses "Стол Овара 180х90 - 51.900".
  - A home-page Avito review (Яна, "Не договорились"): "указана стоимость, по факту стоимость выше почти в два раза".
- **Customer impact:** The buyer can't predict the final quote and suspects bait pricing. The set page tells them they save nothing by buying the set.
- **Commercial impact:** Lead loss after the manager's quote. A negative review is already public.
- **Confidence:** Confirmed (numbers). The impact is a Well-supported hypothesis.
- **Recommendation:**
  - One price list as the single source of truth.
  - Show "от N ₽" plus what drives the price (size, top, cushions).
  - Give sets a visible bundle benefit ("комплект дешевле на N ₽, чем по отдельности"), or present them honestly as configurations.
  - Use old prices only where they were genuinely charged.
- **Validation:** Log the quoted vs listed price in the CRM. Re-run `a01/comps.py` after the fix.
- **Effort:** M.

### S6. Segments: B2B lacks proof and contract terms; designers are not addressed; dacha and premium are mixed
- **Problem:** The site names three audiences but builds a convincing offer for none of them.
- **Location:** /b2b; home; site-wide.
- **Evidence:**
  - /b2b offers "Срок реализации от 4 недель", "Скидки оптовым покупателям", "БРЕНДИРОВАНИЕ МЕБЕЛИ" (logo on cushions) and "Открыть презентацию" (the target wasn't visible in the crawl).
  - It has no case studies, client names, photos of installed restaurants or hotels, volume pricing, contract-grade fabric or fire-safety documents, payment-by-contract terms or a dedicated B2B contact.
  - Its "popular for business" list is 14 residential-style rattan sets at 162 700–397 000 and is not priced per seat.
  - Designers/architects get no page, trade terms, 3D/CAD files, sample kit or commission. "Дизайнеры" on the site means ESTIVO's own staff.
  - Private buyers get mixed signals: "ДЛЯ ДОМА, ДАЧИ" plus "по доступным ценам" next to "Rolls-Royce" and "знак статуса". The median set price is ~230 000, which is not a typical dacha budget (Well-supported hypothesis; see 02-russian-market).
- **Customer impact:** A HoReCa buyer can't judge capacity or reliability, so they will ask for references anyway or go to 4SIS/АртРотанг, which have portfolio and partner pages (07-competitors). Designers have no reason to specify ESTIVO.
- **Commercial impact:** B2B and designer orders are the largest and least seasonal tickets, and they are the obvious off-season pipeline (Oct–Feb). They are left uncaptured.
- **Confidence:** Confirmed (content gaps). The commercial weight is a Well-supported hypothesis.
- **Recommendation:**
  - Choose a primary segment: affluent private homes/cottages with terraces, with HoReCa as the second.
  - Build a B2B page with 3–5 real cases (photo, venue, quantity, lead time), per-seat price guidance, volume tiers, contract fabrics, the documents provided (certificates, VAT invoice; "Безналичный расчёт с НДС" already exists) and an early-booking offer for the next season.
  - Add a "Дизайнерам и архитекторам" section: trade discount, fabric/colour cards, dimensions/3D files, sample loan.
- **Validation:** Tag leads by segment in the CRM and track the share and average check of B2B and designer leads quarter on quarter.
- **Effort:** M.

### S7. Catalogue hygiene contradicts a premium maker
- **Problem:** Template leftovers and test items are live and indexed in the sitemap.
- **Location:** sitemap-store.xml / product pages.
- **Evidence (Confirmed):**
  - Tilda demo products: "Sac Marin Yellow" 108р. (×2), "Underwater wearable watches" 90р. (×2) and "Dining Chair by esteban+moreno" 79р./200р. (×2), with "Add here some interesting details about the product…".
  - Duplicates prefixed "Copy:" («Copy: Кресло Бари L (роуп)», «Copy: Комплект мебели из ротанг "№25"»).
  - "Error get alias" renders on all 234 product pages.
  - The /onas "НАШИ БЕСТСЕЛЛЕРЫ" block is five nameless, priceless "комплект из ротанга" pages (one with the typo "Цвет ронагта").
  - Four Christmas-tree skirts ("Юбка для Ёлки", 6 200–12 000р.) sit among the outdoor furniture in /price and /aksessuary with no context.
  - A set PDP is tagged "Тип: Места для хранения".
- **Customer and commercial impact:** These are visible signs of neglect on a site asking for 200–500 k. The bestsellers block on "О нас" shows no bestseller at all. The tree skirts could be a genuine off-season line but are hidden.
- **Confidence:** Confirmed.
- **Recommendation:**
  - Delete or unpublish the demo/Copy/stub products and fix the /onas bestsellers.
  - Either drop the tree skirts or give them a seasonal "Новогодний декор из ротанга" collection with a story (an off-season revenue idea; validate demand).
  - The UX/SEO agents cover "Error get alias".
- **Validation:** Re-crawl sitemap-store and grep.
- **Effort:** S.

## 6. Top 5 priorities (strategy view)
1. **Fix the position:** replace the "СКИДКИ ДО 70%" hero with a maker promise plus proof, reframe the sale as explained showroom/stock clearance, and stop discounts deeper than ~30–40 % on current models (S1). S–M.
2. **One value proposition everywhere:** a concrete "Почему ESTIVO" block (own Tolyatti workshop, custom size/colour, lead time, one warranty, 0 % for 12 months, photo report/sample) on the home page, hubs and PDPs, and link or merge /promo (S2). S–M.
3. **Make the claims honest and provable:** synthetic rattan stated plainly, one climate range, the frame alloy per product, and a "Производство" page with photo/video and a dated portfolio (S3). M.
4. **Reconcile prices:** one price list, "от" pricing, a visible set benefit, real old prices only (S5). M.
5. **Merge the two catalogues into one range by use, with material as a filter,** and give rope items full specs (S4). Then build the B2B/designer proof pages for the off-season pipeline (S6). M–L.

Quick win alongside: remove the demo/Copy/stub products and the nameless bestsellers (S7). S.

## 7. Open questions and data needed
- **Sales mix:** what share of revenue and leads is rope vs rattan vs tables, B2C vs B2B vs designers, Tolyatti/Samara vs the rest of Russia? This decides the primary segment and the catalogue structure.
- **Margins:** can ESTIVO afford −70–87 % markdowns? Are the sale items showroom samples, old stock or regular production? This decides how to present the sale.
- **Quoted vs listed price** on recent leads, and the top reasons leads are lost. This tests S5 and the Avito "в два раза" complaint.
- **The truth behind the claims:** frame material per model (aluminium or steel), weaving hours, test data, certificates actually held, the company's founding year and which entity sells (ИП Мелихова vs ООО «Эстиво»).
- **Is /promo the paid-traffic destination,** and are its offers (free sample, gift coffee table, 5-year warranty, worldwide delivery) real and current?
- **B2B track record:** the names and photos of venues furnished, typical order size and lead time for 20+ seats, and what "Открыть презентацию" opens.
- **Demand data:** Yandex Wordstat/Metrika for "мебель из роупа", "искусственный ротанг", "натуральный ротанг" (to size the cost of the mislabelling) and brand queries.
