from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Numeric, Date, Time, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
from config import bogota_now


perfiles_permisos = Table(
    "perfiles_permisos", Base.metadata,
    Column("id_perfil", Integer, ForeignKey("perfiles.id", ondelete="CASCADE"), primary_key=True),
    Column("id_permiso", Integer, ForeignKey("permisos.id", ondelete="CASCADE"), primary_key=True),
)


class Perfil(Base):
    __tablename__ = "perfiles"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), unique=True, nullable=False)
    descripcion = Column(Text)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=bogota_now)
    updated_at = Column(DateTime, default=bogota_now, onupdate=bogota_now)

    usuarios = relationship("Usuario", back_populates="perfil", foreign_keys="Usuario.id_perfil")
    permisos = relationship("Permiso", secondary=perfiles_permisos, back_populates="perfiles")


class Permiso(Base):
    __tablename__ = "permisos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), unique=True, nullable=False)
    codigo = Column(String(100), unique=True, nullable=False)
    descripcion = Column(Text)
    created_at = Column(DateTime, default=bogota_now)

    perfiles = relationship("Perfil", secondary=perfiles_permisos, back_populates="permisos")


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombres = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    cedula = Column(String(20), unique=True, nullable=False)
    email = Column(String(150), default="", nullable=False)
    celular = Column(String(15), unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    id_perfil = Column(Integer, ForeignKey("perfiles.id"), nullable=False)
    email_verificado = Column(Boolean, default=False)
    celular_verificado = Column(Boolean, default=False)
    foto_cedula = Column(Text)
    verificado_por_admin = Column(Boolean, default=False)
    puntos_confianza = Column(Integer, default=100)
    activo = Column(Boolean, default=True)
    motivo_bloqueo = Column(Text)
    id_perfil_original = Column(Integer, ForeignKey("perfiles.id"))
    created_at = Column(DateTime, default=bogota_now)
    updated_at = Column(DateTime, default=bogota_now, onupdate=bogota_now)

    perfil = relationship("Perfil", back_populates="usuarios", foreign_keys=[id_perfil])
    perfil_original = relationship("Perfil", foreign_keys=[id_perfil_original], viewonly=True)
    viajes = relationship("Viaje", back_populates="campesino", foreign_keys="Viaje.id_campesino")


class Categoria(Base):
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), unique=True, nullable=False)
    descripcion = Column(Text)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=bogota_now)

    productos = relationship("Producto", back_populates="categoria")


class Calidad(Base):
    __tablename__ = "calidades"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), unique=True, nullable=False)
    descripcion = Column(Text)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=bogota_now)


class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    id_categoria = Column(Integer, ForeignKey("categorias.id"))
    id_creador = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    unidad = Column(String(20), default="kg")
    precio = Column(Numeric(12, 2), nullable=True)
    foto_url = Column(Text)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=bogota_now)

    categoria = relationship("Categoria", back_populates="productos")
    creador = relationship("Usuario")


class Plaza(Base):
    __tablename__ = "plazas"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), unique=True, nullable=False)
    direccion = Column(Text)
    latitud = Column(Numeric(10, 7))
    longitud = Column(Numeric(10, 7))
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=bogota_now)


class Viaje(Base):
    __tablename__ = "viajes"

    id = Column(Integer, primary_key=True, index=True)
    id_campesino = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    fecha_viaje = Column(Date, nullable=False)
    hora_inicio = Column(Time)
    hora_fin = Column(Time)
    notas = Column(Text)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=bogota_now)
    updated_at = Column(DateTime, default=bogota_now, onupdate=bogota_now)

    campesino = relationship("Usuario", back_populates="viajes", foreign_keys=[id_campesino])
    ubicaciones = relationship("ViajeUbicacion", back_populates="viaje", cascade="all, delete-orphan")
    productos = relationship("ViajeProducto", back_populates="viaje", cascade="all, delete-orphan")


class ViajeUbicacion(Base):
    __tablename__ = "viaje_ubicaciones"

    id = Column(Integer, primary_key=True, index=True)
    id_viaje = Column(Integer, ForeignKey("viajes.id", ondelete="CASCADE"), nullable=False)
    id_plaza = Column(Integer, ForeignKey("plazas.id"))
    latitud = Column(Numeric(10, 7), nullable=False)
    longitud = Column(Numeric(10, 7), nullable=False)
    direccion = Column(Text)
    foto_url = Column(Text)
    activa = Column(Boolean, default=True)
    created_at = Column(DateTime, default=bogota_now)

    viaje = relationship("Viaje", back_populates="ubicaciones")
    plaza = relationship("Plaza")


class ViajeProducto(Base):
    __tablename__ = "viaje_productos"

    id = Column(Integer, primary_key=True, index=True)
    id_viaje = Column(Integer, ForeignKey("viajes.id", ondelete="CASCADE"), nullable=False)
    id_producto = Column(Integer, ForeignKey("productos.id"), nullable=False)
    id_calidad = Column(Integer, ForeignKey("calidades.id"))
    precio = Column(Numeric(12, 2), nullable=False)
    cantidad_inicial = Column(Numeric(12, 2), nullable=False)
    cantidad_disponible = Column(Numeric(12, 2), nullable=False)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=bogota_now)
    updated_at = Column(DateTime, default=bogota_now, onupdate=bogota_now)

    viaje = relationship("Viaje", back_populates="productos")
    producto = relationship("Producto")
    calidad = relationship("Calidad")
    ofertas = relationship("OfertaFlash", back_populates="viaje_producto", cascade="all, delete-orphan")
    fotos = relationship("ProductoFoto", back_populates="viaje_producto", cascade="all, delete-orphan")


