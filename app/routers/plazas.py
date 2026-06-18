from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Plaza
from app.schemas import PlazaOut, PlazaCreate, PlazaUpdate
from app.auth import verificar_permiso

router = APIRouter(prefix="/plazas", tags=["Plazas"])


@router.get("", response_model=list[PlazaOut])
def listar_plazas(db: Session = Depends(get_db)):
    return db.query(Plaza).filter(Plaza.activo == True).order_by(Plaza.nombre).all()


@router.post("", response_model=PlazaOut, status_code=201)
def crear_plaza(
    data: PlazaCreate,
    db: Session = Depends(get_db),
    _=Depends(verificar_permiso("gestionar_plazas")),
):
    if db.query(Plaza).filter(Plaza.nombre == data.nombre).first():
        raise HTTPException(status_code=400, detail="Ya existe una plaza con ese nombre")
    plaza = Plaza(**data.model_dump())
    db.add(plaza)
    db.commit()
    db.refresh(plaza)
    return plaza


@router.put("/{plaza_id}", response_model=PlazaOut)
def actualizar_plaza(
    plaza_id: int,
    data: PlazaUpdate,
    db: Session = Depends(get_db),
    _=Depends(verificar_permiso("gestionar_plazas")),
):
    plaza = db.query(Plaza).filter(Plaza.id == plaza_id).first()
    if not plaza:
        raise HTTPException(status_code=404, detail="Plaza no encontrada")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(plaza, key, value)
    db.commit()
    db.refresh(plaza)
    return plaza
