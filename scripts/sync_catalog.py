"""Sincroniza catálogo público SOLO si se cuenta con autorización del proveedor.
Variables: CATALOG_SOURCE_URL, CATALOG_AUTHORIZED=yes. Sin dependencias externas.
"""
import json, os, time, urllib.request
from pathlib import Path
from urllib.parse import urlencode

BASE=os.getenv('CATALOG_SOURCE_URL','').rstrip('/')
if os.getenv('CATALOG_AUTHORIZED','').lower() != 'yes' or not BASE:
    raise SystemExit('Sincronización desactivada. Se requiere autorización y URL configurada.')
if not BASE.startswith('https://'):
    raise SystemExit('Se requiere HTTPS.')

# Shopify publica hasta 250 artículos por página en este endpoint legado.
# Comprobar con el proveedor el método de paginación permitido y los límites.
products=[]
for page in range(1,101):
    url=BASE+'/products.json?'+urlencode({'limit':250,'page':page})
    req=urllib.request.Request(url,headers={'User-Agent':'GEE-Catalog-AuthorizedSync/1.0','Accept':'application/json'})
    try:
        with urllib.request.urlopen(req,timeout=25) as response:
            batch=json.load(response).get('products',[])
    except Exception as exc:
        raise SystemExit(f'Error consultando página {page}: {exc}')
    if not isinstance(batch,list): raise SystemExit('Respuesta inválida')
    products.extend(batch)
    if len(batch)<250:break
    time.sleep(1)
else: raise SystemExit('Se alcanzó el límite de páginas configurado; revisar paginación.')

result=[]
for p in products:
    variants=p.get('variants') or []
    first=variants[0] if variants else {}
    tags=p.get('tags') or []
    if isinstance(tags,str): tags=[t.strip() for t in tags.split(',') if t.strip()]
    # Etiquetas y product_type no contienen necesariamente la jerarquía real del menú.
    category=p.get('product_type') or 'Otros'
    subcategory=''
    compare=first.get('compare_at_price')
    price=first.get('price') or 0
    offer=bool(compare and float(compare)>float(price)) or any(str(t).lower()=='oferta' for t in tags)
    result.append({'id':str(p.get('id')),'title':p.get('title','Sin título'),'brand':p.get('vendor',''),
       'category':category,'subcategory':subcategory,'price':float(price),'compareAtPrice':float(compare) if compare else None,
       'offer':offer,'available':any(v.get('available') for v in variants),'sku':first.get('sku',''),
       'description':__import__('re').sub(r'<[^>]*>',' ',p.get('body_html') or '').strip(),
       'image':(p.get('images') or [{}])[0].get('src',''),
       'updatedAt':p.get('updated_at',''),'url':BASE+'/products/'+p.get('handle',''),
       'variants':[{'title':v.get('title',''),'available':bool(v.get('available'))} for v in variants], 'tags':tags})
if not result:raise SystemExit('Catálogo vacío; se conserva el archivo anterior.')
out=Path(__file__).resolve().parents[1]/'data/products.json'
out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'Sincronizados {len(result)} productos.')
