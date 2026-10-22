# 02 — Russian market & consumer expectations (Agent 2)

Scope: the needs, objections, buying habits and trust expectations of Russian buyers of premium garden and terrace furniture, checked against what estivo63.ru (the live Tilda site) actually says. Audit date: 2026-10-20, which is off-season for outdoor furniture.
Confidence labels: **Confirmed** (I saw it myself), **Well-supported hypothesis** (backed by an external source or several signals), **Preliminary assumption** (needs data).

---

## 1. What I inspected

**Site corpus (Playwright crawl, read from `corpus/`):** `/` (home), `/promo`, `/dostavka`, `/vozvrat`, `/kontakty`, `/onas`, and the product pages crawled so far: `/kreslo/tproduct/278562776182-kreslo-volterra-lyuks-iz-rotanga`, `/divan/tproduct/490442938932-divan-palermo-iz-rotanga`, plus prices grepped from all 15 `*tproduct*` files present at the time. I also grepped the whole corpus (54 pages at the time) for warranty, lead times, phone numbers, instalments, lifting/assembly and messengers. From `crawl_results.jsonl` I took the outbound links (socials, Avito), the form fields and the trackers.

**External, read-only:**
- Yandex Maps search "estivo" in Tolyatti, the org cards 1216563733 and 58438486173, and the reviews tab of 1216563733 (WebFetch).
- VK `vk.com/estivo_tlt` (one Playwright visit, logged out).
- Avito profiles linked from the site: `7cba9cbb…` (Playwright) and `91b69cd0…` (Playwright, blocked).
- WebSearch on Russian payment habits, BNPL, seasonality, review behaviour, the WhatsApp block, MAX, the Instagram advertising ban, VAT 2026 and the distance-selling return rules.

**Could not access:**
- **2GIS:** WebFetch returned 404 or connection refused, and Playwright got a bot-check form. I did not try to get past the check.
- **Avito profile `91b69cd0…`:** "Доступ ограничен: проблема с IP".
- **Ozon:** WebFetch failed (too many redirects).
- **Wildberries and Otzovik:** not checked directly. Web search found no ESTIVO listings, which does not prove there are none.
- **Rusprofile and RBC Companies** (status of ООО «Эстиво»): 404 and 401.

I submitted no forms and sent no messages.

---

## 2. Market context (external evidence)

