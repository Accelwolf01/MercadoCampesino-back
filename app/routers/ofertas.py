from datetime import date, datetime
from typing import Optional
from sqlalchemy import or_
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models import OfertaFlash, ViajeProducto, Viaje, Usuario
from app.schemas import OfertaFlashOut, OfertaFlashFullOut, OfertaFlashCreate
from app.auth import get_current_user, verificar_permiso

router = APIRouter(prefix="/ofertas", tags=["Ofertas Flash"])


@router.get("/mis-ofertas", response_model=list[OfertaFlashFullOut])
def mis_ofertas(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return (
        db.query(OfertaFlash)
        .options(
            joinedload(OfertaFlash.viaje_producto)
            .joinedload(ViajeProducto.producto),
            joinedload(OfertaFlash.viaje_producto)
            .joinedload(ViajeProducto.viaje),
        )
        .join(ViajeProducto)
        .join(Viaje)
        .filter(Viaje.id_campesino == usuario.id)
        .order_by(OfertaFlash.created_at.desc())
        .all()
    )


@router.get("/activas", response_model=list[OfertaFlashFullOut])
def ofertas_activas(db: Session = Depends(get_db)):
    from config import bogota_today, bogota_now
    hoy = bogota_today()
    hora_actual = bogota_now().time()
    return (
        db.query(OfertaFlash)
        .join(ViajeProducto)
        .join(Viaje)
        .filter(OfertaFlash.activa == True)
        .filter(ViajeProducto.activo == True)
        .filter(ViajeProducto.cantidad_disponible > 0)
        .filter(Viaje.activo == True)
        .filter(Viaje.fecha_viaje == hoy)
        .filter(
            or_(
                Viaje.hora_fin == None,
                Viaje.hora_fin > hora_actual,
            )
        )
        .order_by(OfertaFlash.created_at.desc())
        .all()
    )


@router.post("/viaje-producto/{vp_id}", response_model=OfertaFlashOut, status_code=201)
def activar_oferta(
    vp_id: int,
    data: OfertaFlashCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(verificar_permiso("activar_ofertas")),
):
    vp = db.query(ViajeProducto).filter(ViajeProducto.id == vp_id).first()
    if not vp:
        raise HTTPException(status_code=404, detail="Producto del viaje no encontrado")

    viaje = vp.viaje
    if viaje.id_campesino != usuario.id:
        raise HTTPException(status_code=403, detail="Este producto no te pertenece")

    if data.descuento_porcentaje < 1 or data.descuento_porcentaje > 100:
        raise HTTPException(status_code=400, detail="El descuento debe estar entre 1% y 100%")

    precio_oferta = float(vp.precio) * (100 - data.descuento_porcentaje) / 100

    for o in vp.ofertas:
        o.activa = False

    oferta = OfertaFlash(
        id_viaje_producto=vp_id,
        descuento_porcentaje=data.descuento_porcentaje,
        precio_oferta=precio_oferta,
        cantidad_limite=data.cantidad_limite,
    )
    db.add(oferta)
    db.commit()
    db.refresh(oferta)
    return oferta


@router.put("/{oferta_id}/desactivar", response_model=OfertaFlashOut)
def desactivar_oferta(
    oferta_id: int,
    db: Session = Depends(get_db),
    _=Depends(verificar_permiso("activar_ofertas")),
):
    oferta = db.query(OfertaFlash).filter(OfertaFlash.id == oferta_id).first()
    if not oferta:
        raise HTTPException(status_code=404, detail="Oferta no encontrada")
    oferta.activa = False
    db.commit()
    db.refresh(oferta)
    return oferta


@router.put("/{oferta_id}/editar", response_model=OfertaFlashFullOut)
def editar_oferta(
    oferta_id: int,
    data: OfertaFlashCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(verificar_permiso("activar_ofertas")),
):
    oferta = db.query(OfertaFlash).filter(OfertaFlash.id == oferta_id).first()
    if not oferta:
        raise HTTPException(status_code=404, detail="Oferta no encontrada")

    vp = oferta.viaje_producto
    if not vp or vp.viaje.id_campesino != usuario.id:
        raise HTTPException(status_code=403, detail="Esta oferta no te pertenece")

    if data.descuento_porcentaje < 1 or data.descuento_porcentaje > 100:
        raise HTTPException(status_code=400, detail="El descuento debe estar entre 1% y 100%")

    oferta.descuento_porcentaje = data.descuento_porcentaje
    oferta.precio_oferta = float(vp.precio) * (100 - data.descuento_porcentaje) / 100
    oferta.cantidad_limite = data.cantidad_limite
    db.commit()
    db.refresh(oferta)
    return oferta


@router.delete("/{oferta_id}", status_code=204)
def eliminar_oferta(
    oferta_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(verificar_permiso("activar_ofertas")),
):
    oferta = db.query(OfertaFlash).filter(OfertaFlash.id == oferta_id).first()
    if not oferta:
        raise HTTPException(status_code=404, detail="Oferta no encontrada")

    vp = oferta.viaje_producto
    if not vp or vp.viaje.id_campesino != usuario.id:
        raise HTTPException(status_code=403, detail="Esta oferta no te pertenece")

    db.delete(oferta)
    db.commit()
