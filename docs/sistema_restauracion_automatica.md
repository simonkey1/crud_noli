# Sistema de Restauración Automática

Este sistema permite restaurar automáticamente la base de datos usando los artifacts de backup creados por GitHub Actions.

## 🎯 Funcionalidades

### 1. Restauración Automática Post-Deploy

- **Se activa automáticamente después de cada deploy exitoso**
- Verifica si la base de datos quedó vacía o con pocos datos
- Descarga automáticamente el backup creado antes del deploy
- Restaura la base de datos si tiene menos de 10 registros

### 2. Restauración Manual

- Permite ejecutar la restauración cuando lo necesites
- Opciones para elegir qué backup usar
- Posibilidad de forzar la restauración

## 🚀 Configuración Inicial

### 1. Secrets de GitHub (ya configurados)

Tu repositorio debe tener estos secrets configurados:

```
DATABASE_URL          # URL de conexión a la base de datos
POSTGRES_USER         # Usuario de PostgreSQL
POSTGRES_PASSWORD     # Contraseña de PostgreSQL
POSTGRES_DB          # Nombre de la base de datos
POSTGRES_SERVER      # Servidor de PostgreSQL
POSTGRES_PORT        # Puerto de PostgreSQL (default: 5432)
JWT_SECRET_KEY       # Clave secreta para JWT
```

### 2. Token Personal de GitHub (para uso manual)

Para activar manualmente las restauraciones:

1. Ve a: https://github.com/settings/tokens
2. Click en "Generate new token (classic)"
3. Selecciona estos permisos:
   - `repo` (Full control of private repositories)
   - `workflow` (Update GitHub Action workflows)
4. Copia el token generado

## 📋 Formas de Usar el Sistema

### Opción 1: Desde GitHub Actions (Web)

1. Ve a tu repositorio en GitHub
2. Click en "Actions" → "Auto Restore from Backup"
3. Click en "Run workflow"
4. Configura las opciones:
   - **backup_artifact_name**: Nombre del artifact (opcional)
   - **force_restore**: Marcar para forzar restauración
5. Click en "Run workflow"

### Opción 2: Script de Python (Multiplataforma)

```bash
# Configurar token
export GITHUB_TOKEN=tu_token_aqui

# Ejecutar script interactivo
python scripts/trigger_restore.py
```

### Opción 3: Script de PowerShell (Windows)

```powershell
# Configurar token
$env:GITHUB_TOKEN = "tu_token_aqui"

# Ejecutar script interactivo
.\scripts\trigger_restore.ps1

# O con parámetros directos:
.\scripts\trigger_restore.ps1 -ListArtifacts
.\scripts\trigger_restore.ps1 -ArtifactName "pre-deploy-backup" -ForceRestore
```

### Opción 4: API de GitHub (curl)

```bash
curl -X POST \
  -H "Accept: application/vnd.github.v3+json" \
  -H "Authorization: token TU_TOKEN" \
  -d '{"ref":"main","inputs":{"force_restore":"true"}}' \
  https://api.github.com/repos/simonkey1/crud_noli/actions/workflows/auto-restore.yml/dispatches
```

## 🔧 Workflows Disponibles

### 1. auto-restore.yml

- **Activación**: Automática después de cada deploy exitoso + Manual
- **Función**: Restaura la base de datos desde artifacts si tiene pocos datos
- **Umbral**: Restaura automáticamente si hay menos de 10 registros
- **Inputs**:
  - `backup_artifact_name`: Qué backup usar
  - `force_restore`: Forzar incluso si la DB tiene datos

### 2. ci-cd.yml (existente)

- **Función**: Deploy principal con backup automático
- **Crea**: Artifact "pre-deploy-backup" antes de cada deploy

### 3. backup-database.yml (existente)

- **Función**: Backup programado diario
- **Horario**: Cada día a las 2:00 AM UTC

## 📊 Monitoreo y Logs

### Ver el Estado de la Base de Datos

```bash
python scripts/backup_database.py --status
```

### Ver Backups Disponibles

```bash
python scripts/backup_database.py --list
```

### Ver Logs del Workflow

1. Ve a "Actions" en tu repositorio
2. Click en el workflow que se ejecutó
3. Revisa los logs de cada paso

## 🚨 Casos de Uso Comunes

### Caso 1: Deploy Exitoso Dejó la DB Vacía (Automático)

**Solución**: El sistema detecta automáticamente que hay menos de 10 registros y restaura el backup.

### Caso 2: Quieres Probar un Backup Específico

```powershell
.\scripts\trigger_restore.ps1 -ArtifactName "backup_20250128_120000" -ForceRestore
```

### Caso 3: Rollback Manual Urgente

1. Ve a GitHub Actions
2. "Run workflow" en "Auto Restore from Backup"
3. Marca "force_restore: true"
4. Click "Run workflow"

### Caso 4: Ver Qué Backups Están Disponibles

```bash
python scripts/trigger_restore.py
# Elige opción 1
```

## ⚠️ Consideraciones Importantes

### Seguridad

- Los tokens de GitHub son sensibles - no los compartas
- Los secrets están cifrados en GitHub Actions
- Los backups se eliminan automáticamente después de 30 días

### Performance

- La restauración puede tomar varios minutos
- Se verifica la integridad del backup antes de restaurar
- El sistema valida que la restauración fue exitosa

### Limitaciones

- Solo funciona con artifacts de GitHub (máximo 30 días)
- Requiere acceso a internet para descargar artifacts
- El tamaño del backup está limitado por GitHub Actions (2GB)

## 🔍 Troubleshooting

### Error: "No se encontró archivo de backup"

**Causa**: El artifact no contiene un archivo .zip válido
**Solución**: Verificar que el backup se creó correctamente

### Error: "Context access might be invalid"

**Causa**: Advertencias de VS Code sobre secrets
**Solución**: Es normal, los secrets se resuelven en runtime

### Error: "Authentication failed"

**Causa**: Token de GitHub inválido o sin permisos
**Solución**: Verificar token y permisos (repo + workflow)

### Error: "Database connection failed"

**Causa**: Problemas de conectividad o configuración
**Solución**: Verificar secrets de database en GitHub

## 📈 Mejoras Futuras

- [ ] Notificaciones por email/Slack
- [ ] Backups incrementales
- [ ] Retención configurable de artifacts
- [ ] Dashboard de monitoreo
- [ ] Restauración selectiva por tabla

---

💡 **Tip**: Siempre prueba el sistema de restauración en un entorno de desarrollo antes de usarlo en producción.
