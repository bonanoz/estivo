# 05 — Sales copy and offer audit (Agent 5)

All quotes come verbatim from the Playwright corpus (`corpus/*.txt`, complete: 276 pages, 234 of them product pages) and `crawl_results.jsonl`. I did not re-visit the live site. I counted things with Python over the corpus (script: `a05/scan.py`).

## 1. What I inspected

- **Key pages, read in full:** `/` (home.txt), `/promo`, `/onas`, `/b2b`, `/dostavka`, `/vozvrat`, `/offer` (an unlinked "Коммерческое предложение" page that is in the sitemap), `/kontakty`.
- **Catalogue hubs:** `/rotang`, `/roup`, `/komplekty`, `/komplektyroup`, `/price`, `/kreslo`, `/kresloroup`, `/salerotang`, `/saleroup`.
- **Product pages:**
  - All 234 were scanned by script for titles, buttons, error strings, material, care, warranty and lead-time wording.
  - About 30 were read in full: sets №1, 6, 23, 24, 25 (Copy), 27, 28, 30, 31, 40, 46, 53, 55, 60, 61, 64, 65, 71, 90; sale sets 12, 32, 41; sofas Вольтерра Люкс, Палермо and the two corner Вольтерра pages; chairs Палермо, Терлаго and Турин pouf; tables Палермо, Римини and the ДПК add-on; Комо cocoons; roup items Милан, Милан Ретта, Бари table, Бари L Copy; Укрывной чехол; the colour swatches; the Tilda demo products.
- **Cart and checkout:** I used `shots/cart_opened.png`, `shots/product60_after_cart_click.png` and the form schema in `crawl_results.jsonl` (186 pages carry the checkout form).
- **Not done:**
  - I did not open the checkout's success message or the popups live, so their microcopy is unverified.
  - I did not check whether the chosen rattan colour reaches the cart line. The drawer shows only the name, quantity and price.
  - The FAQ answers are collapsed accordions, so the corpus holds only the questions.

## 2. Findings

### C1. The warranty has four versions, and none of them appears on a product page
- **Problem:** The site gives several different warranty terms, and none of them reaches the place where people decide to buy.
- **Location:**
  - `/` and the duplicate landing pages: «Гарантия 3 года и доставка по всей России от 3 дней»
  - `/b2b`: «Гарантия 3 года»
  - `/vozvrat`: «24 МЕСЯЦА»
  - `/promo`: «ГАРАНТИЯ 5 ЛЕТ на все изделия»
  - `/offer`: «Гарантия качества на материалы плетения 3 года» (this one covers the weave material only)
  - Agent 02 found «24 месяца» on VK as well.
- **Evidence:**
  - 0 of 234 product pages contain the root «аранти».
  - The lifespan claims also disagree: «прослужит не менее 10 лет» (9 occurrences), but the corner sofa says «служит не менее двух десятилетий».
  - **Confirmed.**
- **Customer impact:** A buyer spending 150–400k ₽ reads the mismatch as unreliability. On the product page itself they find no warranty at all.
- **Commercial impact:** Trust is lost at the moment of decision. The «5 лет» promise may also create a legal obligation, because a buyer can hold the seller to the best advertised term (Preliminary; needs a lawyer).
- **Recommendation:** The owner picks one term per component, based on what the company actually honours, for example:
  - каркас — [уточнить] лет
  - плетение — [уточнить]
  - ткань и наполнитель подушек — [уточнить]

  Then:
  - Publish the table on `/vozvrat`.
  - Replace the other claims with one line plus a link: «Гарантия [N] — подробнее».
  - Remove «5 ЛЕТ» from `/promo` unless that is the real term.
  - Choose between «10 лет» and «двух десятилетий».
- **Validation:** Grep the corpus again for «аранти» and «лет» after the fix.
- **Effort:** S

### C2. Weather and temperature claims contradict each other, and the SEO text describes natural rattan while the product is plastic
- **Problem:** The site gives three temperature ranges, and its long SEO text describes a different material from the one the products are made of.
- **Location:**
  - «от -70 до +70°С»: `/`, `/roup`, `/b2b` (9 occurrences)
  - «от -50 до +80°С»: `/rotang`
  - «от -40 до +40»: product pages (15 occurrences)
  - The SEO block on `/` describes natural rattan: «лоза прошла правильную атмосферную сушку, а лаковое покрытие нанесено минимум в четыре слоя», «проваривает её для эластичности», «Истинная мебель плетеная из ротанга природного происхождения».
  - Every product page says «Материал плетения: Искусственный эко-ротанг», and `/b2b` says «Говоря простыми словами, — пластик».
