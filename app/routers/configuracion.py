from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Configuracion
from app.schemas import ConfiguracionOut, ConfiguracionUpdate
from app.auth import verificar_permiso

router = APIRouter(prefix="/configuracion", tags=["Configuración"])


@router.get("", response_model=list[ConfiguracionOut])
def listar_config(db: Session = Depends(get_db)):
    return db.query(Configuracion).order_by(Configuracion.clave).all()


@router.put("/{clave}", response_model=ConfiguracionOut)
def actualizar_config(
    clave: str,
    data: ConfiguracionUpdate,
    db: Session = Depends(get_db),
    _=Depends(verificar_permiso("gestionar_config")),
):
    conf = db.query(Configuracion).filter(Configuracion.clave == clave).first()
    if not conf:
        raise HTTPException(status_code=404, detail="Configuracion no encontrada")
    conf.valor = data.valor
    db.commit()
    db.refresh(conf)
    return conf
