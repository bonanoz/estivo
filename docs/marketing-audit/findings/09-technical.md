# 09: Technical and e-commerce audit of estivo63.ru (Agent 9)

Date: 2026-10-20. Live Tilda site only. The Django repo was not used as evidence.

## 1. What I inspected

- **The full crawl dataset.** `crawl_results.jsonl` has 276 URLs: 42 from sitemap.xml and 234 from sitemap-store.xml. I also used `corpus/*.txt` and `mobile_results.json` (14 key pages, iPhone 13 **emulation**, not a real device).
- **Per-URL table.** `findings/09-crawl.tsv` has one row per URL with these columns: url, status, title, description_len, canonical, h1_count, price, old_price, issues. Prices are parsed from the product-page text.
- **My own live checks** used Python Playwright with Chrome, run sequentially with 1.5 s gaps. Scripts and raw output are in `a09/` (`check.py`, `check2.py`, `check_out.json`, `check2_out.json`). They covered:
  - all 9 internal link targets that appear on crawled pages but are missing from both sitemaps;
  - the 3 robots-disallowed pages;
  - `http://www.estivo63.ru/` (redirect chain and canonical);
  - schema.org microdata on 4 product pages that have no price or demo content;
  - 16 external links (status only);
  - failed requests on `/` and `/kreslo`.
- **Not verified:**
  - Real page weight. Every resource reports a transfer size of 0 because the CDN sends no Timing-Allow-Origin header, so the `kb` fields in `perf` are meaningless.
  - Whether Yandex Metrika works for real visitors.
  - Avito profile pages (Avito returned 429 or timed out for the bot).
  - Search Console or Webmaster data and the indexed-page count.

## 2. Findings

### F1. Tilda demo products are live, indexable and in the sitemap
- **Problem:** 6 template products from Tilda's demo store are published.
- **Location:**
  - `/tproduct/661752667342-dining-chair-by-estebanmoreno` and `/tproduct/897024892502-…` "Dining Chair by esteban+moreno", 79р. (old price 200р.)
  - `/tproduct/498455188682-…` and `/661985197072-underwater-wearable-watches`, 90р.
  - `/tproduct/121969165582-…` and `/322548644472-sac-marin-yellow`, 108р.
- **Evidence:**
  - The body text is the Tilda placeholder ("Add here some interesting details about the product…").
  - The microdata reads `price=79.00 RUB, InStock`.
  - All 6 URLs are listed in sitemap-store.xml.
- **Customer and commercial impact:** Anyone landing on these pages from search sees a broken shop. Search engines may index 79-ruble "chairs" under the ESTIVO brand. This erodes trust in a premium brand.
- **Confidence:** Confirmed.
- **Recommendation:** Delete the products in the Tilda store. Also delete `/tproduct/175447806982-sale-roup`, which is an empty "sale роуп" card with no price or text.
- **Validation:** Check that sitemap-store.xml no longer lists them and that the URLs return 404.
- **Effort:** S

### F2. Broken internal links (404), including the "Цвет ротанга" link on product pages
- **Problem:** Three internal targets return 404 Not Found.
- **Location and evidence** (all checked live):
  - `https://estivo63.ru/ctvetarotang` is linked from 12 pages: `/rotang`, `/page64428687.html`, and product pages such as `/kreslo/tproduct/884701107752-kreslo-terlago-iz-rotanga`, where it sits behind the "Цвет ротанга" label. The real page is `/cvetrotanga` (the typo is "ctveta" vs "cveta").
  - `https://estivo63.ru/stul` is linked from `/rotang` and `/page64428687.html`.
  - `https://estivo63.ru/79272004303` is linked from `/offer`. This is a phone number entered as a relative URL, so a "call" link on the B2B commercial offer page leads to a 404.
- **Customer impact:** A buyer who wants to see colours, chairs, or call from the B2B offer hits a dead end at exactly the point of decision.
- **Commercial impact:** Lost leads from a catalogue of high-ticket items.
- **Confidence:** Confirmed.
- **Recommendation:**
  - Point the colour links to `/cvetrotanga`.
  - Point `/stul` to `/kresloroup`, or create the page.
  - Change the `/offer` link to `tel:+79272004303`.
- **Validation:** Re-run `a09/check.py`.
- **Effort:** S