- **Evidence:** Corpus grep. **Confirmed.**
- **Customer impact:**
  - «-70°C» is not credible, and the true range is unclear.
  - A buyer who reads the SEO text and then learns the material is polyethylene may feel misled. The Avito review about the price being «выше почти в два раза» shows that buyers already notice this kind of gap.
- **Commercial impact:** Disputes, returns and refund demands become more likely. Misdescribing the material carries a risk under the consumer protection law (ЗоЗПП) on product information (Well-supported hypothesis).
- **Recommendation:**
  - Use one tested range, «[уточнить: диапазон по паспорту материала]», everywhere.
  - Rewrite the SEO paragraphs so they describe искусственный ротанг (ПЭ-лента) on an aluminium frame. Delete lozа, lacquer and «проваривает».
- **Validation:** Ask the supplier for the material datasheet. Grep the corpus again.
- **Effort:** M (S for the numbers)

### C3. The frame material is inconsistent
- **Problem:** Product pages disagree with themselves about what the frame is made of.
- **Location:**
  - Most rattan product pages list «Каркас: Металл, порошковый окрас» in the spec block and then «Каркас мебели сделан из прочного алюминия» in the body.
  - The Турин pouf says «Каркас мебели сделан из тонкостенной стали».
  - Roup Милан and Новара offer the option «Материал: Сталь / Алюминий» with no price difference explained.
  - The Палермо table says «Каркас: Металл» and then «из монолитного… алюминия».
  - The Римини table says «монолитного, легкого и прочного металла».
- **Evidence:** **Confirmed.**
- **Customer impact:** Aluminium against steel is the main reason outdoor furniture costs what it does, because aluminium does not rust. Saying «Металл» hides that argument.
- **Recommendation:**
  - Spec line: «Каркас: алюминий, порошковая окраска» where that is true, and «сталь, порошковая окраска» where it is steel.
  - Explain the Сталь/Алюминий option in one line: [уточнить: разница в цене и весе].
- **Effort:** S

### C4. Product pages don't answer pre-purchase questions
- **Problem:** Most product pages leave out the facts a buyer needs before ordering.
- **Location:** All 234 product pages.
- **Evidence (script counts):**
  - Material and frame info appears on 28 of 234 pages.
  - Dimensions in «ДxШxВ» form appear on 12 of 234.
  - Care appears on 1 of 234 (Турин: «Неприхотлив в уходе, можно мыть»).
  - Warranty appears on 0, lead time on 0, delivery on 0.
  - All 41 roup product pages (`/price/...`) are 175–270 characters of visible text: name, price, «BUY NOW», «Цвета роупа», nothing else. Example: «Стол Бари 210х100 см - 64 900».
  - Sets list only their components and prices. Example, №60: «Угловой диван Вольтерра Люкс L-образной формы, 220х280 см, 2х3 места + угол, 139.000 / Стол Палермо с подстольем 120х180 см, 56.900 / Кресло Палермо, 20.800х4=83.200 / Итого: 279.100». They give no material, dimensions of the chairs, cushion fabric or lead time.
  - **Confirmed.**
- **Customer impact:**
  - Every buyer has to call to learn basics: is it in stock or made to order, how long it takes, whether it fits, how to store it in winter.
  - The colour swatches (/cvetrotanga) are separate «products» with a «BUY NOW» button.
- **Commercial impact:**
  - Calls go up and conversion falls (Well-supported).
  - Competitors show lead time on every card (Agent 07, F2).
  - The facts already exist elsewhere on the site but are not reused:
    - `/offer`: «Сроки изготовления мебели от 14 дней», «Вы оплачиваете 50%… оставшиеся 50%… перед его отгрузкой»
    - `/b2b`: «Срок реализации от 4 недель»
    - `/vozvrat`: «не более 120 кг на одно посадочное место»
    - Комо: «выдерживает максимальную нагрузку до 200 кг»
- **Recommendation:** Add the product-description template in §5 as a fixed block on every product page. Fill it per category first (rattan sets, roup chairs, HPL tables), then per item.
- **Effort:** M–L

