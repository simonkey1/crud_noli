# CRUD Noli - Sistema de Gestión de Inventario y Ventas

Este proyecto es una aplicación web desarrollada con **FastAPI** y **Jinja2**, orientada a la gestión de inventario, ventas y transacciones para pequeños negocios.

## ⚙️ Tecnologías utilizadas

- **Backend**: 
  - Python 3.x
  - FastAPI (Framework web)
  - SQLModel/SQLAlchemy (ORM)
  - JWT (Autenticación)
  - Jinja2 (Motor de plantillas)
  - Pytest (Testing)

- **Frontend**:
  - HTML/CSS
  - JavaScript
  - TailwindCSS (Framework CSS)
  - Modo oscuro completo

- **Base de datos**:
  - PostgreSQL
  - Migraciones con Alembic

- **Despliegue**:
  - Render (Hosting)
  - GitHub Actions (CI/CD)

## � Funcionalidades principales

### Gestión de inventario (CRUD)
- Administración de productos y categorías
- Control de stock
- Códigos de barras
- Imágenes de productos

### Sistema de ventas (POS)
- Interfaz intuitiva para cajeros
- Carrito de compras
- Múltiples métodos de pago (efectivo, débito, crédito, transferencia)
- Generación de órdenes

### Gestión de transacciones
- Historial de ventas
- Filtros por fecha, método de pago y estado
- Detalles de transacciones
- Cierre de caja

### Reportes
- Generación de PDF para transacciones
- Reportes de cierres de caja
- Estadísticas de ventas

### Seguridad
- Autenticación con JWT
- Protección de rutas
- Permisos por tipo de usuario

## 🚀 Instalación y ejecución

### Requisitos previos
- Python 3.8 o superior
- PostgreSQL
- pip

### Pasos para instalación

1. Clona el repositorio:
```bash
git clone https://github.com/simonkey1/crud_noli.git
cd crud_noli
```

2. Crea un entorno virtual e instala las dependencias:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Configura las variables de entorno:
Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:
```
DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/nombre_db
JWT_SECRET_KEY=tu_clave_secreta
ENVIRONMENT=development
```

4. Ejecuta las migraciones:
```bash
alembic upgrade head
```

5. Inicia la aplicación:
```bash
uvicorn main:app --reload
```

6. Accede a la aplicación en tu navegador: `http://localhost:8000`

## 📊 Estructura del proyecto

```
crud_noli/
├── core/               # Configuración principal
├── db/                 # Conexión y dependencias de base de datos
├── migrations/         # Migraciones Alembic
├── models/             # Modelos SQLModel
├── routers/            # Endpoints API y rutas web
├── schemas/            # Esquemas Pydantic
├── scripts/            # Scripts utilitarios
├── services/           # Lógica de negocio
├── static/             # Archivos estáticos (CSS, JS, imágenes)
├── templates/          # Plantillas Jinja2
├── tests/              # Tests
├── main.py             # Punto de entrada
└── requirements.txt    # Dependencias
```

## 🧪 Testing

Ejecuta los tests con:
```bash
pytest
```

## 🛠️ Modo desarrollo

Para ejecutar la aplicación en modo desarrollo con recarga automática:
```bash
uvicorn main:app --reload
```

## 📝 Licencia

Este proyecto está licenciado bajo la Licencia GNU GPL v3.

## 👤 Autor

- [simonkey1](https://github.com/simonkey1)

---

Hecho con ❤️ para pequeños negocios.