### F3. Duplicate, template and junk pages in sitemap.xml
- **Problem:** Of the 42 sitemap pages, at least 8 are duplicates or work leftovers.
- **Evidence:**
  - `/page212667309.html` has text, title and description byte-identical to `/` and a self-canonical, so it is a full duplicate of the home page.
  - Three "Copy of Плетеная мебель из ротанга и роупа ручной работы для дома и бизнеса" pages exist: `/page69400427.html`, `/page74937106.html`, `/page125687636.html`. Their text overlaps `/` by 78–88 % (difflib quick ratio).
  - `/page87158106.html` "Copy of политика конфиденциальности" contains Tilda filler: "Book design is the art of…", "Zero Block", "Click "Block Editor" to enter the edit mode".
  - `/policy02` is identical to `/policy`.
  - `/page68304349.html` is titled "Blank page" and duplicates the contacts block.
  - `/page60195393.html` "Отзывы Эстиво" contains no reviews. Its text is 99 % identical to the blank page (footer only).
  - `/page155943176.html` "Главная страница" is a 463-character stub: "Shop", a list of "Перейти", 2 images both without alt.
  - None of these pages is linked from any other crawled page; the only links to them are self-links.
- **Customer and commercial impact:** These pages split ranking signals with the real home page and can show up in search as "Copy of…" or empty pages. The empty "Отзывы" page actively damages trust if it is found.
- **Confidence:** Confirmed.
- **Recommendation:** Unpublish them, or set noindex and remove them from the sitemap. If they must stay, set their canonical to `/`.
- **Validation:** Re-fetch sitemap.xml.
- **Effort:** S

### F4. www and non-www both serve the site; there is no host redirect
- **Evidence:** `http://www.estivo63.ru/` redirects to `https://www.estivo63.ru/` with status 200 and no move to `estivo63.ru`. http→https works.
- **Mitigation:** The www page has `<link rel=canonical href="https://estivo63.ru/">`. Product and section pages carry self-canonicals on the main host.
- **Impact:** Low. The canonical tag consolidates signals, but links and ads can still split across hosts.
- **Confidence:** Confirmed (one navigation plus one canonical read).
- **Recommendation:** Add a 301 from www to the bare domain in the Tilda domain settings. Set the main mirror in Yandex Webmaster.
- **Effort:** S

### F5. Product microdata reports price 0 for "price on request" items, and there is no JSON-LD anywhere
- **Evidence:**
  - All 234 product pages have Tilda microdata (Product/Offer with price, priceCurrency, availability).
  - Live check: "Цена по запросу" items publish `price=0 RUB, InStock`. These include `/komplekty/tproduct/827181619422-komplekt-mebeli-iz-stropi` and `/onas/tproduct/644560710182-komplekt-iz-rotanga`.
  - `/uglovyedivany/tproduct/425279570482-…volterra-lyuks…` has empty lowPrice/highPrice plus about 20 offers at `price=0`.
  - On the item side: 21 product pages show no price at all, and 5 have the meta description "Цена по запросу".
  - The site has 0 JSON-LD blocks, 0 BreadcrumbList and 0 Organization/LocalBusiness markup on any of the 276 pages.
- **Impact:** Search engines may show "0 ₽" in rich results, or reject the offers as invalid. There is no local-business entity (address, phone, opening hours) for Yandex or Google.
- **Confidence:** Confirmed for the markup itself. The effect on search snippets is a **well-supported hypothesis**.
- **Recommendation:**
  - Give the 0-price items a real "from" price, or remove their Offer.
  - Add Organization/LocalBusiness JSON-LD to the header or footer (Tulupova 12A, phone, hours) and BreadcrumbList to sections.
- **Effort:** S–M

### F6. Sale prices conflict with catalogue prices for the same product
- **Problem:** The same product name appears in both a catalogue section and a sale section with prices that do not agree. 14 names are duplicated across sections or within one section.
- **Evidence** (prices parsed from the corpus):

| Product | Catalogue | Sale section |
|---|---|---|
| Комплект мебели из роупа 5 | /komplektyroup **119 700** | /saleroup **226 900** (old 346 200) |
| Комплект мебели из роупа 17 | /komplektyroup **226 600** | /saleroup **345 000** (old 542 600) |
| Комплект мебели из роупа 2 | /komplektyroup 224 600 | /saleroup old price 121 500 |
| Комплект мебели из роупа 4 | /komplektyroup 360 200 | /saleroup old price 332 300 |
| Комплект мебели из роупа 1 | /komplektyroup 166 500 | /saleroup old price 134 800 |
| Комплект мебели из роупа 3 | /komplektyroup 121 500 | /saleroup old price 145 500 |
| Кокон «Комо Люкс 2х» | /kreslopodves 79 900 | /salerotang **10 000** (old 79 900), −87 %, a possible typo |
| Юбка для ёлки воздушная/цилиндр | /aksessuary 5 200 | /price 6 200 |

  - Different products share one name: "Комплект мебели из ротанга 32", "6" and "58" each appear twice in /salerotang with different prices. "Этажерка Лофт с HPL" appears twice in /price (39 000, and 26 000 with old price 39 000).
  - Consistent pairs exist too: роупа 15/16, Комо, №19.
