# G&EE — Catálogo en GitHub Pages

Sitio estático adaptable a móviles, con filtros, subcategorías, búsqueda, precios en colones y fichas de productos.

## Publicación
Subir los archivos conservando la estructura. En GitHub: Settings > Pages > Deploy from a branch > main > /(root) > Save.

## Datos
`data/products.json` contiene **productos ficticios**. Editar ese archivo para agregar productos propios o autorizados.

## Sincronización
El workflow `.github/workflows/sync.yml` está **desactivado por defecto**. Requiere permiso del proveedor para copiar y reutilizar productos e imágenes. Solo entonces configurar en Settings > Secrets and variables > Actions > Variables:
- `CATALOG_AUTHORIZED` = `yes`
- `CATALOG_SOURCE_URL` = URL HTTPS de la tienda que autorizó el uso (sin barra final).

Después se puede ejecutar en Actions > Sincronizar catálogo autorizado > Run workflow. La programación es cada 6 horas (puede retrasarse). El endpoint público no da cantidades exactas ni webhooks; tampoco proporciona por sí solo la jerarquía de menús. Para categorías y subcategorías exactas hace falta una exportación/estructura oficial de colecciones y menús, y para casi tiempo real webhooks oficiales.

La sincronización utiliza la paginación `page` heredada, que puede no funcionar en todas las tiendas. Antes de habilitarla, verificar con el proveedor el método compatible y los límites de acceso. Si falla, conserva el catálogo anterior.

## Ofertas
Si un producto tiene `offer:true`, muestra solo `compareAtPrice` tachado (si existe); no muestra el precio rebajado. Esto es una presentación solicitada, no una indicación del precio efectivo de venta.

## Seguridad
Nunca agregar tokens privados de Shopify al repositorio ni al JavaScript del navegador.
