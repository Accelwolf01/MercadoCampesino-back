# MercadoCampesino API

Backend REST para la plataforma que conecta campesinos de Cundinamarca con consumidores de Bogotá.

## Requisitos

- Python 3.12+
- PostgreSQL 15+
- pip

## Instalación

```bash
cd backend

# Crear entorno virtual
python -m venv venv
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Crear base de datos en PostgreSQL
psql -U postgres -c "CREATE DATABASE MercadoCampesino;"

# Inicializar tablas y datos de prueba
psql -U postgres -d MercadoCampesino -f bd/init.sql
```

## Configuración

Editar `.env`:

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=MercadoCampesino
DB_USER=postgres
DB_PASSWORD=*
SECRET_KEY=mercadocampesino_secret_key_2026
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

## Ejecutar

```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## Documentación interactiva

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Flujo de registro

1. **Cualquier usuario se registra** via `POST /auth/registro` con tipo `campesino` o `consumidor`
2. La cuenta se crea **inactiva** — no puede iniciar sesión
3. Un **superadmin o administrador** lista los pendientes via `GET /usuarios/pendientes/verificacion`
4. El admin verifica la identidad y activa via `PUT /usuarios/{id}/verificar`
5. El usuario ya puede iniciar sesión normalmente

## Login de prueba

| Email | Contraseña | Perfil |
|-------|-----------|--------|
| superadmin@mercadocampesino.co | SuperAdmin2026! | superadmin |
| superadmin2@mercadocampesino.co | SuperAdmin2026! | superadmin |

## Endpoints principales

- `POST /auth/login` — Iniciar sesión
- `POST /auth/registro` — Registro público
- `GET /auth/me` — Perfil del usuario autenticado
- `POST /auth/cambiar-password` — Cambiar contraseña
- `GET/POST /categorias` — CRUD categorías
- `GET/POST /calidades` — CRUD calidades
- `GET/POST /productos` — CRUD productos
- `GET/POST /plazas` — CRUD plazas
- `GET/POST /viajes` — CRUD viajes (hasta 5 fotos por producto + foto de ubicación)
- `POST /viajes/{id}/ubicacion` — Actualizar ubicación en vivo
- `PUT /viajes/producto/{id}` — Editar precio/stock
- `GET /viajes/historial/ventas` — Historial de ventas
- `POST /preordenes` — Crear preorden
- `PUT /preordenes/{id}/entregar` — Marcar como entregado
- `PUT /preordenes/{id}/no-retiro` — Marcar no retiro
- `GET /resenias/usuario/{id}` — Reseñas de un usuario
- `POST /resenias` — Dejar reseña
- `POST /resenias/{id}/responder` — Responder reseña
- `POST /resenias/{id}/reportar` — Reportar reseña
- `POST /ofertas/activar` — Activar oferta flash
- `GET /mapa` — Ver mapa con filtros

## Estructura del proyecto

```
backend/
├── .env
├── requirements.txt
├── main.py                  # FastAPI app + CORS
├── config.py                # Config desde .env
├── README.md
├── bd/
│   └── init.sql             # Esquema completo de BD
└── app/
    ├── database.py          # SQLAlchemy engine
    ├── models.py            # 15 modelos ORM
    ├── schemas.py           # Pydantic validators
    ├── auth.py              # JWT + bcrypt + permisos
    └── routers/
        ├── auth.py          # Login, registro
        ├── usuarios.py      # CRUD + verificación
        ├── perfiles.py      # CRUD perfiles
        ├── permisos.py      # Listar permisos
        ├── categorias.py    # CRUD categorías
        ├── calidades.py     # CRUD calidades
        ├── productos.py     # CRUD productos
        ├── plazas.py        # CRUD plazas
        ├── viajes.py        # CRUD viajes
        ├── preordenes.py    # Preórdenes
        ├── resenias.py      # Reseñas
        ├── ofertas.py       # Ofertas flash
        └── mapa.py          # Mapa + filtros
```
