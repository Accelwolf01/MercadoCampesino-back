from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models import Ticket, TicketRespuesta, Usuario
from app.schemas import TicketCreate, TicketOut, TicketRespuestaCreate, TicketRespuestaOut
from app.auth import get_current_user

router = APIRouter(prefix="/soporte", tags=["Soporte"])

ESTADOS = ("abierto", "en_progreso", "finalizado")


def _load_ticket(db: Session, ticket_id: int):
    return (
        db.query(Ticket)
        .options(
            joinedload(Ticket.remitente),
            joinedload(Ticket.respuestas).joinedload(TicketRespuesta.autor),
        )
        .filter(Ticket.id == ticket_id)
        .first()
    )


@router.post("/tickets", response_model=TicketOut, status_code=201)
def crear_ticket(
    data: TicketCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    ticket = Ticket(id_remitente=usuario.id, asunto=data.asunto, mensaje=data.mensaje)
    db.add(ticket)
    db.commit()
    return _load_ticket(db, ticket.id)


@router.get("/tickets", response_model=list[TicketOut])
def listar_tickets(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    q = db.query(Ticket).options(
        joinedload(Ticket.remitente),
        joinedload(Ticket.respuestas).joinedload(TicketRespuesta.autor),
    )
    if usuario.id_perfil not in (1, 2):
        q = q.filter(Ticket.id_remitente == usuario.id)
    return q.order_by(Ticket.created_at.desc()).all()


@router.get("/tickets/pendientes", response_model=list[TicketOut])
def tickets_pendientes(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    if usuario.id_perfil not in (1, 2):
        raise HTTPException(status_code=403, detail="Solo administradores")
    return (
        db.query(Ticket)
        .options(
            joinedload(Ticket.remitente),
            joinedload(Ticket.respuestas).joinedload(TicketRespuesta.autor),
        )
        .filter(Ticket.estado != "finalizado")
        .order_by(Ticket.created_at.desc())
        .all()
    )


@router.put("/tickets/{ticket_id}/estado", response_model=TicketOut)
def cambiar_estado(
    ticket_id: int,
    nuevo_estado: str,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    if usuario.id_perfil not in (1, 2):
        raise HTTPException(status_code=403, detail="Solo administradores")
    if nuevo_estado not in ESTADOS:
        raise HTTPException(status_code=400, detail=f"Estado inválido. Usa: {', '.join(ESTADOS)}")
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")
    ticket.estado = nuevo_estado
    db.commit()
    return _load_ticket(db, ticket.id)


@router.post("/tickets/{ticket_id}/respuestas", response_model=TicketRespuestaOut, status_code=201)
def agregar_respuesta(
    ticket_id: int,
    data: TicketRespuestaCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")
    if ticket.id_remitente != usuario.id and usuario.id_perfil not in (1, 2):
        raise HTTPException(status_code=403, detail="No puedes responder este ticket")
    rta = TicketRespuesta(id_ticket=ticket.id, id_autor=usuario.id, mensaje=data.mensaje)
    db.add(rta)
    db.commit()
    db.refresh(rta)
    return rta


@router.get("/tickets/{ticket_id}/respuestas", response_model=list[TicketRespuestaOut])
def listar_respuestas(
    ticket_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")
    if ticket.id_remitente != usuario.id and usuario.id_perfil not in (1, 2):
        raise HTTPException(status_code=403, detail="No puedes ver este ticket")
    return (
        db.query(TicketRespuesta)
        .options(joinedload(TicketRespuesta.autor))
        .filter(TicketRespuesta.id_ticket == ticket_id)
        .order_by(TicketRespuesta.created_at)
        .all()
    )
