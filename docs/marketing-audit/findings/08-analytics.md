# 08 — Analytics implementation and acquisition fit (Agent 8)

Audit date: 2026-10-20. Live Tilda site https://estivo63.ru only. No forms were submitted and no orders placed.
I had no access to Yandex Metrika, Yandex Direct, Tilda leads, a CRM or the order book, so this file contains **no traffic, conversion or revenue numbers**. Everything below comes from page source, browser network logs and window objects.
Confidence labels: **Confirmed** (I observed it), **Well-supported hypothesis**, **Preliminary assumption**.

## 1. What I inspected

| What | How |
|---|---|
| `trackers`, `third_party_hosts`, `tracker_hits`, `console` for all 42 non-product pages | `crawl_results.jsonl` |
| Saved HTML of `/` and `/promo` (`page_.html`, `page_promo.html`) | Metrika snippet, Tilda stat snippet, cookie banner (T657) |
| **Run 1** (`agent08/track.py` → `agent08/run1.json`): `/`, `/promo?utm_source=test&utm_campaign=test&utm_medium=cpc&yclid=123`, `/komplekty`, `/komplekty/tproduct/126951985332-komplekt-mebeli-iz-rotanga-30` | Real Chrome through Playwright. Logged every request, hooked `dataLayer.push` and `ym()`, probed `ym`, `Ya`, `dataLayer`, `gtag`, `ga`, `google_tag_manager`, `_tmr`, `VK`, `fbq`, `tildastat`, cookies and localStorage. Opened the `/promo` popup (`#popup:myform`) and read every form input. Added items to the cart from the catalogue and the PDP. |
| **Run 2** (`agent08/track2.py` → `agent08/run2.json`) | Same flows, but with the real Metrika `tag.js` (see F1). Every Metrika hit was logged and then **aborted**, so nothing reached the client's counter. |
| Tilda library code: `static.tildacdn.com/js/tilda-forms-1.0.min.js`, `tilda-cart-1.1.min.js` (saved in `agent08/vendor/`) | Read the UTM-cookie logic and the add-to-cart event logic |
| Titles, descriptions and H1s of all 276 URLs | `crawl_results.jsonl` |
| WebSearch for the four target queries, "estivo63.ru", "Эстиво"; WebFetch on the Telegram and VK links from the footer | Acquisition fit |

**Could not access:**
- A real Yandex SERP or Yandex Direct ads. `ya.ru` times out from this machine, and Yandex shows bot checks, which I may not bypass. The WebSearch tool is a US engine, not Yandex. Its results are a weak proxy, and absence there proves nothing.
- vk.com: WebFetch is refused.
- The Telegram channel's posts: the channel is private (invite link).
- Any back-office data: Metrika, Direct, Tilda Leads, CRM, order book.
- Real form submission and checkout submission: not done, per the brief.

## 2. Findings

### F1. Metrika 93915751 is correctly installed, but `mc.yandex.ru` is unreachable from this audit machine. This is a local network issue, not a site fault.
- **Location:** every page, footer `<!-- Yandex.Metrika counter 93915751 -->`.
- **Evidence (Confirmed):**
  - The snippet is `ym(window.mainMetrikaId,"init",{clickmap:true,trackLinks:true,accurateTrackBounce:true,webvisor:true,…,ecommerce:"dataLayer"})`. It is wrapped in `setTimeout(…,2000)`, so it loads 2 s after page start. There is a `<noscript>` pixel `mc.yandex.ru/watch/93915751`.
  - Tilda's own stat script (`tilda-stat-1.0.min.js` → POST `stat.tildaapi.com/event/`) fires on every page.
  - No other analytics or ad tags exist: `gtag`, `ga`, `google_tag_manager`, `_tmr` (VK/Mail.ru Top), `VK` pixel and `fbq` are all undefined. `dataLayer` exists only as the Metrika e-commerce container; there is no GTM.
  - Run 1: `tag.js` failed on every page (`ERR_CONNECTION_CLOSED`, `ERR_CONNECTION_TIMED_OUT`). Three direct retries outside the page also failed (two timeouts, one "socket disconnected before TLS"). From the same machine, `mc.yandex.com` and `mc.webvisor.org` failed TLS and `ya.ru` timed out, but `mc.yandex.by/metrika/tag.js` returned 200 (223 KB). So Yandex hosts are blocked selectively on this network.
  - Run 2 served that same `tag.js` in place of the blocked one. The counter initialised (`Ya._metrika.counters` was present), `_ym_uid` and `_ym_d` cookies were set, and pageview hits to `/watch/93915751` were generated for `/`, `/komplekty`, the PDP and `/promo` (with UTMs and yclid in `page-url`).
