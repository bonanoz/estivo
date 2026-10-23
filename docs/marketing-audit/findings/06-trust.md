# 06 — Trust signals and purchase objections (Agent 6)

Scope: every on-site trust signal on the live Tilda site estivo63.ru, and the objections a first-time buyer from another city has before paying 100k–300k ₽. Audit date: 2026-10-20. This file builds on `02-russian-market.md` (F1 warranty, F2 phones/entities, F5 review trail, F8 messengers, F9 return fine print) and does not repeat those findings. Where it extends them, it says so.
Confidence labels: **Confirmed** (seen by me), **Well-supported hypothesis**, **Preliminary assumption**.

---

## 1. What I inspected

**Corpus (all 276 pages, crawl complete):** full text of `/` (home), `/vozvrat`, `/offer`, `/kontakty`, `/onas`, `/dostavka`, `/policy`, `/policy02`, `/b2b`, `/promo`, the orphan pages `page60195393.html` ("Отзывы Эстиво"), `page87158106.html` ("Copy of политика конфиденциальности"), and a Python scan of all 234 product pages for trust terms (warranty, certificate, contract, prepayment, damage, assembly, colour, entity details, phones). `crawl_results.jsonl`: every outbound link across all pages (counts below). `page_.html` (home HTML) to map link labels.

**My own Playwright runs (real Chrome, desktop 1440 px, scripts in `a06/`):**
- Home: screenshots of the certificate carousel, reviews block and production-stages block (`a06/v_cert_1.png`, `a06/v_reviews_1.png`, `a06/v_reviews_2.png`, `a06/v_prod_1.png`, `a06/v_prod_2.png`). I pulled the record DOM to get image URLs and link targets.
- Certificate images: I downloaded the 3 carousel images from static.tildacdn.com (not estivo63.ru) into `dl06/` and read them at full resolution.
- External links, one visit each (`a06/ext.json`, `a06/ext_*.png`): Telegram invite, VK, Instagram, Pinterest (pin.it), both Avito profiles, Google Drive PDF, the 2 Yandex Disk files, the `project10482059.tilda.ws` mirror, and the 2 wa.me numbers.
- Existing screenshots `shots/onas_desktop.png` and `shots/kontakty_desktop.png`.

**Not done or not accessible:** I submitted no forms and sent no messages. I could not check whether the WhatsApp numbers have live accounts (wa.me only resolves to a generic "Чат в WhatsApp с +7 …" page). I could not see Instagram post dates while logged out. I did not check the INNs in EGRUL (rusprofile/RBC failed for Agent 2). I did not test the mobile layout of the trust blocks.

### Outbound link inventory (from crawl_results.jsonl, 276 URLs)
| Link | Pages | Status today (my visit) |
|---|---|---|
| `t.me/+7zVfVsf1abszODYy` | 154 | Works. It is a **channel** "ESTIVO \|Плетеная мебель\| Роуп \|Ротанг\|", **276 subscribers**, not a chat with a manager. The channel bio lists **another phone, "8-9272-689-404"**, and "TG: @estivo63". |
| `vk.com/estivo_tlt` | 154 | Works (redirects to vk.ru). 1.2K subscribers, a post dated 8 Oct; "Отзывы" discussion with 13 comments, last 25 Jun 2025. |
| `instagram.com/estivo.tlt` | 153 | Works. 1,838 followers; highlights include "ПРОИЗВОДСТВО", "Отзывы", "В наличии". Post dates not visible logged out. Meta is designated extremist in Russia (see 02-F8). |
| `wa.me/79272004303` | 153 + 40 | Resolves to WhatsApp's send page. WhatsApp is blocked in Russia since Feb 2026 (02-F8). Account status not verifiable. |
| `pin.it/4AWL8Yise` | 39 | Works → Pinterest "ESTIVO63", **2 followers**, latest board "1 год" / "2 года" old. The link carries a personal `invite_code`/`sender` share parameter. |
| Avito `91b69cd0…` ("Смотреть отзывы на Авито" button on home) | 5 | **"Пользователь не найден"** (page fully rendered). Agent 2 reported this profile as IP-blocked; on my visit it loaded and shows the profile is gone. |
| Avito `7cba9cbb…` (Avito widget links) | 5 | **"Пользователь не найден"** (HTTP 439, same text). |
| `drive.google.com/…1T1e8K3f…` (menu item "Кашпо" on `/roup`, `/promo`, `page155943176`) | 4 | Opens **"Kashpo 2024.pdf", 75 pages, "Вазоны и кашпо премиум-класса 2024 год"**, in which the maker says "Мы работаем с бетоном, чугуном, металлом, древесиной и стеклопластиком" and mentions MOSCOWFLOWERSHOW medals. |
| `disk.yandex.ru/i/jiOYIIzZqJNizg` | 2 | Same "Kashpo 2024.pdf". |
| `disk.yandex.ru/i/nHY_mHmHS4C5sw` ("Скачать презентацию" on `/offer`) | 1 | Works: "5. ESTIVO Commercial .pdf". |
| `project10482059.tilda.ws/` (+`/rotang`) on `/offer` | 1 | A full public mirror of the site on Tilda's technical domain. |
| `tel:+7(917)824-67-22`, `wa.me/79178246722` | 1 (`/promo`) | A different number from the rest of the site (02-F2). |

