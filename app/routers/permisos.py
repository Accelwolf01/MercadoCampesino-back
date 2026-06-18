from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Permiso
from app.schemas import PermisoOut
from app.auth import verificar_permiso

router = APIRouter(prefix="/permisos", tags=["Permisos"])


@router.get("", response_model=list[PermisoOut])
def listar_permisos(
    db: Session = Depends(get_db),
    _=Depends(verificar_permiso("gestionar_roles")),
):
    return db.query(Permiso).order_by(Permiso.nombre).all()
