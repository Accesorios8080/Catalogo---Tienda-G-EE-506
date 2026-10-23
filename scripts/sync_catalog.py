import urllib.request
import json
import datetime
import os

SOURCE_URL = "https://eltigrecr.com/products.json?limit=250&page="
DATA_FILE = "data/catalog_data.json"

def detect_subcat(title_lower, type_lower, tags_lower):
    if any(k in title_lower or k in type_lower or k in tags_lower for k in ['zapato', 'zapatos', 'tenis', 'sandalia', 'sandalias', 'calzado', 'bota', 'tacón', 'tacon', 'plataforma', 'pantufla']): return "CALZADO"
    if any(k in title_lower or k in type_lower or k in tags_lower for k in ['blazer', 'cardigan', 'sueter', 'abrigo', 'jacket']): return "ABRIGOS Y JACKETS"
    if 'polo' in title_lower or 'polo' in type_lower: return "POLO"
    if 'camiseta' in title_lower or 't-shirt' in title_lower: return "CAMISETAS"
    if 'camisa' in title_lower or 'camisas' in type_lower: return "CAMISAS"
    if 'blusa' in title_lower or 'blusas' in type_lower: return "BLUSAS"
    if 'short' in title_lower or 'bermuda' in title_lower: return "SHORTS"
    if 'enagua' in title_lower or 'falda' in title_lower: return "ENAGUAS"
    if 'jean' in title_lower or 'jeans' in title_lower: return "JEANS"
    if 'pantalon' in title_lower or 'pantalón' in title_lower or 'pants' in title_lower: return "PANTALONES"
    if 'vestido' in title_lower or 'vestidos' in type_lower: return "VESTIDOS"
    if 'enterizo' in title_lower or 'jumpsuit' in title_lower: return "ENTERIZOS"
    if 'conjunto' in title_lower: return "CONJUNTO"
    return "OTROS"

def fetch_all_products():
    page = 1
    all_products = []
    
    while True:
        url = f"{SOURCE_URL}{page}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        try:
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                products = data.get('products', [])
                if not products:
                    break
                
                for p in products:
                    title = p.get('title', '')
                    vendor = p.get('vendor', '') or ''
                    body_html = p.get('body_html', '') or ''
                    images = p.get('images', [])
                    
                    if not images or not images[0].get('src'):
                        continue
                    
                    img_url = images[0].get('src')
                    
                    full_text = f"{title} {vendor} {body_html}".lower()
                    if 'tigre' in full_text or 'distribuidora' in full_text:
                        continue
                    
                    tags_lower = [t.lower() for t in p.get('tags', [])]
                    title_lower = title.lower()
                    type_lower = p.get('product_type', '').lower()
                    vendor_lower = vendor.lower()
                    
                    is_levis = 'levi' in title_lower or 'levi' in vendor_lower or any('levi' in t for t in tags_lower)
                    is_footwear = any(k in title_lower or k in type_lower or k in tags_lower for k in [
                        'zapato', 'zapatos', 'tenis', 'sandalia', 'sandalias', 'calzado', 'bota', 'botas', 'tacón', 'plataforma', 'mule', 'pantufla'
                    ])
                    
                    if is_levis:
                        category = "LEVI'S"
                    elif is_footwear:
                        category = "CALZADO"
                    elif any(k in tags_lower for k in ['caballero', 'hombre']) or any(k in title_lower for k in ['caballero', 'hombre', 'polo hombre']):
                        category = "CABALLERO"
                    elif any(k in tags_lower for k in ['niña', 'nina']) or 'niña' in title_lower or 'nina' in title_lower:
                        category = "NIÑA"
                    elif any(k in tags_lower for k in ['niño', 'nino']) or 'niño' in title_lower or 'nino' in title_lower:
                        category = "NIÑO"
                    else:
                        category = "DAMA"
                    
                    subcat = detect_subcat(title_lower, type_lower, tags_lower)
                    
                    variants = p.get('variants', [])
                    if not variants:
                        continue
                    
                    first_var = variants[0]
                    price = float(first_var.get('price', 0))
                    compare_at = float(first_var.get('compare_at_price', 0)) if first_var.get('compare_at_price') else 0
                    
                    is_offer = compare_at > price or any(k in tags_lower or k in title_lower for k in ['oferta', 'liquidación', 'liquidacion', 'descuento', 'promo', 'sale'])
                    
                    # REGLA ESTRICTA: Se toma el precio original más alto y se omite cualquier precio de rebaja
                    regular_price = max(price, compare_at)
                    
                    sizes = []
                    for v in variants:
                        if v.get('available', False):
                            size_val = v.get('option1') or v.get('title')
                            if size_val and size_val != 'Default Title':
                                sizes.append(size_val.strip().upper())
                    
                    sizes = list(set(sizes))
                    
                    item = {
                        "id": p.get('id'),
                        "name": title,
                        "brand": "G&EE",
                        "sku": first_var.get('sku', ''),
                        "category": category,
                        "subcategory": subcat,
                        "regular_price": regular_price,
                        "is_offer": is_offer,
                        "available_sizes": sizes,
                        "image_url": img_url,
                        "updated_at": p.get('updated_at')
                    }
                    all_products.append(item)
                    
                page += 1
                if page > 60:
                    break
        except Exception as e:
            break
            
    return all_products

def main():
    os.makedirs("data", exist_ok=True)
    products = fetch_all_products()
    payload = {
        "last_sync": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "total_items": len(products),
        "products": products
    }
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
