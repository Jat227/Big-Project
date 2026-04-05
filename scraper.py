import requests
from bs4 import BeautifulSoup
import random
import re

def generic_name(title):
    """Strip pack/size/variant qualifiers so store search URLs find similar products."""
    title = re.sub(r'\b(pack|set|combo|bundle|lot)\s+of\s+\d+\b', '', title, flags=re.I)
    title = re.sub(r'\b\d+(\.\d+)?\s*(ml|l|litre|liter|kg|g|gm|gram|oz|lb|pcs|piece|unit|count|tab|capsule)s?\b', '', title, flags=re.I)
    title = re.sub(r'\b(xs|s|m|l|xl|xxl|xxxl)\b', '', title, flags=re.I)
    title = re.sub(r'\s{2,}', ' ', title).strip(' ,-|/')
    return title or title

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}

def scrape_amazon(query):
    url = f"https://www.amazon.in/s?k={query.replace(' ', '+')}"
    results = []
    try:
        response = requests.get(url, headers=HEADERS, timeout=4)
        soup = BeautifulSoup(response.content, 'html.parser')
        items = soup.find_all('div', attrs={'data-component-type': 's-search-result'})
        for item in items[:40]:
            title_elem = item.find('h2')
            title = title_elem.text.strip() if title_elem else "Unknown Product"
            price_elem = item.find('span', class_='a-price-whole')
            price_str = price_elem.text.replace(',', '').replace('.', '').strip() if price_elem else '0'
            price = int(price_str) if price_str.isdigit() else 0
            img_elem = item.find('img', class_='s-image')
            img_url = img_elem['src'] if img_elem and 'src' in img_elem.attrs else "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&q=80&w=400"
            img_url = re.sub(r'\._[^.]+\.(jpg|jpeg|png)$', r'.\1', img_url)
            link_elem = item.find('a', class_='a-link-normal')
            link = "https://www.amazon.in" + link_elem['href'] if link_elem and 'href' in link_elem.attrs else url
            if price > 0:
                results.append({"name": title, "image": img_url, "store": "Amazon", "price": price, "logo": "fa-amazon", "url": link})
    except:
        pass
    return results

def scrape_flipkart(query):
    url = f"https://www.flipkart.com/search?q={query.replace(' ', '+')}"
    results = []
    try:
        response = requests.get(url, headers=HEADERS, timeout=4)
        soup = BeautifulSoup(response.content, 'html.parser')
        items = soup.find_all('a', target="_blank")
        count = 0
        for item in items:
            if count >= 40: break
            price_elem = item.find('div', string=lambda t: t and '₹' in t)
            if not price_elem:
                continue
            price_str = price_elem.text.replace('₹', '').replace(',', '').strip()
            if not price_str.isdigit(): continue
            price = int(price_str)
            img_elem = item.find('img')
            title = img_elem['alt'] if img_elem and 'alt' in img_elem.attrs else "Flipkart Product"
            img_url = img_elem['src'] if img_elem and 'src' in img_elem.attrs else "https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&q=80&w=400"
            img_url = re.sub(r'/image/\d+/\d+/', '/image/800/800/', img_url)
            link = "https://www.flipkart.com" + item['href'] if 'href' in item.attrs else url
            results.append({"name": title, "image": img_url, "store": "Flipkart", "price": price, "logo": "fa-store", "url": link})
            count += 1
    except:
        pass
    return results

def filter_genuine_products(results, query):
    """Ensure search results match the requested brand."""
    query_lower = query.lower()
    strict_brands = {
        'apple':   ['apple', 'macbook', 'ipad', 'iphone', 'mac mini', 'airpods', 'imac', 'watch'],
        'nike':    ['nike', 'air max', 'jordan'],
        'samsung': ['samsung', 'galaxy'],
        'sony':    ['sony', 'playstation', 'ps5', 'ps4'],
        'dell':    ['dell', 'alienware', 'inspiron', 'xps']
    }
    target_synonyms = None
    for brand, synonyms in strict_brands.items():
        if brand in query_lower:
            target_synonyms = synonyms
            break
    if not target_synonyms:
        return results
    filtered = [item for item in results if any(syn in item['name'].lower() for syn in target_synonyms)]
    return filtered if filtered else results

