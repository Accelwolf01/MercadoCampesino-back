from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Producto, ViajeProducto, OfertaFlash, ProductoFoto, Usuario
from app.schemas import ProductoOut, ProductoCreate, ProductoUpdate
from app.auth import verificar_permiso, get_current_user

router = APIRouter(prefix="/productos", tags=["Productos"])


@router.get("", response_model=list[ProductoOut])
def listar_productos(
    id_categoria: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    q = db.query(Producto).filter(Producto.activo == True)
    if id_categoria:
        q = q.filter(Producto.id_categoria == id_categoria)
    return q.order_by(Producto.nombre).all()


@router.get("/mis-productos", response_model=list[ProductoOut])
def mis_productos(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return db.query(Producto).filter(
        Producto.id_creador == usuario.id
    ).order_by(Producto.nombre).all()


@router.get("/{producto_id}", response_model=ProductoOut)
def obtener_producto(producto_id: int, db: Session = Depends(get_db)):
    prod = db.query(Producto).filter(Producto.id == producto_id).first()
    if not prod:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return prod


@router.post("", response_model=ProductoOut, status_code=201)
def crear_producto(
    data: ProductoCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    prod_data = data.model_dump()
    if prod_data.get("id_creador") is None:
        prod_data["id_creador"] = usuario.id
    prod = Producto(**prod_data)
    db.add(prod)
    db.commit()
    db.refresh(prod)
    return prod


@router.put("/{producto_id}", response_model=ProductoOut)
def actualizar_producto(
    producto_id: int,
    data: ProductoUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    prod = db.query(Producto).filter(Producto.id == producto_id).first()
    if not prod:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    if prod.id_creador and prod.id_creador != usuario.id and usuario.perfil_id not in (1, 2):
        raise HTTPException(status_code=403, detail="No puedes editar este producto")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(prod, key, value)
    if "activo" in data.model_dump(exclude_unset=True):
        vp_ids = [vp.id for vp in db.query(ViajeProducto).filter(ViajeProducto.id_producto == producto_id).all()]
        if vp_ids:
            db.query(OfertaFlash).filter(OfertaFlash.id_viaje_producto.in_(vp_ids)).update(
                {OfertaFlash.activa: prod.activo}, synchronize_session=False
            )
            db.query(ViajeProducto).filter(ViajeProducto.id.in_(vp_ids)).update(
                {ViajeProducto.activo: prod.activo}, synchronize_session=False
            )
    db.commit()
    db.refresh(prod)
    return prod


@router.delete("/{producto_id}", status_code=204)
def eliminar_producto(
    producto_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    prod = db.query(Producto).filter(Producto.id == producto_id).first()
    if not prod:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    if prod.id_creador and prod.id_creador != usuario.id and usuario.perfil_id not in (1, 2):
        raise HTTPException(status_code=403, detail="No puedes eliminar este producto")
    vp_ids = [vp.id for vp in db.query(ViajeProducto).filter(ViajeProducto.id_producto == producto_id).all()]
    if vp_ids:
        db.query(OfertaFlash).filter(OfertaFlash.id_viaje_producto.in_(vp_ids)).delete(synchronize_session=False)
        db.query(ProductoFoto).filter(ProductoFoto.id_viaje_producto.in_(vp_ids)).delete(synchronize_session=False)
        db.query(ViajeProducto).filter(ViajeProducto.id.in_(vp_ids)).delete(synchronize_session=False)
    db.delete(prod)
    db.commit()
