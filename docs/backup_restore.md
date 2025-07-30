# Backup y Recuperación de Datos

Este documento proporciona instrucciones para realizar copias de seguridad de la base de datos y restaurar datos en caso de pérdidas.

## 🛡️ Prevención de pérdida de datos

### Backups Automáticos

El sistema está configurado para realizar backups automáticos diarios a través de GitHub Actions. Estos backups se almacenan como artefactos en GitHub y se conservan durante 14 días.

### Nuevos Scripts de Backup Manual

Además de los backups automáticos, ahora disponemos de scripts especializados para crear y restaurar backups manualmente, especialmente útiles antes y después de despliegues a producción.

#### Scripts disponibles:

1. **backup_database.py**: Crea copias de seguridad de los datos
2. **restore_database.py**: Restaura datos desde copias anteriores

Estos scripts están diseñados para proteger contra pérdidas de datos durante despliegues, migraciones o problemas con el servicio de hosting.

#### Cómo usar los nuevos scripts:

```bash
# Crear un backup completo de la base de datos
python scripts/backup_database.py

# Restaurar desde un backup (por defecto usa el más reciente)
python scripts/restore_database.py

# Restaurar desde un backup específico
python scripts/restore_database.py --backup-file backups/backup_20230615_123045.zip
```

Los nuevos scripts incluyen:

- **Backups compresos**: Los datos se guardan en archivos ZIP para reducir espacio
- **Registro de backups**: Cada operación se registra en `database_backup.log`
- **Verificación automática**: Se comprueba la integridad de los datos antes y después del backup
- **Protección contra sobrescritura**: Confirmación requerida para restaurar en entorno de producción

### Backups Manuales

También puedes realizar backups manuales en cualquier momento:

```bash
# Realizar un backup completo
python scripts/db_utils/database_backup.py backup

# Listar backups disponibles
python scripts/db_utils/database_backup.py list
```

Los backups se guardan en el directorio `backups/` y contienen archivos JSON con los datos de cada tabla.

## 🔄 Restauración de Datos

En caso de pérdida de datos, puedes restaurar desde un backup usando los nuevos scripts:

```bash
# Restaurar desde el backup más reciente
python scripts/restore_database.py

# Restaurar desde un backup específico
python scripts/restore_database.py --backup-dir backups/backup_20230615_123045

# Restaurar desde un archivo ZIP
python scripts/restore_database.py --backup-file backups/backup_20230615_123045.zip

# Restaurar específicamente solo productos y categorías
python scripts/restore_database.py --include productos,categorias

# Mostrar backups disponibles sin restaurar
python scripts/restore_database.py --list
```

Si prefieres usar los scripts anteriores:

```bash
# Restaurar desde un backup específico (preservando elementos existentes)
python scripts/db_utils/database_backup.py restore backups/backup_YYYYMMDD_HHMMSS

# Restaurar sobrescribiendo elementos existentes
python scripts/db_utils/database_backup.py restore backups/backup_YYYYMMDD_HHMMSS --force
```

## 🚨 Recuperación de Emergencia

Si necesitas crear rápidamente datos de muestra para iniciar el sistema:

```bash
# Crear productos de muestra
python scripts/seed_sample_products.py sample
```

## 📦 Exportación e Importación

Para migrar datos entre entornos:

```bash
# Exportar productos actuales a JSON
python scripts/seed_sample_products.py export

# Restaurar productos desde un archivo JSON
python scripts/seed_sample_products.py restore productos_backup.json
```

## ⚠️ Solución de problemas comunes

### Pérdida de datos durante el despliegue

Si los datos se pierden durante un despliegue:

1. Verifica que la variable `ENVIRONMENT=production` esté configurada en el entorno de producción
2. Restaura desde el backup más reciente usando `python scripts/restore_database.py`
3. Si los nuevos scripts no están disponibles en el entorno, usa `python scripts/db_utils/database_backup.py restore`
4. Si no hay backup, utiliza los scripts de datos de muestra para crear datos iniciales

### Base de datos inaccesible

Si la base de datos no responde:

1. Verifica la configuración de conexión en las variables de entorno
2. Confirma que el servicio de base de datos esté activo
3. Revisa los logs de la aplicación para ver errores específicos

### Inconsistencia en los datos

Si encuentras inconsistencias en los datos (ej. productos sin categorías):

1. Ejecuta `python scripts/check_db.py` para diagnóstico
2. Utiliza `python scripts/db_utils/database_backup.py restore` para restaurar desde un backup coherente

## 🔒 Mejores prácticas

1. Realiza backups antes de cada despliegue importante usando `python scripts/backup_database.py`
2. Configura la variable `BACKUP_AUTO=true` en el entorno para activar backups automáticos antes de las migraciones
3. Verifica periódicamente que los backups automáticos se estén ejecutando correctamente
4. Considera implementar un sistema de almacenamiento de backups externo (AWS S3, Google Cloud Storage, etc.)
5. Mantén copias locales de los backups críticos
6. Programa backups regulares mediante tareas programadas o GitHub Actions

## 📅 Programación de Backups Automáticos

Para configurar backups automáticos diarios en un servidor Linux, puedes usar cron:

```bash
# Editar el crontab
crontab -e

# Agregar esta línea para un backup diario a las 2 AM
0 2 * * * cd /ruta/a/tu/proyecto && python scripts/backup_database.py >> /var/log/backup.log 2>&1
```

Para Windows, puedes usar el Programador de tareas.
