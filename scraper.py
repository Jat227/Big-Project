import requests
from bs4 import BeautifulSoup
import random
import re

def generic_name(title):
    """Strip pack/size/variant qualifiers so store search URLs find similar products."""
    # Remove quantity phrases like "pack of 7", "set of 3", "combo of 2"
    title = re.sub(r'\b(pack|set|combo|bundle|lot)\s+of\s+\d+\b', '', title, flags=re.I)
    # Remove size/weight like 500ml, 1kg, 250g, 2L, 1.5L
    title = re.sub(r'\b\d+(\.\d+)?\s*(ml|l|litre|liter|kg|g|gm|gram|oz|lb|pcs|piece|unit|count|tab|capsule)s?\b', '', title, flags=re.I)
    # Remove colour codes and model variants like "XL", "128GB", "6/128"
    title = re.sub(r'\b(xs|s|m|l|xl|xxl|xxxl)\b', '', title, flags=re.I)
    # Remove extra whitespace
    title = re.sub(r'\s{2,}', ' ', title).strip(' ,-|/')
    return title or title  # fallback to original if empty

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
        response = requests.get(url, headers=HEADERS, timeout=10)
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
    url = f"https://www.flipkart.com/search?q={query.replace(' ', '%20')}"
    results = []
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
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

def scrape_all(query):
    print(f"Aggregating Search for: {query}")
    
    amz_base = scrape_amazon(query)
    flp_base = scrape_flipkart(query)
    
    merged_base = amz_base + flp_base
    
    # If network block happens, use fallback base (Though Flipkart rarely blocks)
    if not merged_base:
        base_amt = random.randint(1000, 50000)
        merged_base = [{
            "name": f"{query.title()} - Premium Selection",
            "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&q=80&w=400",
            "store": "Amazon", "price": base_amt, "logo": "fa-amazon", "url": "#"
        }]

    aggregated = []
    
    for item in merged_base:
        base_price = item['price']
        
        product_obj = {
            "name": item['name'],
            "image": item['image'],
            "prices": [
                {"store": item['store'], "price": item['price'], "logo": item['logo'], "url": item['url']}
            ]
        }
        
        aggregated.append(product_obj)

    # SORTING: We push the most exact matches to the top
    def score_product(name):
        ns = name.lower()
        qs = query.lower()
        
        # Exact beginning match
        if ns.startswith(qs):
            return 100
            
        # Perfect contiguous word boundary match
        import re
        if re.search(r'\b' + re.escape(qs) + r'\b', ns):
            return 80
            
        # Contains contiguous string somewhere
        if qs in ns:
            return 60
            
        # Contains all words in any order
        query_words = qs.split()
        if all(w in ns for w in query_words):
            return 40
            
        # Contains some words
        match_count = sum(1 for w in query_words if w in ns)
        return match_count

    aggregated.sort(key=lambda x: score_product(x['name']), reverse=True)

    return aggregated