### C5. Lead time contradicts itself
- **Problem:** The site gives three lead times and never says which applies when.
- **Location and evidence:**
  - `/offer`: «Сроки изготовления мебели от 14 дней»
  - `/b2b`: «Срок реализации от 4 недель»
  - Home SEO text: «В течение нескольких недель»
  - Home benefit: «доставка по всей России от 3 дней». This is transit time, but it reads as total time.
  - Home process: «Если мебель есть в наличии, то мы сразу оформим доставку». No product shows whether it is in stock, except one sale set: «В наличии - цвет МОККО».
  - **Confirmed.**
- **Recommendation:** Use two separate statements:
  - «В наличии — отгрузка за [уточнить] дней»
  - «Под заказ — изготовление [уточнить: срок] + доставка ТК ГТА [уточнить] дней»

  Show the right one on each card.
- **Effort:** S (copy) + M (stock data)

### C6. Discounts are inconsistent, the numbers don't add up, and the promo is out of season
- **Problem:** The sale figures and promo copy contain several errors and conflicts.
- **Location and evidence:**
  - **Discount ceiling:** The home banner says «СКИДКИ ДО 70%», but `/salerotang` contains bigger cuts: «Кокон «Комо Люкс 2х» … 10 000р. 79 900р.» (−87.5%, probably a missing digit) and Бари armchairs at −76% to −78%. **Confirmed.**
  - **Wrong percentage:** On `/promo`, «345.300 ₽ → 245.300₽ Ваша выгода - 30%!». The real figure is 28.96% (100 000 / 345 300). Claiming 30% is an overstatement. **Confirmed.**
  - **Old price ≠ catalogue price:** «Кресло из Роупа «Бари» 6 900р. 28 900р.» on sale, while `/kresloroup` lists «Кресло Бари (роуп) 29 900р.». «Кресло Палермо - 19.900х6» in the Copy №25 set, while the product page says 20 800. **Confirmed.**
  - **Out of season:** «СПЕЦИАЛЬНОЕ ПРЕДЛОЖЕНИЕ ДЛЯ ВАС - ЛЕТНИЕ ПРИВИЛЕГИИ» in October. «АКЦИЯ МЕСЯЦА / АКЦИЯ НЕДЕЛИ / в этом месяце» carry no dates. «Акция: кофейный столик для всех новых клиентов» is repeated 7 times in a ticker, with no conditions. **Confirmed.**
  - **Unsupported claims:** «ДОСТАВКА в любую точку мира» contradicts «доставка по всей России» everywhere else. «РАССРОЧКА ПЛАТЕЖА без переплат» is not «0%». **Confirmed.**
- **Customer impact:** Inflated or fake-looking "was" prices and undated urgency are what Russian buyers are most suspicious of. Advertising law (ФЗ «О рекламе», ст. 5) treats an untrue price comparison as improper advertising (Preliminary; legal check).
- **Recommendation:**
  - Every promo gets an end date and conditions.
  - The "was" price must equal the catalogue price.
  - Percentages must be computed, not rounded up.
  - Fix the 10 000 ₽ typo.
  - Replace «в любую точку мира» with «по всей России».
- **Validation:** A script comparing sale "was" prices with catalogue prices.
- **Effort:** S

### C7. Numbered set names carry no meaning and point to different sets
- **Problem:** The set numbers don't identify a set, and the same number means different sets in different sections.
- **Location:** `/komplekty`, `/salerotang`, `/komplektyroup`, and 108 product titles of the form «Комплект мебели из ротанга «№NN»».
- **Evidence:**
  - Same number, different set: «Комплект мебели из ротанга «№34»» costs 163 000 р. in the catalogue. On sale, «Комплект мебели из ротанга 34» has an old price of 303 100 р., while sale «35» has an old price of 163 000. Sale «33» has an old price of 313 300, which is the catalogue price of «№36». The numbering is shifted by one.
  - Duplicates in the sale list: «…32» appears twice (179 000/231 300 and 79 000/174 500), and so do «…58» and «…6».
  - Five different products on `/onas` and `/rotang` are all titled in lowercase «комплект из ротанга».
  - The name says nothing about size or seating. A buyer cannot tell №53 from №55 without opening both.
  - **Confirmed.**
