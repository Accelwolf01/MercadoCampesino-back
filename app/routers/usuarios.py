from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Usuario, Perfil
from app.schemas import UsuarioCreate, UsuarioUpdate, UsuarioOut
from pydantic import BaseModel


class ResetPasswordBody(BaseModel):
    nueva_password: str
from app.auth import hash_password, verificar_permiso

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


@router.get("", response_model=list[UsuarioOut])
def listar_usuarios(
    db: Session = Depends(get_db),
    _=Depends(verificar_permiso("gestionar_usuarios")),
):
    return db.query(Usuario).all()


@router.get("/{usuario_id}", response_model=UsuarioOut)
def obtener_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    _=Depends(verificar_permiso("gestionar_usuarios")),
):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario


@router.post("", response_model=UsuarioOut, status_code=201)
def crear_usuario(
    data: UsuarioCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(verificar_permiso("gestionar_usuarios")),
):
    if db.query(Usuario).filter(
        (Usuario.email == data.email) | (Usuario.cedula == data.cedula)
    ).first():
        raise HTTPException(status_code=400, detail="Email o cédula ya registrados")

    perfil = db.query(Perfil).filter(Perfil.id == data.id_perfil).first()
    if not perfil:
        raise HTTPException(status_code=400, detail="Perfil no válido")

    if perfil.nombre == "superadmin" and usuario_actual.id_perfil != 1:
        raise HTTPException(status_code=403, detail="Solo un superadmin puede crear otro superadmin")
    if perfil.nombre == "admin" and usuario_actual.id_perfil not in (1, 2):
        raise HTTPException(status_code=403, detail="Solo un admin o superadmin puede crear un admin")

    usuario = Usuario(
        nombres=data.nombres,
        apellidos=data.apellidos,
        cedula=data.cedula,
        email=data.email,
        celular=data.celular,
        password_hash=hash_password(data.password),
        id_perfil=data.id_perfil,
        verificado_por_admin=True,
        activo=True,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


@router.put("/{usuario_id}", response_model=UsuarioOut)
def actualizar_usuario(
    usuario_id: int,
    data: UsuarioUpdate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(verificar_permiso("gestionar_usuarios")),
):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    update_data = data.model_dump(exclude_unset=True)

    if "id_perfil" in update_data:
        perfil = db.query(Perfil).filter(Perfil.id == update_data["id_perfil"]).first()
        if not perfil:
            raise HTTPException(status_code=400, detail="Perfil no válido")
        if perfil.nombre == "superadmin" and usuario_actual.id_perfil != 1:
            raise HTTPException(status_code=403, detail="Solo un superadmin puede asignar el perfil superadmin")
        if perfil.nombre == "admin" and usuario_actual.id_perfil not in (1, 2):
            raise HTTPException(status_code=403, detail="Solo un admin o superadmin puede asignar el perfil admin")

    for key, value in update_data.items():
        setattr(usuario, key, value)

    db.commit()
    db.refresh(usuario)
    return usuario


@router.delete("/{usuario_id}", status_code=204)
def eliminar_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    _=Depends(verificar_permiso("gestionar_usuarios")),
):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    db.delete(usuario)
    db.commit()


@router.get("/pendientes/verificacion", response_model=list[UsuarioOut])
def pendientes_verificacion(
    db: Session = Depends(get_db),
    _=Depends(verificar_permiso("verificar_campesinos")),
):
    return (
        db.query(Usuario)
        .filter(
            Usuario.verificado_por_admin == False,
            Usuario.activo == False,
        )
        .order_by(Usuario.created_at)
        .all()
    )


@router.put("/{usuario_id}/verificar", response_model=UsuarioOut)
def verificar_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    _=Depends(verificar_permiso("verificar_campesinos")),
):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    usuario.verificado_por_admin = True
    usuario.activo = True
    db.commit()
    db.refresh(usuario)
    return usuario


@router.put("/{usuario_id}/bloquear", response_model=UsuarioOut)
def bloquear_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    _=Depends(verificar_permiso("gestionar_usuarios")),
):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    perfil_bloqueado = db.query(Perfil).filter(Perfil.nombre == "bloqueado").first()
    usuario.id_perfil = perfil_bloqueado.id
    usuario.activo = True
    db.commit()
    db.refresh(usuario)
    return usuario


@router.put("/{usuario_id}/activar", response_model=UsuarioOut)
def activar_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    _=Depends(verificar_permiso("gestionar_usuarios")),
):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if usuario.perfil.nombre != "bloqueado":
        raise HTTPException(status_code=400, detail="El usuario no está bloqueado")
    perfil_consumidor = db.query(Perfil).filter(Perfil.nombre == "consumidor").first()
    usuario.id_perfil = perfil_consumidor.id
    db.commit()
    db.refresh(usuario)
    return usuario


@router.put("/{usuario_id}/reset-password")
def reset_password(
    usuario_id: int,
    body: ResetPasswordBody,
    db: Session = Depends(get_db),
    _=Depends(verificar_permiso("gestionar_usuarios")),
):
    if len(body.nueva_password) < 6:
        raise HTTPException(status_code=400, detail="La contraseña debe tener al menos 6 caracteres")
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    usuario.password_hash = hash_password(body.nueva_password)
    db.commit()
    return {"mensaje": "Contraseña restablecida correctamente"}
