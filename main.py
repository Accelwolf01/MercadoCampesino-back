from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, usuarios, perfiles, permisos
from app.routers import categorias, calidades, productos, plazas, viajes
from app.routers import preordenes, resenias, ofertas, mapa
from app.database import SessionLocal
from app.seed import init_db, seed_data
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    db = SessionLocal()
    try:
        seed_data(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title="MercadoCampesino API",
    description="Backend de MercadoCampesino - Conexión directa entre campesinos y consumidores",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(usuarios.router)
app.include_router(perfiles.router)
app.include_router(permisos.router)
app.include_router(categorias.router)
app.include_router(calidades.router)
app.include_router(productos.router)
app.include_router(plazas.router)
app.include_router(viajes.router)
app.include_router(preordenes.router)
app.include_router(resenias.router)
app.include_router(ofertas.router)
app.include_router(mapa.router)


@app.get("/")
def root():
    return {"mensaje": "MercadoCampesino API", "version": "1.0.0"}