- **Customer impact:** A buyer who saw «№34» on sale and asks for it by phone may be quoted a different set. This is the same kind of complaint as the «стоимость выше почти в два раза» Avito review.
- **Recommendation:** Name sets by their lead piece and seating count, using only real components. For example, set №60 becomes: «Обеденная группа «Вольтерра Люкс» на 9–10 персон: угловой диван 220×280 + стол «Палермо» 180×120 + 4 кресла «Палермо»».

  How the seat count was worked out: the sofa has «2х3 места + угол». The total is 4 armchairs + 5 sofa seats + the corner seat; [уточнить] whether the corner counts as a seat.

  Keep the old number only as an article code: «Арт. К-60».
- **Effort:** M

### C8. Typos, template junk and inconsistent naming
- **Problem:** The copy contains template leftovers, misspellings and inconsistent naming.
- **Evidence (all Confirmed):**
  - **«Error get alias»:** raw template error text on all 234 product pages.
  - **«Copy:» titles:** «Copy: Кресло Бари L (роуп)» (visible in the `/kresloroup` listing at 32 900 р.) and «Copy: Комплект мебели из ротанг "№25"». Four duplicate landing pages are titled «Copy of Плетеная мебель…», and there is «Copy of политика конфиденциальности».
  - **Tilda demo products in the sitemap:** «Underwater wearable watches» (90 р., with English placeholder text «Add here some interesting details about the product…»), «Sac Marin Yellow», «Dining Chair by esteban+moreno». Also «sale роуп» (an empty page) and a «Blank page».
  - **«из ротанг»** (wrong case): 9 product titles, and the sale list has «Комплект мебели из ротанг 21/22/27/28». The catalogue has «ротанг "№20»», where the opening quote doesn't match the closing one.
  - **Quote styles:** «» in 94 titles, "" in 9, and none in the rest. One title has «№«34»», with the number outside the quotes.
  - **English buttons:** «BUY NOW» and «More products» on 41 pages (all roup items and the colour swatches). Rattan pages say «В корзину».
  - **Model names:**
    - «Вольтера Люкс» (title of the corner-sofa page and inside the sofa text «Диван Вольтера двухместный») vs «Вольтерра Люкс».
    - «Риммини Лаунж» in the title vs «Римини» in the body; the correct Russian spelling is «Римини».
    - «Кресло из Роупа «Бари»», with a capital Р.
    - «Кресло Милан Ретта (ротанг)», but the text says «Цвета роупа» and the body says «оплетено полипропиленовой лентой».
    - Commercial-offer copy says «НРL», written with Cyrillic Н and Р.
  - **Wrong type labels:** set №61 has «Тип: Места для хранения». The cover has «Тип: Аксессур». The cover is also «Укрывной Чехол», with a stray capital, and shows «15 000р.» together with «Цена по запросу».
  - **Size typos:** the Палермо table lists «90х90х700», «200х100х700», «220х100х700», i.e. 7-metre-tall tables, next to the correct «…х70».
  - **Grammar on `/`:**
    - «Производство полного цикла: от идеи до реализации по ключ» → «под ключ»
    - «Стол со шпоном на металлическим каркасе» → «металлическом»
    - «Производство, которые включает» → «которое»
    - «Наши ресурсы позволяют создавать нам» → «позволяют нам создавать»
    - Process steps are numbered 1, 2, 4, 3, 5, 6, 6, 7, 8, and «Контроль качества» appears twice.
  - **Grammar on `/b2b`:** «В нашем цеху изготавливаются плетеная мебель» → «изготавливается»; «и тд» → «и т. д.».
  - **`/dostavka` and `/b2b`:** «транспортной компаний ГТА» → «компанией». «CПОСОБЫ ОПЛАТЫ» starts with a Latin C.
  - **`/vozvrat`:** «в результаты некачественной сборки» → «в результате». The page has the heading «Гарантийные обязательства распространяются на…» but places «износ мебели» and «повреждения… нанесенные покупателем» so that the two lists are hard to tell apart.
  - **`/promo`:** the typewriter heading is captured as «ВНИМ|». It reads as a broken word on a slow first paint (Preliminary).
  - **Dimension format:** «ДxШxВ» uses a Latin x and «2х» uses a Cyrillic х; it should be «Д × Ш × В».
- **Customer impact:** For a brand that calls itself «Rolls-Royce среди мебели», visible template errors and demo products contradict the premium claim on every product page.
- **Recommendation:**
  - Remove «Error get alias». This is a technical fix; see agent 09.
  - Delete or unpublish the demo and Copy products.
  - Apply one naming pattern: «[Тип] «[Модель]» из [ротанга/роупа]». Russian quotes «» everywhere, «×» for dimensions, Russian buttons everywhere.