- **Customer impact:** none.
- **Commercial impact:** none if visitors in Russia can reach `mc.yandex.ru`. **Well-supported hypothesis:** they can, because the failure is specific to this machine's network.
- **Recommendation:** treat the orchestrator's `ERR_CONNECTION_CLOSED` as an artefact of the audit environment. Confirm in Metrika → Settings → counter status, "Проверить счётчик".
- **Validation:** Metrika "Посещаемость" today shows non-zero visits; open `estivo63.ru/?_ym_debug=1` from a normal Russian connection.
- **Effort:** S.

### F2. Add-to-cart is not measured at all: no e-commerce "add", no goal and no virtual pageview.
- **Location:** "В корзину" on catalogue cards (`/komplekty`) and on the PDP.
- **Evidence (Confirmed):**
  - In both runs, adding to the cart grew localStorage `tcart` (0→1 item on the PDP, 1→2 items on the catalogue). Yet **zero** `dataLayer.push`, zero `ym()` calls and zero Metrika hits followed, even with the real `tag.js` loaded.
  - The cause is in `tilda-cart-1.1.min.js`: `if(tcart__addProduct(Y),"y"==window.tcart_sendevent_onadd) try{Tilda.sendEcommerceEvent("add",[Y])}…`. The page HTML never sets `tcart_sendevent_onadd` (0 occurrences in `page_.html` and `page_promo.html`).
  - What does fire: a PDP view pushes `{"event":"viewProduct","ecommerce":{"detail":{"products":[{"name":"Комплект мебели из ротанга «№30»","price":"231300.0000",…}]}}}` and `ym(93915751,"hit","/tilda/product/detail/126951985332/",{params:{order_price:231300,currency:"RUB"}})`.
  - Opening the `/promo` popup "КОНСУЛЬТАЦИЯ" fired nothing.
- **Customer impact:** none directly.
- **Commercial impact:** the funnel has a hole between "viewed product" and "submitted cart/lead". The owner cannot see cart abandonment, which products get carted, or whether the missing cart feedback on the PDP (orchestrator note) loses people. Metrika's e-commerce reports will show views and (Well-supported hypothesis) purchases from the cart form, but no "add" step.
- **Recommendation:** enable "send add-to-cart events" in Tilda (Site settings → Analytics / e-commerce; it sets `tcart_sendevent_onadd='y'`). Create Metrika goals for: cart add (`/tilda/cart/add/*` or the e-commerce add), cart opened, checkout form submitted, popup form submitted, and clicks on `tel:`, `wa.me` and `t.me`.
- **Validation:** repeat run 2 and expect a `dataLayer` push with `ecommerce.add`. Check that the goal counts appear in Metrika within 24 h.
- **Effort:** S.

