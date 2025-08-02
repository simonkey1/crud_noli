# Reorganización del Proyecto (30 de julio de 2025)

## Cambios realizados

### 1. Archivos .py vacíos o duplicados

- Se han movido los siguientes archivos .py vacíos a `scripts/mp_utils` con extensión `.bak`:
  - actualizar_mp_config_db.py
  - actualizar_vendedor_comprador.py
  - configure_mp_test_users.py
  - diagnostico_mp.py
  - update_mp_config.py

### 2. Scripts de utilidades de base de datos

- Se han movido los siguientes scripts a `scripts/db_utils`:
  - add_column.py
  - check_db.py
  - check_db_cli.py

### 3. Archivos de log

- Se han creado y movido los logs a la carpeta `logs/`:
  - database_backup.log
  - database_cleanup.log

### 4. Scripts de Docker

- Se han creado copias de los scripts Docker en `scripts/docker_utils/`:
  - deploy.bat
  - deploy.sh
  - docker-entrypoint.sh
- Los originales permanecen en la raíz porque son referenciados directamente por Docker

## Estructura actual del proyecto

```
crud_noli/
├── backups/          # Backups de la base de datos
├── config/           # Archivos de configuración
├── core/             # Configuraciones centrales
├── db/               # Módulos de base de datos
├── docs/             # Documentación
├── logs/             # Archivos de log
├── migrations/       # Migraciones de Alembic
├── models/           # Modelos de datos
├── routers/          # Rutas de la API
├── schemas/          # Esquemas Pydantic
├── scripts/          # Scripts utilitarios
│   ├── db_utils/     # Utilidades de base de datos
│   ├── docker_utils/ # Utilidades de Docker (copias)
│   ├── mp_utils/     # Utilidades de Mercado Pago
│   └── obsolete/     # Scripts obsoletos
├── services/         # Servicios de la aplicación
├── static/           # Archivos estáticos
├── templates/        # Plantillas HTML
├── tests/            # Tests
├── utils/            # Utilidades generales
└── ... archivos de configuración ...
```

## Notas

- Los archivos Docker (deploy.bat, deploy.sh, docker-entrypoint.sh) se mantienen en la raíz ya que son referenciados directamente por Dockerfile y docker-compose.yml
- Se recomienda usar los scripts desde sus nuevas ubicaciones en scripts/ para mantener organizado el proyecto