- **Effort:** S

### C9. The hero and benefit copy sells abstractions and skips the facts that justify the price
- **Problem:** The headline copy is vague and boastful, while the concrete facts that explain the price sit unused in other places.
- **Location:** `/` hero and benefits.
- **Evidence:**
  - Hero: «ПЛЕТЁНАЯ МЕБЕЛЬ РУЧНОЙ РАБОТЫ ДЛЯ ДОМА, ДАЧИ И БИЗНЕСА / Каждое изделие - инвестиция в атмосферу и возврат вложений».
  - Benefits: «ESTIVO - это Rolls-Royce среди мебели для открытых пространств», «Каждое изделие - Эверест мастерства», «Партнёрство с ESTIVO - знак статуса», «тысячи часов ручной работы», «Мы скрыли технологии внутри».
  - Strong facts that never reach the hero:
    - `/onas`: «В нашей команде более 20 профессионалов… три цеха по сборке, отдельный цех по алюминиевой сварке и окраске металла и складские помещения 650 кв. м»
    - `/offer`: «Произведено более 10 000 единиц мебели», «Охватили более 60 городов России», «Более 1 500 довольных корпоративных и частных клиентов», restaurant clients «Марусовка. Казань / Австерия. Тольятти / Glampoint. Калининград / MEWS. Тольятти»
    - `/dostavka`: «Беспроцентная рассрочка до 12 месяцев»
    - `/promo`: «Отправим образец за свой счёт»
  - **Confirmed.**
- **Customer impact:** «Инвестиция… и возврат вложений» means nothing to a private buyer. The brand comparisons («Rolls-Royce») invite scepticism and borrow another company's trademark (Preliminary legal risk). The question «why does it cost 250k?» is answered only in a hidden SEO block.
- **Commercial impact:** A weaker hero makes it harder to justify a price in the same band as national makers (Agent 07, F1).
- **Recommendation:** Rewrite as in §5. Drop «Rolls-Royce» and «Эверест». Move the real numbers into the hero and benefit blocks. Check the `/offer` figures with the owner before reuse (I cannot verify them).
- **Effort:** S

### C10. The B2B page states benefits without proof, and `/offer` uses an unsourced statistic
- **Problem:** The B2B pitch is thin, and the commercial offer relies on a statistic with no source.
- **Evidence:**
  - `/offer`: «увеличивают средний чек на 48%» / «на 34%», with no source.
  - `/b2b` does not use the 50/50 payment terms, the volume discount table («300 000 руб. … 1 000 000 руб. / 5% 10% 15% 20%») or the restaurant clients, all of which exist on `/offer`.
  - `/b2b` says «Скидки оптовым покупателям» but gives no numbers.
  - The /offer prices disagree with the catalogue: «Кресло Милан» costs 23 400 руб. on `/offer` («*Цены указаны без НДС») and 26 400 р. on the product page. That may be legitimate because of VAT, but it is not explained.
  - **Confirmed.**
- **Recommendation:**
  - Put the discount table, payment terms and named clients on `/b2b`.
  - Either cite the 48% and 34% figures or remove them.
  - Label prices consistently: «цена с НДС / без НДС».
- **Effort:** S

### C11. Cart and checkout microcopy gives no reassurance
- **Problem:** The cart and checkout don't tell a buyer what happens after they submit.
- **Location:** The cart drawer «Ваш заказ» and the checkout form on 186 pages.
- **Evidence:**
  - The drawer shows the line, «Сумма» and «Оформить заказ», with no colour, no lead time and no note on delivery or payment (`shots/cart_opened.png`).
  - On a product page opened by direct URL, «В корзину» gives no feedback (`shots/product60_after_cart_click.png`; orchestrator observation).
  - The form: «Ваше имя», a phone field, Delivery radios «Доставка транспортной компанией / Самовывоз», a consent box and a comment, with the button «Оформить заказ».
  - Nothing says this is a request, not a purchase, even though the footer says the site «не является публичной офертой».
  - Cards that say «Цена по запросу» still have «В корзину».
  - **Confirmed.**
