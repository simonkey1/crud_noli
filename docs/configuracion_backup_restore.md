# 🚀 GUÍA: CONFIGURAR RESTAURACIÓN AUTOMÁTICA DE BACKUP

## 📋 Estado Actual

✅ **Deploy funcionando** en Render
✅ **Backup creado** con 264 registros
✅ **Sistema de timezone** corregido
✅ **render.yaml** configurado para auto-restore

## 🎯 Pasos para Activar Restauración Automática

### 1. 📦 Subir Backup a GitHub (MANUAL)

1. **Ve a tu repositorio en GitHub**:

   ```
   https://github.com/simonkey1/crud_noli
   ```

2. **Ir a Releases**:

   - Click en "Releases" (lado derecho)
   - Click en "Create a new release"

3. **Configurar el Release**:

   - **Tag**: `backup-manual-20250811`
   - **Title**: `Manual Backup Database - 2025-08-11`
   - **Description**:

     ```markdown
     # 📦 Backup Manual de Base de Datos

     **Archivo**: backup_20250811_185629.zip
     **Fecha**: 2025-08-11
     **Registros**: 264 registros

     ## Contenido

     - Productos: 116 registros
     - Categorías: 16 registros
     - Transacciones: 56 registros
     - Usuarios: 2 registros
     - Cierres de caja: 7 registros
     - Items: 67 registros

     ## Uso

     Este backup puede restaurarse automáticamente configurando:
     GITHUB_BACKUP_URL=URL_DE_DESCARGA_DIRECTA
     ```

4. **Subir Archivo**:

   - Arrastra el archivo: `backups/backup_20250811_185629.zip`
   - Click en "Publish release"

5. **Copiar URL de Descarga**:
   - Una vez creado, click derecho en el archivo
   - "Copiar enlace"
   - La URL será algo como:
     ```
     https://github.com/simonkey1/crud_noli/releases/download/backup-manual-20250811/backup_20250811_185629.zip
     ```

### 2. 🔧 Configurar Render

1. **Ve a Render Dashboard**:

   ```
   https://dashboard.render.com
   ```

2. **Selecciona tu servicio** `grano-sabor-api`

3. **Ve a Environment**:

   - Click en "Environment" en el menú izquierdo

4. **Agregar Variables**:

   ```
   GITHUB_BACKUP_URL=https://github.com/simonkey1/crud_noli/releases/download/backup-manual-20250811/backup_20250811_185629.zip
   POST_DEPLOY_RESTORE=true
   AUTO_RESTORE_ON_EMPTY=true
   FORCE_ADMIN_CREATION=true
   ```

5. **Guardar y Redeploy**:
   - Click "Save Changes"
   - El servicio se redeployará automáticamente

### 3. 🧪 Verificar Restauración

Una vez que termine el redeploy:

1. **Logs de Deploy**:

   - Ve a "Logs" en Render
   - Busca mensajes como:
     ```
     ✅ Restauración desde GitHub completada exitosamente
     ```

2. **Verificar en la App**:
   - Ve a tu aplicación
   - Deberías ver todos tus productos, categorías, etc.

## 🔄 Automatización Futura

### GitHub Actions (Ya configurado)

- **Backup automático diario** a las 2am
- **Se sube automáticamente** como release
- **Se puede ejecutar manualmente** desde GitHub Actions

### Render Post-Deploy (Configurado)

- **Detecta BD vacía** automáticamente
- **Descarga último backup** desde GitHub
- **Restaura datos** preservando IDs
- **Resetea secuencias** automáticamente

## 🎉 Resultado Final

Después de esta configuración:

✅ **Cada commit** → Render redeploy → BD vacía → Restauración automática
✅ **Backup diario** automático a las 2am
✅ **Sin conflictos de IDs** gracias al nuevo sistema
✅ **Timezone correcto** desde el primer momento

## 🚨 Notas Importantes

- **La primera restauración** puede tomar 1-2 minutos
- **Revisa los logs** de Render para confirmar éxito
- **Guarda la URL del backup** por si necesitas cambiarla
- **El sistema mantiene** las relaciones entre tablas intactas

---

## 📞 Si hay problemas:

1. **Logs de Render** → Environment → Logs
2. **Verificar variables** de entorno
3. **URL del backup** debe ser accesible públicamente
4. **Probar manualmente** desde el dashboard
