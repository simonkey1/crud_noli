# Backup y Recuperación de Datos

Este documento proporciona instrucciones para realizar copias de seguridad de la base de datos y restaurar datos en caso de pérdidas.

## 🛡️ Sistema de Backups Multicapa

El sistema cuenta con tres niveles de protección de datos:

### 1️⃣ Backups Automáticos vía GitHub Actions

El sistema está configurado para realizar backups automáticos diarios a través de GitHub Actions:
- ⏱️ **Programación**: Se ejecuta automáticamente todos los días a las 00:00 UTC
- 🔄 **Retención**: Los backups se almacenan como artefactos en GitHub y se conservan durante 14 días
- 🔒 **Seguridad**: Utiliza variables de entorno seguras (secrets) para acceder a la base de datos
- 🖱️ **Ejecución manual**: También se puede activar manualmente desde la interfaz de GitHub

Este método no requiere intervención manual y funciona incluso si nadie está monitoreando el sistema.

### 2️⃣ Script de Backup Automático Local/Servidor

El nuevo script `backup_automatico.py` puede programarse en el servidor o ambiente local:
- 🔁 **Rotación**: Implementa una política de rotación automática (mantiene solo los N backups más recientes)
- 📊 **Logging**: Registra detalladamente cada operación en archivos de log
- 📅 **Programable**: Puede configurarse con tareas programadas de Windows o cron en Linux

Este método es ideal para servidores propios o como capa adicional de seguridad.

### 3️⃣ Backups Manuales bajo demanda

Para operaciones críticas o momentos específicos, se pueden crear backups manuales:
- ⚡ **Rápido**: Ejecución inmediata con un solo comando
- 🎯 **Específico**: Ideal antes de migraciones, actualizaciones o cambios importantes
- 📦 **Portable**: Genera archivos ZIP fáciles de descargar y almacenar

#### Scripts disponibles:

1. **backup_database.py**: Crea copias de seguridad completas de los datos
2. **restore_database.py**: Restaura datos desde copias anteriores
3. **backup_automatico.py**: Nuevo script con rotación automática de backups

Estos scripts están diseñados para proteger contra pérdidas de datos durante despliegues, migraciones o problemas con el servicio de hosting.

#### Cómo usar los scripts:

```bash
# 1. Crear un backup completo de la base de datos (manual)
python -m scripts.backup_database --create

# 2. Ejecutar backup con rotación automática (mantiene los últimos 10)
python -m scripts.backup_automatico

# 3. Listar backups disponibles
python -m scripts.backup_database --list

# 4. Restaurar desde un backup específico
python -m scripts.restore_database --restore --id backup_20250730_153331
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

## 🔄 Respaldos Recientes (Julio 2025)

Se ha creado un nuevo backup completo del sistema con fecha 30 de julio de 2025:

- Backup ID: `backup_20250730_153331`
- Ubicación: `backups/backup_20250730_153331.zip`
- Contenido: 16 categorías, 91 productos, 3 usuarios

Para restaurar este backup específico:

```bash
# Restaurar desde este backup específico
python -m scripts.restore_database --restore --id backup_20250730_153331
```

Además, se ha implementado un nuevo script para backups automáticos programados:

```bash
# Ejecutar backup automático con rotación (mantiene últimos 10 backups)
python -m scripts.backup_automatico

# Ejecutar backup automático configurando cuántos mantener
python -m scripts.backup_automatico --max-backups 5
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

### En GitHub Actions (ya configurado)

El workflow `database_backup.yml` ya está configurado para ejecutarse diariamente. Para ejecutarlo manualmente:
1. Ve a la pestaña "Actions" en tu repositorio de GitHub
2. Selecciona el workflow "Database Backup"
3. Haz clic en "Run workflow"

### En servidores Linux/Render

Para configurar backups automáticos diarios con el nuevo script:

```bash
# Editar el crontab
crontab -e

# Agregar esta línea para un backup diario a las 2 AM
0 2 * * * cd /ruta/a/tu/proyecto && python -m scripts.backup_automatico --max-backups 10 >> /var/log/backup.log 2>&1
```

### En Windows (servidor local)

Para configurar en el Programador de tareas de Windows:

1. Abre el Programador de tareas
2. Crea una tarea nueva:
   - Nombre: "Backup Diario CRUD Noli"
   - Desencadenador: Diario a las 2:00 AM
   - Acción: Iniciar un programa
   - Programa: `C:\ruta\a\python.exe`
   - Argumentos: `-m scripts.backup_automatico --max-backups 10`
   - Iniciar en: `C:\ruta\a\tu\proyecto`

## 🔄 Flujo de Trabajo Recomendado

Para una protección óptima de datos:

1. **Diariamente (automático)**:
   - GitHub Actions ejecuta backups automáticos (sin intervención)
   
2. **Antes de actualizaciones importantes**:
   - Ejecuta un backup manual: `python -m scripts.backup_database --create`
   
3. **Mensualmente**:
   - Descarga algunos backups de GitHub Actions como respaldo externo
   - Verifica que todos los sistemas de backup estén funcionando

4. **En caso de emergencia**:
   - Sigue la guía de restauración en la sección "Respaldos Recientes"