---

## 2. Findings

### T1. The "certificates" belong to another company and have all expired
- **Problem:** The certificate carousel shown under "ВСЯ МЕБЕЛЬ ИМЕЕТ СООТВЕТСТВУЮЩИЕ СЕРТИФИКАТЫ БЕЗОПАСНОСТИ И КАЧЕСТВА" is on the home page and on **all 234 product pages**. All three documents in it are issued to a different legal entity, and all three have expired. None of them is a certificate for furniture made by ESTIVO.
- **Location:** `/` section "Сертификация" (records `rec793012432` + `rec801823230`), and the same block on every `/…/tproduct/…` page.
- **Evidence (read from the full-resolution images, Confirmed):**
  1. "СЕРТИФИКАТ СООТВЕТСТВИЯ № RU.04ПТС0.C02183", voluntary system "Промтехсертификация", "Выдан: Общество с ограниченной ответственностью «АВП РОТАНГ»", Dimitrovgrad, Ulyanovsk oblast, ИНН 7329012820. It certifies a **quality management system** (ГОСТ Р ИСО 9001-2015), not a product. "Действует до: 27.06.2025".
  2. "РАЗРЕШЕНИЕ на применение знака соответствия" for the same certificate, issued to «АВП РОТАНГ», "Действует до: 27.06.2025".
  3. "ЭКОЛОГИЧЕСКИЙ СЕРТИФИКАТ СООТВЕТСТВИЯ" (voluntary system "ЕВРАЗСТАНДАРТ"). The object is "Экоротанг (Rammus - волокно)", meaning the **rattan fibre**, not furniture. The holder is «АВП РОТАНГ» (zakaz@rammus.ru). "Действителен до 18.04.2020".
  - Neither ESTIVO entity (ООО «ЭСТИВО», ИНН 6321368220, or ИП Мелихова, ИНН 632147606449) appears on any of them. There is no declaration of conformity (декларация) and no certificate number in the page text.
- **Customer impact:** A careful buyer or a B2B/HoReCa procurement officer who zooms in sees a supplier's certificates that expired 4 months to 6 years ago. That turns a trust claim into evidence of carelessness, or worse, of misleading claims. Most visitors won't read them. But the buyers who do (B2B, larger orders) are exactly the high-value ones.
- **Commercial impact:** Risk to B2B deals that require documents. Reputational and possibly legal risk: an advertising claim that "all furniture has certificates" backed by another firm's expired documents could be read as unreliable advertising under 38-ФЗ (Preliminary assumption; legal check needed).
- **Confidence:** Confirmed (documents read). The legal reading is a preliminary assumption.
- **Recommendation:** Remove the claim and the carousel now. Replace them with what is true, for example: "Волокно ротанга — сертифицированный материал Rammus (АВП Ротанг)", but only with a valid, current supplier document. If ESTIVO wants a furniture claim, it should obtain its own declaration of conformity or a voluntary certificate for its products and show the number with a link to the registry (pub.fsa.gov.ru).
- **Validation:** Re-check the home page and one product page after the fix. Ask the owner whether ESTIVO holds any document in its own name.
- **Effort:** S (removal), M (getting its own document).