- **Customer impact:**
  - In two cases the "sale" price is higher than the regular catalogue price.
  - The "old" price does not match the catalogue price, which makes the discount look invented.
  - Under ZoZPP/FAS practice, a fictitious old price is a misleading-advertising risk (**preliminary assumption**; get legal review).
- **Confidence:** Confirmed that the site displays these prices. Which price is correct is unknown.
- **Recommendation:** Keep one product record per item and show its sale price through Tilda's old-price field rather than a cloned card. Give each set a unique name.
- **Validation:** Re-run `a09/analyze.py -v` (the "SAME NAME MULTI-SECTION" section).
- **Effort:** M

### F7. "Error get alias" on every product page, plus untranslated or typo template labels
- **Evidence:**
  - The raw text "Error get alias" is rendered once on each of the 234 product pages (234/234, counted in the corpus).
  - The 30 /price products and 11 /cvetrotanga swatch products show the English Tilda labels "More products" and "BUY NOW" (41 pages).
  - The typo "Цвет ронагта" appears on `/onas/tproduct/…` cards.
  - Two titles start with "Copy:": `/price/tproduct/501161551833-copy-kreslo-bari-l-roup` and `/tproduct/685095834682-copy-komplekt-mebeli-iz-rotang-25`.
  - "Комплект мебели из ротанг NN" (wrong case) appears in several titles.
- **Impact:** The pages read as broken on every product view and undercut the premium positioning.
- **Confidence:** Confirmed.
- **Recommendation:**
  - Find the store or product block with the broken alias. It is most likely a product-card setting that links to a missing page; that is a **hypothesis**.
  - Translate the button labels in the store block settings and fix the titles.
- **Effort:** S

### F8. Metadata and headings are missing almost everywhere
- **Evidence:**
  - Only 4 of 42 sitemap pages have a meta description and an H1 (`/`, `/rotang`, `/roup`, plus the duplicate `/page212667309.html`). `/onas` has a description but no H1.
  - Key commercial pages have neither a description nor an H1: `/komplekty`, `/kreslo`, `/salerotang`, `/price`, `/dostavka`, `/kontakty`, `/b2b`, `/promo`.
  - Generic or odd titles: "B2B", "Диваны", "Аксессуары", "Блог", "Blank page", "Главная страница", "политика конфиденциальности02", "Комплекты роуп".
  - Only 15 of 234 product pages have a meta description, and 5 of those are just "Цена по запросу". Every product page has exactly 1 H1.
  - og:image is missing on 40 of 42 sitemap pages, including `/`. Only `/promo` and `/page155943176.html` have one.
- **Impact:** Search engines write their own snippets for most pages, and links shared in messengers show no preview image (**well-supported hypothesis**).
- **Confidence:** Confirmed.
- **Recommendation:** Write a title, description, H1 and og:image for the about 25 real section pages first, then templated descriptions for products.
- **Effort:** M

### F9. Images and media
- **Evidence:**
  - 267 of 276 pages have images without alt text. Catalogue pages report only 1 `<img>` because Tilda cards use CSS backgrounds, so product images in lists carry no alt at all.
  - The home page and `/roup` load .mp4 videos from `www.dl.dropboxusercontent.com`. In my run these requests ended `ERR_ABORTED` and `/roup` reached the load event only after 5.3 s in the crawl.
  - The home page also pulls in the Avito reviews widget (smartwidgets.ru plus 6 Avito image hosts). In my second run `res.smartwidgets.ru/app.js` timed out, and the home page's DOMContentLoaded took 22.4 s (load 27.1 s). In the crawl run, DCL was 0.5 s and the load event had not fired after about 5.5 s.
- **Impact:** Dropbox is not a CDN. A third-party widget that hangs can delay first render, which the second run showed.
- **Confidence:**
  - Confirmed: the requests, failures and timings observed from this machine.
  - **Preliminary assumption:** that visitors see the same delay.
- **Recommendation:** Host the videos on Tilda or Kinescope/Rutube and load the widget async, or replace it with static Avito review screenshots and a link.
- **Validation:** Run Lighthouse or PageSpeed from a Russian location.
- **Effort:** S–M

### F10. Yandex Metrika tag.js fails to load from this test machine on every page
- **Evidence:**
  - The console shows `net::ERR_CONNECTION_CLOSED` for `https://mc.yandex.ru/metrika/tag.js` on 151 of 276 crawled pages and on both of my live runs.
  - No mc.yandex.ru response was received.
  - `window.ym` exists, but it is the inline stub.
  - No other analytics is present: no gtag, no VK/Top@Mail.ru pixel, no fbq.
- **Impact:** If this also happens for real visitors, there is no traffic or conversion data at all.
- **Confidence:** **Preliminary assumption.** It is most likely a local network block. The site cannot be judged from this alone.
- **Recommendation:** Check in Metrika that visits arrive and that goals exist for form submissions and the cart "Оформить заказ". Consider adding a VK Ads pixel.
- **Effort:** S

