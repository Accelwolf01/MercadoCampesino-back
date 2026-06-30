import uuid
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import ChatConversacion, ChatMensaje, Usuario
from app.schemas import (
    ChatConversacionCreate, ChatConversacionOut, ChatConversacionMiniOut,
    ChatMensajeCreate, ChatMensajeOut,
)
from app.auth import get_current_user_optional, verificar_permiso

router = APIRouter(prefix="/chat", tags=["Chat en vivo"])


@router.post("/conversaciones", status_code=201)
def crear_conversacion(
    data: ChatConversacionCreate,
    db: Session = Depends(get_db),
    usuario: Usuario | None = Depends(get_current_user_optional),
):
    token = str(uuid.uuid4())
    conv = ChatConversacion(
        nombre=data.nombre,
        email=data.email,
        cedula=data.cedula,
        id_usuario=usuario.id if usuario else None,
        session_token=token,
    )
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return {"id": conv.id, "session_token": token}


@router.post("/conversaciones/{conv_id}/mensajes", status_code=201)
def enviar_mensaje(
    conv_id: int,
    data: ChatMensajeCreate,
    token: str = Query(""),
    db: Session = Depends(get_db),
    usuario: Usuario | None = Depends(get_current_user_optional),
):
    conv = db.query(ChatConversacion).filter(ChatConversacion.id == conv_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")

    if usuario:
        pass
    elif conv.session_token != token:
        raise HTTPException(status_code=403, detail="Token inválido")

    if conv.estado == "finalizado":
        raise HTTPException(status_code=400, detail="La conversación ya finalizó")

    msg = ChatMensaje(
        id_conversacion=conv_id,
        mensaje=data.mensaje,
        es_admin=False,
    )
    db.add(msg)
    conv.updated_at = None
    db.commit()
    db.refresh(msg)
    return ChatMensajeOut.model_validate(msg)


@router.get("/conversaciones/{conv_id}")
def obtener_conversacion(
    conv_id: int,
    token: str = Query(""),
    db: Session = Depends(get_db),
    usuario: Usuario | None = Depends(get_current_user_optional),
):
    conv = db.query(ChatConversacion).filter(ChatConversacion.id == conv_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")

    if usuario:
        if usuario.id_perfil in (1, 2):
            pass
        elif usuario.id == conv.id_usuario:
            pass
        else:
            raise HTTPException(status_code=403, detail="No tienes acceso a esta conversación")
    elif conv.session_token != token:
        raise HTTPException(status_code=403, detail="Token inválido")

    return ChatConversacionOut.model_validate(conv)


@router.get("/admin/pendientes", response_model=list[ChatConversacionMiniOut])
def conversaciones_pendientes(
    db: Session = Depends(get_db),
    _=Depends(verificar_permiso("gestionar_usuarios")),
):
    return (
        db.query(ChatConversacion)
        .filter(ChatConversacion.estado.in_(["abierto", "en_curso"]))
        .order_by(ChatConversacion.created_at.desc())
        .all()
    )


@router.get("/admin/asignadas", response_model=list[ChatConversacionMiniOut])
def conversaciones_asignadas(
    db: Session = Depends(get_db),
    admin: Usuario = Depends(verificar_permiso("gestionar_usuarios")),
):
    return (
        db.query(ChatConversacion)
        .filter(
            ChatConversacion.id_admin_asignado == admin.id,
            ChatConversacion.estado.in_(["abierto", "en_curso"]),
        )
        .order_by(ChatConversacion.updated_at.desc().nullslast())
        .all()
    )


@router.get("/admin/historial", response_model=list[ChatConversacionMiniOut])
def historial_conversaciones(
    q: str = Query(""),
    estado: str = Query(""),
    desde: date | None = Query(None),
    hasta: date | None = Query(None),
    limit: int = Query(20, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    _=Depends(verificar_permiso("gestionar_usuarios")),
):
    query = db.query(ChatConversacion)

    if estado:
        query = query.filter(ChatConversacion.estado == estado)
    if desde:
        query = query.filter(ChatConversacion.created_at >= desde)
    if hasta:
        query = query.filter(ChatConversacion.created_at <= hasta)
    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(
                ChatConversacion.nombre.ilike(like),
                ChatConversacion.email.ilike(like),
                ChatConversacion.cedula.ilike(like),
            )
        )

    return query.order_by(ChatConversacion.created_at.desc()).offset(offset).limit(limit).all()


@router.put("/admin/{conv_id}/tomar")
def tomar_conversacion(
    conv_id: int,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(verificar_permiso("gestionar_usuarios")),
):
    conv = db.query(ChatConversacion).filter(ChatConversacion.id == conv_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")
    if conv.estado == "finalizado":
        raise HTTPException(status_code=400, detail="La conversación ya finalizó")
    if conv.id_admin_asignado and conv.id_admin_asignado != admin.id:
        raise HTTPException(status_code=400, detail="Otro admin ya tomó esta conversación")

    conv.id_admin_asignado = admin.id
    if conv.estado == "abierto":
        conv.estado = "en_curso"
    db.commit()
    return {"mensaje": "Conversación asignada"}


@router.post("/admin/{conv_id}/mensajes", status_code=201)
def responder_admin(
    conv_id: int,
    data: ChatMensajeCreate,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(verificar_permiso("gestionar_usuarios")),
):
    conv = db.query(ChatConversacion).filter(ChatConversacion.id == conv_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")
    if conv.estado == "finalizado":
        raise HTTPException(status_code=400, detail="La conversación ya finalizó")

    if not conv.id_admin_asignado:
        conv.id_admin_asignado = admin.id
    if conv.estado == "abierto":
        conv.estado = "en_curso"

    msg = ChatMensaje(
        id_conversacion=conv_id,
        mensaje=data.mensaje,
        es_admin=True,
        id_admin=admin.id,
    )
    db.add(msg)
    conv.updated_at = None
    try:
        db.commit()
        db.refresh(msg)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al guardar mensaje: {str(e)}")
    return ChatMensajeOut.model_validate(msg)


@router.put("/admin/{conv_id}/finalizar")
def finalizar_conversacion(
    conv_id: int,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(verificar_permiso("gestionar_usuarios")),
):
    conv = db.query(ChatConversacion).filter(ChatConversacion.id == conv_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")
    conv.estado = "finalizado"
    conv.updated_at = None
    db.commit()
    return {"mensaje": "Conversación finalizada"}

