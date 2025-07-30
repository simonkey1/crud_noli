# Guía del Flujo CI/CD Mejorado

## Descripción General

El nuevo flujo de CI/CD implementa un proceso más seguro y verificable para el despliegue de la aplicación, añadiendo backups automáticos y verificación post-despliegue.

## Características Principales

### 1. Backup automático antes del despliegue

Antes de realizar cualquier cambio en la aplicación o base de datos, el sistema:
- Crea automáticamente un backup completo de la base de datos
- Guarda este backup como un artefacto en GitHub por 30 días
- Asegura que incluso si algo sale mal, siempre haya una copia de seguridad reciente

### 2. Proceso de verificación post-despliegue

Después de desplegar en Render, el sistema:
- Realiza comprobaciones automáticas para verificar que la aplicación está funcionando
- Intenta conectarse a la URL de la aplicación hasta 15 veces
- Proporciona feedback claro sobre el estado del despliegue

### 3. Separación clara de responsabilidades

El flujo está dividido en cuatro jobs claramente definidos:
- `backup-and-test`: Crea backup y ejecuta tests
- `migrate`: Aplica migraciones a Supabase
- `deploy`: Maneja el despliegue en Render
- `notify`: Proporciona notificaciones sobre el resultado

## Configuración Necesaria

Para que este flujo funcione correctamente, debes configurar los siguientes secrets en tu repositorio de GitHub:

1. Datos de conexión:
   - `DATABASE_URL`: URL de conexión a la base de datos
   - `SUPABASE_DB_URL`: URL para migraciones de Supabase
   - `APP_URL`: URL de tu aplicación desplegada (ej: https://mi-app.onrender.com)

2. Credenciales:
   - `JWT_SECRET_KEY`: Clave secreta para JWT
   - `ADMIN_USERNAME` y `ADMIN_PASSWORD`: Credenciales de administrador
   - `FILEBASE_KEY`, `FILEBASE_SECRET` y `FILEBASE_BUCKET`: Credenciales para almacenamiento de archivos

3. Configuración de Render:
   - `RENDER_TOKEN`: Token de API de Render
   - `RENDER_SERVICE_ID`: ID del servicio en Render

## Proceso de Ejecución

1. Al hacer push a la rama main o al activar manualmente el workflow:
   - Se crea un backup completo de la base de datos
   - Se ejecutan los tests para verificar que todo funciona

2. Si los tests pasan:
   - Se aplican las migraciones de Supabase
   - Se despliega la aplicación en Render

3. Después del despliegue:
   - Se verifica que la aplicación esté accesible
   - Se envían notificaciones del resultado

## Solución de Problemas

Si el despliegue falla:

1. Verifica los logs en la sección "Actions" de GitHub
2. Consulta el artefacto "pre-deploy-backup" para restaurar si es necesario
3. Usa el comando `python -m scripts.restore_database --restore` para restaurar desde el backup

## Ejecución Manual

Puedes ejecutar este workflow manualmente desde la interfaz de GitHub:
1. Ve a la pestaña "Actions"
2. Selecciona "CI/CD Pipeline" en el menú izquierdo
3. Haz clic en "Run workflow" y selecciona la rama main
