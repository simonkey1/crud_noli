# Guía de Despliegue y Dockerización

Esta guía explica cómo desplegar la aplicación usando Docker y cómo manejar los backups de la base de datos.

## Requisitos previos

- Docker y Docker Compose instalados
- Python 3.9 o superior

## Instrucciones para despliegue

### Despliegue con Docker (Recomendado)

1. **Crear un backup antes del despliegue**:

   ```bash
   python scripts/tools/check_db_cli.py --backup
   ```

2. **Desplegar con el script automático**:

   En Linux/Mac:

   ```bash
   ./deploy.sh
   ```

   En Windows:

   ```
   deploy.bat
   ```

   Este script realiza automáticamente:

   - Backup de la base de datos
   - Detiene contenedores existentes
   - Reconstruye y levanta los contenedores
   - Verifica que la aplicación esté funcionando

3. **Acceder a la aplicación**:
   La aplicación estará disponible en: http://localhost:8000

### Manejo de backups

1. **Listar backups disponibles**:

   ```bash
   python scripts/restore_from_backup.py --list
   ```

2. **Restaurar desde un backup específico**:

   ```bash
   python scripts/restore_from_backup.py --restore backup_20250730_120000
   ```

3. **Restaurar desde el backup más reciente**:

   ```bash
   python scripts/restore_from_backup.py --restore latest
   ```

4. **Restaurar sin confirmación** (usar con precaución):
   ```bash
   python scripts/restore_from_backup.py --restore latest --force
   ```

### Verificación del estado de la base de datos

Para comprobar el estado de la base de datos:

```bash
python scripts/tools/check_db_cli.py --all
```

O para operaciones específicas:

```bash
python scripts/tools/check_db_cli.py --check     # Verificar conexión
python scripts/tools/check_db_cli.py --count     # Contar registros
python scripts/tools/check_db_cli.py --backup    # Crear backup
```

## Solución de problemas

Si la aplicación no se inicia correctamente después del despliegue:

1. Verificar los logs de Docker:

   ```bash
   docker-compose logs -f
   ```

2. Comprobar la conexión a la base de datos:

   ```bash
   python scripts/tools/check_db_cli.py --check
   ```

3. Restaurar desde un backup si es necesario:
   ```bash
   python scripts/restore_from_backup.py --restore latest
   ```

## Notas importantes

- Los backups se almacenan en la carpeta `backups/`
- La base de datos se persiste en un volumen Docker llamado `crud_noli_postgres_data`
- Todas las operaciones de backup y restauración requieren confirmación por seguridad
