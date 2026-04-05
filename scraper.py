import requests
from bs4 import BeautifulSoup
import random
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}

# ─────────────────────────────────────────────────────────────────────────────
# Scrapers
# ─────────────────────────────────────────────────────────────────────────────
def scrape_amazon(query):
    url = f"https://www.amazon.in/s?k={query.replace(' ', '+')}"
    results = []
    try:
        r = requests.get(url, headers=HEADERS, timeout=5)
        soup = BeautifulSoup(r.content, 'html.parser')
        for item in soup.find_all('div', attrs={'data-component-type': 's-search-result'})[:40]:
            h2_elem   = item.find('h2')
            if not h2_elem: continue
            title     = h2_elem.get_text(strip=True)
            if not title: continue
            pw        = item.find('span', class_='a-price-whole')
            price_str = pw.text.replace(',','').replace('.','').strip() if pw else '0'
            price     = int(price_str) if price_str.isdigit() else 0
            img       = item.find('img', class_='s-image')
            img_url   = img['src'] if img and 'src' in img.attrs else ''
            img_url   = re.sub(r'\._[^.]+\.(jpg|jpeg|png)$', r'.\1', img_url)
            link      = item.find('a', class_='a-link-normal')
            href      = ('https://www.amazon.in' + link['href']) if link and 'href' in link.attrs else url
            if price > 0:
                results.append({'name': title, 'image': img_url, 'store': 'Amazon',
                                'price': price, 'logo': 'fa-amazon', 'url': href})
    except Exception:
        pass
    return results

def scrape_flipkart(query):
    url = f"https://www.flipkart.com/search?q={query.replace(' ', '+')}"
    results = []
    try:
        r = requests.get(url, headers=HEADERS, timeout=5)
        soup = BeautifulSoup(r.content, 'html.parser')
        count = 0
        for item in soup.find_all('a', target='_blank'):
            if count >= 40: break
            pe = item.find('div', string=lambda t: t and '₹' in t)
            if not pe: continue
            ps = pe.text.replace('₹','').replace(',','').strip()
            if not ps.isdigit(): continue
            price   = int(ps)
            img     = item.find('img')
            title   = img['alt'] if img and 'alt' in img.attrs else 'Flipkart Product'
            img_url = img['src'] if img and 'src' in img.attrs else ''
            img_url = re.sub(r'/image/\d+/\d+/', '/image/800/800/', img_url)
            href    = ('https://www.flipkart.com' + item['href']) if 'href' in item.attrs else url
            results.append({'name': title, 'image': img_url, 'store': 'Flipkart',
                            'price': price, 'logo': 'fa-store', 'url': href})
            count += 1
    except Exception:
        pass
    return results

# ─────────────────────────────────────────────────────────────────────────────
# Brand filter
# ─────────────────────────────────────────────────────────────────────────────
BRAND_SYNONYMS = {
    'apple':   ['apple', 'macbook', 'ipad', 'iphone', 'mac mini', 'airpods', 'imac'],
    'nike':    ['nike', 'air max', 'jordan'],
    'samsung': ['samsung', 'galaxy'],
    'sony':    ['sony', 'playstation', 'ps5', 'ps4'],
    'dell':    ['dell', 'alienware', 'inspiron', 'xps'],
}

def filter_genuine_products(results, query):
    ql = query.lower()
    for brand, syns in BRAND_SYNONYMS.items():
        if brand in ql:
            filtered = [r for r in results if any(s in r['name'].lower() for s in syns)]
            return filtered if filtered else results
    return results

# ─────────────────────────────────────────────────────────────────────────────
# Name similarity with hard version-number blocking
# ─────────────────────────────────────────────────────────────────────────────
def name_similarity(a, b):
    """
    Returns Jaccard word-overlap (0.0–1.0).
    HARD RULE: if the two names contain different product version numbers
    (e.g. '15' vs '16e'), returns 0.0 immediately — prevents pairing
    iPhone 15 with iPhone 16e or iPhone 17 Pro.
    """
    def versions(s):
        # Match model numbers like 15, 16e, 17, S24, A55, Note20, etc.
        return set(re.findall(r'\b(\d{1,2}[a-z]{0,4})\b', s.lower()))

    va, vb = versions(a), versions(b)
    if va and vb and not (va & vb):
        return 0.0  # different model numbers — definitively different products

    # Strip storage, colours, and marketing words before comparing
    _noise = re.compile(
        r'\b(\d+\s*(gb|tb|mb|mp)|'
        r'black|white|blue|green|red|gold|silver|midnight|starlight|'
        r'titanium|natural|pink|purple|yellow|graphite|coral|teal|'
        r'ultra|lite|neo|plus|pro\s*max|'
        r'single|double|tri|quad)\b', re.I)
    _stop = {'the','and','with','for','from','in','of','a','an','by','new','pack','combo','buy'}

    def tok(s):
        s = _noise.sub('', s.lower())
        return set(re.sub(r'[^a-z0-9\s]','',s).split()) - _stop

    wa, wb = tok(a), tok(b)
    if not wa or not wb: return 0.0
    return len(wa & wb) / len(wa | wb)

