# Sistema de Gestión Hotelera (SGH)

## 📋 Descripción
Sistema completo de gestión hotelera desarrollado con Python, Streamlit y PostgreSQL. Automatiza procesos de reserva, check-in/check-out, facturación y generación de reportes.

## 🚀 Características
- **Gestión de Reservas**: Creación, modificación y cancelación de reservas
- **Check-in/Check-out**: Procesamiento eficiente de entradas y salidas
- **Dashboard Interactivo**: KPIs y métricas en tiempo real
- **Reportes PDF**: Exportación de reportes de ocupación e ingresos
- **Gestión de Huéspedes**: Registro y seguimiento de huéspedes
- **Facturación**: Generación automática de facturas

## 📦 Requisitos Previos
- Python 3.9+
- PostgreSQL 12+
- pip (gestor de paquetes Python)

## 🔧 Instalación

### 1. Configuración del entorno
```bash
cd hotel-management-system
python -m venv venv
.\venv\Scripts\Activate.ps1   # Windows PowerShell
pip install -r requirements.txt
```

### 2. Base de datos PostgreSQL
Crear la base de datos y ejecutar los scripts en orden:

**Opción A - Con psql (línea de comandos):**
```bash
# Crear base de datos
psql -U postgres -c "CREATE DATABASE hotel_db;"

# Ejecutar scripts en este orden (desde la raíz del proyecto):
psql -U postgres -d hotel_db -f database\schema.sql
psql -U postgres -d hotel_db -f database\seeds.sql
psql -U postgres -d hotel_db -f database\indexes.sql
psql -U postgres -d hotel_db -f database\views.sql
```

**Opción B - Script automático (Windows):**
```bash
# Configurar variables si usas credenciales diferentes
$env:DB_PASSWORD = "tu_password"
.\scripts\init_db.bat
```

### 3. Configurar variables de entorno
Copia `.env.example` a `.env` y ajusta los valores:
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=hotel_db
DB_USER=postgres
DB_PASSWORD=tu_password
```

### 4. Ejecutar la aplicación
Desde la **raíz del proyecto** (donde está `requirements.txt`):
```bash
.\venv\Scripts\Activate.ps1
streamlit run src\app.py
```
La app se abrirá en el navegador (por defecto http://localhost:8501).

**Credenciales de prueba:**
- Admin: `admin` / `password123`
- Gerente: `gerente` / `password123`
- Recepcionista: `recepcion1` / `password123`

## 📁 Estructura del proyecto
```
hotel-management-system/
├── database/          # Scripts SQL
├── src/               # Código fuente
│   ├── config/        # Configuración y BD
│   ├── models/        # Modelos de datos
│   ├── controllers/   # Lógica de negocio
│   ├── views/         # Interfaces Streamlit
│   └── utils/         # Utilidades
├── scripts/           # Scripts de inicialización
└── .env               # Variables de entorno
```