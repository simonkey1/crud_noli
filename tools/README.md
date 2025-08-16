# Herramientas del Proyecto

Esta carpeta contiene herramientas y utilidades para el mantenimiento del proyecto.

## 📁 Estructura

### `database/`

- Scripts de backup y restauración de base de datos
- Herramientas de mantenimiento de tablas
- Utilities para limpieza de datos

### `timezone_tests/`

- Tests y verificaciones del sistema de timezone
- Herramientas de monitoreo de zona horaria
- Verificaciones de transiciones DST

### Archivos de Deploy

- `deploy.sh` / `deploy.bat`: Scripts de despliegue
- `post_deploy.sh` / `post_deploy.bat`: Scripts post-despliegue

## 🚀 Uso

### Backup de Base de Datos

```bash
# Linux/Mac
./tools/database/crear_backup.sh

# Windows
tools\database\crear_backup.bat
```

### Verificación de Timezone

```bash
python tools/timezone_tests/monitor_timezone.py
```

### Deploy

```bash
# Linux/Mac
./tools/deploy.sh

# Windows
tools\deploy.bat
```
