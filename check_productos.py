import zipfile
import json

# Verificar productos reales en el backup
backup_file = 'backups/backup_20250812_014035.zip'

try:
    with zipfile.ZipFile(backup_file, 'r') as z:
        productos_data = json.loads(z.read('productos.json').decode('utf-8'))
        
        print(f'📦 productos.json contiene {len(productos_data)} productos:')
        
        for i, producto in enumerate(productos_data[:10]):  # Mostrar primeros 10
            nombre = producto.get('nombre', 'Sin nombre')
            codigo = producto.get('codigo_barra', 'Sin código')
            precio = producto.get('precio', 0)
            print(f'  {i+1}. {nombre} - ${precio} - {codigo}')
        
        if len(productos_data) > 10:
            print(f'  ... y {len(productos_data) - 10} productos más')
        
        print(f'\\n✅ ¡Este backup SÍ tiene {len(productos_data)} productos!')
        print('El problema es que el manifest.json no está contando bien.')
            
except Exception as e:
    print(f'Error: {e}')
