import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database.connection import SessionLocal, Base, engine
from app.models import Category, Product, User, ShoppingList, ShoppingListItem, PurchaseHistory
from datetime import datetime, timedelta

def seed():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # 1. Categories
    category_names = [
        "Electronics", "Grocery", "Fashion", "Fitness", "Gaming", 
        "Home", "Personal Care", "Books", "Travel"
    ]
    categories = {}
    for name in category_names:
        c = Category(name=name)
        db.add(c)
        db.commit()
        db.refresh(c)
        categories[name] = c

    # 2. Category-Agnostic Products
    products_data = [
        # --- Electronics & Laptops ---
        {
            "name": "Acer Nitro V Gaming Laptop",
            "description": "Intel Core i5-13420H, 16GB RAM, 512GB SSD, RTX 4050 6GB GPU, 15.6 inch 144Hz FHD.",
            "brand": "Acer", "category": "Electronics", "price": 76990.0,
            "rating": 4.4, "review_count": 890, "availability": True, "seasonality": None,
            "attributes": {"ram_gb": 16, "storage_gb": 512, "gpu": "RTX 4050", "cpu": "i5-13420H", "weight_kg": 2.1, "battery_hours": 5.0, "ml_capable": True, "gaming_score": 0.88, "portability_score": 0.65},
            "tags": ["laptop", "gaming", "machine learning", "ml", "rtx 4050", "acer"]
        },
        {
            "name": "ASUS TUF Gaming A15",
            "description": "AMD Ryzen 7 7735HS, 16GB DDR5, 512GB NVMe, RTX 4050, 90Whr long-lasting battery.",
            "brand": "ASUS", "category": "Electronics", "price": 79990.0,
            "rating": 4.5, "review_count": 1200, "availability": True, "seasonality": None,
            "attributes": {"ram_gb": 16, "storage_gb": 512, "gpu": "RTX 4050", "cpu": "Ryzen 7 7735HS", "weight_kg": 2.2, "battery_hours": 7.5, "ml_capable": True, "gaming_score": 0.90, "portability_score": 0.68},
            "tags": ["laptop", "gaming", "machine learning", "ml", "asus", "ryzen 7"]
        },
        {
            "name": "Lenovo IdeaPad Slim 5 AI",
            "description": "Intel Core Ultra 5 125H, 16GB LPDDR5X, 1TB SSD, Intel Arc Graphics, 1.4kg ultra-light.",
            "brand": "Lenovo", "category": "Electronics", "price": 68990.0,
            "rating": 4.6, "review_count": 450, "availability": True, "seasonality": None,
            "attributes": {"ram_gb": 16, "storage_gb": 1024, "gpu": "Intel Arc", "cpu": "Ultra 5 125H", "weight_kg": 1.4, "battery_hours": 10.0, "ml_capable": False, "gaming_score": 0.50, "portability_score": 0.95},
            "tags": ["laptop", "lightweight", "portable", "travel", "lenovo", "office"]
        },
        {
            "name": "Apple MacBook Air M2",
            "description": "Apple M2 chip 8-core CPU, 8GB Unified Memory, 256GB SSD, Liquid Retina Display.",
            "brand": "Apple", "category": "Electronics", "price": 89900.0,
            "rating": 4.8, "review_count": 3400, "availability": True, "seasonality": None,
            "attributes": {"ram_gb": 8, "storage_gb": 256, "gpu": "M2 8-core", "cpu": "Apple M2", "weight_kg": 1.24, "battery_hours": 18.0, "ml_capable": True, "gaming_score": 0.45, "portability_score": 0.98},
            "tags": ["laptop", "macbook", "apple", "premium", "battery", "lightweight"]
        },
        # --- Audio & Headphones ---
        {
            "name": "Sony WH-1000XM4 Wireless ANC Headphones",
            "description": "Industry leading active noise cancelling, 30hr battery life, multipoint connection.",
            "brand": "Sony", "category": "Electronics", "price": 19990.0,
            "rating": 4.7, "review_count": 8500, "availability": True, "seasonality": None,
            "attributes": {"anc": True, "battery_hours": 30, "driver_mm": 40, "mic": True, "weight_g": 254},
            "tags": ["headphones", "anc", "wireless", "sony", "music", "premium"]
        },
        {
            "name": "boAt Rockerz 550 Wireless",
            "description": "50mm dynamic drivers, 20 hours playback, physical noise isolation.",
            "brand": "boAt", "category": "Electronics", "price": 1799.0,
            "rating": 4.1, "review_count": 15000, "availability": True, "seasonality": None,
            "attributes": {"anc": False, "battery_hours": 20, "driver_mm": 50, "mic": True, "weight_g": 245},
            "tags": ["headphones", "boat", "budget", "wireless", "bluetooth", "under 2000"]
        },
        {
            "name": "Sony WH-CH520 On-Ear Headphones",
            "description": "Up to 50-hour battery life, DSEE upscaling, lightweight ergonomic fit.",
            "brand": "Sony", "category": "Electronics", "price": 3990.0,
            "rating": 4.3, "review_count": 4200, "availability": True, "seasonality": None,
            "attributes": {"anc": False, "battery_hours": 50, "driver_mm": 30, "mic": True, "weight_g": 147},
            "tags": ["headphones", "sony", "budget", "wireless", "under 5000"]
        },
        # --- Grocery & Staples ---
        {
            "name": "Organic Rolled Oats 1kg",
            "description": "100% whole grain rolled oats, high fiber, gluten-free certified.",
            "brand": "True Elements", "category": "Grocery", "price": 320.0,
            "rating": 4.5, "review_count": 1800, "availability": True, "seasonality": None,
            "attributes": {"weight_kg": 1.0, "dietary": ["Gluten-Free", "Vegan"], "protein_g": 13.0, "organic": True},
            "tags": ["oats", "grocery", "breakfast", "fiber", "healthy", "diet"]
        },
        {
            "name": "Quaker Rolled Oats 1kg",
            "description": "Quick cooking whole oat grain for breakfast porridge and smoothies.",
            "brand": "Quaker", "category": "Grocery", "price": 199.0,
            "rating": 4.4, "review_count": 9200, "availability": True, "seasonality": None,
            "attributes": {"weight_kg": 1.0, "dietary": ["Vegetarian"], "protein_g": 11.5, "organic": False},
            "tags": ["oats", "grocery", "quaker", "breakfast", "substitute"]
        },
        {
            "name": "Raw Pressery Almond Milk 1L",
            "description": "Unsweetened plant-based milk enriched with Vitamin D & B12.",
            "brand": "Raw Pressery", "category": "Grocery", "price": 280.0,
            "rating": 4.2, "review_count": 890, "availability": True, "seasonality": None,
            "attributes": {"volume_l": 1.0, "dairy_free": True, "sugar_free": True},
            "tags": ["milk", "almond milk", "vegan", "dairy free", "grocery"]
        },
        {
            "name": "Amul Taaza Homogenised Toned Milk 1L",
            "description": "Pasteurised toned milk with 3.0% fat, rich in calcium.",
            "brand": "Amul", "category": "Grocery", "price": 72.0,
            "rating": 4.7, "review_count": 30000, "availability": True, "seasonality": None,
            "attributes": {"volume_l": 1.0, "fat_percent": 3.0, "dairy_free": False},
            "tags": ["milk", "doodh", "amul", "dairy", "grocery"]
        },
        {
            "name": "Fortune Sunlite Refined Sunflower Oil 1L",
            "description": "Enriched with Vitamins A & D, heart friendly cooking oil.",
            "brand": "Fortune", "category": "Grocery", "price": 145.0,
            "rating": 4.5, "review_count": 12000, "availability": True, "seasonality": None,
            "attributes": {"volume_l": 1.0, "oil_type": "Sunflower"},
            "tags": ["oil", "cooking oil", "fortune", "grocery"]
        },
        # --- Gaming & Work from Home setup ---
        {
            "name": "Logitech MX Master 3S Wireless Performance Mouse",
            "description": "8K DPI track-on-glass sensor, quiet clicks, MagSpeed scrolling.",
            "brand": "Logitech", "category": "Gaming", "price": 8995.0,
            "rating": 4.7, "review_count": 5200, "availability": True, "seasonality": None,
            "attributes": {"dpi": 8000, "wireless": True, "ergonomic": True, "battery_days": 70},
            "tags": ["mouse", "logitech", "office", "setup", "wireless mouse"]
        },
        {
            "name": "Logitech G213 Prodigy Gaming Keyboard",
            "description": "Mech-Dome keys, RGB lighting, spill-resistant, dedicated media controls.",
            "brand": "Logitech", "category": "Gaming", "price": 3995.0,
            "rating": 4.3, "review_count": 4800, "availability": True, "seasonality": None,
            "attributes": {"layout": "Full Size", "rgb": True, "switch_type": "Mech-Dome", "wired": True},
            "tags": ["keyboard", "gaming", "rgb", "logitech", "setup"]
        },
        {
            "name": "LG 24-inch FHD IPS Ultragear Gaming Monitor 144Hz",
            "description": "1ms MBR, AMD FreeSync, sRGB 99% color gamut, tilt adjustable.",
            "brand": "LG", "category": "Electronics", "price": 10990.0,
            "rating": 4.4, "review_count": 3100, "availability": True, "seasonality": None,
            "attributes": {"screen_size_inch": 24, "refresh_rate_hz": 144, "panel": "IPS", "resolution": "1080p"},
            "tags": ["monitor", "display", "gaming", "setup", "wfh", "144hz"]
        },
        # --- Travel & Seasonal ---
        {
            "name": "Mi 20000mAh 50W Fast Charging Power Bank",
            "description": "Triple port output, type-C 50W fast charging for phones and laptops.",
            "brand": "Xiaomi", "category": "Travel", "price": 3499.0,
            "rating": 4.5, "review_count": 7600, "availability": True, "seasonality": "Travel",
            "attributes": {"capacity_mah": 20000, "wattage": 50, "ports": 3},
            "tags": ["power bank", "travel", "charger", "battery", "xiaomi"]
        },
        {
            "name": "Universal All-in-One Travel Adapter with 20W PD",
            "description": "Works in US, UK, EU, AU over 150 countries with 3 USB + Type-C ports.",
            "brand": "Amkette", "category": "Travel", "price": 1299.0,
            "rating": 4.3, "review_count": 1400, "availability": True, "seasonality": "Travel",
            "attributes": {"countries": 150, "usb_ports": 4, "surge_protection": True},
            "tags": ["travel adapter", "adapter", "travel", "accessories"]
        },
        {
            "name": "Havells Warmio PTC Ceramic Room Heater 1500W",
            "description": "PTC ceramic heating element with oscillation, tip-over switch.",
            "brand": "Havells", "category": "Home", "price": 2899.0,
            "rating": 4.2, "review_count": 950, "availability": True, "seasonality": "Winter",
            "attributes": {"wattage": 1500, "heating_type": "PTC Ceramic", "oscillation": True},
            "tags": ["heater", "room heater", "winter", "home", "havells"]
        }
    ]

    for p in products_data:
        cat = categories[p.pop("category")]
        prod = Product(**p, category_id=cat.id)
        db.add(prod)
    
    db.commit()

    # 3. Create Default Demo User & History
    demo_user = User(
        name="Demo User",
        email="demo@cartmind.ai",
        preferences={"preferred_brands": ["Sony", "Logitech", "Amul"], "budget_monthly": 80000}
    )
    db.add(demo_user)
    db.commit()
    db.refresh(demo_user)

    # 4. Create Active Shopping List
    basket = ShoppingList(user_id=demo_user.id, name="My Basket", status="active")
    db.add(basket)
    db.commit()
    db.refresh(basket)

    # Add 1 initial item to basket (Amul Milk)
    milk_prod = db.query(Product).filter(Product.name.like("%Amul%")).first()
    if milk_prod:
        db.add(ShoppingListItem(shopping_list_id=basket.id, product_id=milk_prod.id, raw_query="Amul milk 1L", quantity=1.0, unit="liter"))

    # 5. Purchase History (for Repeat Purchase Recommendation test)
    oats_prod = db.query(Product).filter(Product.name.like("%True Elements%")).first()
    if oats_prod:
        past_date = datetime.utcnow() - timedelta(days=32)
        history_item = PurchaseHistory(
            user_id=demo_user.id,
            product_id=oats_prod.id,
            quantity=1.0,
            price_paid=320.0,
            purchased_at=past_date,
            category_name="Grocery"
        )
        db.add(history_item)

    db.commit()
    db.close()
    print("Database seeded with realistic multi-category products and user history.")

if __name__ == "__main__":
    seed()