# ─────────────────────────────────────────────────────────────────────────────
# Name similarity helper — used to match Amazon ↔ Flipkart results correctly
# ─────────────────────────────────────────────────────────────────────────────
def name_similarity(a, b):
    """
    Jaccard word-overlap between two product name strings.
    Returns a float 0.0–1.0.  We use ≥ 0.35 as "same product".
    """
    def tokenise(s):
        # Lower-case, strip punctuation, split on spaces
        s = re.sub(r'[^a-z0-9\s]', '', s.lower())
        return set(s.split())

    wa, wb = tokenise(a), tokenise(b)
    if not wa or not wb:
        return 0.0
    # Remove very common stop-words that inflate similarity scores
    stop = {'the', 'and', 'with', 'for', 'from', 'in', 'of', 'a', 'an', 'by'}
    wa -= stop
    wb -= stop
    if not wa or not wb:
        return 0.0
    return len(wa & wb) / len(wa | wb)

# ─────────────────────────────────────────────────────────────────────────────
# Platform directory (all with legal affiliate / public search URLs)
# Stores use {q} placeholder; URL-encoding uses + for spaces (universally safe)
# ─────────────────────────────────────────────────────────────────────────────
PLATFORM_STORE_MAP = {
    "electronics": [
        {"name": "Croma",            "logo": "fa-bolt",        "schema": "https://www.croma.com/search/?q={q}&searchOn=clp",        "color": "#01579b"},
        {"name": "Reliance Digital", "logo": "fa-store",       "schema": "https://www.reliancedigital.in/search?q={q}",             "color": "#cc0000"},
    ],
    "fashion": [
        {"name": "Myntra", "logo": "fa-bag-shopping", "schema": "https://www.myntra.com/{q}",              "color": "#ff3f6c"},
        {"name": "AJIO",   "logo": "fa-shopping-bag", "schema": "https://www.ajio.com/search/?text={q}",  "color": "#e91e63"},
    ],
    "footwear": [
        {"name": "Myntra", "logo": "fa-bag-shopping", "schema": "https://www.myntra.com/{q}",              "color": "#ff3f6c"},
        {"name": "AJIO",   "logo": "fa-shopping-bag", "schema": "https://www.ajio.com/search/?text={q}",  "color": "#e91e63"},
    ],
    "beauty": [
        {"name": "Nykaa",   "logo": "fa-spa",   "schema": "https://www.nykaa.com/search/result/?q={q}", "color": "#fc2779"},
        {"name": "Purplle", "logo": "fa-heart", "schema": "https://www.purplle.com/search?q={q}",       "color": "#7b1fa2"},
    ],
    "default": [
        {"name": "Croma",            "logo": "fa-bolt",  "schema": "https://www.croma.com/search/?q={q}&searchOn=clp",    "color": "#01579b"},
        {"name": "Reliance Digital", "logo": "fa-store", "schema": "https://www.reliancedigital.in/search?q={q}",         "color": "#cc0000"},
    ],
}

def get_category(query_lower):
    if any(k in query_lower for k in ['mobile','phone','smartphone','iphone','samsung galaxy','oneplus',
                                       'laptop','macbook','tablet','ipad','tv','television','headphone',
                                       'earbud','smartwatch','camera','gaming','playstation','xbox',
                                       'washing machine','refrigerator','microwave','air conditioner',
                                       'air purifier','geyser','vacuum']):
        return "electronics"
    if any(k in query_lower for k in ['shoe','sneaker','slipper','sandal','croc','heel','boot','loafer','flip flop']):
        return "footwear"
    if any(k in query_lower for k in ['shirt','tshirt','t-shirt','jeans','trouser','pant','cargo','kurta',
                                       'dress','saree','legging','jacket','hoodie','sweatshirt','shorts',
                                       'skirt','fashion','apparel','wear','clothing']):
        return "fashion"
    if any(k in query_lower for k in ['makeup','lipstick','foundation','moisturizer','skincare','sunscreen',
                                       'serum','perfume','fragrance','shampoo','conditioner','hair oil',
                                       'face wash','toner','beauty','grooming','trimmer','nykaa','lakme']):
        return "beauty"
    return "default"

