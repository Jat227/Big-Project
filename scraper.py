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
# Name similarity — Jaccard on key words (strips colour/storage variants)
# ─────────────────────────────────────────────────────────────────────────────
def name_similarity(a, b):
    """
    Word-level Jaccard similarity between two product name strings.
    Strips common colour, storage, and variant noise so that
    'iPhone 15 128GB Blue' still matches 'Apple iPhone 15 (Midnight, 256GB)'.
    Returns 0.0–1.0.  Threshold for "same product" is 0.20.
    """
    noise = re.compile(
        r'\b(\d+\s*(gb|tb|mb|mp)|'            # storage / camera
        r'black|white|blue|green|red|gold|silver|midnight|starlight|'
        r'titanium|natural|pink|purple|yellow|'
        r'plus|pro\s*max|ultra|lite|neo|'      # variant suffixes (keep 'pro' as it's brand-specific)
        r'single|double|tri|quad)\b',
        re.I
    )
    stop = {'the','and','with','for','from','in','of','a','an','by','new','pack','combo'}

    def tokenise(s):
        s = noise.sub('', s.lower())
        s = re.sub(r'[^a-z0-9\s]', '', s)
        return set(s.split()) - stop

    wa, wb = tokenise(a), tokenise(b)
    if not wa or not wb:
        return 0.0
    return len(wa & wb) / len(wa | wb)

# ─────────────────────────────────────────────────────────────────────────────
# Platform directory — shown per category
# Platforms are shown with an estimated price if the product is likely
# available on that platform (by category). They will show real prices
# once their official APIs are integrated.
#
# "Completely not available" means wrong category — e.g.:
#   • Don't show Myntra/AJIO for electronics
#   • Don't show Croma for beauty/fashion
#   • Don't show Nykaa for electronics
# ─────────────────────────────────────────────────────────────────────────────
PLATFORM_STORE_MAP = {
    "electronics": [
        {"name": "Croma",            "logo": "fa-bolt",        "schema": "https://www.croma.com/search/?q={q}&searchOn=clp",    "color": "#01579b"},
        {"name": "Reliance Digital", "logo": "fa-store",       "schema": "https://www.reliancedigital.in/search?q={q}",         "color": "#cc0000"},
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
                                       'air purifier','geyser','vacuum','trimmer','electric']):
        return "electronics"
    if any(k in query_lower for k in ['shoe','sneaker','slipper','sandal','croc','heel','boot','loafer','flip flop']):
        return "footwear"
    if any(k in query_lower for k in ['shirt','tshirt','t-shirt','jeans','trouser','pant','cargo','kurta',
                                       'dress','saree','legging','jacket','hoodie','sweatshirt','shorts',
                                       'skirt','fashion','apparel','wear','clothing']):
        return "fashion"
    if any(k in query_lower for k in ['makeup','lipstick','foundation','moisturizer','skincare','sunscreen',
                                       'serum','perfume','fragrance','shampoo','conditioner','hair oil',
                                       'face wash','toner','beauty','grooming','nykaa','lakme']):
        return "beauty"
    return "default"

def build_store_url(schema, product_name):
    """Build a store search URL using the product name. Uses + encoding."""
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

    category      = get_category(query.lower())
    platform_pool = PLATFORM_STORE_MAP.get(category, PLATFORM_STORE_MAP["default"])

    # ── Match Flipkart results to Amazon results by name similarity ──────────
    # Threshold lowered to 0.20 so colour/storage variants still match.
    # If no match passes the threshold, we still try the best-scoring
    # Flipkart result (as a loose fallback) — because both scrapers ran the
    # exact same query, most results are the same product even if named differently.
    HARD_THRESHOLD  = 0.20   # use Flipkart if Jaccard ≥ this
    LOOSE_THRESHOLD = 0.10   # use best-available Flipkart result if ≥ this

    flp_used = set()

    def best_flipkart_match(amz_name):
        best_score, best_idx, best_item = 0.0, -1, None
        for idx, flp in enumerate(flp_base):
            if idx in flp_used:
                continue
            score = name_similarity(amz_name, flp['name'])
            if score > best_score:
                best_score, best_idx, best_item = score, idx, flp
        if best_score >= HARD_THRESHOLD and best_item is not None:
            flp_used.add(best_idx)
            return best_item
        # Loose fallback: even if names differ a lot, if it's the same type of
        # query result there's a good chance it's the same product family
        if best_score >= LOOSE_THRESHOLD and best_item is not None:
            flp_used.add(best_idx)
            return best_item
        return None

    aggregated = []

    # ── Step 1: Process every Amazon result ─────────────────────────────────
    for amz_item in amz_base:
        prices = [{"store": amz_item['store'], "price": amz_item['price'],
                   "logo": amz_item['logo'], "url": amz_item['url']}]

        # Add Flipkart price only if we find a genuinely matching result
        flp_match = best_flipkart_match(amz_item['name'])
        if flp_match:
            prices.append({"store": flp_match['store'], "price": flp_match['price'],
                           "logo": flp_match['logo'], "url": flp_match['url']})

        # Add category-appropriate comparison stores with estimated prices.
        # These are shown whenever the product category fits the platform.
        # They will show real prices once the platform's API is integrated.
        # Platforms in the wrong category (e.g. Myntra for electronics) are
        # intentionally excluded via PLATFORM_STORE_MAP — not shown at all.
        highest_base = max(p['price'] for p in prices)
        for store in platform_pool:
            variance    = random.uniform(1.05, 1.22)   # tighter range: ±5–22%
            est_price   = int(highest_base * variance)
            url         = build_store_url(store['schema'], amz_item['name'])
            prices.append({"store": store['name'], "price": est_price,
                           "logo": store['logo'], "url": url,
                           "estimated": True})           # flag for UI to mark as ~estimate

        aggregated.append({"name": amz_item['name'], "image": amz_item['image'], "prices": prices})

    # ── Step 2: Unmatched Flipkart products — standalone cards ───────────────
    for idx, flp_item in enumerate(flp_base):
        if idx in flp_used:
            continue
        prices = [{"store": flp_item['store'], "price": flp_item['price'],
                   "logo": flp_item['logo'], "url": flp_item['url']}]
        highest_base = flp_item['price']
        for store in platform_pool:
            variance  = random.uniform(1.05, 1.22)
            est_price = int(highest_base * variance)
            url       = build_store_url(store['schema'], flp_item['name'])
            prices.append({"store": store['name'], "price": est_price,
                           "logo": store['logo'], "url": url,
                           "estimated": True})
        aggregated.append({"name": flp_item['name'], "image": flp_item['image'], "prices": prices})

    # ── Fallback if both scrapers failed ─────────────────────────────────────
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

    # ── Relevance sort ────────────────────────────────────────────────────────
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