### F3. UTM tags are not stored. Leads that start on an ad landing page and finish elsewhere lose their source.
- **Location:** `/promo?utm_…` → any other page → cart or form.
- **Evidence (Confirmed):**
  - After loading `/promo?utm_source=test&utm_medium=cpc&utm_campaign=test&yclid=123`, waiting 9 s, opening the popup and typing a name, no `TILDAUTM` cookie existed.
  - The only hidden form inputs are `formservices[]` ×2, `tildaspec-phone-part[]-iso` and `Phone`. There is no UTM field.
  - Cause in `tilda-forms-1.0.min.js`: the cookie is written only `if(r.length>0&&(!window.tildastatcookie||"no"!=window.tildastatcookie))`, and every page sets `window.tildastatcookie='no'`.
  - At submit, Tilda adds `tildaspec-referer: window.location.href` and `tildaspec-cookie: document.cookie`.
  - So: a lead sent **from the same /promo URL** will carry the UTMs in the referer (Well-supported hypothesis; not submitted). A visitor who clicks "Популярные позиции" → `/komplekty` → cart checkout will arrive with a referer of `/komplekty` and no UTM (Well-supported hypothesis).
  - Metrika itself still attributes the *visit* to the UTM, because the hit carries it.
- **Customer impact:** none.
- **Commercial impact:** in Tilda Leads, email and Telegram notifications and any CRM, ad-driven orders look "direct". The owner cannot compute cost per lead per campaign. This is the single biggest blocker to judging whether /promo or Direct pays off.
- **Recommendation:**
  - Turn off the "do not save cookies" setting that produces `tildastatcookie='no'`, with consent wording updated (see F6), so `TILDAUTM` persists for 30 days.
  - Alternatively, add hidden fields for utm_source, utm_medium, utm_campaign, utm_term and yclid, filled from the first-touch URL that sessionStorage holds.
  - Pass `_ym_uid` (ClientID) with each lead, so Metrika offline conversions or the CRM can link leads back to visits.
- **Validation:** load `/promo?utm_source=x`, go to `/komplekty`, then check `document.cookie` contains `TILDAUTM`. Send one internal test lead and check Tilda Leads shows the UTMs.
- **Effort:** S–M.

### F4. Calls and messenger contacts are probably the main conversion, but they are not tracked and three different phone numbers are in circulation.
- **Location:** header/footer `+7 927 200 43 03` and `wa.me/79272004303`; `/promo` `+7(917)824-67-22` (one `wa.me/79178246722` link); Telegram channel description `8-9272-689-404`.
- **Evidence (Confirmed):**
  - No call-tracking script (Calltouch, CoMagic, Mango, Yandex call tracking) appears in any request or window object.
  - Footer links on every page go to `t.me/+7zVfVsf1abszODYy` (channel "ESTIVO |Плетеная мебель| Роуп |Ротанг|", 276 subscribers per t.me), `vk.com/estivo_tlt`, Instagram, WhatsApp and Avito profiles.
  - Metrika `trackLinks:true` records outbound clicks. Whether goals exist for them is unknown (no Metrika access).
  - **Preliminary assumption:** the `/promo` number is an ad-specific or static call-tracking number. If it is, that is good practice, but it contradicts the site number and is unlabelled.
- **Customer impact:** a visitor who sees different numbers on the ad page and the main site may doubt they are the same company.
- **Commercial impact:** for a premium, high-ticket, appointment-only product, phone and WhatsApp are likely where deals start (Preliminary assumption). Without goals or call tracking, channel ROI is invisible.
- **Recommendation:** create JavaScript or click goals in Metrika for `tel:`, `wa.me`, `t.me` and `vk.com`. Decide which numbers are official. If the /promo number exists for tracking, keep it deliberately and log calls to it by source. Consider Yandex Metrika call tracking (paid).
- **Validation:** after one week, goal reports show non-zero messenger and phone clicks per source. Manager call logs match the number shown on each landing page.
- **Effort:** S (goals); M (call tracking).