class ProductoFoto(Base):
    __tablename__ = "producto_fotos"

    id = Column(Integer, primary_key=True, index=True)
    id_viaje_producto = Column(Integer, ForeignKey("viaje_productos.id", ondelete="CASCADE"), nullable=False)
    url = Column(Text, nullable=False)
    orden = Column(Integer, default=0)
    created_at = Column(DateTime, default=bogota_now)

    viaje_producto = relationship("ViajeProducto", back_populates="fotos")


class Preorden(Base):
    __tablename__ = "preordenes"

    id = Column(Integer, primary_key=True, index=True)
    id_viaje_producto = Column(Integer, ForeignKey("viaje_productos.id"), nullable=False)
    id_consumidor = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    cantidad = Column(Numeric(12, 2), nullable=False)
    estado = Column(String(20), default="pendiente")
    created_at = Column(DateTime, default=bogota_now)
    updated_at = Column(DateTime, default=bogota_now, onupdate=bogota_now)

    viaje_producto = relationship("ViajeProducto")
    consumidor = relationship("Usuario")


class Resenia(Base):
    __tablename__ = "resenias"

    id = Column(Integer, primary_key=True, index=True)
    id_autor = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    id_destino = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    id_viaje = Column(Integer, ForeignKey("viajes.id"))
    puntuacion = Column(Integer, nullable=False)
    comentario = Column(Text)
    respuesta = Column(Text)
    reportada = Column(Boolean, default=False)
    created_at = Column(DateTime, default=bogota_now)

    autor = relationship("Usuario", foreign_keys=[id_autor])
    destino = relationship("Usuario", foreign_keys=[id_destino])


class OfertaFlash(Base):
    __tablename__ = "ofertas_flash"

    id = Column(Integer, primary_key=True, index=True)
    id_viaje_producto = Column(Integer, ForeignKey("viaje_productos.id"), nullable=False)
    descuento_porcentaje = Column(Numeric(5, 2), nullable=False)
    precio_oferta = Column(Numeric(12, 2), nullable=False)
    cantidad_limite = Column(Numeric(12, 2))
    activa = Column(Boolean, default=True)
    created_at = Column(DateTime, default=bogota_now)
    updated_at = Column(DateTime, default=bogota_now, onupdate=bogota_now)

    viaje_producto = relationship("ViajeProducto", back_populates="ofertas")


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    id_remitente = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    asunto = Column(String(200), nullable=False)
    mensaje = Column(Text, nullable=False)
    estado = Column(String(20), default="abierto")
    created_at = Column(DateTime, default=bogota_now)
    updated_at = Column(DateTime, default=bogota_now, onupdate=bogota_now)

    remitente = relationship("Usuario", foreign_keys=[id_remitente])
    respuestas = relationship("TicketRespuesta", back_populates="ticket", cascade="all, delete-orphan", order_by="TicketRespuesta.created_at")


class TicketRespuesta(Base):
    __tablename__ = "ticket_respuestas"

    id = Column(Integer, primary_key=True, index=True)
    id_ticket = Column(Integer, ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False)
    id_autor = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    mensaje = Column(Text, nullable=False)
    created_at = Column(DateTime, default=bogota_now)

    ticket = relationship("Ticket", back_populates="respuestas")
    autor = relationship("Usuario", foreign_keys=[id_autor])


class ChatConversacion(Base):
    __tablename__ = "chat_conversaciones"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(200), nullable=False)
    email = Column(String(200), default="")
    cedula = Column(String(20), default="")
    id_usuario = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    session_token = Column(String(100), nullable=False, index=True)
    estado = Column(String(20), default="abierto")
    id_admin_asignado = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    created_at = Column(DateTime, default=bogota_now)
    updated_at = Column(DateTime, default=bogota_now, onupdate=bogota_now)

    usuario = relationship("Usuario", foreign_keys=[id_usuario])
    admin_asignado = relationship("Usuario", foreign_keys=[id_admin_asignado])
    mensajes = relationship("ChatMensaje", back_populates="conversacion", cascade="all, delete-orphan", order_by="ChatMensaje.created_at")


class ChatMensaje(Base):
    __tablename__ = "chat_mensajes"

    id = Column(Integer, primary_key=True, index=True)
    id_conversacion = Column(Integer, ForeignKey("chat_conversaciones.id", ondelete="CASCADE"), nullable=False)
    mensaje = Column(Text, nullable=False)
    es_admin = Column(Boolean, default=False)
    id_admin = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    created_at = Column(DateTime, default=bogota_now)

    conversacion = relationship("ChatConversacion", back_populates="mensajes")
    admin = relationship("Usuario", foreign_keys=[id_admin])


class Configuracion(Base):
    __tablename__ = "configuracion"

    clave = Column(String(100), primary_key=True, index=True)
    valor = Column(String(500), nullable=False)
    descripcion = Column(Text, nullable=True)
    created_at = Column(DateTime, default=bogota_now)
    updated_at = Column(DateTime, default=bogota_now, onupdate=bogota_now)
