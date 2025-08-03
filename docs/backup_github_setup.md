# Configuración de Backups y Restauración con GitHub

## Configuración del Token de GitHub

Para permitir la restauración automática de backups desde GitHub durante el despliegue, necesitarás configurar lo siguiente:

### 1. Crear un Token de Acceso Personal en GitHub

1. Inicia sesión en tu cuenta de GitHub
2. Ve a Configuración (Settings) -> Configuración del desarrollador (Developer settings) -> Tokens de acceso personal (Personal access tokens)
3. Haz clic en "Generar nuevo token" (Generate new token) -> "Tokens (clásicos)" (Tokens classic)
4. Dale un nombre descriptivo como "Backup Restoration Token"
5. Selecciona los siguientes permisos:
   - `repo`: Acceso completo a repositorios
   - `workflow`: Si planeas usar GitHub Actions
6. Haz clic en "Generar token" (Generate token)
7. **¡IMPORTANTE!** Copia el token generado y guárdalo en un lugar seguro, no podrás verlo nuevamente

### 2. Crear un Repositorio para los Backups

1. Crea un nuevo repositorio en GitHub (recomendable que sea privado)
2. Puedes nombrarlo como `crud_noli_backups` o algo similar
3. No inicialices el repositorio con README u otros archivos

### 3. Configurar las Variables en Render

En el panel de control de Render, en la configuración de tu servicio:

1. Ve a la sección "Environment Variables"
2. Agrega estas variables:
   - `GITHUB_BACKUP_URL`: URL donde se alojará tu archivo zip de backup 
     (Ejemplo: `https://github.com/USUARIO/REPO/releases/download/latest/backup.zip`)
   - `GITHUB_TOKEN`: El token de acceso personal que generaste

### 4. Subir un Backup a GitHub Releases

Para subir un backup manualmente:

1. Crea un backup usando `python scripts/backup_database.py --create`
2. Sube el archivo ZIP generado a GitHub Releases:
   - Ve a tu repositorio en GitHub
   - Haz clic en "Releases" en la barra lateral derecha
   - Haz clic en "Create a new release"
   - Tag version: `latest` (o la versión que prefieras)
   - Título: "Latest Backup" (o similar)
   - Arrastra el archivo ZIP del backup al área de adjuntos
   - Haz clic en "Publish release"

## Uso de los Scripts de Restauración

### Restauración Manual Local

Para restaurar manualmente desde el último backup local:

- En Windows: Ejecuta `restaurar_ultimo_backup.bat`
- En Linux/Mac: Ejecuta `./restaurar_ultimo_backup.sh`

### Creación de un Nuevo Backup

Para crear un nuevo backup:

- En Windows: Ejecuta `crear_backup.bat`
- En Linux/Mac: Ejecuta `./crear_backup.sh`

### Restauración Manual desde GitHub

Para restaurar manualmente desde GitHub:

```bash
python scripts/github_restore.py --url URL_DEL_BACKUP --token TU_TOKEN
```

## Automatización Futura

En el futuro, puedes implementar un flujo de trabajo de GitHub Actions que:

1. Cree un backup periódicamente
2. Lo suba automáticamente a GitHub Releases
3. Actualice la versión "latest" con el backup más reciente

Esto permitirá que tu aplicación siempre restaure desde el backup más reciente durante los despliegues.