### F5. Search acquisition fit is weak: metadata misses the commercial and local queries, and ESTIVO did not appear in any external search I could run.
- **Location:** site-wide metadata.
- **Evidence (Confirmed, from the crawl):**
  - Only **5 of 42** non-product pages have a meta description (`/`, `/rotang`, `/roup`, `/onas`, `/page212667309.html`). Only **4 of 42** have an H1 (`/`, `/rotang`, `/roup`, `/page212667309.html`).
  - Product pages: **15 of 234** have a description. All 234 have an H1.
  - "Тольятти" appears in title/description/H1 only on `/onas`. "Самара" appears **nowhere**, and "купить" only on `/rotang` and `/roup`.
  - Category titles are bare, for example "Кресла из ротанга", "Диваны", "B2B" and "Доставка и оплата". They carry no commercial modifier, no city and no "ручной работы / производитель".
  - Against the target queries:
    - "мебель из ротанга купить": only `/rotang` ("Плетёная мебель из ротанга на заказ | Купить мебель из натурального ротанга") targets it.
    - "мебель из роупа": `/roup` ("Мебель из роупа ручной работы | Купить мебель из роупа для дома и сада").
    - "садовая мебель Тольятти" and "плетёная мебель Самара": **no page targets these**.
  - Duplicates that dilute the home page: `/page212667309.html` repeats the home title and description, with a self-canonical. Three "Copy of Плетеная мебель из ротанга и роупа…" pages (`/page69400427.html`, `/page74937106.html`, `/page125687636.html`) and `/page68304349.html` "Blank page" sit in the sitemap. Tilda demo products ("Dining Chair by esteban+moreno", "Underwater wearable watches", "Sac Marin Yellow", 2 copies each under `/tproduct/`) return 200.
  - WebSearch (US engine, not Yandex) for the four queries returned aggregators: vseinstrumenti.ru, productcenter.ru, 2gis.ru, sostav.ru ratings, SMK-ROTANG mentions, "Карусель Удачи". It returned **no ESTIVO result**, and nothing at all for `"estivo63.ru"` or "Эстиво". **This does not show ESTIVO's Yandex ranking**: I could not open the Yandex SERP or see Direct ads.
- **Customer impact:** searchers in Tolyatti and Samara for "садовая/плетёная мебель" get no local landing page.
- **Commercial impact (Well-supported hypothesis):** organic acquisition is limited to brand and "ротанг/роуп" head terms. Local intent, which drives showroom visits, is not captured.
- **Recommendation:**
  - Write titles and descriptions for every category in the form "{Категория} из ротанга — купить в Тольятти и Самаре | ESTIVO, ручная работа".
  - Add H1s on category pages.
  - Build one local landing page, "Плетёная / садовая мебель в Тольятти и Самаре", with the showroom address and delivery.
  - Unpublish or noindex the Copy/Blank/demo pages and `/page212667309.html`.
  - Add the business to Yandex Business (Справочник).
- **Validation:** Yandex Webmaster → "Поисковые запросы" and "Страницы в поиске" before and after, plus position tracking for the four queries.
- **Effort:** M.

### F6. Webvisor and Metrika load before any consent, and the privacy policy does not mention cookies or Metrika.
- **Location:** cookie banner T657 on every page; `/policy`.
- **Evidence (Confirmed):**
  - The banner reads "Мы используем файлы cookie для обеспечения наилучшего взаимодействия с сайтом." and has a single "ХОРОШО" button. It is informational only.
  - In run 2, Metrika initialised and set `_ym_uid` without any click on the banner.
  - `webvisor:true` records sessions, including what users type into forms (Metrika masks some fields by default).
  - `/policy` (18 k characters) contains no "cookie", "Метрик" or "Яндекс".
  - The script carries `data-tilda-cookie-type="analytics"`, so Tilda's consent integration could gate it, but it is not doing so here.
- **Customer impact:** low visible impact.
- **Commercial impact (Preliminary assumption, not legal advice):** this is a compliance exposure under 152-FZ practice regarding cookies and analytics identifiers. It also connects to F3: re-enabling Tilda cookies for UTM storage should come with policy wording.
- **Recommendation:** add the cookies, Yandex Metrika and Webvisor to the privacy policy. Consider Tilda's consent mode with an "analytics" category. Have a lawyer confirm.
- **Validation:** legal review; recheck that `_ym_uid` behaviour matches the chosen consent mode.
- **Effort:** S.

