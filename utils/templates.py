"""
utils/templates.py - Configuración centralizada de plantillas Jinja2
"""

from fastapi.templating import Jinja2Templates
from utils.timezone import format_datetime_santiago, convert_to_santiago

# Crear una única instancia de Jinja2Templates para toda la aplicación
templates = Jinja2Templates(directory="templates")

# Filtro para formatear fechas en zona horaria Santiago
def datetime_santiago(dt, format="%d/%m/%Y %H:%M"):
    return format_datetime_santiago(dt, format)

# Filtro para convertir a zona horaria Santiago
def to_santiago(dt):
    return convert_to_santiago(dt)

# Filtro para formatear solo fecha (sin hora) en zona horaria Santiago
def date_santiago(dt, format="%d/%m/%Y"):
    return format_datetime_santiago(dt, format)

# Registrar los filtros personalizados
templates.env.filters["datetime_santiago"] = datetime_santiago
templates.env.filters["to_santiago"] = to_santiago
templates.env.filters["date"] = date_santiago
