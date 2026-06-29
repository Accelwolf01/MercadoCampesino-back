from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models import Resenia, Usuario, Perfil
from app.schemas import ReseniaOut, ReseniaCreate, UsuarioOut as ReseniaUsuarioOut
from app.auth import get_current_user, verificar_permiso

router = APIRouter(prefix="/resenias", tags=["Reseñas"])


@router.get("/mis-resenias", response_model=list[ReseniaOut])
def mis_resenias(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return (
        db.query(Resenia)
        .options(
            joinedload(Resenia.autor),
            joinedload(Resenia.destino),
        )
        .filter(Resenia.id_autor == usuario.id)
        .order_by(Resenia.created_at.desc())
        .all()
    )


@router.get("/usuario/{usuario_id}", response_model=list[ReseniaOut])
def resenias_de_usuario(usuario_id: int, db: Session = Depends(get_db)):
    return (
        db.query(Resenia)
        .options(
            joinedload(Resenia.autor),
            joinedload(Resenia.destino),
        )
        .filter(Resenia.id_destino == usuario_id)
        .order_by(Resenia.created_at.desc())
        .all()
    )


@router.get("/campesinos-activos", response_model=list[ReseniaUsuarioOut])
def campesinos_activos(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return (
        db.query(Usuario)
        .join(Usuario.perfil)
        .filter(Usuario.activo == True, Perfil.nombre == "campesino")
        .order_by(Usuario.nombres)
        .all()
    )


@router.post("", response_model=ReseniaOut, status_code=201)
def crear_resenia(
    data: ReseniaCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(verificar_permiso("dejar_resenia")),
):
    if data.id_destino == usuario.id:
        raise HTTPException(status_code=400, detail="No puedes hacerte una reseña a ti mismo")

    destino = db.query(Usuario).filter(Usuario.id == data.id_destino).first()
    if not destino:
        raise HTTPException(status_code=404, detail="Usuario destino no encontrado")

    resenia = Resenia(
        id_autor=usuario.id,
        id_destino=data.id_destino,
        id_viaje=data.id_viaje,
        puntuacion=data.puntuacion,
        comentario=data.comentario,
    )
    db.add(resenia)
    db.commit()
    resenia = (
        db.query(Resenia)
        .options(joinedload(Resenia.autor), joinedload(Resenia.destino))
        .filter(Resenia.id == resenia.id)
        .first()
    )
    return resenia


@router.put("/{resenia_id}/responder", response_model=ReseniaOut)
def responder_resenia(
    resenia_id: int,
    respuesta: str,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(verificar_permiso("responder_resenias")),
):
    res = db.query(Resenia).filter(Resenia.id == resenia_id).first()
    if not res or res.id_destino != usuario.id:
        raise HTTPException(status_code=404, detail="Reseña no encontrada")
    res.respuesta = respuesta
    db.commit()
    db.refresh(res)
    return res


@router.put("/{resenia_id}/reportar", response_model=ReseniaOut)
def reportar_resenia(
    resenia_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    res = db.query(Resenia).filter(Resenia.id == resenia_id).first()
    if not res:
        raise HTTPException(status_code=404, detail="Reseña no encontrada")
    res.reportada = True
    db.commit()
    db.refresh(res)
    return res


@router.get("/reportadas", response_model=list[ReseniaOut])
def resenias_reportadas(
    db: Session = Depends(get_db),
    _=Depends(verificar_permiso("moderar_resenias")),
):
    return (
        db.query(Resenia)
        .filter(Resenia.reportada == True)
        .order_by(Resenia.created_at.desc())
        .all()
    )


@router.delete("/{resenia_id}", status_code=204)
def eliminar_resenia(
    resenia_id: int,
    db: Session = Depends(get_db),
    _=Depends(verificar_permiso("moderar_resenias")),
):
    res = db.query(Resenia).filter(Resenia.id == resenia_id).first()
    if not res:
        raise HTTPException(status_code=404, detail="Reseña no encontrada")
    db.delete(res)
    db.commit()