- **Customer impact:** «Оформить заказ» sounds like a binding purchase with payment, which is a barrier on a 279k basket. The buyer also doesn't know when they will be called.
- **Recommendation:** See the microcopy in §5.
- **Effort:** S

### C12. Legal identity and contacts conflict inside the copy
- **Problem:** Different pages name different sellers and phone numbers.
- **Evidence:**
  - The footer on all main pages says «ИП МЕЛИХОВА МИРОСЛАВА СЕРГЕЕВНА».
  - `/promo` says «ООО “Эстиво” ОГРН: 1146320022089».
  - The phone is «+7(917)824-67-22» on `/promo` and «+7 927 200 43 03» elsewhere.
  - The pickup address is «ул. Туполева, 12А, ТД Вояж» on `/dostavka` and «б-р Туполева 12А. Офис 2-4» in the footer.
  - **Confirmed.** Agent 02, F2 covers this in depth.
- **Recommendation:** Name one seller and one phone number. If both the ИП and the ООО are real, state which one signs the contract.
- **Effort:** S

## 3. Pre-purchase question coverage

| Question | Where answered | On product page? |
|---|---|---|
| Material | `/b2b` (honest: «пластик»); rattan product pages | 28/234; roup pages: none |
| Weather and temperature | 3 conflicting ranges | partly, «-40…+40» |
| Care and winter storage | «легко моется», «Неприхотлив в уходе»; a review mentions bringing a cocoon indoors for winter | 1/234 |
| Dimensions | single items yes; sets give sofa and table sizes only | 12/234 in spec form |
| Lead time | 14 days / 4 weeks / «несколько недель» | 0 |
| Delivery | `/dostavka` (ГТА, insured; no cost or time) | 0 |
| Warranty | 3 / 24 months / 5 / 3 on weave | 0 |
| Why this price | only in the SEO block on `/`; aluminium, hand weaving, own workshop | 0 |
| Payment | `/dostavka` (0% for 12 months) and `/offer` (50/50) | 0 |

## 4. Warranty: how to resolve the conflict

1. The owner confirms the real terms in writing, per component: frame, weave, cushions and fabric. Use the vendor datasheets where possible.
2. Choose the term the company can always honour. If it is 24 months, then «5 лет» on `/promo` and «3 года» on `/` must go. If it is 3 years on the weave only, say exactly that.
3. Make `/vozvrat` the single source of truth. Add a component table, two clean lists (Покрывается / Не покрывается), the load limit («120 кг на посадочное место») and how to make a claim.
4. Everywhere else use the short form «Гарантия [N] на каркас и плетение — условия», linked to `/vozvrat`, including product pages and the cart.
5. Remove the conflicting claims from `/promo`, `/offer` and VK in the same release.

## 5. Proposed rewrites (Russian, with English glosses)

Placeholders in [уточнить: …] must be filled by the owner. Nothing here is invented. Every claim comes from a source quoted above.

### 5.1 Home hero
- **H1:** «Плетёная мебель из ротанга и роупа — своё производство в Тольятти»
  (Woven rattan and rope furniture, made in our own workshop in Tolyatti.)
- **Subheadline:** «Каркас из алюминия, плетение вручную. Делаем по каталогу и по вашим размерам, доставляем по всей России. Рассрочка 0% до 12 месяцев.»
  (Aluminium frame, hand-woven. From the catalogue or made to your size, delivered across Russia. 0% instalments for up to 12 months.)
  - *Source:* `/onas` (aluminium workshop), `/` (custom projects), `/dostavka`.
  - *Check:* that every frame is aluminium (see C3). If not, say «металлический каркас».
- **Proof strip:** «Гарантия [уточнить: N] · Изготовление от [уточнить: срок] · 3 цеха и склад 650 м² · Доставка ТК ГТА до двери, груз застрахован»
  (Warranty [N] · made in [lead time] · 3 workshops and a 650 m² warehouse · door-to-door delivery by GTA, insured cargo.)
- **CTAs:**
  - Primary: «Подобрать комплект» (Find my set)
  - Secondary: «Смотреть каталог ротанга» / «Смотреть каталог роупа» (Browse the rattan / rope catalogue)

### 5.2 Promo hero (`/promo`)
- **Heading:** «Комплект «Милан 3XL» — подарки к заказу до [уточнить: дата]»
  (The Milan 3XL set: gifts with your order until [date].)
