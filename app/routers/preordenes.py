from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models import Preorden, ViajeProducto, Viaje, Usuario, Producto, Categoria
from app.schemas import PreordenOut, PreordenCreate
from app.auth import get_current_user, verificar_permiso

router = APIRouter(prefix="/preordenes", tags=["Preórdenes"])


@router.get("", response_model=list[PreordenOut])
def mis_preordenes(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(verificar_permiso("realizar_preorden")),
):
    return (
        db.query(Preorden)
        .options(
            joinedload(Preorden.viaje_producto)
            .joinedload(ViajeProducto.producto)
            .joinedload(Producto.categoria),
            joinedload(Preorden.viaje_producto)
            .joinedload(ViajeProducto.viaje)
            .joinedload(Viaje.campesino),
        )
        .filter(Preorden.id_consumidor == usuario.id)
        .order_by(Preorden.created_at.desc())
        .all()
    )


@router.get("/campesino", response_model=list[PreordenOut])
def preordenes_recibidas(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(verificar_permiso("ver_preordenes")),
):
    return (
        db.query(Preorden)
        .options(joinedload(Preorden.consumidor))
        .join(ViajeProducto, ViajeProducto.id == Preorden.id_viaje_producto)
        .join(Viaje, Viaje.id == ViajeProducto.id_viaje)
        .filter(Viaje.id_campesino == usuario.id)
        .order_by(Preorden.created_at.desc())
        .all()
    )


@router.post("", response_model=PreordenOut, status_code=201)
def crear_preorden(
    data: PreordenCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(verificar_permiso("realizar_preorden")),
):
    vp = db.query(ViajeProducto).filter(ViajeProducto.id == data.id_viaje_producto).first()
    if not vp or not vp.activo:
        raise HTTPException(status_code=400, detail="Producto no disponible")

    if data.cantidad > vp.cantidad_disponible:
        raise HTTPException(status_code=400, detail=f"Solo hay {vp.cantidad_disponible} disponibles")

    preorden = Preorden(
        id_viaje_producto=data.id_viaje_producto,
        id_consumidor=usuario.id,
        cantidad=data.cantidad,
    )

    vp.cantidad_disponible -= data.cantidad
    db.add(preorden)
    db.commit()
    preorden = (
        db.query(Preorden)
        .options(
            joinedload(Preorden.viaje_producto)
            .joinedload(ViajeProducto.producto)
            .joinedload(Producto.categoria),
            joinedload(Preorden.viaje_producto)
            .joinedload(ViajeProducto.viaje)
            .joinedload(Viaje.campesino),
        )
        .filter(Preorden.id == preorden.id)
        .first()
    )
    return preorden


@router.put("/{preorden_id}/entregar", response_model=PreordenOut)
def entregar_preorden(
    preorden_id: int,
    db: Session = Depends(get_db),
    _=Depends(verificar_permiso("ver_preordenes")),
):
    pre = db.query(Preorden).filter(Preorden.id == preorden_id).first()
    if not pre:
        raise HTTPException(status_code=404, detail="Preorden no encontrada")
    pre.estado = "entregado"
    db.commit()
    db.refresh(pre)
    return pre


@router.put("/{preorden_id}/no-retiro", response_model=PreordenOut)
def no_retiro(
    preorden_id: int,
    db: Session = Depends(get_db),
    _=Depends(verificar_permiso("ver_preordenes")),
):
    pre = db.query(Preorden).filter(Preorden.id == preorden_id).first()
    if not pre:
        raise HTTPException(status_code=404, detail="Preorden no encontrada")

    pre.estado = "no_retiro"
    vp = pre.viaje_producto
    vp.cantidad_disponible += pre.cantidad
    consumidor = pre.consumidor
    consumidor.puntos_confianza -= 10
    db.commit()
    db.refresh(pre)
    return pre


@router.put("/{preorden_id}/cancelar", response_model=PreordenOut)
def cancelar_preorden(
    preorden_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    pre = db.query(Preorden).filter(Preorden.id == preorden_id).first()
    if not pre or pre.id_consumidor != usuario.id:
        raise HTTPException(status_code=404, detail="Preorden no encontrada")
    if pre.estado != "pendiente":
        raise HTTPException(status_code=400, detail="Solo se pueden cancelar preórdenes pendientes")

    pre.estado = "cancelado"
    vp = pre.viaje_producto
    vp.cantidad_disponible += pre.cantidad
    db.commit()
    db.refresh(pre)
    return pre