| Topic | What the sources say | Confidence |
|---|---|---|
| Seasonality | Garden furniture is a seasonal product. OBI lists it among the top "Сад" categories, with the core buyer aged 35–44 ([retail.ru/OBI](https://www.retail.ru/news/obi-spros-na-tovary-dlya-sada-i-posadok-vyros-na-50-15-sentyabrya-2025-269094/)). Wildberries reports that dacha demand starts earlier in warm springs ([retail.ru/WB 2022](https://www.retail.ru/news/wildberries-iz-za-teploy-vesny-rossiyane-nachali-ranshe-podgotovku-k-dachnomu-se-11-marta-2022-214610/)). Online sales of garden goods grew about 2.85× in 2025, and marketplaces took about 20% of that ([sostav.ru](https://www.sostav.ru/blogs/286022/73130)). | Well-supported hypothesis (exact monthly curve not found; check with Yandex Wordstat) |
| Payment | Bank of Russia survey, 2025: 79% of people use a debit card, 38% pay by SBP QR, 24% by credit card, 6% by free instalment; cash rose to 27% ([expert.ru](https://expert.ru/news/tsb-nazval-debetovuyu-kartu-samym-populyarnym-sposobom-beznalichnoy-oplaty-v-rossii)). | Confirmed (external) |
| Instalments / BNPL | The BNPL market grew to about 940 bn ₽ in 2025 by Dolyami's count, or more than 500 bn ₽ in issued instalments by the Central Bank's count, driven by the high key rate ([robokassa](https://robokassa.com/blog/news/rynok-pokupok-chastyami-bnpl-v-rossii-vyros-do-940-mlrd/), [investfuture](https://investfuture.ru/articles/bnpl-v-rossii-obyemy-rassrochki-vyrosli-na-80-dostignuv-500-mlrd-rubley-1180778969)). One source says the maximum BNPL term has been 6 months since 1 Dec 2025 ([fa.ru PDF](https://www.fa.ru/upload/constructor/335/5vovgaf0iwzk5vywc0ygvozhlre5wxv5/Finansovye-uslugi-marketpleysov-02.06.25.pdf)). | The growth is well-supported. The 6-month cap is a preliminary assumption (one source). |
| Reviews | 95% read reviews before buying online, and 68% do so before every purchase ([Avito study via retail.ru](https://www.retail.ru/news/avito-95-rossiyan-chitayut-otzyvy-pered-tem-kak-sdelat-pokupku-v-internete-29-sentyabrya-2024-245627/)). 62% abandon a purchase after a single negative review, and 27% look for bad reviews on purpose ([fomag.ru / TASS](https://fomag.ru/news-streem/62-rossiyan-otkazyvayutsya-ot-pokupki-posle-odnogo-negativnogo-otzyva-issledovanie/)). | Well-supported |
| Messengers | Russia restricted WhatsApp in stages from late 2025, and the Kremlin confirmed a full block in Feb 2026. It now works only through a VPN, and users are steered to the state messenger MAX ([giga.law](https://giga.law/daily-news/2026/2/12/whatsapp-blocked-for-wnwillingness-to-comply-with-russian-law), [adaderana](https://www.adaderana.lk/news.php?nid=118430), [novayagazeta.eu](https://novayagazeta.eu/en/articles/2025/12/22/russian-regulator-warns-it-could-fully-block-whatsapp-amid-fresh-reports-of-outages-en-news)). Telegram calls have been limited since Aug 2025. In early 2026, fewer than 1% of organisations could open a MAX business account, with a wider rollout planned for spring 2026 ([ppc.world](https://ppc.world/news/max-v-blizhayshie-mesyacy-raskataet-na-vseh-vozmozhnost-sozdaniya-biznes-akkauntov/)). | Well-supported (I found no status update after Feb 2026) |
| Instagram | Advertising on Instagram (a Meta product; Meta is designated extremist in Russia) has been banned since 1 Sep 2025. Fines reach 500k ₽ for legal entities ([ppc.world](https://ppc.world/articles/v-instagram-zapretyat-lyubuyu-reklamu-dazhe-u-blogerov-eksperty-kommentiruyut-novyy-zakonoproekt/), [t-j.ru](https://t-j.ru/ads-ban/)). Whether a plain link from your own site counts as advertising is not settled by these sources. | Ban confirmed. Its effect on a site link is a preliminary assumption. |
| Returns (distance sale) | Under ZoZPP art. 26.1, a buyer can refuse goods within 7 days of receipt. The period becomes 3 months if the return terms were not given in writing at delivery ([garant.ru](https://harant.ru/blog/zashchita-prav-potrebitelej/prodazha-tovara-distanczionnym-sposobom/)). Goods with individually defined properties are excluded, but defects are still covered ([garant.ru](https://harant.ru/blog/grazhdanskoe-pravo/tovar-pod-zakaz-vsegda-li-eto-isklyuchaet-vozvrat-internet-pokupki/)). | Well-supported. Legal review is needed. |
| VAT 2026 | The VAT rate went from 20% to 22% on 1 Jan 2026. The VAT exemption threshold for the simplified tax system (USN) fell to 20 m ₽ under 425-FZ ([ppt.ru](https://ppt.ru/news/idea/byudzhetnyy-paket-na-2026-2028-gody-i-nalogovye-izmeneniya)). | Well-supported |
| Furniture on marketplaces | Bulky, high-ticket furniture converts at about 1–2% on WB and Ozon, with expensive logistics and ads ([uniseller](https://uniseller.io/blog/kak-prodvigat-mebel-na-marketpleisah), [workspace.ru case](https://workspace.ru/cases/na-ozon-eto-nevygodno-govorili-oni-my-nashli-drugoy-marshrut/)). | Preliminary assumption for ESTIVO's category |
| Bulky-goods delivery | For furniture, parking, unloading, lifting to the floor, assembly and removal of the old furniture are each a separate step the buyer cares about ([new-retail.ru](https://new-retail.ru/business/sami_ili_cherez_partnera_sposoby_organizatsii_dostavki_krupnogabaritnykh_tovarov_kgt/)). I found no Russian survey of buyer expectations. | Preliminary assumption |

---

## 3. ESTIVO's external presence (what I found)

| Platform | What I found | Confidence |
|---|---|---|
| **Yandex Maps, main card** `yandex.ru/maps/org/estivo/1216563733/` | "Рейтинг 4,4", "16 оценок", "7 отзывов". All 7 text reviews are positive and dated 2022-07 to 2025-08 (e.g. "Не первый раз сотрудничаем, всегда всё чётко и в срок"). No owner replies are visible. Rubrics: "Магазин мебели", "Мебель на заказ", "Садовая мебель". About 50 photos. The goods section is marked "Давно не обновлялось" and shows e.g. "Шезлонг Бари (роуп)" at 69 000 ₽. Phone shown: "+7 (8482) 78-94-04". I saw no "verified by owner" mark, only "Вы владелец этой организации?". | Rating and count confirmed (WebFetch summary, not a screenshot). Phone and verification status are preliminary. |
| **Yandex Maps, second card** `…/58438486173/` | Same building ("подъезд 4"), "Ещё нет отзывов", "Открыто до 18:00" while the other card says until 19:00. | Confirmed (WebFetch) |
| **2GIS** | Not verified because of the bot-check page. A firm id `2gis.ru/firm/3096753025457971` appeared in search but would not load. | Not verified |
| **Avito** | The home page shows an Avito widget: "5.0 из 5 На основе 36 оценок". The newest dated review in the widget is from 18 Sep 2024. The site's "Смотреть отзывы на Авито" link goes to profile `7cba9cbb…#open-reviews`, which today returns **"Пользователь не найден"**. The second linked profile was IP-blocked. | Dead profile: well-supported (one visit, page fully rendered). Widget content confirmed. |
| **VK** `vk.com/estivo_tlt` | "ESTIVO \| Плетеная мебель \| Роуп \| Ротанг", "1,2K подписчиков". Active, with posts on 8 Oct. A "Отзывы" discussion exists (last activity 25 Jun 2025). On 14 Oct a visitor asked "Где можно в «живую» посмотреть и купить такое кресло". The answer, "Ответили вам в личных сообщениях", came on 16 Oct, two days later. The VK description promises "Гарантия 24 месяца" and "10 лет опыта, более 1000 реализованных комплектов". | Confirmed |
| **Ozon / Wildberries / Yandex Market** | Web search found no ESTIVO listings. I could not load Ozon directly. | Not verified (absence not proven) |
| **Otzovik / IRecommend** | Web search found nothing. | Not verified |

---

## 4. Findings

### F1. Three different warranty promises across the site and VK
- **Problem:** The warranty term changes depending on where the buyer reads it.
- **Location:** `/` ("Гарантия 3 года и доставка по всей России от 3 дней", 4 occurrences), `/vozvrat` ("24 МЕСЯЦА"), `/promo` ("ГАРАНТИЯ 5 ЛЕТ на все изделия"), VK ("Гарантия 24 месяца").
- **Evidence:** Corpus grep. **Confirmed.**
- **Customer impact:** A premium buyer paying 35–245k ₽ to a remote maker they cannot inspect reads the inconsistency as carelessness, or as a sign the seller won't honour the promise. Anyone who checks for bad signals (27% do so on purpose) will find it.
- **Commercial impact:** Lost trust at the decision stage. Possible disputes: under consumer law the buyer can rely on the most favourable advertised term (legal check needed).
- **Recommendation:** Pick one term and state it everywhere. Put a one-line summary on every product card ("Гарантия N мес. на каркас и плетение") and link to `/vozvrat`.
- **Validation:** Re-grep after the fix. Ask managers how often buyers raise the warranty.
- **Effort:** S

### F2. Three phone numbers and two legal entities
- **Problem:** The site shows different phone numbers and two different legal entities.
- **Location and evidence:**
  - Phone numbers: `+7 927 200 43 03` on 93 corpus lines, `+7(917)824-67-22` on `/promo`, and `+7 (8482) 78-94-04` on the Yandex card.
  - Legal entities: the footer on every page says "ИП МЕЛИХОВА МИРОСЛАВА СЕРГЕЕВНА, ИНН 632147606449". `/kontakty` and `/promo` show "ООО “ЭСТИВО” … ИНН 6321368220 … Генеральный директор Кострикин Николай Вячеславович". `/dostavka` offers "Безналичный расчёт с НДС".
- **Confidence:** Confirmed on the site. The Yandex phone is preliminary. I did not check the ООО's status in the state register (EGRUL).
- **Customer impact:** Russian B2B buyers and many private buyers check counterparties (EGRUL, Checko). Two entities with different heads raise the question "кому я плачу?". A paid-ad visitor who calls the 917 number may reach a different person or no one.
- **Commercial impact:** Lost or misrouted calls, and friction for B2B buyers who need a VAT invoice.
- **Recommendation:**
  - Use one sales phone everywhere: site, promo, Yandex, 2GIS, Avito.
  - Show the entity that signs contracts, and state on `/b2b` and `/dostavka` which entity issues VAT invoices (22% from 2026).
  - Remove or explain the second entity.
- **Validation:** Use call tracking or ask managers where calls come from. Check both INNs on egrul.nalog.ru.
- **Effort:** S

### F3. The delivery page leaves out what Russian buyers of bulky goods need to know
- **Problem:** `/dostavka` gives no price, no lead time per region, no lifting or assembly terms, no packaging description and no prepayment terms. The only carrier named is "ГТА", which buyers don't recognise. Delivery claims also contradict each other.
- **Location:** `/dostavka`, `/`, `/promo`.
- **Evidence:**
  - `/dostavka`: "Мебель доставляется транспортной компаний ГТА прямо до двери в любой населенный пункт…", "Свяжитесь с нами и мы подберем для вас самые выгодные условия".
  - No mention of "подъём" or "сборка" anywhere in the corpus (grep).
  - Delivery reach: `/promo` says "ДОСТАВКА в любую точку мира", while `/` says "по всей России от 3 дней".
  - Production time: "Сроки изготовления мебели от 14 дней" and "Срок реализации от 4 недель" appear elsewhere.
  - Pickup address: `/dostavka` says "ул. Туполева, 12А, ТД Вояж", everywhere else says "б-р Туполева 12А. Офис 2-4".
- **Confidence:** Confirmed on the site. That buyers expect cost and lift/assembly up front is a well-supported hypothesis.
- **Customer impact:**
  - Buyers outside Samara region, the main growth audience, cannot estimate the total cost. A 5–7-piece set weighs far more than a parcel, and they need to know whether it arrives assembled and who carries it to a terrace or apartment.
  - "От 3 дней" next to "от 14 дней / от 4 недель" sets a false expectation.
  - People know the large Russian carriers (ПЭК, Деловые Линии, СДЭК, КИТ). "ГТА" means nothing to them; web search did not identify it either.
- **Commercial impact:** Leads stall at "сколько будет стоить доставка в …?", and managers have to answer it by hand every time. Buyers compare against marketplace listings that show delivery cost.
- **Recommendation:** Add a short delivery table with these items:
  - 3–5 example cities with an indicative cost and time (e.g. Самара/Москва/СПб/Краснодар/Екатеринбург)
  - which carriers they work with
  - "мебель приезжает в собранном виде / требуется сборка подушек"
  - lift to the floor and unloading: who does it and the price
  - packaging (the home SEO text already mentions "многослойную транспортную оболочку"; move it here)
  - insurance
  - separate times for "в наличии" and "под заказ" items
  - one pickup address
  
  On product cards, add "Срок: в наличии / изготовление N дней" and "Доставка по России — рассчитаем за 15 минут".
- **Validation:** Tag manager conversations by question type for 4 weeks and track the share of "доставка/сроки" questions. Compare the lead-to-sale rate for non-Samara leads before and after.
- **Effort:** S–M

### F4. Payment and instalment terms are too thin for a high-ticket remote purchase
- **Problem:** The page doesn't name the instalment provider, its terms, prepayment or card payment.
- **Location:** `/dostavka`, `/promo`, product cards.
- **Evidence:**
  - `/dostavka`: "Беспроцентная рассрочка до 12 месяцев", "Наличный расчёт/ СБП", "Безналичный расчёт с НДС", "Оплата по QR-Коду". `/promo`: "РАССРОЧКА ПЛАТЕЖА без переплат".
  - None of these name a bank or BNPL provider, a minimum amount, an approval process, the prepayment share for made-to-order items, or card payment.
  - Instalments appear only on `/dostavka` and `/b2b` (and `/promo`). Product cards (e.g. "34 900р.") show no monthly amount.
- **Confidence:** Confirmed.
- **Customer impact:**
  - Buyers paying 35–250k ₽ amid a high key rate rely on instalments, a market that has grown sharply. They want to see "от 2 908 ₽/мес" on the card.
  - Buying made-to-order furniture from an unknown remote maker, the main fear is the prepayment: how much, under what contract, and what if it never arrives.
  - If the "12 months" is a BNPL product, it may conflict with the reported 6-month cap from Dec 2025.
- **Commercial impact:** Fewer conversions on the high-ticket sets, which carry the margin.
- **Recommendation:**
  - Name the instalment partner (bank or BNPL) and verify that the 12-month term is still offered.
  - Show the monthly payment on product cards and on promo sets.
  - State the prepayment model plainly, e.g. "Договор, предоплата X%, остаток — после фото/видео-приёмки перед отправкой" (the home page already promises "Согласование мебели с клиентом по фото и видеоотчету"; use it as a trust argument).
  - List bank cards explicitly.
- **Validation:** A/B test the monthly-payment line on product cards and track lead rate. Track the share of leads that ask about instalments.
- **Effort:** S

### F5. The review trail is weak and partly broken
- **Problem:** Each review source is small, stale or broken, and the site's own testimonials carry no names.
- **Location:** Home page Avito widget, Yandex Maps, `/promo`.
- **Evidence:**
  - Avito widget: "5.0 из 5 На основе 36 оценок". The newest dated review is from Sep 2024, and the link goes to an Avito profile that says "Пользователь не найден".
  - Yandex: 4.4 from 16 ratings and 7 text reviews, with no owner replies. A second, empty duplicate card exists.
  - 2GIS: unknown.
  - The site's own 3 testimonials are anonymous quotes.
  - `/promo` offers "Разделочная доска за отзыв".
  - The Avito widget on the home page includes the review "Есть конкретная карточка товара, фото и указана стоимость, по факту стоимость выше почти в два раза" (Яна, "Не договорились").
- **Confidence:** Confirmed (the dead Avito profile is well-supported, from one visit).
- **Customer impact:**
  - Russians check reviews on Yandex Maps, 2GIS and Avito before buying from a regional maker. A 4.4 from 16 ratings and an Avito link that leads nowhere look like a business that closed or changed hands.
  - The visible "price twice as high" review feeds the most common objection. A single negative review makes 62% abandon.
- **Commercial impact:** A direct drag on conversion from search and Maps traffic, which is the main channel for local and regional discovery.
- **Recommendation:**
  - Claim and merge the Yandex cards, reply to every review, and update the goods section.
  - Claim the 2GIS card.
  - Fix or remove the dead Avito link.
  - Run a post-delivery review request (QR on the packaging, a message 7–10 days after delivery) pointing to Yandex and 2GIS.
  - Reconsider "доска за отзыв": rewarded reviews may breach platform rules (I could not find Yandex's exact wording, so this is a preliminary assumption) and can be filtered out.
  - Add named, photographed case studies (city, set, date) on the site.
- **Validation:** Count reviews per month on Yandex and 2GIS. Track Yandex Business card actions (calls, routes, site clicks).
- **Effort:** S (setup), then ongoing

### F6. Prices don't match between cards and the final quote, and the positioning sends mixed signals
- **Problem:** Shown prices may not be what buyers pay, and the site's premium language clashes with deep-discount messaging.
- **Location:** Product cards, `/` hero, `/promo`, Avito widget review.
- **Evidence:**
  - Product cards show fixed prices (sample of 15: 16 900–52 400 ₽).
  - The footer says "Сайт носит исключительно информационный характер и не является публичной офертой".
  - The Avito review quoted in F5 says the real price was "почти в два раза" higher.
  - The `/` hero says "СКИДКИ ДО 70%" next to "ESTIVO - это Rolls-Royce среди мебели для открытых пространств". Customers on Yandex praise "по доступным ценам".
  - The Yandex goods section, "давно не обновлялось", shows prices that may be out of date.
- **Confidence:** Confirmed on the site. That buyers see the price gap as bait-and-switch is a well-supported hypothesis (based on the review).
- **Customer impact:** Russian buyers are very sensitive to "цена на сайте ≠ цена у менеджера"; it reads as bait. "Rolls-Royce" plus "–70%" undermines both the premium story and the discount's credibility.
- **Commercial impact:** Leads drop out after the quote, and outdated prices on third-party cards generate negative reviews.
- **Recommendation:**
  - Label prices honestly: "от … ₽ за базовую комплектацию; цена зависит от размера/цвета/ткани".
  - Show what drives the price: size, cushions, frame.
  - Keep Yandex and Avito prices in sync.
  - Replace the superlatives with proof (warranty, load rating "120 кг на место", frame material, years in business "10 лет / 1000+ комплектов" from VK).
  - Limit discount claims to real, dated offers.
- **Validation:** Record the quoted price against the listed price in the CRM. Track why leads are lost.
- **Effort:** S–M

### F7. The site's seasonal messaging is wrong for October, and the off-season goes unused
- **Problem:** Summer and undated promotions are still live in October, and nothing on the site speaks to the off-season.
- **Location:** `/promo`.
- **Evidence:**
  - `/promo` today shows "СПЕЦИАЛЬНОЕ ПРЕДЛОЖЕНИЕ ДЛЯ ВАС - ЛЕТНИЕ ПРИВИЛЕГИИ", "ЗАКАЖИТЕ МИЛАН 3XL в этом месяце", and undated "АКЦИЯ НЕДЕЛИ … 345.300 ₽ 245.300₽ Ваша выгода - 30%!".
  - The site never mentions winter storage, covers as a product, pre-ordering for spring, or indoor use. The only hints are a testimonial ("На зиму переставляю его в дом") and SEO text about wintering.
- **Confidence:** Confirmed on the site. That outdoor-furniture demand is spring-led is a well-supported hypothesis.
- **Customer impact:**
  - Autumn visitors (HoReCa planning next season, dacha owners after the season) find stale summer offers.
  - Undated "акция недели" looks permanent, so it loses its urgency and credibility.
  - Under Russian advertising law, an incentive promotion is expected to state its terms and duration (preliminary assumption; legal check needed).
- **Commercial impact:** Off-season months are when a handmade maker with limited capacity can fill its production schedule.
- **Recommendation:**
  - Run a seasonal content calendar:
    - Oct–Feb: "Закажите к сезону — фиксируем цену, изготовим к маю", a B2B/HoReCa early-booking offer, indoor (интерьер/зимний сад) collections, covers and storage.
    - Mar–Jun: lead time and stock messaging ("в наличии — отправка за N дней").
  - Date every promotion.
- **Validation:** Pull Yandex Wordstat monthly history for "мебель из роупа", "плетеная мебель", "мебель из ротанга" and match the calendar to the peaks. Track lead volume by month.
- **Effort:** S (copy), M (offer mechanics)

### F8. The contact channels don't match how Russians message businesses in 2026
- **Problem:** The site leans on WhatsApp, which is now blocked in Russia, has no MAX, links to Instagram, and nothing shows how fast replies come.
- **Location:** All pages: links block and floating buttons; forms.
- **Evidence:**
  - Every page links `wa.me/79272004303` (twice), a Telegram invite link, `vk.com/estivo_tlt` and `instagram.com/estivo.tlt` (crawl links, 18/18 pages at the time).
  - There is no MAX link.
  - Forms collect only name and phone, with no field for the preferred contact channel.
  - On VK, a buyer's question waited two days for an answer.
- **Confidence:** Confirmed on the site. The WhatsApp block and the Instagram ad ban are well-supported (external sources).
- **Customer impact:**
  - Since Feb 2026 WhatsApp works only through a VPN, so the most prominent "write to us" button fails silently for many visitors.
  - Telegram works but its calls are limited.
  - Older dacha buyers, the 35–55 core group, increasingly have MAX preinstalled.
  - The Instagram link shows a platform blocked in Russia. Linking to it is a legal grey zone after 1 Sep 2025 (preliminary assumption).
- **Commercial impact:** Lost chat leads. Lead-generation sites depend on chat starts.
- **Recommendation:**
  - Make phone and Telegram (a business account or bot, not an invite link) the primary channels.
  - Add MAX once business accounts are available.
  - Keep WhatsApp as a secondary option or remove it.
  - Remove the Instagram link, or have a lawyer review it.
  - Add a "Как удобнее связаться: звонок / Telegram / MAX" option to forms.
  - State the response promise ("ответим за 15 минут в рабочее время") and keep it, including on VK.
- **Validation:** Use UTMs or click goals per messenger in Yandex Metrika (`ym` is present) and compare chat starts by channel over 4 weeks.
- **Effort:** S

### F9. The return and warranty fine print adds uncertainty for custom orders
- **Problem:** The return rules for catalog vs. custom items are unclear, and the warranty wording has errors.
- **Location:** `/vozvrat`.
- **Evidence:**
  - "Возврат возможен … в течение 14 дней после. Но это не распространяется на мебель, выполненную по индивидуальным размерам".
  - "Мебель, изготовленная по индивидуальным проектам и эскизам, возврату не подлежит".
  - The exclusion list includes "износ мебели".
  - The cover list says "дефекты, возникшие в результаты…" (typo).
  - "Каждое изделие создаётся как единственное" appears on `/` and `/onas`.
- **Confidence:** Confirmed on the site. The legal reading is a well-supported hypothesis.
- **Customer impact:** The 14 days is more generous than the legal minimum of 7, which is good. But the buyer can't tell whether a catalog item in a non-default colour counts as "индивидуальный", so they can't tell whether they can return it. Calling every item unique strengthens the impression that nothing can be returned.
- **Commercial impact:** Hesitation on catalog orders, which should be the easy sale.
- **Recommendation:**
  - Spell out that catalog items in any palette colour can be returned within 14 days, and only non-standard sizes or sketches cannot.
  - Add how a return physically works for a bulky item (who pays the carrier, how it is packed).
  - Fix the typos.
  - Have a lawyer check the wording against art. 26.1 and the written-notice requirement (3 months if the written terms are missing).
- **Validation:** Legal review. Count return-related questions in conversations.
- **Effort:** S

### F10. Claims that premium buyers will see through, and too few specifics
- **Problem:** The copy leans on superlatives and implausible numbers, while the product cards lack the specifics buyers compare on.
- **Location:** `/`, product cards.
- **Evidence:**
  - Claims on `/`: "перепады температур от -70 до +70°С", "Каждое изделие - Эверест мастерства", "Rolls-Royce среди мебели".
  - The Вольтерра Люкс card lists "Каркас: Металл, порошковый окрас" while its description says "Каркас мебели сделан из прочного алюминия".
  - The cushion fabric is "Ткань Оксфорд".
  - 16 corpus pages show the visible text "Error get alias".
  - "ВСЯ МЕБЕЛЬ ИМЕЕТ СЕРТИФИКАТЫ" appears with no certificate number shown in the text.
- **Confidence:** The text is confirmed. The buyer reaction is a preliminary assumption.
- **Customer impact:**
  - Buyers comparing with imported and marketplace rattan look for frame material (aluminium vs. steel matters for rust), fabric brand and water resistance, cushion foam, UV rating, and winter-care instructions.
  - Exaggerated numbers reduce the credibility of the true claims.
- **Commercial impact:** Weaker justification for the premium price.
- **Recommendation:**
  - Use a consistent spec block on each card: frame, weave, fabric, foam, max load (the 120 kg is already on `/vozvrat`), warranty, lead time, care and winter storage.
  - Show the certificate or declaration number.
  - Drop the "-70°C" claim unless it is tested.
  - Fix "Error get alias" (Tilda).
- **Validation:** Usability test with 5 target buyers ("достаточно ли информации, чтобы заказать без звонка?").
- **Effort:** M

### F11. Marketplaces and Avito: low priority, but the Avito link needs a decision
- **Problem:** ESTIVO has no confirmed marketplace presence, and the site's Avito presence is a dead link.
- **Evidence:** I found no ESTIVO listings on Ozon, WB or Yandex Market (not fully verified). The site links a dead Avito profile. Sources report 1–2% conversion and high logistics and ad costs for bulky furniture on marketplaces.
- **Confidence:** Preliminary assumption.
- **Recommendation:**
  - Do not prioritise Ozon/WB for custom, bulky handmade sets.
  - Avito, which historically drove 36 ratings, fits regional lead generation better: restore an active, verified Avito business profile and link it correctly.
  - Consider Yandex Market or Ozon only for small standard items (accessories, кашпо, covers) as a discovery test.
- **Validation:** Compare Avito leads and cost per lead against site leads over one season.
- **Effort:** M

---

## 5. Top 5 priorities (Russian-market view)

1. **One warranty, one phone, one legal entity everywhere (F1, F2).** Cheap to fix, and it removes the most visible trust breaks.
2. **Rebuild `/dostavka` around buyer questions (F3, F4):** cost and time examples by city, carriers, lifting and assembly, packaging, prepayment model, named instalment partner with a monthly amount on cards.
3. **Fix the review trail (F5):** claim and merge the Yandex cards, claim 2GIS, replace the dead Avito link, reply to reviews, run post-delivery review requests (no rewards).
4. **Update the messenger setup for 2026 Russia (F8):** phone and Telegram first, MAX when available, WhatsApp demoted, Instagram link removed or reviewed by a lawyer, and a published response-time promise.
5. **Seasonal calendar and honest pricing (F6, F7):** remove the summer offers now, launch a "к сезону 2027" pre-order and B2B early-booking offer, date every promotion, label prices as "от … базовая комплектация".

---

## 6. Open questions and the data needed

- **Search-demand seasonality** for the core queries: Yandex Wordstat monthly history, Samara region and all of Russia.
- **Where leads come from and how they convert:** CRM or Telegram notification log by source (site, VK, Avito, Yandex Maps), share of leads from outside the region, lead→sale rate, typical loss reasons.
- **2GIS card status and reviews:** needs a manual check from a normal browser.
- **The second Avito profile** (`91b69cd0…`): status and review count, needs a manual check.
- **Legal entity:** is ООО «Эстиво» (ИНН 6321368220) still active, and which entity signs contracts and issues VAT invoices? Check egrul.nalog.ru.
- **Instalments:** who provides them, and is the 12-month term still valid after the reported 6-month BNPL cap?
- **Prepayment share and contract template** for made-to-order items.
- **Actual delivery costs and times** to the top 5 destination cities, and whether sets arrive assembled.
- **Which messengers buyers actually use now:** last 3 months of conversations by channel.
- **Whether "ГТА" is a real carrier** or a typo/abbreviation for a known one (e.g. a freight forwarder).
