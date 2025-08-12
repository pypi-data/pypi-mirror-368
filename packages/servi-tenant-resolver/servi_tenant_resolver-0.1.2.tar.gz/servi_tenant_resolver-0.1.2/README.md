# FastAPI Tenant Resolver

[![PyPI version](https://badge.fury.io/py/servi-tenant-resolver.svg)](https://badge.fury.io/py/servi-tenant-resolver)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Una librería simple y robusta para gestionar multitenancy por schema en FastAPI. Diseñada para ser no invasiva y compatible con backends síncronos y asíncronos.

## Características

- **Middleware Desacoplado**: Lee un header configurable (`X-Tenant` por defecto) sin bloquear endpoints públicos.
- **Dependencia Inteligente**: Una única dependencia `get_db` que se adapta para requerir un tenant o para acceder a un schema público.
- **Soporte Síncrono y Asíncrono**: Factorías separadas para `SQLAlchemy` estándar y `asyncio`.
- **Mínima Invasión**: Diseñada para integrarse en proyectos existentes con cambios mínimos.

## Instalación

```bash
pip install servi-tenant-resolver
```

## ¿Cómo Funciona?

La librería separa la **identificación** del tenant de la **configuración** de la base de datos.
1.  **Middleware**: Lee el header y guarda el `tenant_id` en `request.state`. No falla si el header no existe.
2.  **Dependencia**: Los endpoints la usan para obtener una sesión de DB. La dependencia lee el `tenant_id` del `request.state` y configura el `search_path` de PostgreSQL. Falla si el tenant es requerido y no se proveyó.

## Guía de Uso

Esta es la forma recomendada de integrar la librería en una aplicación FastAPI bien estructurada.

### 1. En tu `main.py` (Configuración del Middleware)

```python
# app/main.py
from fastapi import FastAPI
from fastapi_tenant_resolver import create_tenant_middleware

# Puedes personalizar el header si quieres. Por defecto es "X-Tenant".
TenantMiddleware = create_tenant_middleware(header_name="X-Mi-Empresa-Tenant")

app = FastAPI()
app.add_middleware(TenantMiddleware)

# ... incluye tus routers ...
```

### 2. En tu archivo de dependencias (ej. `app/db/session.py`)

Aquí es donde conectas la librería con tu configuración de base de datos.

```python
# app/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from servi_tenant_resolver import get_bd_session_factory

# ... tu configuración de DATABASE_URL y SessionLocal ...
# engine = create_engine(...)
# SessionLocal = sessionmaker(...)

# Usa la factoría de la librería para crear TU ÚNICA dependencia 'get_db'.
# Pásale tu SessionLocal para que sepa cómo crear sesiones.
get_db = get_bd_session_factory(SessionLocal)

# (Para backends asíncronos, usarías create_async_tenant_session_dependency y tu db_manager)
```

### 3. En tus Endpoints

Ahora puedes usar `get_db` de forma dinámica en cualquier router.

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db # <-- Importas tu dependencia ya configurada

router = APIRouter()

# --- Endpoint Privado (requiere tenant) ---
# Se usa `Depends(get_db)` sin argumentos.
@router.get("/profile")
def get_user_profile(db: Session = Depends(get_db)):
    # Falla con error 400 si no se envía el header del tenant.
    # El search_path ya está configurado para el tenant.
    # ... tu lógica ...

# --- Endpoint Público (administrativo) ---
# Se usa `Depends(get_db(public_access=True))`.
@router.get("/admin/system-status")
def get_system_status(db: Session = Depends(get_db(public_access=True))):
    # No requiere header. No falla.
    # El search_path se establece a 'public'.
    # ... tu lógica para el schema public ...
```