- **Body:** «Трёхместный диван, 2 больших кресла, 3 стандартных кресла и стол из HPL Compact. При заказе до [дата] — подставка под горячее, 2 разделочные доски и укрывной чехол на весь комплект в подарок. Цена комплекта: [уточнить].»
  (Three-seat sofa, 2 large armchairs, 3 standard armchairs and an HPL Compact table. Order by [date] and get a trivet, 2 chopping boards and a cover for the whole set as gifts. Set price: [price].)
- **CTA:** «Узнать цену Милан 3XL с подарками» (Get the Milan 3XL price with gifts). The popup heading should name the offer; currently it says a generic «КОНСУЛЬТАЦИЯ».
- **Second offer:** «Угловая зона «Вольтерра Люкс» 220×340 см: 245 300 ₽ вместо 345 300 ₽ (−29%) до [дата]»
  (Volterra Lux corner zone, 220×340 cm: 245,300 ₽ instead of 345,300 ₽ (−29%) until [date].)
  - Corrected percentage. Remove «на 12 персон» unless verified.
- **Seasonal line:** replace «ЛЕТНИЕ ПРИВИЛЕГИИ» with «Закажите зимой — получите к сезону» (Order in winter, have it by the season), only if lead time allows. Otherwise use a neutral «Предложения [месяц]» (Offers for [month]).

### 5.3 CTA labels

| Now | Proposed | Gloss |
|---|---|---|
| BUY NOW / В корзину | «В заявку» or keep «В корзину» everywhere | Add to request |
| More products | «Другие модели» | Other models |
| Оформить заказ (drawer) | «Перейти к заявке» | Go to request |
| Оформить заказ (form button) | «Отправить заявку — цена ни к чему не обязывает» → short: «Получить расчёт» | Get a quote |
| В корзину on «Цена по запросу» cards | «Узнать цену» | Ask for price |
| УЗНАТЬ ПОДРОБНЕЕ (promo) | name the offer: «Узнать цену Вольтерра Люкс» | |
| Отправить заявку (lead forms) | «Получить консультацию» | Get advice |

### 5.4 Cart and checkout microcopy
- **Drawer title:** «Ваша заявка» (Your request)
- **Under the sum:** «Это предварительный расчёт. Оплаты на сайте нет: менеджер перезвонит в течение [уточнить: время], уточнит цвет, сроки и стоимость доставки.»
  (This is a preliminary estimate. There is no payment on the site: a manager will call you back within [time] to confirm colour, lead time and delivery cost.)
- **Trust line:** «Рассрочка 0% до 12 месяцев · Доставка ТК ГТА до двери, груз застрахован · Гарантия [N]»
  (0% instalments for 12 months · door-to-door delivery by GTA, insured · [N] warranty)
- **Delivery radio help text:**
  - «Доставка до двери по России — стоимость рассчитаем при звонке» (Door delivery across Russia; we quote the cost on the call)
  - «Самовывоз: Тольятти, ул. Туполева, 12А (ТД «Вояж»), по записи» (Pickup in Tolyatti, by appointment)