### T2. Two legal entities, plus a sole trader registered in 2023 behind a "10+ years" claim (extends 02-F2)
- **Problem:** The buyer can't tell who the seller is. The footer on every non-product page names one entity, `/kontakty` names another, and the privacy policy names the second one as data operator. Product pages, where buyers add to cart, show no entity at all.
- **Evidence (Confirmed, corpus scan):**
  - The footer on 39 non-product pages reads "Название: ИП МЕЛИХОВА МИРОСЛАВА СЕРГЕЕВНА, ИНН: 632147606449, ОГРИП 323632700013220" plus the bank account. "ОГРИП" is a typo for ОГРНИП. The ОГРНИП prefix "323" means it was registered in **2023** (Well-supported hypothesis: the 2nd–3rd digits of an ОГРНИП encode the year).
  - `/kontakty`: "Общество с ограниченной ответственностью “ЭСТИВО” … ИНН/КПП 6321368220/ 632101001 … ОГРН 1146320022089 … Генеральный директор Кострикин Николай Вячеславович". The legal address is "ул. Луначарского, б-р 17-31", a residential-style address different from the showroom. "Наименование огранизации" is misspelled. The ОГРН prefix "114" means **2014**.
  - `/policy` and `/policy02`: "предпринимаемые ООО “ЭСТИВО” (далее — Оператор)". The home-page popup "О защите и обработке персональных данных" says it was "утверждено Костриковым Н. В." (the director's name misspelled; it is Кострикин on /kontakty).
  - Product pages: 0 of 234 show an entity name, but all 234 show the "не является публичной офертой" disclaimer.
  - The "более 10 лет" claim (`/`, `/offer`, Instagram) matches the ООО's 2014 registration, but bank transfers go to the 2023 ИП.
- **Customer impact:** A buyer paying 100k+ by bank transfer to an individual entrepreneur's account, while the site and policy talk about an ООО, will ask "с кем я заключаю договор и кому плачу?". The buyer's personal data consent names the ООО, yet the payments go to the ИП.
- **Commercial impact:** Stalled prepayments and B2B friction. A potential 152-ФЗ issue if the ИП actually processes the data the ООО is named as operator for (Preliminary assumption).
- **Recommendation:** Decide which entity sells to consumers and which to B2B. Show it in one "Реквизиты" block, the same on every page including product pages. Make the privacy policy operator match it. Fix "ОГРИП", "огранизации" and "Костриковым". If both entities are real (e.g. ООО for B2B with VAT, ИП for retail), say so in one line on `/dostavka`.
- **Validation:** EGRUL/EGRIP lookup of both numbers (status, activity code, address). Ask the owner which entity signs the contract.
- **Effort:** S

### T3. The review proof is fragile: two dead Avito profiles behind the main review widget, three anonymous quotes, and an empty reviews page (extends 02-F5)
- **Evidence (Confirmed):**
  - **Both** linked Avito profiles now return "Пользователь не найден". The button "Смотреть отзывы на Авито" points to `91b69cd0…`, and the widget's "Отзыв Avito" links point to `7cba9cbb…`. So the "5.0 из 5 На основе 36 оценок" widget (a smartwidgets.ru embed) has **no verifiable source** left.
  - The widget's newest review is dated 18 Sep 2024. It shows the same cards repeatedly (the corpus lists Ксения/Александра/Яна… twice) and includes 2 "Не договорились" reviews. One says the price was "выше почти в два раза"; the other, "Товар указан по-другому городу адрес не тот который хотелось", hints at confusion over the listing's location.
  - ESTIVO's own testimonials are three short anonymous quotes with no name, city, date, product or photo («Пользуюсь с большим удовольствием!! И рекомендую вас друзьям!»).
  - The block does have **2 video reviews** (a man in a red T-shirt by a lake; a lakeside pavilion with a lounger). These are the strongest proof on the site, but they carry no caption (name, city, set, date).
  - Orphan page `page60195393.html`, titled "Отзывы Эстиво", is in the sitemap but contains **no reviews**, only header and footer.
  - Layout: in my desktop screenshots the "ПОЧЕМУ ESTIVO" heading overlaps the testimonial cards, and a production-stage card ("6 Контроль качества") floats over the video reviews (`a06/v_reviews_1.png`, `a06/v_reviews_2.png`). This may come from Tilda's scroll animations combined with my programmatic scrolling (Preliminary assumption; check by manual scrolling).
- **Customer impact:** Buyers who click through to verify (27% look for negatives on purpose, see 02) land on "Пользователь не найден". That reads as "the shop was closed or banned on Avito". Anonymous quotes add nothing.
- **Recommendation:** Remove the Avito widget and button, or reconnect them to a live profile. Caption the 2 videos ("Андрей, Тверская обл., комплект …, 2024"). Replace the anonymous quotes with 3–5 named case studies (city, set, price band, delivery time, customer photo). Link to Yandex Maps reviews, the only live third-party rating (4.4/16, see 02). Delete or fill `page60195393.html` and drop it from the sitemap.
- **Effort:** S

### T4. Contact details: one phone on the site, two more in the company's own channels, and two versions of the address
- **Evidence (Confirmed):**
  - "+7 927 200 43 03" appears 309 times and is consistent across the site, apart from `/promo`'s "+7(917)824-67-22" (02-F2).
  - The **Telegram channel the site links to** gives "Тел: 8-9272-689-404", a fourth number after the Yandex card's "+7 (8482) 78-94-04" (02).
  - Address: 275 pages say "г. Тольятти, б-р Туполева 12А. Офис 2-4". `/dostavka`, `/b2b` and `/offer` say "ул. Туполева, 12А, ТД Вояж". These are probably the same building (an office inside the "Вояж" shopping centre), but a visitor from another city can't tell whether these are a showroom and a warehouse, or one place.
  - Hours: "Пн-Пт: 10:00-19:00, Сб: 10:00-18:00, Вс: 10:00-17:00" next to "РАБОТАЕМ ПО ПРЕДВАРИТЕЛЬНОЙ ЗАПИСИ" on 273 pages. Agent 2 saw "до 18:00" on the second Yandex card and "до 19:00" on the first.
  - `/onas` has the heading "ПРИХОДИТЕ В ГОСТИ В НАШ ШОУРУМ В ТОЛЬЯТТИ", but no showroom photo, no entrance photo and no directions. The map area on `/onas` rendered as an empty grey block in the crawl screenshot (`shots/onas_desktop.png`). `/kontakty` has a Yandex map, and the console showed a Yandex Maps "Invalid API key" error on /promo (orchestrator note); whether the map pin renders correctly is unverified.
- **Customer impact:** "По предварительной записи" with fixed hours is contradictory: are they open or not? Remote buyers wondering whether the business is real look for a photographable, findable place. One address in one format, with a photo of the shopfront and showroom, settles it.
- **Recommendation:** One address string everywhere: "г. Тольятти, б-р Туполева, 12А, ТД «Вояж», офис 2-4, 2 этаж (?)". Add a showroom photo, an entrance photo and "как пройти". Rephrase the hours as "Шоурум открыт Пн–Вс по записи: 10–19 / 10–18 / 10–17. Запишитесь за час — встретим". Fix the phone in the Telegram bio and on Yandex.
- **Effort:** S

### T5. The guarantee and return page promises less than it seems, and leaves out the cases buyers worry about
- **What `/vozvrat` actually promises (Confirmed, verbatim):**
  - Covered: "дефекты, возникшие в процессе эксплуатации и перевозки по нашей вине или вине ТК"; "дефекты, возникшие в результаты некачественной сборки или плетения".
  - Excluded: "поломки, вызванные несоблюдением правил нагрузки (не более 120 кг на одно посадочное место)", "повреждения мебели, нанесенные покупателем", "износ мебели".
  - Remedy: "В этих случаях мы вернем вам деньги или заменим неисправный товар. Доставка осуществляется за наш счет". Term: "24 МЕСЯЦА".
  - Return: "Возврат возможен в момент принятия заказа или в течение 14 дней после. Но это не распространяется на мебель, выполненную по индивидуальным размерам"; conditions "в первоначальном товарном виде в упаковке и не имеет следов эксплуатации", "имеется документ, подтверждающий факт покупки этого товара (договор, чек)"; "Мебель, изготовленная по индивидуальным проектам и эскизам, возврату не подлежит".
- **Gaps (Confirmed by corpus scan):**
  - **What the warranty covers** is not named by component: frame welds, powder coating, the weave, fabric fading, foam. The home page says "Гарантия 3 года", `/offer` says "Гарантия качества на материалы плетения 3 года", `/promo` "ГАРАНТИЯ 5 ЛЕТ", `/vozvrat` "24 МЕСЯЦА" (02-F1). So it's unclear whether 3 years applies to the weave material only, and 24 months to the item.
  - **Transport damage procedure:** no instructions such as "вскройте упаковку при водителе, снимите видео, составьте акт с ТК". 0 hits for "брак", "акт", "приёмк".
  - **Colour differs from photo:** 0 hits for "может отличаться"/"монитор". The site never says whether a colour mismatch is a ground for return, or whether samples (образцы) can be posted.
  - **Who pays return shipping** for a bulky item returned in the 14 days (not for a defect): not stated.
  - Whether a catalogue item in a non-default palette colour counts as "индивидуальный" (02-F9).
  - **Repairs after warranty, spare cushions/covers:** not mentioned.
- **Customer impact:** These are exactly the questions a remote buyer asks before a 100k+ prepayment. Silence pushes them to the phone, or away.
- **Recommendation:** Rewrite `/vozvrat` as Q&A blocks: "Что покрывает гарантия (каркас — N лет, плетение — N лет, ткань — N мес.)", "Что делать, если мебель пришла повреждённой (видео распаковки, акт с ТК, мы заменим за свой счёт за N дней)", "Если цвет не совпал", "Возврат каталожной позиции", "Ремонт после гарантии". Put a 3-line summary of it on every product page.
- **Effort:** S–M

### T6. The prepayment model is written down, but only on a page buyers don't see
- **Evidence (Confirmed):** `/offer` (title "Коммерческое предложение"; linked only from `/b2b`) says: "Мы работаем по договору. Вы оплачиваете 50%, мы создаем мебель для вас, оставшиеся 50% оплачиваются после изготовления заказа, перед его отгрузкой." `/dostavka`, `/vozvrat`, `/` and all product pages contain **no "предоплат"** and no "50%". The home page has the strongest reassurance, "Согласование мебели с клиентом по фото и видеоотчету" (production stage 6), but it is not linked to payment.
- **Customer impact:** For a private buyer from another city, "сколько платить вперёд и за что" is the main fear. The answer exists and is reassuring (contract, 50/50, final payment before dispatch after a photo/video report), but it is hidden in a B2B document.
- **Recommendation:** Put on `/dostavka` and on product pages: "Работаем по договору. 50% — предоплата, 50% — после фото- и видеоотчёта о готовой мебели, перед отправкой. Доставка застрахована." Name who signs (see T2).
- **Effort:** S

### T7. "Not a public offer" next to a working cart and fixed prices
- **Evidence (Confirmed):** 272 of 276 pages, including all 234 product pages, show "Сайт носит исключительно информационный характер и не является публичной офертой, определяемой положениями ч. 2 ст. 437 ГК РФ". Meanwhile every product card has a price and a "В корзину" button, the cart heading is "Ваш заказ" and the checkout button is "Оформить заказ" (orchestrator note). Some cards show "Цена по запросу" with "В корзину".
- **Customer impact:** It is legal, and common on Russian sites, but next to a cart and "Оформить заказ" it signals "the price on the site isn't binding". That matches the Avito "Не договорились" review ("по факту стоимость выше почти в два раза"). A buyer will expect re-quoting.
- **Recommendation:** Keep the disclaimer but make the flow honest. Rename the cart button "Отправить заявку на расчёт". Add near the price: "Цена базовой комплектации; точную стоимость с доставкой подтвердим за 15 минут". Show "Цена фиксируется в договоре".
- **Confidence:** Disclaimer and cart Confirmed; the buyer reading is a well-supported hypothesis.
- **Effort:** S

### T8. Little real proof of production or the showroom, and some links lead to off-brand content
- **Evidence (Confirmed):**
  - Production proof: the home production block has one real black-and-white photo (a weaver working on a cocoon chair). `/onas` has a B&W hands-weaving photo, a Tolyatti monument photo and one dining-set photo. The claims are big ("более 20 профессионалов", "три цеха по сборке, отдельный цех по алюминиевой сварке… 650 кв. м", "более 10 000 единиц", "Более 1 500 довольных… клиентов", "более 60 городов" on `/offer`) but there is no video tour, no team photos and no photo of the 650 m² space.
  - The `/onas` "НАШИ БЕСТСЕЛЛЕРЫ" cards are 5 identically named "комплект из ротанга" with blurred images in the crawl screenshot (lazy load not finished, or placeholders; Preliminary assumption).
  - The **"Кашпо" menu item** opens a 75-page third-party-style PDF on Google Drive ("Вазоны и кашпо премиум-класса 2024"; the maker works with "бетоном, чугуном…") that has nothing to do with woven furniture or ESTIVO's description of itself. Google Drive also loads poorly in Russia (Preliminary assumption).
  - The **Telegram link** is a channel (276 subscribers), not a dialogue, so "написать" ends in "Join channel".
  - **Pinterest**: 2 followers, inactive 1–2 years; it adds no proof and signals neglect.
  - **`project10482059.tilda.ws`** exposes a full duplicate of the site on a technical domain, linked from `/offer`.
  - Named HoReCa clients on `/offer` only: "Марусовка. Казань, Австерия. Тольятти, Glampoint. Калининград, MEWS. Тольятти". No photos or links, and not shown to retail visitors.
- **Recommendation:** Add a "Производство" section: a 60–90 s video, 6–8 colour photos of the workshops, team and packing, and a date. Move the HoReCa client list (with photos of installed furniture) onto `/` and `/b2b`. Replace the "Кашпо" PDF with ESTIVO's own planters page, or remove it. Link Telegram to @estivo63 or a manager's account, not the channel invite. Remove Pinterest. Unpublish or password-protect the tilda.ws mirror (Tilda project settings).
- **Effort:** S (links), M (photo and video shoot)

### T9. The privacy and consent setup is duplicated and doesn't match the trackers (low priority, compliance)
- **Evidence (Confirmed):** `/policy` and `/policy02` are byte-identical apart from the title ("политика конфиденциальности02"); `page87158106.html` is a third copy. All three are indexable pages. The policy's processing purposes list only "уточнение деталей заказа" with name, e-mail and phone. It does **not mention cookies or Yandex Metrika**, although the site runs `ym` and a cookie banner ("Мы используем файлы cookie… ХОРОШО"). The legal basis cited is 149-ФЗ only. The footer link "О защите и обработке персональных данных" opens a popup "Положение … утверждено Костриковым Н. В. ООО «ЭСТИВО»".
- **Impact:** Buyers rarely read this, but Roskomnadzor checks and attentive B2B clients do. It adds to the "two entities" confusion in T2.
- **Recommendation:** Keep one policy URL, add cookies/Metrika, align the operator with T2, and remove `/policy02` and `page87158106.html` (or noindex and redirect them). Legal review.
- **Confidence:** Text Confirmed; compliance risk is a preliminary assumption.
- **Effort:** S

---

## 3. Objection map: first-time buyer from another city, budget 100–300k ₽

| # | Objection | Answered on site? | Where / what is missing |
|---|---|---|---|
| 1 | Is this a real company, who exactly am I paying? | **Partly, contradictory** | ИП in the footer vs ООО on /kontakty and in the policy; no entity on product pages (T2) |
| 2 | How much prepayment, under what contract? | **Hidden** | Only `/offer` (B2B): "договор, 50% / 50% перед отгрузкой" (T6) |
| 3 | What if it never arrives / the company disappears? | **No** | No contract sample, no "оплата частями после фотоотчёта" on retail pages, review links dead (T3) |
| 4 | What does delivery to my city cost and how long does it take? | **No** | /dostavka: "Свяжитесь с нами и мы подберем…"; no cost/time examples (02-F3) |
| 5 | What if it arrives damaged? | **Partly** | /dostavka "Груз полностью застрахован"; /vozvrat covers "перевозки по … вине ТК"; no acceptance procedure (T5) |
| 6 | What if the colour differs from the photo? | **No** | 0 mentions; no samples or swatch-mailing offer; only the photo/video approval stage on `/` (T5) |
| 7 | Who assembles it? Does it arrive assembled? Lifting to the floor? | **No** | 0 hits for "собранн", "подъём"; "сборк" only in the warranty context (02-F3) |
| 8 | How long does production take? | **Inconsistent** | "от 14 дней" (/offer), "от 4 недель" (/b2b), "от 3 дней" delivery on `/` |
| 9 | Will the price on the site be the final price? | **No, the disclaimer suggests the opposite** | "не является публичной офертой" + visible Avito review "дороже почти в два раза" (T7) |
| 10 | Warranty length and what it covers | **Contradictory** | 24 мес / 3 года / 5 лет; covered/excluded list on /vozvrat but not per component (T5, 02-F1) |
| 11 | Can I return it if I don't like it? | **Yes, with caveats** | /vozvrat: 14 days, excluding custom sizes; who pays return freight not stated |
| 12 | Is it really their own production and quality? | **Weakly** | 1–2 real production photos; certificates belong to «АВП РОТАНГ» and have expired (T1, T8) |
| 13 | Do others from my region buy from them? | **Weakly** | "более 60 городов" and HoReCa names only on /offer; videos uncaptioned (T3, T8) |
| 14 | Can I see it live first? | **Partly** | Showroom "по предварительной записи" in Tolyatti, no photo; no video-call viewing offer (T4) |
| 15 | Can I pay in instalments, by card? | **Partly** | "Беспроцентная рассрочка до 12 месяцев", no provider named; cards not listed (02-F4) |
| 16 | How do I store or maintain it in winter? | **Partly** | FAQ "Для какого климата подходит мебель?" on `/`, a testimonial; no care guide |
| 17 | How fast will they reply, and where? | **No** | WhatsApp blocked; Telegram link is a channel; no response-time promise (02-F8, T8) |
| 18 | Will I get a receipt and documents? | **Partly** | /vozvrat mentions "договор, чек"; /dostavka "Безналичный расчёт с НДС" |

Summary: of the 18 objections, **1 is answered clearly** (#11), 9 partly or contradictorily, 1 only on a hidden page (#2), and 7 not at all.

---

## 4. Top 5 priorities (trust view)

1. **Remove the certificate claim and carousel now (T1).** It shows another company's expired documents on 235 pages. This is the cheapest fix with the biggest downside if a B2B client notices.
2. **One seller identity (T2):** one entity in the footer, on /kontakty, on product pages and in the policy; typos fixed; payment recipient explained.
3. **Publish the prepayment and damage/colour procedure (T6, T5):** "договор, 50/50 после фото- и видеоотчёта, вскрытие при водителе, замена за наш счёт", on /dostavka, /vozvrat and in a 3-line block on every product page.
4. **Rebuild the proof of reviews and production (T3, T8):** remove the dead Avito widget, caption the 2 videos, add named case studies and the HoReCa client list, add a production video and photos, and fix the Telegram link (dialogue, not channel), "Кашпо" PDF and Pinterest.
5. **Make the cart honest about price (T7):** relabel it "заявка на расчёт", say "цена фиксируется в договоре", and explain what changes the price.

---

## 5. Open questions and data needed

- Does ESTIVO hold any declaration or certificate in its own name? Is «АВП РОТАНГ» (Rammus) its current fibre supplier, and does it have a valid supplier certificate?
- Which entity signs consumer contracts and receives payment: ООО «ЭСТИВО» or ИП Мелихова? Are both active (EGRUL/EGRIP)?
- What happened to both Avito profiles (deleted, blocked, re-registered)? Is there a new one?
- Which phone actually answers: 927-200-43-03, 917-824-67-22, 927-268-94-04, (8482) 78-94-04? Use call tracking or ask managers.
- The share of leads from outside Samara oblast, and how many stall at the prepayment or delivery-cost stage (CRM/Telegram log).
- The actual transit-damage and return rates, which would let the site state concrete numbers ("за 2025 год — N повреждений, все заменены").
- Is the "Кашпо" PDF a partner's catalogue that ESTIVO resells? If so, under what brand?
- Manual check of the home trust blocks with normal scrolling (overlap bug) and on mobile.
