from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Categoria
from app.schemas import CategoriaOut, CategoriaCreate, CategoriaUpdate
from app.auth import verificar_permiso

router = APIRouter(prefix="/categorias", tags=["Categorías"])


@router.get("", response_model=list[CategoriaOut])
def listar_categorias(db: Session = Depends(get_db)):
    return db.query(Categoria).order_by(Categoria.nombre).all()


@router.get("/{categoria_id}", response_model=CategoriaOut)
def obtener_categoria(categoria_id: int, db: Session = Depends(get_db)):
    cat = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return cat


@router.post("", response_model=CategoriaOut, status_code=201)
def crear_categoria(
    data: CategoriaCreate,
    db: Session = Depends(get_db),
    _=Depends(verificar_permiso("gestionar_categorias")),
):
    if db.query(Categoria).filter(Categoria.nombre == data.nombre).first():
        raise HTTPException(status_code=400, detail="Ya existe una categoría con ese nombre")
    cat = Categoria(**data.model_dump())
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


@router.put("/{categoria_id}", response_model=CategoriaOut)
def actualizar_categoria(
    categoria_id: int,
    data: CategoriaUpdate,
    db: Session = Depends(get_db),
    _=Depends(verificar_permiso("gestionar_categorias")),
):
    cat = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(cat, key, value)
    db.commit()
    db.refresh(cat)
    return cat


@router.delete("/{categoria_id}", status_code=204)
def eliminar_categoria(
    categoria_id: int,
    db: Session = Depends(get_db),
    _=Depends(verificar_permiso("gestionar_categorias")),
):
    cat = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    db.delete(cat)
    db.commit()