### F7. /promo is an indexable, generic page whose message does not match a dated campaign. I found no ad or post that it pairs with.
- **Location:** https://estivo63.ru/promo.
- **Evidence (Confirmed):**
  - The page has no `robots` meta, and its canonical is `https://estivo63.ru/promo` (self). It is listed in `sitemap.xml`. Title "Плетёная мебель ручной работы"; no meta description; no H1.
  - The copy is seasonal and undated: "ЛЕТНИЕ ПРИВИЛЕГИИ", "АКЦИЯ МЕСЯЦА". The warranty and phone differ from the main site (orchestrator note and F4).
  - Every offer CTA opens one generic "КОНСУЛЬТАЦИЯ" popup. Its form `form1050461511` has no hidden field naming the offer, so managers cannot tell which promotion produced a lead (Confirmed from the inputs list).
  - I could not see VK posts (blocked) or the private Telegram channel's posts. WebSearch found no ad or post linking to `/promo`. **I cannot say which campaign, if any, drives traffic here.**
- **Customer impact:** an organic visitor in October lands on a "summer" offer with a different phone and warranty.
- **Commercial impact:** if /promo is the Direct landing page, its results cannot be attributed per offer (F3 + generic popup). If it is not used for ads, it is an orphan page that competes with the home page in search.
- **Recommendation:**
  - If /promo serves ads: set it to `noindex`, remove it from the sitemap, date the offer, and use one popup (or a hidden field) per offer.
  - If it does not: unpublish it or redirect it.
- **Validation:** Metrika → Sources for `/promo` (utm_source and yclid share). Direct → the landing page each ad points to.
- **Effort:** S.

## 3. Top 5 priorities (analytics and acquisition)
1. **F3**: make UTMs, yclid and ClientID survive into every lead (cookie or hidden fields). Without it no channel ROI is possible.
2. **F2 + F4**: enable the cart "add" event and create Metrika goals for cart add, checkout submit, popup submit, `tel:`, `wa.me` and `t.me`. Decide the phone-number policy.
3. **F7**: decide what /promo is for (noindex and date it if it is an ad page), and give each offer its own form or hidden field.
4. **F5**: commercial and local metadata (Tolyatti, Samara, "купить") on categories, one local landing page, and removal of Copy/Blank/demo pages.
5. **F6**: privacy policy and consent covering Metrika and Webvisor, done together with the cookie change in F3.

## 4. Open questions and the access needed

| Question | Access / data needed |
|---|---|
| Real traffic by source, the share of Direct and SEO, bounce and depth on /promo | Yandex Metrika 93915751 (guest access is enough) |
| Which goals exist; are form or cart submissions configured as goals; is e-commerce "purchase" arriving | Metrika → Goals, E-commerce report |
| Is Yandex Direct running; which landing pages, keywords and budget; CPC and CPL | Yandex Direct account (read-only) |
| Organic queries and positions; indexed pages; are the Copy/demo pages indexed | Yandex Webmaster |
| How many leads per form, popup, cart and source; do UTMs appear in leads | Tilda → Leads (Заявки) export |
| Lead→sale conversion, average order value, sales cycle | CRM (amoCRM/Bitrix24, if any) or the order book / manager spreadsheet |
| Calls and WhatsApp volumes per number (+7 927 200 43 03, +7 917 824 67 22, 8 927 268 94 04) | Telephony/call logs; purpose of each number |
| What VK, Telegram and Avito posts link to the site, and with what tags | Admin access or exports for VK `estivo_tlt` and the Telegram channel; Avito Pro stats |
| Real Yandex SERP and Direct ads for the four queries | Manual check from a Russian IP, or Wordstat plus a position tracker (Topvisor etc.) |

Scripts and raw outputs: `scratchpad/agent08/track.py`, `track2.py`, `hook.js`, `run1.json`, `run2.json`, `vendor/`.