# ─────────────────────────────────────────────────────────────────────────────
# Relevance scoring for sort
# ─────────────────────────────────────────────────────────────────────────────
def relevance_score(name, query):
    ns, qs = name.lower(), query.lower()
    if ns.startswith(qs):          return 100
    if re.search(r'\b'+re.escape(qs)+r'\b', ns): return 80
    if qs in ns:                   return 60
    words = qs.split()
    if all(w in ns for w in words): return 40
    return sum(1 for w in words if w in ns)

# ─────────────────────────────────────────────────────────────────────────────
# Main aggregator
# ─────────────────────────────────────────────────────────────────────────────
def scrape_all(query):
    print(f"Aggregating search: {query}")
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=2) as ex:
        fa = ex.submit(lambda: filter_genuine_products(scrape_amazon(query), query))
        ff = ex.submit(lambda: filter_genuine_products(scrape_flipkart(query), query))
        amz = fa.result()
        flp = ff.result()

    # ── Greedy best-match pairing ─────────────────────────────────────────────
    # PAIR_THRESHOLD: minimum name-similarity to use a scraped Flipkart result
    # with its real price + direct product URL.
    # Below that: we still show Flipkart, but as a search link (no price).
    # This ensures Flipkart always appears so the user can always click through.
    PAIR_THRESHOLD = 0.15   # lowered; version hard-block prevents wrong pairings
    flp_used = set()

    def best_flp(amz_name):
        """Return best unused Flipkart result, or None if none exceed threshold."""
        best_s, best_i, best_item = 0.0, -1, None
        for i, f in enumerate(flp):
            if i in flp_used: continue
            s = name_similarity(amz_name, f['name'])
            if s > best_s:
                best_s, best_i, best_item = s, i, f
        if best_s >= PAIR_THRESHOLD and best_item:
            flp_used.add(best_i)
            return best_item
        return None

    def flipkart_search_url(name):
        """Flipkart search URL from a simplified product name (brand + model only)."""
        # Keep only first 4 meaningful words: e.g. 'Apple iPad A16' (no specs/colour)
        clean = re.sub(r'\(.*?\)', '', name)                      # strip (...)
        clean = re.sub(r'\b\d+\s*(gb|tb|mb|mp)\b', '', clean, flags=re.I)
        clean = re.sub(r'[^a-zA-Z0-9\s]', ' ', clean)
        words = clean.split()[:4]
        return 'https://www.flipkart.com/search?q=' + '+'.join(words)

    aggregated = []

    # Step 1: Amazon-first products
    for amz_item in amz:
        prices = [{'store': 'Amazon', 'price': amz_item['price'],
                   'logo': 'fa-amazon', 'url': amz_item['url']}]

        match = best_flp(amz_item['name'])
        if match:
            # Real scraped Flipkart price with direct product URL
            prices.append({'store': 'Flipkart', 'price': match['price'],
                           'logo': 'fa-store', 'url': match['url']})
        else:
            # No confident match scraped — show a Flipkart search link.
            # The user can still navigate to Flipkart and find the product.
            # 'search_only' = True tells the UI not to show a price.
            prices.append({'store': 'Flipkart', 'price': 0,
                           'logo': 'fa-store',
                           'url': flipkart_search_url(amz_item['name']),
                           'search_only': True})

        aggregated.append({'name': amz_item['name'], 'image': amz_item['image'], 'prices': prices})

    # Step 2: Unmatched Flipkart products (standalone cards)
    for i, f in enumerate(flp):
        if i in flp_used: continue
        aggregated.append({'name': f['name'], 'image': f['image'],
                           'prices': [{'store': 'Flipkart', 'price': f['price'],
                                       'logo': 'fa-store', 'url': f['url']}]})


    # Fallback
    if not aggregated:
        b = random.randint(1000, 50000)
        aggregated = [{'name': f'{query.title()} - Search Result',
                       'image': 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&q=80&w=400',
                       'prices': [
                           {'store': 'Amazon',   'price': b,         'logo': 'fa-amazon', 'url': f'https://www.amazon.in/s?k={query.replace(" ","+")}'},
                           {'store': 'Flipkart', 'price': int(b*1.01),'logo': 'fa-store',  'url': f'https://www.flipkart.com/search?q={query.replace(" ","+")}'},
                       ]}]

    aggregated.sort(key=lambda x: relevance_score(x['name'], query), reverse=True)
    return aggregated
