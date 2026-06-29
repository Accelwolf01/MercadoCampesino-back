from math import radians, cos, sin, asin, sqrt
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Viaje, ViajeUbicacion
from app.schemas import ViajeOut

router = APIRouter(prefix="/mapa", tags=["Mapa"])


def distancia_km(lat1, lon1, lat2, lon2):
    if not all([lat1, lon1, lat2, lon2]):
        return None
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return R * 2 * asin(sqrt(a))


@router.get("", response_model=list[ViajeOut])
def mapa_viajes(
    latitud: Optional[float] = Query(None),
    longitud: Optional[float] = Query(None),
    radio_km: Optional[float] = Query(10),
    db: Session = Depends(get_db),
):
    from config import bogota_today
    viajes = (
        db.query(Viaje)
        .filter(Viaje.fecha_viaje == bogota_today(), Viaje.activo == True)
        .all()
    )

    if latitud and longitud:
        viajes_filtrados = []
        for v in viajes:
            for u in v.ubicaciones:
                if not u.activa:
                    continue
                dist = distancia_km(latitud, longitud, float(u.latitud), float(u.longitud))
                if dist is not None and dist <= radio_km:
                    viajes_filtrados.append(v)
                    break
        return viajes_filtrados

    return viajes
