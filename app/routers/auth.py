from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models import Usuario, Perfil
from app.schemas import (
    LoginRequest, TokenResponse, UsuarioOut,
    UsuarioRegister, CambioPassword, UsuarioUpdatePerfil,
)
from app.auth import verify_password, create_access_token, get_current_user, hash_password

router = APIRouter(prefix="/auth", tags=["Autenticación"])


class RegistroResponse(BaseModel):
    mensaje: str
    pendiente_verificacion: bool = False


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.cedula == req.cedula).first()
    if not usuario or not verify_password(req.password, usuario.password_hash):
        raise HTTPException(status_code=401, detail="Cédula o contraseña incorrectos")
    if usuario.id_perfil == 5 or usuario.motivo_bloqueo is not None:
        raise HTTPException(status_code=403, detail="Cuenta bloqueada. No tienes permitido iniciar sesión.")
    if not usuario.activo:
        raise HTTPException(status_code=403, detail="Cuenta pendiente de verificación por un administrador")

    token = create_access_token({"sub": str(usuario.id)})

    return TokenResponse(
        access_token=token,
        usuario=UsuarioOut.model_validate(usuario),
    )


@router.post("/registro", status_code=201)
def registro(data: UsuarioRegister, db: Session = Depends(get_db)):
    if db.query(Usuario).filter(Usuario.cedula == data.cedula).first():
        raise HTTPException(status_code=400, detail="Esta cédula ya está registrada")
    if db.query(Usuario).filter(Usuario.celular == data.celular).first():
        raise HTTPException(status_code=400, detail="Este celular ya está registrado")

    perfil = db.query(Perfil).filter(Perfil.nombre == data.tipo).first()
    if not perfil:
        raise HTTPException(status_code=400, detail="Tipo de perfil no válido")

    usuario = Usuario(
        nombres=data.nombres,
        apellidos=data.apellidos,
        cedula=data.cedula,
        email=data.email,
        celular=data.celular,
        password_hash=hash_password(data.password),
        id_perfil=perfil.id,
        foto_cedula=data.foto_cedula,
        activo=False,
        verificado_por_admin=False,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    return RegistroResponse(
        mensaje="Registro exitoso. Un administrador revisará y activará tu cuenta en las próximas 24 horas.",
        pendiente_verificacion=True,
    )


@router.get("/me", response_model=UsuarioOut)
def yo_mismo(usuario: Usuario = Depends(get_current_user)):
    return UsuarioOut.model_validate(usuario)


@router.put("/me", response_model=UsuarioOut)
def actualizar_perfil(
    data: UsuarioUpdatePerfil,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    if db.query(Usuario).filter(Usuario.celular == data.celular, Usuario.id != usuario.id).first():
        raise HTTPException(status_code=400, detail="El celular ya está en uso por otro usuario")
    usuario.nombres = data.nombres
    usuario.apellidos = data.apellidos
    usuario.email = data.email
    usuario.celular = data.celular
    db.commit()
    db.refresh(usuario)
    return UsuarioOut.model_validate(usuario)


@router.put("/cambiar-password")
def cambiar_password(
    data: CambioPassword,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    if not verify_password(data.password_actual, usuario.password_hash):
        raise HTTPException(status_code=400, detail="Contraseña actual incorrecta")
    usuario.password_hash = hash_password(data.password_nueva)
    db.commit()
    return {"mensaje": "Contraseña actualizada correctamente"}