- **Comment placeholder:** «Цвет плетения и подушек, размеры, удобное время для звонка» (Weave and cushion colour, sizes, best time to call)
- **Button:** «Отправить заявку» (Send request)
- **Success message:** «Заявка принята. Перезвоним в [уточнить] с номера +7 927 200 43 03.» (Request received. We'll call you within [time] from +7 927 200 43 03.)
- **Add-to-cart toast:** «Добавлено в заявку · Открыть» (Added to request · Open)

### 5.5 Product-description template

```
[Тип] «[Модель]» из [искусственного ротанга / роупа] — [для чего: терраса, ресторан…]
Цена: [цена] ₽ [за комплект / за шт.] · [В наличии / Под заказ: изготовление [срок]]
Состав (для комплектов): позиция — размер — цена
Размеры: Д × Ш × В, высота сиденья [уточнить]
Материалы: плетение — …; каркас — [алюминий/сталь], порошковая окраска; подушки — ткань …, чехлы съёмные
Улица и погода: [диапазон из паспорта материала]; влага, солнце
Уход и зимнее хранение: [уточнить]
Нагрузка: [кг на место]
Цвета: плетение — [палитра]; подушки — [уточнить]
Гарантия: [N] — условия (ссылка)
Доставка и оплата: ТК ГТА до двери, груз застрахован; самовывоз Тольятти; рассрочка 0% до 12 мес.
Почему такая цена: ручное плетение, свой цех сварки и окраски, [гарантия]
CTA: «В заявку» · «Задать вопрос мастеру»
```

**Filled for set №60, using only data on the site:**

> **Обеденная группа «Вольтерра Люкс» с угловым диваном и 4 креслами «Палермо»** (арт. К-60)
> 279 100 ₽ за комплект · [уточнить: в наличии / под заказ, срок изготовления]
>
> **Состав**
> — Угловой диван «Вольтерра Люкс», Г-образный, 220 × 280 см, 2 × 3 места + угол — 139 000 ₽
> — Стол «Палермо» с подстольем, 180 × 120 см — 56 900 ₽
> — Кресло «Палермо», 690 × 700 × 860 мм — 4 шт. × 20 800 ₽ = 83 200 ₽
>
> **Материалы.** Плетение — искусственный эко-ротанг, ручная работа. Каркас — алюминий [уточнить: на странице указано и «Металл», и «алюминий»], порошковая окраска. Подушки — ткань Оксфорд, водонепроницаемая, чехлы снимаются для стирки. Диван стоит на пластиковых опорах с анодированной накладкой, ножки кресел — с пластиковыми наконечниками, которые не царапают пол. Столешница — закалённое стекло на вакуумных присосках [уточнить: в составе комплекта стекло или ДПК].
>
> **Улица и погода.** Искусственный ротанг не разбухает от влаги, не выгорает на солнце; рабочий диапазон температур — [уточнить: на сайте указаны −40…+40 и −70…+70].
>
> **Уход.** Плетение легко моется; [уточнить: зимнее хранение — в помещении или под укрывным чехлом (чехол есть в каталоге, 15 000 ₽)].
>
> **Нагрузка.** До 120 кг на одно посадочное место (по условиям гарантии).
>
> **Цвет.** Плетение — на выбор из палитры: Горький шоколад, Белый дуб, Индийское дерево, Бронза, Графит, Дымчатый, Карамель, Снежный, Чёрный дуб, Мокко. Подушки — [уточнить].
>
> **Гарантия** [N] — условия. **Доставка** ТК ГТА до двери в любой город России, груз застрахован; самовывоз — Тольятти. **Оплата:** наличные/СБП, безнал с НДС, рассрочка 0% до 12 месяцев.
>
> [В заявку] [Задать вопрос мастеру]

*Gloss:* the Volterra Lux dining group with a corner sofa and 4 Palermo armchairs. It lists the components with sizes and prices, materials, weather, care, load, colours, warranty, delivery and payment. Every fact comes from the №60, Palermo, Volterra Lux, colour-swatch, `/vozvrat` and `/dostavka` pages.

## 6. Top 5 priorities (copy view)
1. **One warranty term, one temperature range and one lead time.** Publish each on `/vozvrat` and show it on every product card and in the cart. Remove «5 лет», «-70…+70» and «в любую точку мира». (C1, C2, C5, C6)
2. **Remove the junk.** Take out «Error get alias» (234 pages), the «Copy:» items, the Tilda demo products and «BUY NOW» / «More products». (C8)
3. **Make promos honest.** Add dates to every promo, make "was" prices match the catalogue, correct «30%» to 29%, fix the 10 000 ₽ cocoon price, and make sure no discount exceeds the «до 70%» headline. (C6)
4. **Rename sets and add the description template.** Replace the meaningless «№NN» names with descriptive ones, starting with the top 20 sets and all 41 roup items. (C4, C7)
5. **Rewrite the hero and B2B around verifiable facts.** Use the workshop, aluminium, 0% instalments and named HoReCa clients. Drop «Rolls-Royce» and the unsourced «48%». (C9, C10)

## 7. Open questions and data needed
- Real warranty terms per component, and who signs the contract (ИП or ООО).
- The material datasheet: temperature range, UV resistance, and whether all frames are aluminium.
- Lead time for stock items and for made-to-order items, and how stock is tracked.
- The real current Milan 3XL price and the promo end dates. Whether the Комо Люкс 2х sale price of 10 000 ₽ is a typo.
- Whether the `/offer` figures (10 000 units, 60 cities, 1 500 clients, restaurant clients) are current and can be published.
- Whether the colour chosen on a product page is passed into the cart and the request. This needs a live Playwright check.
- The FAQ answer text, which is collapsed and not captured in the corpus.
