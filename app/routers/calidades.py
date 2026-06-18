from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Calidad
from app.schemas import CalidadOut, CalidadCreate, CalidadUpdate
from app.auth import verificar_permiso

router = APIRouter(prefix="/calidades", tags=["Calidades"])


@router.get("", response_model=list[CalidadOut])
def listar_calidades(db: Session = Depends(get_db)):
    return db.query(Calidad).filter(Calidad.activo == True).all()


@router.get("/{calidad_id}", response_model=CalidadOut)
def obtener_calidad(calidad_id: int, db: Session = Depends(get_db)):
    c = db.query(Calidad).filter(Calidad.id == calidad_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Calidad no encontrada")
    return c


@router.post("", response_model=CalidadOut, status_code=201)
def crear_calidad(
    data: CalidadCreate,
    db: Session = Depends(get_db),
    _=Depends(verificar_permiso("gestionar_categorias")),
):
    if db.query(Calidad).filter(Calidad.nombre == data.nombre).first():
        raise HTTPException(status_code=400, detail="Ya existe una calidad con ese nombre")
    c = Calidad(**data.model_dump())
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


@router.put("/{calidad_id}", response_model=CalidadOut)
def actualizar_calidad(
    calidad_id: int,
    data: CalidadUpdate,
    db: Session = Depends(get_db),
    _=Depends(verificar_permiso("gestionar_categorias")),
):
    c = db.query(Calidad).filter(Calidad.id == calidad_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Calidad no encontrada")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(c, key, value)
    db.commit()
    db.refresh(c)
    return c


@router.delete("/{calidad_id}", status_code=204)
def eliminar_calidad(
    calidad_id: int,
    db: Session = Depends(get_db),
    _=Depends(verificar_permiso("gestionar_categorias")),
):
    c = db.query(Calidad).filter(Calidad.id == calidad_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Calidad no encontrada")
    db.delete(c)
    db.commit()
