# 07 — Competitor research (Agent 7)

Date of research: 2026-10-20. All competitor data was seen on the live competitor sites on this date. Prices change often; treat them as snapshots.
Confidence labels: **Confirmed** (seen on the page, URL given), **Well-supported hypothesis**, **Preliminary assumption**.

## 1. What I inspected

### ESTIVO baseline (from the Playwright corpus, not re-visited)
- `corpus/komplekty.txt` (https://estivo63.ru/komplekty), `kreslo.txt`, `kresloroup.txt`, `dostavka.txt`, `vozvrat.txt`, `home.txt`, `divan_tproduct_490442938932-divan-palermo-iz-rotanga.txt`, `crawl_results.jsonl` (form fields on that PDP).

### Competitors (WebSearch + WebFetch; Python Playwright with real Chrome for 4sis.ru, where WebFetch returned 502)
| # | Competitor | Pages inspected |
|---|---|---|
| A | **4SIS / Форсис** (large national maker, Moscow) | https://4sis.ru/ ; /dostavka-i-oplata/ ; /dostavka-i-oplata/warranty/ ; /dostavka-i-oplata/credit/ ; PDP https://4sis.ru/store/mebel_iz_roupa_veryevki/launzh_zony_5/s_3_kh_mestnym_divanom/lugano_launzh_zona_5_mestnaya_pletenaya_iz_roupa_alyuminievyy_svetlo_seryy_roup_seryy_melanzh/ |
| B | **Marite.ru** (large national online retailer, Tolyatti city page) | https://www.marite.ru/tolyatti/catalog/mebel-iz-iskusstvennogo-rotanga ; /tolyatti/info/dostavka-i-oplata |
| C | **Deamo-Rotang** (national online retailer, Tolyatti pickup point) | https://deamo-rotang.ru/tolyatti/category/mebel-iz-iskusstvennogo-rotanga |
| D | **Эко-Композит** (regional, Samara + Tolyatti) | https://eko-komposit.ru/catalog/mebel-dlya-sada-i-kafe/mebel-iz-roupa ; https://eko-komposit.ru/dostavka |
| E | **АртРотанг** (Russian maker, Aleksandrov/Moscow, hand weaving) | https://artrotang.ru/ ; /pokupatelyu/dostavka/ ; /pokupatelyu/zakaz-i-oplata/ ; PDP https://artrotang.ru/catalog/moduli-i-divany/divan-uglovoy-s-shirokimi-podlokotnikami-malta/ |
| F | **МарКо** (rope workshop, Sochi, made-to-order) | https://markorotang.com/catalog/mebel-iz-roupa-verevka/ ; /delivery/ ; /warranty/ ; PDP https://markorotang.com/product/kreslo-iz-roupa-i-alyuminiya-dlya-terrasy-ester/ |
| G | **JOYGARDEN** (premium importer/brand, Moscow) | https://joygarden.ru/mebel-iz-roupa-verevochnoe-pletenie/ |
| (ref) | ПаркМебели (reseller hypermarket, Moscow) — price anchor only | https://parkmebel.com/product-category/mebel-iz-roupa/ |

### Not accessed / limits
- Reviews pages, about pages and full warranty pages of B, C, D, G were not opened; their warranty/returns are taken only from the pages listed (gaps marked "not seen").
- 4SIS warranty *length* is not stated on its warranty page (only rules) — not seen.
- No Samara/Tolyatti **manufacturer** of rope/rattan furniture was found (searches: "мебель из искусственного ротанга Самара Тольятти производство", "мебель из роупа Самара производство ручная работа"). The regional players found are resellers/retailers (D, and the Tolyatti pickup points of B/C). **Well-supported hypothesis:** ESTIVO is the only local *maker* in this niche in Samara oblast.
- WebFetch summaries are produced by a model; key numbers were cross-checked where a second fetch/Playwright was available (4SIS, Marko, ArtRotang PDPs). Marite's listing showed three prices per card without labels; I cite only the first (lowest) one as "current" with that caveat.

## 2. ESTIVO price points and terms (Confirmed, corpus)
- Rattan sets, /komplekty: «№19» 59 500р. … «№28» 230 500р.; range seen 59 500 – 313 300р.; two cards "Цена по запросу".
- Rope chairs, /kresloroup: «Стул Верона (роуп)» 17 900р., «Кресло Бари (роуп)» 29 900р., «Кресло Бари Люкс (роуп)» 34 900р., up to 45 600р.
- Rattan chairs, /kreslo: 9 900 – 48 000р.
- Delivery (/dostavka): "транспортной компаний ГТА прямо до двери в любой населенный пункт", "Груз полностью застрахован"; pickup in Tolyatti; payment "Беспроцентная рассрочка до 12 месяцев", "Наличный расчёт/ СБП", "Безналичный расчёт с НДС", "Оплата по QR-Коду". No delivery cost or timing table on that page.
- Warranty: home says "Гарантия 3 года и доставка по всей России от 3 дней"; /vozvrat says "24 МЕСЯЦА" and "Возврат возможен в момент принятия заказа или в течение 14 дней после" (not for individual-size items). **Confirmed inconsistency: 3 years vs 24 months.**
- PDP example (Диван Палермо): one text block, "ДxШxВ: 1400x600x860 мм", colour selector "Цвет ротанга", spec says "Каркас: Металл, порошковый окрас" while the description says "Каркас мебели сделан из прочного алюминия"; a stray "Error get alias" text renders on the page. Checkout form = name, phone, delivery radio, consent, comment, button "Оформить заказ" (Tilda cart → manager follow-up). No lead time, no stock status, no per-product warranty, no reviews on PDP.
- Reviews: home links "Смотреть отзывы на Авито" plus a few quoted reviews.

## 3. Competitor profiles

### A. 4SIS / Форсис — large national maker (Moscow), rope + rattan + HPL, B2C and HoReCa
- **Positioning:** "Форсис - производитель уличной мебели"; title "производитель садовой мебели для дачи, кафе и ресторанов"; showroom "Савеловский Сити"; "2013-2026". Sections: Акции, Портфолио, Партнёрам, Производство, Где купить (dealer network). Confirmed (https://4sis.ru/).
- **Prices seen (Confirmed, https://4sis.ru/ "Новинки"):** «"Лугано" лаунж-зона 5-местная плетеная из роупа» 473 500 руб. (old 538 600, "Экономия 65 100 руб."); «"Романо" стул плетеный из роупа» 28 900 руб. (old 35 496); «"Милан" диван 3-местный плетеный из роупа» 111 900 руб.; «"Бари" лаунж-зона из алюминия» 212 800 руб. Note: 4SIS uses the model names "Бари" and "Милан", the same as ESTIVO's rope chairs.
- **Price presentation:** strike-through old price + "Экономия N руб."; stock badges "Мало / Достаточно / Много / Под заказ от 10 дней". Confirmed.
- **PDP (Лугано):** many photos, packaging dimensions "Габариты упаковки (ДШВ) — 2050×830×1020; …", "Купить в рассрочку", "Все товары коллекции", colour disclaimer. Confirmed.
- **Delivery & payment (https://4sis.ru/dostavka-i-oplata/):** own transport; Moscow 5 500 руб.; "+ 78 руб./км" beyond; to "Деловые линии" terminal in Moscow 4 000 руб. for regions; loaders 3 500 руб., assembly 2 000 руб.; off-season storage and repair offered. Confirmed.
- **Instalments (/dostavka-i-oplata/credit/):** Sber instalment "Срок рассрочки - 24 месяца", "Без первоначального взноса", 50 000 – 5 000 000 р; also a "5% скидка при покупке банковской картой". Confirmed.
- **Warranty/returns (/dostavka-i-oplata/warranty/):** generic legal text (7-day return of proper-quality goods); warranty length not stated there. Confirmed.
- **Flow:** full e-commerce cart + online checkout + public offer ("Договор оферты"); "Заказать Звонок", "Задать вопрос". Confirmed.

### B. Marite.ru — large national online retailer (imports), city sub-site for Tolyatti
- **Positioning:** mass-premium imported rattan; page title promises "распродажа круглый год"; 356 items in the rattan category. Confirmed (https://www.marite.ru/tolyatti/catalog/mebel-iz-iskusstvennogo-rotanga).
- **Prices seen (first price on card; label not shown):** «Комплект … Киото» 20 393 р. (−52%), «Кофейный комплект Пикник Дуэт» 63 158 р. (−47%), «Обеденный комплект Шампань-8» 116 181 р. (−37%). Confirmed with caveat above.
- **Promos:** "Акция", "Успей купить!", countdown timers, "Накопительные скидки". Confirmed.
- **Delivery/payment (/tolyatti/info/dostavka-i-oplata):** ПЭК to city terminal from 8 000 р.; dispatch "в течение 10 рабочих дней"; QR or bank transfer; "Наш салон не работает с банковскими картами" while a banner says "Наличными или банковской картой" (internal contradiction). Warranty **3 months**. Confirmed.
- **Trust:** reviews per product (e.g. "60 отзывов", "87 отзывов"), Yandex rating badge. Confirmed.
- **Flow:** cart + "Купить в 1 клик" + callback + WhatsApp/MAX. Local Tolyatti address ул. Базовая, д. 1 с. 20. Confirmed.

### C. Deamo-Rotang — national online retailer of Asian imports, Tolyatti pickup
- **Positioning:** "Мебель из Индонезии, Китая, Вьетнама", "более 14 лет". Same Tolyatti address as Marite (ул. Базовая, д. 1 с. 20). **Well-supported hypothesis:** B and C share a warehouse or owner.
- **Prices seen (Confirmed, https://deamo-rotang.ru/tolyatti/category/mebel-iz-iskusstvennogo-rotanga):** «Киото» 18 393 ₽ (old 20 393), «Комплект … Пикник» 126 928 ₽, «Обеденная группа … Пикник-8» 224 906 ₽, «Кресло Римини» 17 270 ₽ (old 26 270).
- **Value prop:** "Доставка 1 день", delivery + lifting + assembly; "Предоставляем годовую гарантию"; per-product reviews (42, 38 …); expected-arrival date on some cards ("Приходит 01 Декабря 2026"). Confirmed.
- **Flow:** cart + "Заказать в 1 клик" + callback + Telegram/MAX bots. Confirmed.

### D. Эко-Композит — regional (Samara + Tolyatti) multi-category garden retailer
- **Positioning:** "Купить мебель из роупа (веревки) в Самаре недорого"; offices in Tolyatti (ТЦ «Арбуз») and Samara (ул. Солнечная, 60); also sells decking, fences, pergolas. Maker vs reseller not stated. Confirmed (https://eko-komposit.ru/catalog/mebel-dlya-sada-i-kafe/mebel-iz-roupa).
- **Prices seen:** «Кресло Мия с подушкой» 11 440 р.; «Кресло РИЦА с подушками» 18 040 р.; «Комплект мебели НЕАПОЛЬ» 80 100 р.; «Комплект мебели из роупа КАРЕЛИЯ» 153 490 р.; «КАРЕЛИЯ (6 стульев)» 208 380 р. Confirmed.
- **Delivery/payment (https://eko-komposit.ru/dostavka):** in-stock ships "1-2 рабочих дня"; Samara oblast via partner carriers, driver only to unloading point; Russia via Деловые линии/ПЭК/Энергия/Байкал-сервис at carrier tariff; cash, card terminal, invoice. Warranty, reviews, promos: not seen. Confirmed.
- **Flow:** cart "В корзину" + free consultation form + downloadable "Прайс". Confirmed.

### E. АртРотанг — Russian maker (Aleksandrov, Vladimir obl.; Moscow phones), hand-woven rattan on aluminium
- **Positioning:** "Российское производство", "Ручной труд опытных плетельщиков", "прямые продажи без посредников", "100 лучших товаров России" laureate, B2B pages for hotels/cafés/designers. Confirmed (https://artrotang.ru/).
- **Prices seen:** «Угловой диван 'Мальта'» 113 000 ₽; «Угловой диван 'Бруклин'» 185 000 ₽; «Обеденная группа на 8 персон 'Сицилия'» 315 000 ₽; «Кресло 'Palace'» 55 000 ₽; «Стул Syna» 14 000 ₽. Promo "В честь Юбилея - скидка 10-30% на всю мебель в наличии!", "гарантия лучшей цены". Confirmed.
- **PDP (Мальта) — best spec table seen:** "Размер дивана 170х270 см. Возможно изготовление по Вашим размерам", seat height 45, rattan and cushion colours "на выбор из каталога", "Гарантия, мес: 24", "Гарантия на текстильные элементы, мес: 12", module dimensions, frame "алюминий", "порошковая покраска", cushion filler. Only one large image on that PDP. Confirmed.
- **Delivery (/pokupatelyu/dostavka/):** own vehicle; ≤10 km free; Moscow/MO/Vladimir obl. 3 000–10 000 руб.; Russia via ЖДЭ, ПЭК, СДЭК, Деловые Линии. Confirmed.
- **Order flow (/pokupatelyu/zakaz-i-oplata/):** request → offer → agree sizes/colours → contract → "предоплату 50%" → production → delivery + balance. Cards МИР/VISA/Mastercard accepted. Plus "Загрузить фото" (send a photo for a price/lead-time estimate) and "Заказать мебель по своим размерам". Confirmed.

### F. МарКо — rope/rattan workshop, Sochi, made-to-order, ships across Russia
- **Positioning:** "Российский производитель плетеной мебели"; "Мастерская «МарКо» изготавливает мебель из роупа в Сочи"; Production page, restoration/repair service, wholesale tags "ОПТ ОТ 30 ШТ". Confirmed (https://markorotang.com/catalog/mebel-iz-roupa-verevka/).
- **Prices seen:** «Стул плетеный Корд» 24 000 ₽; «Кресло из роупа и алюминия «Эстер»» 41 000 ₽; «Диван Эстер 2-местный» 51 000 ₽; «Кресло плетеное Камелия из роупа» 56 000 ₽; catalog filter 22 000 – 308 000 ₽. Confirmed.
- **Lead time shown per card:** "В наличии", "Заканчивается", "35 дней", "60 дней". PDP: "Срок изготовления: 25 дней", "Нашли дешевле?", "Купить в 1 клик", "Размеры: ш/г/в 78*78*75 см", materials list. Confirmed.
- **Delivery (/delivery/):** Деловые Линии, СДЭК, Энергия, ПЭК; cost on request; "При заказе от 200 000 рублей доставка бесплатная"; arrives assembled; prepayment 70 %, balance on readiness. Confirmed.
- **Warranty (/warranty/):** "24 месяца"; 7-day return of proper-quality goods. Confirmed.

### G. JOYGARDEN — premium brand/importer, Moscow showroom + Zvenigorod outlet
- **Positioning:** "СТИЛЬНАЯ МЕБЕЛЬ ДЛЯ ВАШЕГО ЗАГОРОДНОГО ДОМА, РЕСТОРАНА, ОТЕЛЯ И СПА"; teak/acacia/aluminium frames with rope; B2B for designers/marketplaces. Confirmed (https://joygarden.ru/mebel-iz-roupa-verevochnoe-pletenie/).
- **Prices seen:** «Плетеное кресло LUCCA» 24 493 ₽ (old 34 490); «Диванная группа КАЛИСТО M» 172 160 ₽; «Диванная группа LUCCA» 164 960 ₽; «Обеденная группа из тика ТАЛАРА L» 445 316 ₽. Badges "в наличии / предзаказ / скоро поступит / Продано". Confirmed.
- **Flow:** cart + "Заказать в 1 клик" + quick view + compare + wishlist. Separate pages for Оплата и Доставка, Гарантия, Обмен и возврат, Сертификаты (contents not opened).

### Reference price anchor — ПаркМебели (Moscow "Гипермаркет садовой мебели", resells Royal Family, 4SIS, ROTANG LUX, Brafab)
- «Palermo кресло с подушками» 18 000 ₽; «Verona кресло с подушками» 28 860 ₽; «Канны диван двухместный» 74 880 ₽; «Кофейный комплект Royal Family CHLOE» 176 735 ₽ (old 271 900). Category "Бесплатная доставка по России". Confirmed (https://parkmebel.com/product-category/mebel-iz-roupa/). Not a primary competitor (multi-brand reseller), but shows that 4SIS is also sold through resellers.

## 4. Comparison table

| | ESTIVO | 4SIS | Marite | Deamo | Эко-Композит | АртРотанг | МарКо | JOYGARDEN |
|---|---|---|---|---|---|---|---|---|
| Type | Maker, Tolyatti | Maker, Moscow, national + dealers | Importer/e-tailer | Importer/e-tailer | Regional retailer Samara/Tlt | Maker, Vladimir obl. | Workshop, Sochi | Premium importer/brand |
| Rope armchair, seen | 17 900–45 600р. | stool 28 900 | — | — | 11 440–18 150 | (rattan) 55 000 | 41 000–56 000 | 22 393–24 493 (sale) |
| Set / lounge, seen | 59 500–313 300р. | 111 900 (sofa) – 473 500 | 20 393–116 181 | 18 393–224 906 | 42 680–208 380 | 113 000–315 000 | up to 308 000 (filter) | 164 960–490 840 |
| Old price / discount shown | separate "Акции" pages; "СКИДКИ ДО 70%" banner | yes, "Экономия N руб." | yes, up to −53 %, timers | yes | no | promo banner 10–30 % | sale category | yes |
| Stock / lead time on card | not seen | Мало/Много/Под заказ от 10 дней | arrival dates | arrival dates | not seen | Хит/Новинка, "в наличии" section | В наличии / 35 / 60 дней | в наличии / предзаказ |
| PDP specs | ДxШxВ + 3 material lines | packaging dims, collection | — (not opened) | — | — | full spec table incl. seat height, warranty, custom size | dims, materials, lead time | — |
| Delivery cost published | no | yes (Moscow tariffs + per km) | conditional free | "Доставка 1 день" | carrier tariff | yes (zones) | free from 200 000 | — |
| Instalments | 0 %, up to 12 mo | Sber, 24 mo, 0 % | not seen | not seen | not seen | not seen | not seen | not seen |
| Warranty | 3 years (home) vs 24 mo (/vozvrat) | length not stated | 3 months | 1 year | not seen | 24 mo + 12 mo textiles | 24 mo | page exists |
| Reviews on site | Avito link + quotes | reviews page | per product, counts | per product, counts | not seen | reviews + certificates + "100 лучших товаров" | reviews page | reviews page |
| Purchase flow | Tilda cart → request form, manager | full e-com cart + Sber credit | cart + 1-click | cart + 1-click | cart + consult form + price list | cart + request/photo upload + 50 % prepay | cart + 1-click + 70 % prepay | cart + 1-click |

All cells: Confirmed from the URLs in section 3, except "—" (not seen).

## 5. Findings

### F1. ESTIVO sits in the same price band as the national makers, not the importers
- **Problem:** ESTIVO's rope chairs (17 900–45 600р.) and rattan sets (59 500–313 300р.) overlap 4SIS, АртРотанг and МарКо, and are well above Marite/Deamo/Эко-Композит imports (sets from ~18–45 k).
- **Evidence:** section 4 table. **Customer impact:** a shopper comparing on Yandex sees cheaper "looks the same" imports first; the reason to pay more (handmade, local, warranty, custom) must be explicit on the card/PDP. **Commercial impact:** price objections and lost leads to cheaper importers. **Confidence:** Confirmed (prices), Well-supported hypothesis (impact). **Recommendation:** on listing and PDP, state the maker proof next to the price: "собственное производство в Тольятти", lead time, warranty, custom size/colour. **Validation:** A/B or before/after on PDP→request rate; ask managers for the share of "дорого" objections. **Effort:** S.

### F2. Competitors show lead time / stock on every card; ESTIVO shows none
- **Evidence:** МарКо "Срок изготовления: 25 дней", "35 дней"; 4SIS "Под заказ от 10 дней", "Мало"; Deamo "Приходит 01 Декабря 2026". ESTIVO PDP: none (Confirmed). Home claims "доставка по всей России от 3 дней", which reads as shipping time, not production. **Customer impact:** uncertainty about when furniture arrives — a key question for a seasonal product. **Commercial impact:** more calls, more drop-off before the request. **Confidence:** Confirmed. **Recommendation:** add "В наличии / Изготовление N дней" to each product. **Validation:** count questions about timing in manager chats before/after. **Effort:** S (Tilda product field / label).

### F3. Warranty is stated inconsistently on ESTIVO, while makers use warranty as a selling point
- **Evidence:** ESTIVO home "Гарантия 3 года" vs /vozvrat "24 МЕСЯЦА" (Confirmed). АртРотанг puts "Гарантия, мес: 24" and "на текстильные элементы, мес: 12" in every spec table; МарКо 24 mo; Deamo 1 year; Marite 3 months. **Customer impact:** contradiction undermines trust; yet ESTIVO's warranty is among the best in the set. **Commercial impact:** missed differentiator vs importers. **Confidence:** Confirmed. **Recommendation:** pick one figure, put it in every PDP spec block and on cards ("Гарантия 3 года" if true), split frame/weave vs textiles like АртРотанг. **Validation:** legal/owner confirmation; page check. **Effort:** S.

### F4. Instalments: ESTIVO's 0 %/12 mo is a real advantage but hidden on /dostavka
- **Evidence:** ESTIVO "Беспроцентная рассрочка до 12 месяцев" only on /dostavka (Confirmed in corpus). 4SIS has a dedicated credit page and a "Купить в рассрочку" button on the PDP, 24 months via Sber. No other competitor in the set advertises instalments on the pages seen. **Recommendation:** show "от N ₽/мес" or "0 % рассрочка 12 мес" next to price on PDP and in the cart. Confirm the provider and conditions before showing a monthly amount. **Confidence:** Confirmed (presence), Well-supported hypothesis (conversion lift). **Effort:** S–M.

### F5. PDP depth: ESTIVO is thinner than the best maker competitor
- **Evidence:** АртРотанг PDP: dimensions per module, seat height, frame treatment, cushion filler, colour catalogues for rattan and fabric, warranty, "Возможно изготовление по Вашим размерам". ESTIVO Палермо PDP: one ДxШxВ, three material lines, frame contradiction "Металл" vs "алюминия", stray "Error get alias" text (Confirmed; present in all 48 product pages in the corpus at the time of checking). **Recommendation:** fixed spec template per product (dims, seat height, weight, frame alloy + coating, weave, cushion fabric + filler, max load "120 кг на одно посадочное место" already on /vozvrat, warranty, lead time, custom-size availability); remove "Error get alias". **Effort:** M (content for ~230 products).

### F6. Delivery cost transparency
- **Evidence:** 4SIS and АртРотанг publish tariffs/zones; МарКо publishes a free-delivery threshold (200 000 ₽); ESTIVO says only "Свяжитесь с нами и мы подберем для вас самые выгодные условия" (Confirmed). **Customer impact:** buyers outside Samara oblast cannot estimate total cost. **Recommendation:** publish 3–4 example costs (e.g. armchair / set to Samara, Moscow, Kazan, Krasnodar by ГТА) or a free-delivery threshold if margins allow. **Confidence:** Confirmed (gap), Preliminary assumption (effect size). **Effort:** S.

### F7. Social proof format
- **Evidence:** Marite/Deamo show review counts on each product card; АртРотанг shows reviews + certificates + an award; ESTIVO links out to Avito and repeats the same quote (Confirmed: the same review text appears twice in home.txt). **Recommendation:** embed real Avito/Yandex rating with count and date, attach photo reviews to the products they relate to, add "Наши работы" with installed projects (АртРотанг/4SIS have portfolio sections). **Effort:** M.

### F8. Custom-made path is a maker's advantage that ESTIVO can make visible
- **Evidence:** АртРотанг "Загрузить фото" (send a photo for a price and lead-time estimate) and "Заказать мебель по своим размерам"; МарКо made-to-order with stated days. ESTIVO has a designer consultation on home ("Получить персональную консультацию дизайнера"), but no per-product "сделать в моём размере/цвете" CTA seen in the PDP corpus. **Recommendation:** secondary PDP CTA "Изготовить в моём размере / цвете" → short form with photo upload. **Confidence:** Confirmed (competitor), Well-supported hypothesis (ESTIVO gap; verify in UX findings). **Effort:** S–M.

### F9. Model-name collision with 4SIS
- **Evidence:** 4SIS sells «"Бари" лаунж-зона» and «"Милан" диван»; ESTIVO sells «Кресло Бари (роуп)», «Кресло Милан (роуп)». **Impact:** brand-search queries like "кресло Бари роуп" may surface 4SIS, a larger site. **Confidence:** Confirmed (names), Preliminary assumption (SEO effect). **Recommendation:** use "ESTIVO Бари" in titles/H1; check Yandex Wordstat/Webmaster for these queries. **Effort:** S.

## 6. Lessons that fit ESTIVO
1. Lead time / stock status on every card (МарКо, 4SIS).
2. Full spec table with warranty and custom-size line on every PDP (АртРотанг).
3. Instalment visible next to the price (4SIS).
4. Clear, published delivery cost examples or a free-delivery threshold (АртРотанг, МарКо).
5. Transparent order steps for made-to-order work: request → spec → contract → prepayment → production → delivery (АртРотанг /zakaz-i-oplata/). ESTIVO's lead model fits this exactly; a "Как мы работаем" block would reduce calls.
6. Maker proof: production page/video, portfolio of installed terraces, certificates (4SIS "Производство", АртРотанг award + certificates). ESTIVO already claims "Производство полного цикла" and certificates — show them.
7. Old price + "Экономия N ₽" format on sale items (4SIS) is clearer than a generic "СКИДКИ ДО 70%" banner — if the old price is real and documented.
8. Off-season services (4SIS: storage, repair; МарКо: restoration) — a natural upsell for a local maker in Tolyatti.

## 7. Approaches that are NOT suitable for ESTIVO
1. **Permanent deep discounts, countdown timers, "Успей купить!" (Marite/Deamo).** Undermines a handmade premium positioning ("Rolls-Royce среди мебели"), and fake urgency/permanent "old prices" carry legal risk under consumer-protection and advertising law. Use real seasonal sales only.
2. **Full online checkout with prepayment and a public offer (4SIS).** ESTIVO deliberately runs lead generation, the footer says the site "не является публичной офертой", and made-to-order items need a spec agreement first. A "Купить в 1 клик" button that just creates a lead is fine; card payment at checkout is not, for now.
3. **Racing importers on price (Marite/Deamo/Эко-Композит: 11–45 k sets/chairs).** ESTIVO's cost base (local handmade) cannot win there; compete on warranty, lead time, custom size and local service instead.
4. **"Доставка 1 день" style promises (Deamo).** Not credible for made-to-order furniture; ESTIVO's own "от 3 дней" already risks over-promising if it means only in-stock items.
5. **Huge multi-brand catalogues / compare / quick view (JOYGARDEN, ПаркМебели).** ESTIVO has ~230 SKUs incl. colour swatches stored as products; adding compare/quick-view adds complexity with little gain on Tilda. Fix catalogue hygiene first.
6. **Wholesale-only tags on retail cards (МарКо "ОПТ ОТ 30 ШТ").** Confusing for private buyers; keep B2B on /b2b.
7. **"Гарантия лучшей цены" / "Нашли дешевле?" (АртРотанг, МарКо).** For unique handmade models there is no like-for-like price to match; it invites haggling and conflicts with premium positioning.

## 8. Top 5 priorities (competitor view)
1. Add lead time / in-stock status to every product (F2). S.
2. Unify warranty (3 years vs 24 months) and show it on every PDP (F3). S.
3. Show the 0 % instalment next to the price (F4). S–M.
4. Standard PDP spec template + fix "Error get alias" / frame contradiction (F5). M.
5. Publish delivery cost examples or a free-delivery threshold (F6). S.

## 9. Open questions / data needed
- Real ESTIVO lead times per product family and what is in stock — needed for F2.
- Which warranty is legally offered (3 years or 24 months), and is textile covered separately?
- Instalment provider and terms (bank, min amount) — needed to show "от N ₽/мес".
- GTA delivery tariffs for typical parcels to 4–5 cities.
- Manager CRM data: share of leads lost on price, timing, delivery cost; source of leads (Avito vs site vs Yandex).
- Yandex Wordstat / Webmaster for "кресло из роупа", "мебель из роупа Самара/Тольятти", "кресло Бари роуп" — to size the 4SIS name collision and the local-maker opportunity.
- Whether Marite and Deamo are one business (same Tolyatti address) — affects how many real local rivals exist.
