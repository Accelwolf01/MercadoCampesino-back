from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models import Viaje, ViajeUbicacion, ViajeProducto, ProductoFoto, OfertaFlash, Producto, Usuario
from app.schemas import (
    ViajeOut, ViajeCreate, ViajeUpdate,
    ViajeUbicacionCreate, ViajeProductoCreate,
)
from app.auth import get_current_user, verificar_permiso

router = APIRouter(prefix="/viajes", tags=["Viajes"])


@router.get("", response_model=list[ViajeOut])
def listar_viajes(
    id_campesino: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    q = db.query(Viaje).filter(Viaje.activo == True)
    if id_campesino:
        q = q.filter(Viaje.id_campesino == id_campesino)
    return q.order_by(Viaje.fecha_viaje.desc()).all()


@router.get("/mis-viajes", response_model=list[ViajeOut])
def mis_viajes(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return (
        db.query(Viaje)
        .filter(Viaje.id_campesino == usuario.id)
        .order_by(Viaje.fecha_viaje.desc())
        .all()
    )


@router.get("/activos", response_model=list[ViajeOut])
def viajes_activos_hoy(
    id_plaza: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    from datetime import date
    q = db.query(Viaje).options(
        joinedload(Viaje.campesino),
        joinedload(Viaje.ubicaciones).joinedload(ViajeUbicacion.plaza),
        joinedload(Viaje.productos).joinedload(ViajeProducto.producto),
    ).filter(Viaje.fecha_viaje == date.today(), Viaje.activo == True)

    if id_plaza:
        subq = db.query(ViajeUbicacion.id_viaje).filter(
            ViajeUbicacion.id_plaza == id_plaza, ViajeUbicacion.activa == True
        ).subquery()
        q = q.filter(Viaje.id.in_(subq))

    return q.order_by(Viaje.hora_inicio).all()


@router.get("/{viaje_id}", response_model=ViajeOut)
def obtener_viaje(viaje_id: int, db: Session = Depends(get_db)):
    viaje = db.query(Viaje).filter(Viaje.id == viaje_id).first()
    if not viaje:
        raise HTTPException(status_code=404, detail="Viaje no encontrado")
    return viaje


@router.post("", response_model=ViajeOut, status_code=201)
def crear_viaje(
    data: ViajeCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(verificar_permiso("publicar_viajes")),
):
    viaje = Viaje(
        id_campesino=usuario.id,
        fecha_viaje=data.fecha_viaje,
        hora_inicio=data.hora_inicio,
        hora_fin=data.hora_fin,
        notas=data.notas,
    )
    db.add(viaje)
    db.flush()

    for ubi in data.ubicaciones:
        viaje.ubicaciones.append(ViajeUbicacion(**ubi.model_dump()))

    for prod in data.productos:
        p = db.query(Producto).filter(Producto.id == prod.id_producto).first()
        if not p:
            raise HTTPException(status_code=400, detail=f"Producto {prod.id_producto} no encontrado")
        vp = ViajeProducto(
            id_producto=prod.id_producto,
            id_calidad=prod.id_calidad,
            precio=prod.precio,
            cantidad_inicial=prod.cantidad_inicial,
            cantidad_disponible=prod.cantidad_inicial,
        )
        for i, url in enumerate(prod.fotos[:5]):
            vp.fotos.append(ProductoFoto(url=url, orden=i))
        viaje.productos.append(vp)

    db.commit()
    db.refresh(viaje)
    return viaje


@router.put("/{viaje_id}", response_model=ViajeOut)
def actualizar_viaje(
    viaje_id: int,
    data: ViajeUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    viaje = db.query(Viaje).filter(Viaje.id == viaje_id).first()
    if not viaje or viaje.id_campesino != usuario.id:
        raise HTTPException(status_code=404, detail="Viaje no encontrado")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(viaje, key, value)
    db.commit()
    db.refresh(viaje)
    return viaje


@router.post("/{viaje_id}/ubicacion", response_model=ViajeOut)
def actualizar_ubicacion(
    viaje_id: int,
    data: ViajeUbicacionCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(verificar_permiso("marcar_ubicacion")),
):
    viaje = db.query(Viaje).filter(Viaje.id == viaje_id).first()
    if not viaje or viaje.id_campesino != usuario.id:
        raise HTTPException(status_code=404, detail="Viaje no encontrado")

    for u in viaje.ubicaciones:
        u.activa = False

    viaje.ubicaciones.append(ViajeUbicacion(**data.model_dump(), activa=True))
    db.commit()
    db.refresh(viaje)
    return viaje


@router.put("/producto/{vp_id}", response_model=ViajeOut)
def actualizar_precio_stock(
    vp_id: int,
    precio: Optional[float] = Query(None),
    cantidad_disponible: Optional[float] = Query(None),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(verificar_permiso("editar_precios_stock")),
):
    vp = db.query(ViajeProducto).filter(ViajeProducto.id == vp_id).first()
    if not vp:
        raise HTTPException(status_code=404, detail="Producto del viaje no encontrado")
    if vp.viaje.id_campesino != usuario.id:
        raise HTTPException(status_code=403, detail="Este producto no te pertenece")

    if precio is not None:
        vp.precio = precio
    if cantidad_disponible is not None:
        vp.cantidad_disponible = cantidad_disponible

    db.commit()
    db.refresh(vp.viaje)
    return vp.viaje


@router.post("/{viaje_id}/productos", response_model=ViajeOut)
def agregar_producto_a_viaje(
    viaje_id: int,
    data: ViajeProductoCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    viaje = db.query(Viaje).filter(Viaje.id == viaje_id).first()
    if not viaje or viaje.id_campesino != usuario.id:
        raise HTTPException(status_code=404, detail="Viaje no encontrado")
    vp = ViajeProducto(
        id_viaje=viaje.id,
        id_producto=data.id_producto,
        precio=data.precio,
        cantidad_inicial=data.cantidad_inicial,
        cantidad_disponible=data.cantidad_inicial,
    )
    db.add(vp)
    db.commit()
    db.refresh(vp)
    return vp.viaje


@router.delete("/producto/{vp_id}", status_code=204)
def retirar_producto_de_viaje(
    vp_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    vp = db.query(ViajeProducto).filter(ViajeProducto.id == vp_id).first()
    if not vp:
        raise HTTPException(status_code=404, detail="Producto del viaje no encontrado")
    if vp.viaje.id_campesino != usuario.id:
        raise HTTPException(status_code=403, detail="No puedes modificar este viaje")
    db.query(OfertaFlash).filter(OfertaFlash.id_viaje_producto == vp_id).delete()
    db.query(ProductoFoto).filter(ProductoFoto.id_viaje_producto == vp_id).delete()
    db.delete(vp)
    db.commit()


@router.get("/historial/ventas", response_model=list[ViajeOut])
def historial_ventas(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(verificar_permiso("ver_historial_ventas")),
):
    return (
        db.query(Viaje)
        .filter(Viaje.id_campesino == usuario.id)
        .order_by(Viaje.fecha_viaje.desc())
        .all()
    )
