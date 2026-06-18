from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Perfil, Permiso
from app.schemas import PerfilCreate, PerfilUpdate, PerfilOut
from app.auth import verificar_permiso

router = APIRouter(prefix="/perfiles", tags=["Perfiles"])


@router.get("", response_model=list[PerfilOut])
def listar_perfiles(
    db: Session = Depends(get_db),
    _=Depends(verificar_permiso("gestionar_roles")),
):
    return db.query(Perfil).all()


@router.get("/{perfil_id}", response_model=PerfilOut)
def obtener_perfil(
    perfil_id: int,
    db: Session = Depends(get_db),
    _=Depends(verificar_permiso("gestionar_roles")),
):
    perfil = db.query(Perfil).filter(Perfil.id == perfil_id).first()
    if not perfil:
        raise HTTPException(status_code=404, detail="Perfil no encontrado")
    return perfil


@router.post("", response_model=PerfilOut, status_code=201)
def crear_perfil(
    data: PerfilCreate,
    db: Session = Depends(get_db),
    _=Depends(verificar_permiso("gestionar_roles")),
):
    if db.query(Perfil).filter(Perfil.nombre == data.nombre).first():
        raise HTTPException(status_code=400, detail="Ya existe un perfil con ese nombre")

    perfil = Perfil(nombre=data.nombre, descripcion=data.descripcion)
    db.add(perfil)
    db.flush()

    if data.permisos_ids:
        permisos = db.query(Permiso).filter(Permiso.id.in_(data.permisos_ids)).all()
        perfil.permisos = permisos

    db.commit()
    db.refresh(perfil)
    return perfil


@router.put("/{perfil_id}", response_model=PerfilOut)
def actualizar_perfil(
    perfil_id: int,
    data: PerfilUpdate,
    db: Session = Depends(get_db),
    _=Depends(verificar_permiso("gestionar_roles")),
):
    perfil = db.query(Perfil).filter(Perfil.id == perfil_id).first()
    if not perfil:
        raise HTTPException(status_code=404, detail="Perfil no encontrado")

    update_data = data.model_dump(exclude_unset=True)
    permisos_ids = update_data.pop("permisos_ids", None)

    for key, value in update_data.items():
        setattr(perfil, key, value)

    if permisos_ids is not None:
        permisos = db.query(Permiso).filter(Permiso.id.in_(permisos_ids)).all()
        perfil.permisos = permisos

    db.commit()
    db.refresh(perfil)
    return perfil


@router.delete("/{perfil_id}", status_code=204)
def eliminar_perfil(
    perfil_id: int,
    db: Session = Depends(get_db),
    _=Depends(verificar_permiso("gestionar_roles")),
):
    from app.models import Usuario
    perfil = db.query(Perfil).filter(Perfil.id == perfil_id).first()
    if not perfil:
        raise HTTPException(status_code=404, detail="Perfil no encontrado")
    if perfil.nombre in ("superadmin", "bloqueado"):
        raise HTTPException(status_code=400, detail="No se puede eliminar este perfil")

    usuarios = db.query(Usuario).filter(Usuario.id_perfil == perfil_id).count()
    if usuarios > 0:
        raise HTTPException(status_code=400, detail="Hay usuarios usando este perfil. Reasígnelos primero")

    db.delete(perfil)
    db.commit()


@router.post("/{perfil_id}/permisos", status_code=201)
def asignar_permiso(
    perfil_id: int,
    data: dict,
    db: Session = Depends(get_db),
    _=Depends(verificar_permiso("gestionar_roles")),
):
    perfil = db.query(Perfil).filter(Perfil.id == perfil_id).first()
    if not perfil:
        raise HTTPException(status_code=404, detail="Perfil no encontrado")
    permiso = db.query(Permiso).filter(Permiso.id == data.get("id_permiso")).first()
    if not permiso:
        raise HTTPException(status_code=404, detail="Permiso no encontrado")
    if permiso not in perfil.permisos:
        perfil.permisos.append(permiso)
    db.commit()
    return {"mensaje": "Permiso asignado"}


@router.delete("/{perfil_id}/permisos/{permiso_id}", status_code=204)
def remover_permiso(
    perfil_id: int,
    permiso_id: int,
    db: Session = Depends(get_db),
    _=Depends(verificar_permiso("gestionar_roles")),
):
    perfil = db.query(Perfil).filter(Perfil.id == perfil_id).first()
    if not perfil:
        raise HTTPException(status_code=404, detail="Perfil no encontrado")
    permiso = db.query(Permiso).filter(Permiso.id == permiso_id).first()
    if not permiso:
        raise HTTPException(status_code=404, detail="Permiso no encontrado")
    if permiso in perfil.permisos:
        perfil.permisos.remove(permiso)
    db.commit()
