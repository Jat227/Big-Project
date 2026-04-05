document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('searchInput');
    const searchBtn   = document.getElementById('searchBtn');
    const loadingState    = document.getElementById('loadingState');
    const resultsContainer = document.getElementById('resultsContainer');
    const queryText   = document.getElementById('queryText');
    const productGrid = document.getElementById('productGrid');
    const landingPage = document.getElementById('landingPage');

    const categoryList    = document.getElementById('categoryList');
    const filtersContainer = document.getElementById('filtersContainer');
    const mainLayout      = document.getElementById('mainLayout');

    // Mobile sidebar toggle
    const sidebar        = document.getElementById('sidebar');
    const sidebarOverlay = document.getElementById('sidebarOverlay');
    const filterToggleBtn = document.getElementById('filterToggleBtn');

    if (filterToggleBtn) {
        filterToggleBtn.addEventListener('click', () => {
            sidebar.classList.add('open');
            sidebarOverlay.classList.add('active');
        });
    }
    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', () => {
            sidebar.classList.remove('open');
            sidebarOverlay.classList.remove('active');
        });
    }

    // ── Support notice dismiss ──────────────────────────────────────────────
    const supportNotice = document.getElementById('supportNotice');
    const supportClose  = document.getElementById('supportNoticeClose');
    if (supportClose && supportNotice) {
        // Restore dismissed state from session
        if (sessionStorage.getItem('supportDismissed')) supportNotice.style.display = 'none';
        supportClose.addEventListener('click', () => {
            supportNotice.style.display = 'none';
            sessionStorage.setItem('supportDismissed', '1');
        });
    }

    // ── Sale Alert Ticker (all with direct sale/deals page URLs) ────────────
    const SALE_ALERTS = [
        // Amazon
        { icon: 'fa-bolt',    platform: 'Amazon',           color: '#ff9f00', text: 'Up to 40% OFF on Smartphones — Today Only!',      url: 'https://www.amazon.in/deals' },
        { icon: 'fa-fire',    platform: 'Amazon',           color: '#ff9f00', text: 'Apple iPhone 15 — Limited Stock Deal!',            url: 'https://www.amazon.in/s?k=iphone+15&deals-widget=%7B%22version%22%3A1%7D' },
        { icon: 'fa-percent', platform: 'Amazon',           color: '#ff9f00', text: 'Prime Deal: Smart TVs from ₹7,999',               url: 'https://www.amazon.in/deals?deals-widget=%7B%22version%22%3A1%2C%22browseNodeId%22%3A1389396031%7D' },
        { icon: 'fa-tag',     platform: 'Amazon',           color: '#ff9f00', text: 'Laptops & Accessories — Extra Bank Discounts',      url: 'https://www.amazon.in/s?k=laptops&deals-widget=%7B%22version%22%3A1%7D' },
        // Flipkart
        { icon: 'fa-tag',     platform: 'Flipkart',         color: '#2874f0', text: 'Big Saving Days — Electronics up to 60% OFF',      url: 'https://www.flipkart.com/offers-list/big-saving-days' },
        { icon: 'fa-percent', platform: 'Flipkart',         color: '#2874f0', text: 'Fashion Sale — Min 50% OFF on Top Brands',         url: 'https://www.flipkart.com/clothing-and-accessories' },
        { icon: 'fa-bolt',    platform: 'Flipkart',         color: '#2874f0', text: 'Home Appliance Fest — Up to 45% OFF',              url: 'https://www.flipkart.com/offers-list/home-appliances-deals' },
        { icon: 'fa-fire',    platform: 'Flipkart',         color: '#2874f0', text: 'Beauty Products — Up to 35% OFF',                  url: 'https://www.flipkart.com/beauty-and-personal-care' },
        // Croma
        { icon: 'fa-bolt',    platform: 'Croma',            color: '#01579b', text: 'Electronics Sale — Up to 30% OFF on Laptops & TVs', url: 'https://www.croma.com/offers' },
        { icon: 'fa-percent', platform: 'Croma',            color: '#01579b', text: 'Mobiles — Best Prices + Exchange Offers',          url: 'https://www.croma.com/mobile-phones' },
        // Reliance Digital
        { icon: 'fa-store',   platform: 'Reliance Digital', color: '#cc0000', text: 'Weekend Sale — Smart ACs & Refrigerators on Offer', url: 'https://www.reliancedigital.in/offers' },
        // Myntra
        { icon: 'fa-bag-shopping', platform: 'Myntra',      color: '#ff3f6c', text: 'End of Reason Sale — Fashion up to 80% OFF',       url: 'https://www.myntra.com/myntra-big-fashion-festival' },
        { icon: 'fa-tag',    platform: 'Myntra',            color: '#ff3f6c', text: 'Nike & Adidas — Exclusive Offers on Footwear',      url: 'https://www.myntra.com/sport-shoes' },
        // AJIO
        { icon: 'fa-shopping-bag', platform: 'AJIO',        color: '#e91e63', text: 'Grand Orange Sale — Up to 85% OFF on Fashion',     url: 'https://www.ajio.com/s/deal-of-the-day-8521541' },
        { icon: 'fa-percent', platform: 'AJIO',             color: '#e91e63', text: 'Trending Styles — New Arrivals Every Day',          url: 'https://www.ajio.com/new-arrivals' },
        // Nykaa
        { icon: 'fa-spa',     platform: 'Nykaa',            color: '#fc2779', text: 'Nykaa Beauty Carnival — Up to 50% OFF',            url: 'https://www.nykaa.com/offers/beauty-offers' },
        { icon: 'fa-heart',   platform: 'Nykaa',            color: '#fc2779', text: 'Skincare & Makeup — Top Brands at Best Prices',     url: 'https://www.nykaa.com/offers' },
    ];

    const buildSaleAlerts = () => {
        const track = document.getElementById('saleAlertTrack');
        if (!track) return;
        const items = [...SALE_ALERTS, ...SALE_ALERTS]; // duplicate for seamless loop
        track.innerHTML = items.map(a => `
            <a class="sale-alert-item" href="${a.url}" target="_blank" rel="noopener" title="Go to ${a.platform} sale">
                <i class="fa-solid ${a.icon}"></i>
                <span class="platform-tag" style="background:${a.color}55;">${a.platform}</span>
                ${a.text}
            </a>
        `).join('');
    };
    buildSaleAlerts();


    // ── Trending Products (static curated — will be dynamic with real API) ──
    const TRENDING_DATA = [
        {
            name: '📱 Trending Mobiles',
            icon: 'fa-mobile-screen',
            search: 'Smartphones',
            products: [
                { name: 'Apple iPhone 15 128GB', price: '₹69,999', badge: 'Best Seller', img: 'https://m.media-amazon.com/images/I/61bK6PMOC3L._AC_SY450_.jpg', url: "/api/search?q=iPhone+15" },
                { name: 'Samsung Galaxy S24 256GB', price: '₹74,999', badge: 'Trending', img: 'https://m.media-amazon.com/images/I/71Sa3dqTqzL._AC_SY450_.jpg', url: "/api/search?q=Samsung+Galaxy+S24" },
                { name: 'OnePlus 12 256GB', price: '₹64,999', badge: 'Hot Deal', img: 'https://m.media-amazon.com/images/I/71RrMLGTtBL._AC_SY450_.jpg', url: "/api/search?q=OnePlus+12" },
                { name: 'Xiaomi Redmi Note 13 Pro', price: '₹24,999', badge: 'Value Pick', img: 'https://m.media-amazon.com/images/I/61bK6PMOC3L._AC_SY450_.jpg', url: "/api/search?q=Redmi+Note+13+Pro" },
                { name: 'Google Pixel 8a', price: '₹52,999', badge: 'New Launch', img: 'https://m.media-amazon.com/images/I/71Sa3dqTqzL._AC_SY450_.jpg', url: "/api/search?q=Google+Pixel+8a" },
                { name: 'Vivo V30 Pro 256GB', price: '₹39,999', badge: 'Popular', img: 'https://m.media-amazon.com/images/I/71RrMLGTtBL._AC_SY450_.jpg', url: "/api/search?q=Vivo+V30+Pro" },
            ]
        },
        {
            name: '💻 Top Electronics',
            icon: 'fa-laptop',
            search: 'Laptops',
            products: [
                { name: 'Apple MacBook Air M2 13"', price: '₹1,09,900', badge: 'Best Seller', img: 'https://m.media-amazon.com/images/I/71f5Eu5lJSL._AC_SY450_.jpg', url: "/api/search?q=MacBook+Air+M2" },
                { name: 'Sony WH-1000XM5 Headphones', price: '₹26,990', badge: 'Editor\'s Choice', img: 'https://m.media-amazon.com/images/I/61Lh0sRzerL._AC_SY450_.jpg', url: "/api/search?q=Sony+WH1000XM5" },
                { name: 'Samsung 65" 4K Smart TV', price: '₹69,990', badge: 'Trending', img: 'https://m.media-amazon.com/images/I/71f5Eu5lJSL._AC_SY450_.jpg', url: "/api/search?q=Samsung+65+4K+TV" },
                { name: 'HP Pavilion 15 Core i5', price: '₹54,999', badge: 'Popular', img: 'https://m.media-amazon.com/images/I/61Lh0sRzerL._AC_SY450_.jpg', url: "/api/search?q=HP+Pavilion+15" },
                { name: 'Apple Watch Series 9', price: '₹41,900', badge: 'Hot Pick', img: 'https://m.media-amazon.com/images/I/71f5Eu5lJSL._AC_SY450_.jpg', url: "/api/search?q=Apple+Watch+Series+9" },
                { name: 'Canon EOS R50 Camera', price: '₹65,995', badge: 'New', img: 'https://m.media-amazon.com/images/I/61Lh0sRzerL._AC_SY450_.jpg', url: "/api/search?q=Canon+EOS+R50" },
            ]
        },
        {
            name: '👟 Fashion & Footwear',
            icon: 'fa-shirt',
            search: 'Fashion Clothing',
            products: [
                { name: 'Nike Air Max 270', price: '₹9,595', badge: 'Best Seller', img: 'https://m.media-amazon.com/images/I/71Ix-A5KVXL._AC_UX695_.jpg', url: "/api/search?q=Nike+Air+Max+270" },
                { name: 'Adidas Ultraboost 22', price: '₹14,999', badge: 'Trending', img: 'https://m.media-amazon.com/images/I/71Ix-A5KVXL._AC_UX695_.jpg', url: "/api/search?q=Adidas+Ultraboost+22" },
                { name: 'Levi\'s 511 Slim Fit Jeans', price: '₹2,999', badge: 'Popular', img: 'https://m.media-amazon.com/images/I/71Ix-A5KVXL._AC_UX695_.jpg', url: "/api/search?q=Levis+511+Jeans" },
                { name: 'Puma Men\'s Sports T-Shirt', price: '₹799', badge: 'Value', img: 'https://m.media-amazon.com/images/I/71Ix-A5KVXL._AC_UX695_.jpg', url: "/api/search?q=Puma+Sports+Tshirt" },
                { name: 'H&M Women\'s Floral Dress', price: '₹1,499', badge: 'Trending', img: 'https://m.media-amazon.com/images/I/71Ix-A5KVXL._AC_UX695_.jpg', url: "/api/search?q=HM+Floral+Dress" },
                { name: 'Crocs Classic Clog', price: '₹3,399', badge: 'Hot', img: 'https://m.media-amazon.com/images/I/71Ix-A5KVXL._AC_UX695_.jpg', url: "/api/search?q=Crocs+Classic+Clog" },
            ]
        },
        {
            name: '🛒 Home Appliances',
            icon: 'fa-blender',
            search: 'Home Appliances',
            products: [
                { name: 'LG 260L 3-Star Refrigerator', price: '₹29,990', badge: 'Best Seller', img: 'https://m.media-amazon.com/images/I/51c1O9XTSJL._AC_SY450_.jpg', url: "/api/search?q=LG+260L+Refrigerator" },
                { name: 'Samsung 7kg Washing Machine', price: '₹22,490', badge: 'Popular', img: 'https://m.media-amazon.com/images/I/51c1O9XTSJL._AC_SY450_.jpg', url: "/api/search?q=Samsung+7kg+Washing+Machine" },
                { name: 'Daikin 1.5 Ton 5-Star AC', price: '₹44,990', badge: 'Top Rated', img: 'https://m.media-amazon.com/images/I/51c1O9XTSJL._AC_SY450_.jpg', url: "/api/search?q=Daikin+1.5+Ton+AC" },
                { name: 'IFB 25L Microwave Oven', price: '₹9,490', badge: 'Trending', img: 'https://m.media-amazon.com/images/I/51c1O9XTSJL._AC_SY450_.jpg', url: "/api/search?q=IFB+Microwave+Oven" },
                { name: 'Dyson V15 Detect Vacuum', price: '₹52,900', badge: 'Premium', img: 'https://m.media-amazon.com/images/I/51c1O9XTSJL._AC_SY450_.jpg', url: "/api/search?q=Dyson+V15+Vacuum" },
                { name: 'Philips Air Purifier AC1215', price: '₹12,995', badge: 'Best Air', img: 'https://m.media-amazon.com/images/I/51c1O9XTSJL._AC_SY450_.jpg', url: "/api/search?q=Philips+Air+Purifier" },
            ]
        },
        {
            name: '💄 Beauty & Grooming',
            icon: 'fa-spray-can',
            search: 'Beauty Products',
            products: [
                { name: 'L\'Oreal Paris Revitalift Serum', price: '₹849', badge: 'Best Seller', img: 'https://m.media-amazon.com/images/I/71hDmf4WZLL._AC_SY450_.jpg', url: "/api/search?q=LOreal+Revitalift+Serum" },
                { name: 'Maybelline Fit Me Foundation', price: '₹449', badge: 'Trending', img: 'https://m.media-amazon.com/images/I/71hDmf4WZLL._AC_SY450_.jpg', url: "/api/search?q=Maybelline+Fit+Me+Foundation" },
                { name: 'Lakme 9-to-5 Primer', price: '₹349', badge: 'Popular', img: 'https://m.media-amazon.com/images/I/71hDmf4WZLL._AC_SY450_.jpg', url: "/api/search?q=Lakme+9to5+Primer" },
                { name: 'Dove Deep Moisture Body Lotion', price: '₹299', badge: 'Value', img: 'https://m.media-amazon.com/images/I/71hDmf4WZLL._AC_SY450_.jpg', url: "/api/search?q=Dove+Body+Lotion" },
                { name: 'Philips QT4001 Trimmer', price: '₹999', badge: 'Best Grooming', img: 'https://m.media-amazon.com/images/I/71hDmf4WZLL._AC_SY450_.jpg', url: "/api/search?q=Philips+Trimmer" },
                { name: 'Biotique Bio Morning Nectare SPF', price: '₹199', badge: 'Daily', img: 'https://m.media-amazon.com/images/I/71hDmf4WZLL._AC_SY450_.jpg', url: "/api/search?q=Biotique+Sunscreen" },
            ]
        },
    ];

    const renderTrendingSections = () => {
        const container = document.getElementById('trendingSections');
        if (!container) return;
        container.innerHTML = TRENDING_DATA.map(section => `
            <div class="trending-section">
                <div class="trending-section-header">
                    <h2><i class="fa-solid ${section.icon}"></i> ${section.name}</h2>
                    <a data-search="${section.search}">See All <i class="fa-solid fa-chevron-right"></i></a>
                </div>
                <div class="trending-row">
                    ${section.products.map(p => `
                        <div class="mini-card" data-search="${p.name}">
                            <div class="mini-card-img" style="background-image:url('${p.img}')"></div>
                            <div class="mini-card-info">
                                <div class="mini-card-badge">${p.badge}</div>
                                <div class="mini-card-name">${p.name}</div>
                                <div class="mini-card-price">${p.price}</div>
                                <div class="mini-card-stores">Amazon &amp; Flipkart</div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `).join('');

        // Wire up clicks on mini cards to search
        container.querySelectorAll('.mini-card').forEach(card => {
            card.addEventListener('click', () => {
                const q = card.getAttribute('data-search');
                searchInput.value = q;
                performSearch();
            });
        });

        // Wire up "See All" links
        container.querySelectorAll('[data-search]').forEach(a => {
            if (a.tagName === 'A') {
                a.addEventListener('click', () => {
                    searchInput.value = a.getAttribute('data-search');
                    performSearch();
                });
            }
        });
    };
    renderTrendingSections();

    window.currentProducts = [];

    // eCommerce Categories with deep, per-category filter schemas
    const CATEGORIES = [
        {
            name: "Mobiles & Tablets",
            search: "Smartphones",
            icon: "fa-mobile-screen",
            sub: [
                { name: "Apple iPhone", search: "iPhone" },
                { name: "Samsung Galaxy", search: "Samsung Mobile" },
                { name: "OnePlus", search: "OnePlus Mobile" },
                { name: "Vivo / Oppo", search: "Vivo Mobile" },
                { name: "Tablets", search: "Tablet" }
            ],
            filters: [
                { type: "price", label: "Price Range", options: [
                    { label: "Under ₹10k", value: "under_10000" },
                    { label: "₹10k – ₹30k", value: "10k_30k" },
                    { label: "₹30k – ₹60k", value: "30k_60k" },
                    { label: "Over ₹60k", value: "over_60k" }
                ]},
                { type: "keyword", label: "Brand", options: [
                    { label: "Apple", value: "apple" },
                    { label: "Samsung", value: "samsung" },
                    { label: "OnePlus", value: "oneplus" },
                    { label: "Xiaomi", value: "xiaomi" },
                    { label: "Realme", value: "realme" }
                ]},
                { type: "suffix", label: "RAM", options: [
                    { label: "4 GB RAM", value: "4GB RAM" },
                    { label: "8 GB RAM", value: "8GB RAM" },
                    { label: "12 GB RAM", value: "12GB RAM" }
                ]},
                { type: "suffix", label: "Storage", options: [
                    { label: "64 GB", value: "64GB" },
                    { label: "128 GB", value: "128GB" },
                    { label: "256 GB", value: "256GB" },
                    { label: "512 GB", value: "512GB" }
                ]},
                { type: "keyword", label: "Color", options: [
                    { label: "Black", value: "black" },
                    { label: "White", value: "white" },
                    { label: "Blue", value: "blue" },
                    { label: "Gold", value: "gold" }
                ]}
            ]
        },
        {
            name: "Electronics",
            search: "Electronics",
            icon: "fa-laptop",
            sub: [
                { name: "Laptops & MacBooks", search: "Laptop" },
                { name: "Smartwatches", search: "Smartwatch" },
                { name: "Headphones & Earbuds", search: "Headphones" },
                { name: "Cameras", search: "Digital Camera" },
                { name: "Gaming Consoles", search: "PlayStation" }
            ],
            filters: [
                { type: "price", label: "Price Range", options: [
                    { label: "Under ₹5k", value: "under_5000" },
                    { label: "₹5k – ₹30k", value: "5k_30k" },
                    { label: "₹30k – ₹80k", value: "30k_80k" },
                    { label: "Over ₹80k", value: "over_80k" }
                ]},
                { type: "keyword", label: "Brand", options: [
                    { label: "Apple", value: "apple" },
                    { label: "Samsung", value: "samsung" },
                    { label: "Sony", value: "sony" },
                    { label: "Dell", value: "dell" },
                    { label: "HP", value: "hp" },
                    { label: "Bose", value: "bose" }
                ]},
                { type: "suffix", label: "Storage", options: [
                    { label: "256 GB SSD", value: "256GB SSD" },
                    { label: "512 GB SSD", value: "512GB SSD" },
                    { label: "1 TB SSD", value: "1TB SSD" }
                ]},
                { type: "suffix", label: "RAM", options: [
                    { label: "8 GB RAM", value: "8GB RAM" },
                    { label: "16 GB RAM", value: "16GB RAM" },
                    { label: "32 GB RAM", value: "32GB RAM" }
                ]}
            ]
        },
        {
            name: "Fashion & Apparel",
            search: "Fashion Clothing",
            icon: "fa-shirt",
            sub: [
                { name: "Men's T-Shirts", search: "Men T-Shirt" },
                { name: "Men's Jeans", search: "Men Jeans" },
                { name: "Men's Shoes", search: "Men Shoes" },
                { name: "Men's Cargos", search: "Men Cargo Pants" },
                { name: "Women's Dresses", search: "Women Dresses" },
                { name: "Women's Kurta", search: "Women Kurta" },
                { name: "Women's Shoes", search: "Women Shoes" },
                { name: "Sports Shoes", search: "Sports Shoes" }
            ],
            filters: [
                { type: "price", label: "Price Range", options: [
                    { label: "Under ₹500", value: "under_500" },
                    { label: "₹500 – ₹2k", value: "500_2k" },
                    { label: "₹2k – ₹5k", value: "2k_5k" },
                    { label: "Over ₹5k", value: "over_5k" }
                ]},
                { type: "keyword", label: "Brand", options: [
                    { label: "Nike", value: "nike" },
                    { label: "Adidas", value: "adidas" },
                    { label: "Puma", value: "puma" },
                    { label: "Zara", value: "zara" },
                    { label: "H&M", value: "h&m" },
                    { label: "Levis", value: "levi" }
                ]},
                { type: "suffix", label: "Type / Style", options: [
                    { label: "Slim Fit", value: "slim fit" },
                    { label: "Regular Fit", value: "regular fit" },
                    { label: "Baggy / Loose", value: "baggy" },
                    { label: "Boot Cut", value: "bootcut" },
                    { label: "Skinny", value: "skinny" },
                    { label: "Cargo", value: "cargo" },
                    { label: "Sports / Running", value: "running" },
                    { label: "Formal", value: "formal" },
                    { label: "Casual", value: "casual" }
                ]},
                { type: "keyword", label: "Color", options: [
                    { label: "Black", value: "black" },
                    { label: "White", value: "white" },
                    { label: "Blue", value: "blue" },
                    { label: "Grey", value: "grey" }
                ]}
            ]
        },
        {
            name: "Footwear",
            search: "Shoes",
            icon: "fa-shoe-prints",
            sub: [
                { name: "Sports / Running", search: "Sports Running Shoes" },
                { name: "Formal Shoes", search: "Formal Leather Shoes" },
                { name: "Casual Sneakers", search: "Casual Sneakers" },
                { name: "Slippers & Flip-Flops", search: "Slippers Flip Flops" },
                { name: "Crocs & Clogs", search: "Crocs clogs" },
                { name: "Heels & Wedges", search: "Women Heels" },
                { name: "Sandals", search: "Sandals" }
            ],
            filters: [
                { type: "price", label: "Price Range", options: [
                    { label: "Under ₹1k", value: "under_1000" },
                    { label: "₹1k – ₹5k", value: "1k_5k" },
                    { label: "₹5k – ₹15k", value: "5k_15k" },
                    { label: "Over ₹15k", value: "over_15k" }
                ]},
                { type: "keyword", label: "Brand", options: [
                    { label: "Nike", value: "nike" },
                    { label: "Adidas", value: "adidas" },
                    { label: "Puma", value: "puma" },
                    { label: "Crocs", value: "crocs" },
                    { label: "Bata", value: "bata" },
                    { label: "Woodland", value: "woodland" }
                ]},
                { type: "suffix", label: "Type", options: [
                    { label: "Sports / Running", value: "running" },
                    { label: "Formal", value: "formal" },
                    { label: "Casual", value: "casual" },
                    { label: "Slippers", value: "slipper" },
                    { label: "Flip Flops", value: "flip flop" },
                    { label: "Crocs", value: "croc" },
                    { label: "Heels", value: "heel" }
                ]},
                { type: "suffix", label: "Size (UK)", options: [
                    { label: "UK 6", value: "uk 6" },
                    { label: "UK 7", value: "uk 7" },
                    { label: "UK 8", value: "uk 8" },
                    { label: "UK 9", value: "uk 9" },
                    { label: "UK 10", value: "uk 10" }
                ]},
                { type: "keyword", label: "Color", options: [
                    { label: "Black", value: "black" },
                    { label: "White", value: "white" },
                    { label: "Red", value: "red" },
                    { label: "Blue", value: "blue" }
                ]}
            ]
        },
        {
            name: "Home Appliances",
            search: "Home Appliances",
            icon: "fa-blender",
            sub: [
                { name: "Refrigerators", search: "Refrigerator" },
                { name: "Washing Machines", search: "Washing Machine" },
                { name: "Microwave Ovens", search: "Microwave Oven" },
                { name: "Air Conditioners", search: "Air Conditioner" },
                { name: "Air Purifiers", search: "Air Purifier" }
            ],
            filters: [
                { type: "price", label: "Price Range", options: [
                    { label: "Under ₹10k", value: "under_10000" },
                    { label: "₹10k – ₹30k", value: "10k_30k" },
                    { label: "₹30k – ₹60k", value: "30k_60k" },
                    { label: "Over ₹60k", value: "over_60k" }
                ]},
                { type: "keyword", label: "Brand", options: [
                    { label: "Samsung", value: "samsung" },
                    { label: "LG", value: "lg" },
                    { label: "Whirlpool", value: "whirlpool" },
                    { label: "Voltas", value: "voltas" },
                    { label: "IFB", value: "ifb" }
                ]},
                { type: "suffix", label: "Capacity", options: [
                    { label: "1 Ton", value: "1 ton" },
                    { label: "1.5 Ton", value: "1.5 ton" },
                    { label: "200 Litre", value: "200L" },
                    { label: "300 Litre", value: "300L" }
                ]}
            ]
        },
        {
            name: "Beauty & Grooming",
            search: "Beauty Products",
            icon: "fa-spray-can",
            sub: [
                { name: "Makeup & Cosmetics", search: "Makeup" },
                { name: "Skincare", search: "Skincare" },
                { name: "Fragrances & Perfumes", search: "Perfume" },
                { name: "Hair Care", search: "Hair Care" },
                { name: "Grooming Kits", search: "Grooming Kit" }
            ],
            filters: [
                { type: "price", label: "Price Range", options: [
                    { label: "Under ₹500", value: "under_500" },
                    { label: "₹500 – ₹2k", value: "500_2k" },
                    { label: "Over ₹2k", value: "over_2k" }
                ]},
                { type: "keyword", label: "Brand", options: [
                    { label: "MAC", value: "mac" },
                    { label: "Lakme", value: "lakme" },
                    { label: "Maybelline", value: "maybelline" },
                    { label: "L'Oreal", value: "loreal" },
                    { label: "Nykaa", value: "nykaa" }
                ]},
                { type: "suffix", label: "Category", options: [
                    { label: "Lipstick", value: "lipstick" },
                    { label: "Foundation", value: "foundation" },
                    { label: "Moisturizer", value: "moisturizer" },
                    { label: "Sunscreen", value: "sunscreen" },
                    { label: "Serum", value: "serum" }
                ]}
            ]
        },
        {
            name: "Toys & Games",
            search: "Toys Kids Games",
            icon: "fa-puzzle-piece",
            sub: [
                { name: "Board Games", search: "Board Games" },
                { name: "Action Figures", search: "Action Figures" },
                { name: "Building Blocks", search: "LEGO Building Blocks" },
                { name: "Remote Control", search: "RC Remote Control Toy" },
                { name: "Puzzles", search: "Puzzle Jigsaw" }
            ],
            filters: [
                { type: "price", label: "Price Range", options: [
                    { label: "Under ₹500", value: "under_500" },
                    { label: "₹500 – ₹2k", value: "500_2k" },
                    { label: "Over ₹2k", value: "over_2k" }
                ]},
                { type: "keyword", label: "Age Group", options: [
                    { label: "0–2 Years", value: "infant" },
                    { label: "3–5 Years", value: "toddler" },
                    { label: "6–12 Years", value: "kids" },
                    { label: "Teens+", value: "teen" }
                ]}
            ]
        }
    ];

    // Track active category filters
    window.activeCategoryFilters = null;

    // Build Categories UI (horizontal top-nav)
    // Since .sub-cat-list uses position:fixed, we must set top/left via JS on hover
    const renderCategories = () => {
        categoryList.innerHTML = '';
        CATEGORIES.forEach(cat => {
            const li = document.createElement('li');
            li.className = 'cat-item-container';
            li.innerHTML = `
                <div class="cat-item-top">
                    <span><i class="fa-solid ${cat.icon}" style="margin-right:6px;"></i>${cat.name}</span>
                    <i class="fa-solid fa-chevron-down" style="font-size:0.75rem;margin-left:6px;"></i>
                </div>
                <ul class="sub-cat-list">
                    <li class="sub-item" data-search="${cat.search}">See All in ${cat.name}</li>
                    ${cat.sub.map(s => `<li class="sub-item" data-search="${s.search}">${s.name}</li>`).join('')}
                </ul>
            `;

            // Position the fixed dropdown under the trigger
            const trigger = li.querySelector('.cat-item-top');
            const subList = li.querySelector('.sub-cat-list');
            const positionDropdown = () => {
                const rect = trigger.getBoundingClientRect();
                subList.style.top  = (rect.bottom + 4) + 'px';
                subList.style.left = rect.left + 'px';
            };
            li.addEventListener('mouseenter', positionDropdown);

            const subItems = li.querySelectorAll('.sub-item');
            subItems.forEach(subItem => {
                subItem.addEventListener('click', (e) => {
                    e.stopPropagation();
                    document.querySelectorAll('.sub-item').forEach(el => el.classList.remove('active'));
                    subItem.classList.add('active');
                    const query = subItem.getAttribute('data-search');
                    searchInput.value = query;
                    window.activeCategoryFilters = cat.filters;
                    performSearch();
                });
            });

            categoryList.appendChild(li);
        });
    };
    
    // Build per-category filters from the schema
    const buildFilters = (filterSchema) => {
        filtersContainer.innerHTML = '';
        if (!filterSchema || filterSchema.length === 0) return;

        filterSchema.forEach(group => {
            const div = document.createElement('div');
            div.className = 'filter-group';
            const opts = group.options.map(opt =>
                `<label class="filter-option"><input type="checkbox" name="${group.type}" data-value="${opt.value}"> ${opt.label}</label>`
            ).join('');
            div.innerHTML = `<h4>${group.label}</h4>${opts}`;
            filtersContainer.appendChild(div);
        });

        // Wireup: every checkbox triggers a re-search with updated suffix
        filtersContainer.querySelectorAll('input[type="checkbox"]').forEach(box => {
            box.addEventListener('change', () => applyFilters());
        });
    };

    // Collect checked filter values, build suffix, then re-fetch from backend
    const applyFilters = () => {
        const baseQuery = searchInput.value.trim();
        if (!baseQuery) return;

        // Collect suffix-type selections (RAM, Storage, Type, Size, Category)
        const suffixes = Array.from(filtersContainer.querySelectorAll('input[name="suffix"]:checked'))
            .map(b => b.getAttribute('data-value'));
        
        // Collect keyword-type selections (Brand, Color)
        const keywords = Array.from(filtersContainer.querySelectorAll('input[name="keyword"]:checked'))
            .map(b => b.getAttribute('data-value'));

        // Re-run backend search with refined query (brand + spec terms appended)
        const extras = [...keywords, ...suffixes];
        const refinedQuery = extras.length > 0 ? `${baseQuery} ${extras.join(' ')}` : baseQuery;

        // Price filter is applied locally after fetch
        const priceBoxes = Array.from(filtersContainer.querySelectorAll('input[name="price"]:checked'))
            .map(b => b.getAttribute('data-value'));

        // Pass keywords separately so performSearchWithQuery can hard-filter by brand too
        performSearchWithQuery(refinedQuery, priceBoxes, keywords);
    };


    // Helper to parse price range value strings
    const matchPrice = (lp, priceValues) => {
        for (const val of priceValues) {
            const [lo, hi] = val.split('_').map(v => {
                if (v === 'under') return null;
                if (v === 'over') return null;
                return parseInt(v.replace(/[^0-9]/g, ''), 10) * (v.includes('k') ? 1000 : 1);
            });
            if (val.startsWith('under') && lp < parseInt(val.split('_')[1].replace(/[^0-9]/g,'')) * (val.includes('k') ? 1000 : 1)) return true;
            if (val.startsWith('over') && lp > parseInt(val.split('_')[1].replace(/[^0-9]/g,'')) * (val.includes('k') ? 1000 : 1)) return true;
            if (lo !== null && hi !== null && lp >= lo && lp <= hi) return true;
        }
        return false;
    };


    // Initialize UI
    renderCategories();

    // Core search — fetches from backend with the given query, then applies price filter locally
    const performSearchWithQuery = async (query, priceFilter = [], keywordFilter = []) => {
        if (!query) return;
        queryText.innerText = `"${query}"`;
        resultsContainer.classList.add('hidden');
        loadingState.classList.remove('hidden');

        try {
            const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
            if (!response.ok) throw new Error("Network response was not ok");
            let data = await response.json();

            // Hard-filter by keyword (brand / color) — only show products matching ALL checked keywords
            if (keywordFilter.length > 0) {
                data = data.filter(p => {
                    const name = (p.name || '').toLowerCase();
                    return keywordFilter.every(kw => name.includes(kw.toLowerCase()));
                });
            }

            // Apply price filter locally after fetch
            if (priceFilter.length > 0) {
                data = data.filter(p => {
                    if (!p.prices || p.prices.length === 0) return false;
                    const lp = p.prices.reduce((prev, curr) => prev.price < curr.price ? prev : curr).price;
                    return matchPrice(lp, priceFilter);
                });
            }

            window.currentProducts = data;
            loadingState.classList.add('hidden');
            mainLayout.classList.remove('hidden');
            renderProducts(window.currentProducts);
            resultsContainer.classList.remove('hidden');

            const cards = document.querySelectorAll('.product-card');
            cards.forEach((card, i) => setTimeout(() => {
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, i * 60));
        } catch (error) {
            console.error('Error fetching data:', error);
            loadingState.classList.add('hidden');
            productGrid.innerHTML = '<div style="grid-column:1/-1;text-align:center;color:var(--text-secondary)">Backend error. Check server on port 5001.</div>';
            resultsContainer.classList.remove('hidden');
        }
    };


    const performSearch = async () => {
        const query = searchInput.value.trim();
        if (!query) return;

        // Hide landing page on first search
        if (landingPage) landingPage.style.display = 'none';

        // On a fresh search (not from a filter change), rebuild filters for the active category
        const filterSchema = window.activeCategoryFilters || null;
        buildFilters(filterSchema);

        // Close mobile sidebar if open
        if (sidebar) sidebar.classList.remove('open');
        if (sidebarOverlay) sidebarOverlay.classList.remove('active');

        await performSearchWithQuery(query);
    };


    searchBtn.addEventListener('click', performSearch);
    searchInput.addEventListener('keypress', (e) => {
        if(e.key === 'Enter') performSearch();
    });

    // Auto-detect category from search text and update filters live
    const CATEGORY_KEYWORDS = [
        {
            keys: ['mobile', 'phone', 'smartphone', 'iphone', 'samsung galaxy', 'oneplus', 'realme', 'redmi', 'oppo', 'vivo', 'tablet', 'ipad'],
            catName: 'Mobiles & Tablets'
        },
        {
            keys: ['laptop', 'macbook', 'notebook', 'pc', 'computer', 'monitor', 'headphone', 'earphone', 'earbud', 'smartwatch', 'camera', 'playstation', 'xbox'],
            catName: 'Electronics'
        },
        {
            keys: ['shoe', 'sneaker', 'slipper', 'sandal', 'croc', 'heel', 'boot', 'loafer', 'flip flop'],
            catName: 'Footwear'
        },
        {
            keys: ['shirt', 'tshirt', 't-shirt', 'jeans', 'jean', 'trouser', 'pant', 'cargo', 'kurta', 'dress', 'saree', 'legging', 'jacket', 'hoodie', 'sweatshirt', 'tracksuit', 'shorts', 'skirt'],
            catName: 'Fashion & Apparel'
        },
        {
            keys: ['tv', 'television', 'washing machine', 'air conditioner', 'refrigerator', 'fridge', 'microwave', 'air purifier', 'dishwasher', 'geyser', 'water heater', 'vacuum cleaner'],
            catName: 'Home Appliances'
        },
        {
            keys: ['makeup', 'lipstick', 'foundation', 'moisturizer', 'skincare', 'sunscreen', 'serum', 'perfume', 'fragrance', 'shampoo', 'conditioner', 'hair oil', 'face wash', 'toner'],
            catName: 'Beauty & Grooming'
        },
        {
            keys: ['toy', 'lego', 'puzzle', 'board game', 'action figure', 'remote control car', 'doll', 'bicycle', 'scooter'],
            catName: 'Toys & Games'
        }
    ];

    let _detectDebounce = null;
    const detectAndApplyCategory = (text) => {
        if (!text || text.length < 3) return;
        const lower = text.toLowerCase();
        for (const entry of CATEGORY_KEYWORDS) {
            if (entry.keys.some(k => lower.includes(k))) {
                const matched = CATEGORIES.find(c => c.name === entry.catName);
                if (matched) {
                    window.activeCategoryFilters = matched.filters;
                    // Only rebuild filters if sidebar is already open (after a search)
                    if (!mainLayout.classList.contains('hidden')) {
                        buildFilters(matched.filters);
                    }
                }
                return;
            }
        }
    };

    searchInput.addEventListener('input', () => {
        clearTimeout(_detectDebounce);
        _detectDebounce = setTimeout(() => detectAndApplyCategory(searchInput.value.trim()), 300);
    });

    const renderProducts = (productsToRender) => {
        productGrid.innerHTML = '';

        if (productsToRender.length === 0) {
            productGrid.innerHTML = '<div style="grid-column:1/-1;text-align:center;font-size:1.1rem;margin-top:2rem;color:var(--text-secondary);">No products found. Try a different search.</div>';
            return;
        }

        // Solid FA icons (not brand icons)
        const solidIcons = new Set(['fa-store','fa-shopping-cart','fa-bullseye','fa-camera','fa-bolt',
            'fa-check','fa-bag-shopping','fa-spa','fa-recycle','fa-heart','fa-shopping-bag']);

        productsToRender.forEach(product => {
            const lowestPriceStore = product.prices.reduce((prev, curr) => prev.price < curr.price ? prev : curr);
            const card = document.createElement('div');
            card.className = 'product-card';

            // Sort: Amazon & Flipkart first, then by price
            const sorted = [...product.prices].sort((a, b) => {
                const ap = (a.store==='Amazon'||a.store==='Flipkart') ? 1 : 0;
                const bp = (b.store==='Amazon'||b.store==='Flipkart') ? 1 : 0;
                if (ap !== bp) return bp - ap;
                return a.price - b.price;
            });

            // Desktop: vertical stack of price rows
            const priceRowsHTML = sorted.map(priceObj => {
                const isLowest  = priceObj.price === lowestPriceStore.price;
                const formatted = priceObj.price.toLocaleString('en-IN');
                const iconClass = solidIcons.has(priceObj.logo) ? 'fa-solid' : 'fa-brands';
                return `
                    <div class="price-row ${isLowest ? 'best-price' : ''}">
                        <div class="store-info">
                            <i class="${iconClass} ${priceObj.logo}"></i>
                            <span>${priceObj.store}</span>
                            ${isLowest ? '<span class="badge">Lowest</span>' : ''}
                        </div>
                        <div class="price-action">
                            <span class="price-amount">₹${formatted}</span>
                            <a href="${priceObj.url}" target="_blank" rel="noopener" class="buy-btn">View Deal</a>
                        </div>
                    </div>`;
            }).join('');

            // Mobile ticker: horizontal scrolling strip with price pills
            const tickerItems = [...sorted, ...sorted].map(priceObj => {
                const isLowest  = priceObj.price === lowestPriceStore.price;
                const formatted = priceObj.price.toLocaleString('en-IN');
                const iconClass = solidIcons.has(priceObj.logo) ? 'fa-solid' : 'fa-brands';
                return `
                    <a href="${priceObj.url}" target="_blank" rel="noopener"
                       class="price-pill ${isLowest ? 'price-pill-best' : ''}">
                        <i class="${iconClass} ${priceObj.logo}"></i>
                        <span class="pill-store">${priceObj.store}</span>
                        <span class="pill-price">₹${formatted}</span>
                        <span class="pill-btn">Buy</span>
                    </a>`;
            }).join('');

            const cheapestUrl = lowestPriceStore.url;
            card.innerHTML = `
                <a href="${cheapestUrl}" target="_blank" rel="noopener" style="display:block;text-decoration:none;">
                    <div class="product-image" style="background-image:url('${product.image}')"></div>
                </a>
                <div class="product-info">
                    <h3 class="product-title">${product.name}</h3>
                    <!-- Desktop view: vertical rows -->
                    <div class="price-comparison desktop-prices">${priceRowsHTML}</div>
                    <!-- Mobile view: horizontal ticker -->
                    <div class="price-ticker mobile-prices">
                        <div class="price-ticker-track">${tickerItems}</div>
                    </div>
                </div>
            `;
            productGrid.appendChild(card);
        });
    }
});

