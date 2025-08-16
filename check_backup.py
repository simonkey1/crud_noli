import zipfile
import json

# Verificar el contenido del mejor backup
backup_file = 'backups/backup_20250812_014035.zip'

try:
    with zipfile.ZipFile(backup_file, 'r') as z:
        manifest = json.loads(z.read('manifest.json').decode('utf-8'))
        
        print('📊 Contenido COMPLETO del backup_20250812_014035.zip:')
        print('=' * 50)
        
        for key, value in manifest.items():
            print(f'{key}: {value}')
        
        print('')
        print('� Archivos en el backup:')
        for filename in z.namelist():
            print(f'  {filename}')
        
        print('')
        productos = manifest.get('productos', 0)
        if productos > 10:
            print(f'✅ Excelente: Este backup tiene {productos} productos!')
        elif productos > 0:
            print(f'⚠️ Atención: Solo tiene {productos} producto(s)')
        else:
            print('❌ No tiene productos - Este backup parece ser solo de configuración/usuarios/órdenes')
            
except Exception as e:
    print(f'Error: {e}')