### F11. Content outside the sitemap; robots.txt check
- **Evidence:**
  - All 6 blog posts under `/news/tpost/…` return 200, have the meta robots "index, follow" and contain about 7–8.6k characters each. None is in any sitemap; they are reachable only from `/news`. All 6 are dated 10.09.2026, and their titles stuff in "Тольятти".
  - `/promo` is in sitemap.xml and indexable (no robots meta, self-canonical), but it is linked only from itself. No other page links to it.
  - The robots.txt-disallowed pages `/page54267073.html` ("footer"), `/page54720871.html` ("header") and `/page54768443.html` ("подвал для товара") are Tilda service pages. They return 200 and are not linked from any crawled page. No problem there.
  - `/offer` links to a staging mirror at `project10482059.tilda.ws` (`/rotang` returns 200).
- **Impact:**
  - The blog gets slower discovery.
  - The staging mirror risks duplicate-content indexing if it is not closed (**hypothesis**: I did not check its robots).
  - The promo landing page gets no internal traffic.
- **Confidence:** Confirmed.
- **Recommendation:**
  - Make sure Tilda generates a blog sitemap, or submit the posts in Yandex Webmaster.
  - Link `/promo` from the home page and the sale sections if it is meant for organic visitors; otherwise noindex it as an ads-only landing page.
  - Replace the tilda.ws links and close the project subdomain.
- **Effort:** S

### F12. Mobile layout (iPhone 13 emulation, 14 key pages)
- **Evidence:**
  - `/rotang` overflows horizontally: the layout viewport is 415 px against the device's 390 px.
  - On desktop, `/` and the 4 home duplicates have scrollWidth 1460 at a 1440 px viewport, so there is a 20 px horizontal scroll.
  - Links or buttons smaller than 32 px: 34–79 per page (`/rotang` 79, `/price` 72, `/` 65, `/komplektyroup` 60, `/promo` 54).
  - The first-screen element list starts with the hidden menu items, so this metric is noisy. The counts include off-canvas menu links.
- **Confidence:** Confirmed for the overflow. The tap-target count is rough.
- **Recommendation:** Find the oversized block on `/rotang` and `/` (Zero Block elements past the grid) and enlarge footer and menu tap areas.
- **Effort:** S

### F13. External links
- **Reachable:**
  - t.me/+7zVfVsf1abszODYy (200)
  - vk.com/estivo_tlt (200)
  - wa.me/79272004303 and wa.me/79178246722 (200; the second is the /promo number, a different one)
  - pin.it, which redirects to ru.pinterest.com/ESTIVO63 (200)
  - both disk.yandex.ru files (200)
  - Google Drive with `?usp=drivesdk` (200; the variant without the parameter timed out)
  - instagram.com/estivo.tlt (200 from this machine)
- **Inconclusive:** both Avito profiles (429 rate-limit, and a timeout).
- **Also found:** `tel:` and `mailto:` links on the site are well-formed; my first pass reported a double "tel:tel:" prefix, but that came from my own script.
- **Confidence:** Confirmed as stated.

## 3. Top 5 priorities

1. **Remove demo, junk and copy pages.** These are the 6 demo products, the "sale роуп" stub, and the 8 copy/blank/placeholder/empty-review pages listed in F1 and F3. Effort is S and it has the biggest trust payoff.
2. **Fix the 3 broken links.** `/ctvetarotang` from the "Цвет ротанга" link on product pages, `/stul`, and the call link on `/offer` (F2).
3. **Make sale and catalogue prices agree** and stop cloning products into sale sections (F6). This is both a trust issue and a legal one.
4. **Remove "Error get alias" and the English "BUY NOW / More products" labels** on 234 and 41 product pages, and fix the `price=0` microdata (F5, F7).
5. **Write titles, descriptions, H1s and og:image for the section pages, and add Organization/LocalBusiness and BreadcrumbList JSON-LD** (F5, F8). Then confirm that Metrika actually records visits and goals (F10).

## 4. Open questions and data needed

- **Metrika:** access to the counter, to check that visits arrive and that goals exist for forms and the cart.
- **Webmaster data:** Yandex Webmaster and Google Search Console exports showing indexed pages, whether the "Copy of"/demo pages and the tilda.ws mirror are indexed, and the chosen main mirror.
- **Prices:** which prices are authoritative for the sets listed in F6.
- **Real-user performance:** CrUX or PageSpeed data from Russia. The crawl's transfer sizes are 0 because of cross-origin resources, so page weight is unmeasured.
- **Legal entity:** whether the site belongs to ИП Мелихова М.С. (ИНН 632147606449, the footer on all pages) or ООО "Эстиво" (/promo). See also findings/02, F2.
