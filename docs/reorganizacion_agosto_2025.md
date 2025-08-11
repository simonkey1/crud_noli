# Reorganización de Archivos - Agosto 2025

## Resumen

El 3 de agosto de 2025 se realizó una reorganización de los archivos del proyecto para mejorar la estructura del directorio y mantener la raíz más limpia. Los scripts y utilidades fueron organizados en subcarpetas dentro del directorio `scripts/`.

## Estructura Actual

### scripts/backup/

- Contiene scripts relacionados con la creación, restauración y manejo de backups:
  - actualizar_cierres.bat
  - actualizar_cierres.sh
  - crear_backup.bat
  - crear_backup.sh
  - restaurar_backup.py
  - restaurar_ultimo_backup.bat
  - restaurar_ultimo_backup.sh

### scripts/deployment/

- Contiene scripts relacionados con el despliegue y reinicio de la aplicación:
  - deploy.bat
  - deploy.sh
  - post_deploy.bat
  - post_deploy.sh
  - reiniciar_app.bat

### scripts/tools/

- Contiene herramientas de utilidad y diagnóstico:
  - add_column.py
  - check_db.py
  - check_db_cli.py
  - check_table_structure.py
  - diagnostico_mp.py
  - eliminar_duplicados.bat
  - update_mp_config.py
  - update_orden_table.py

### scripts/maintenance/

- Reservado para scripts de mantenimiento futuros

## Referencias Actualizadas

Se actualizaron las referencias en los siguientes archivos:

- docs/deployment.md
- scripts/docker_utils/deploy.bat
- scripts/docker_utils/deploy.sh
- scripts/mp_utils/update_mp_config.py

## Notas

- Para ejecutar los scripts ahora ubicados en subcarpetas, usar la ruta relativa correspondiente.
- Los archivos esenciales para la aplicación permanecen en la raíz del proyecto.
- Para futuras adiciones, seguir la estructura de directorios establecida.