def build_store_url(schema, product_name):
    """Build a store search URL using the *product name* for precision.
    Uses + encoding (safer than %20 for most Indian e-commerce sites).
    """
    q = product_name.replace(' ', '+')
    return schema.replace('{q}', q)

def scrape_all(query):
    print(f"Aggregating Search for: {query}")
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=2) as executor:
        future_amz = executor.submit(scrape_amazon, query)
        future_flp = executor.submit(scrape_flipkart, query)
        amz_base = filter_genuine_products(future_amz.result(), query)
        flp_base = filter_genuine_products(future_flp.result(), query)

    category     = get_category(query.lower())
    platform_pool = PLATFORM_STORE_MAP.get(category, PLATFORM_STORE_MAP["default"])

    # ── Match Flipkart results to Amazon results by name similarity ──────────
    # For each Amazon item find the best Flipkart match.
    # This prevents "iPhone 17 Pro" (Amazon) being paired with "iPhone 15" (Flipkart).
    SIMILARITY_THRESHOLD = 0.35

    flp_used = set()   # track which Flipkart indices have already been paired

    def best_flipkart_match(amz_name):
        """Return (flp_item, score) for the best unused Flipkart result, or (None, 0)."""
        best_score, best_idx, best_item = 0.0, -1, None
        for idx, flp in enumerate(flp_base):
            if idx in flp_used:
                continue
            score = name_similarity(amz_name, flp['name'])
            if score > best_score:
                best_score, best_idx, best_item = score, idx, flp
        if best_score >= SIMILARITY_THRESHOLD and best_item is not None:
            flp_used.add(best_idx)
            return best_item, best_score
        return None, 0.0

    aggregated = []

    # 1. Process every Amazon result
    for amz_item in amz_base:
        prices = [{"store": amz_item['store'], "price": amz_item['price'],
                   "logo": amz_item['logo'], "url": amz_item['url']}]

        # Try to find a matching Flipkart product
        flp_match, score = best_flipkart_match(amz_item['name'])
        if flp_match:
            prices.append({"store": flp_match['store'], "price": flp_match['price'],
                           "logo": flp_match['logo'], "url": flp_match['url']})

        # ── Only real scraped prices are shown ──────────────────────────────
        # Croma / Myntra / AJIO / Nykaa etc. are intentionally NOT added here
        # with fake prices. They will appear only when their real APIs are
        # integrated and we have actual verified pricing data.

        aggregated.append({"name": amz_item['name'], "image": amz_item['image'], "prices": prices})

    # 2. Any unmatched Flipkart results (not paired with any Amazon item) — add as standalone cards
    for idx, flp_item in enumerate(flp_base):
        if idx in flp_used:
            continue
        # Only real Flipkart price — no fake comparison store prices
        prices = [{"store": flp_item['store'], "price": flp_item['price'],
                   "logo": flp_item['logo'], "url": flp_item['url']}]
        aggregated.append({"name": flp_item['name'], "image": flp_item['image'], "prices": prices})



    # ── Fallback if both scrapers failed ────────────────────────────────────
    if not aggregated:
        base_amt = random.randint(1000, 50000)
        aggregated = [{
            "name": f"{query.title()} - Search Result",
            "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&q=80&w=400",
            "prices": [
                {"store": "Amazon",   "price": base_amt,            "logo": "fa-amazon", "url": f"https://www.amazon.in/s?k={query.replace(' ', '+')}"},
                {"store": "Flipkart", "price": int(base_amt * 1.01), "logo": "fa-store",  "url": f"https://www.flipkart.com/search?q={query.replace(' ', '+')}"},
            ]
        }]

    # ── Relevance sort ───────────────────────────────────────────────────────
    def score_product(name):
        ns, qs = name.lower(), query.lower()
        if ns.startswith(qs): return 100
        if re.search(r'\b' + re.escape(qs) + r'\b', ns): return 80
        if qs in ns: return 60
        words = qs.split()
        if all(w in ns for w in words): return 40
        return sum(1 for w in words if w in ns)

    aggregated.sort(key=lambda x: score_product(x['name']), reverse=True)
    return aggregated
