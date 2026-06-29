from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, Literal
from datetime import date, time, datetime


class LoginRequest(BaseModel):
    cedula: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: "UsuarioOut"


class PermisoOut(BaseModel):
    id: int
    nombre: str
    codigo: str
    descripcion: Optional[str] = None

    class Config:
        from_attributes = True


class PerfilOut(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str] = None
    activo: bool
    permisos: list[PermisoOut] = []

    class Config:
        from_attributes = True


class PerfilCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    permisos_ids: list[int] = []


class PerfilUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    activo: Optional[bool] = None
    permisos_ids: Optional[list[int]] = None


class UsuarioCreate(BaseModel):
    nombres: str
    apellidos: str
    cedula: str
    email: str = ""
    celular: str
    password: str
    id_perfil: int

    @field_validator("cedula")
    @classmethod
    def validar_cedula(cls, v):
        if not v.strip():
            raise ValueError("La cédula es obligatoria")
        return v.strip()

    @field_validator("celular")
    @classmethod
    def validar_celular(cls, v):
        if len(v) < 7:
            raise ValueError("El celular debe tener al menos 7 dígitos")
        return v

    @field_validator("password")
    @classmethod
    def validar_password(cls, v):
        if len(v) < 6:
            raise ValueError("La contraseña debe tener al menos 6 caracteres")
        return v


class UsuarioUpdatePerfil(BaseModel):
    nombres: str
    apellidos: str
    email: str
    celular: str


class UsuarioUpdate(BaseModel):
    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    email: Optional[EmailStr] = None
    celular: Optional[str] = None
    id_perfil: Optional[int] = None
    activo: Optional[bool] = None


class UsuarioOut(BaseModel):
    id: int
    nombres: str
    apellidos: str
    cedula: str
    email: str
    celular: str
    id_perfil: int
    perfil: Optional[PerfilOut] = None
    email_verificado: bool
    celular_verificado: bool
    verificado_por_admin: bool
    foto_cedula: Optional[str] = None
    puntos_confianza: int
    activo: bool
    created_at: datetime

    class Config:
        from_attributes = True


class CategoriaOut(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str] = None
    activo: bool

    class Config:
        from_attributes = True


class CategoriaCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None


class CategoriaUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    activo: Optional[bool] = None


class CalidadOut(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str] = None
    activo: bool

    class Config:
        from_attributes = True


class CalidadCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None


class CalidadUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    activo: Optional[bool] = None


class ProductoOut(BaseModel):
    id: int
    nombre: str
    id_categoria: Optional[int] = None
    categoria: Optional[CategoriaOut] = None
    id_creador: Optional[int] = None
    unidad: str
    precio: Optional[float] = None
    foto_url: Optional[str] = None
    activo: bool

    class Config:
        from_attributes = True


class ProductoUpdate(BaseModel):
    nombre: Optional[str] = None
    id_categoria: Optional[int] = None
    unidad: Optional[str] = None
    precio: Optional[float] = None
    foto_url: Optional[str] = None
    activo: Optional[bool] = None


class ProductoCreate(BaseModel):
    nombre: str
    id_categoria: Optional[int] = None
    id_creador: Optional[int] = None
    unidad: str = "kg"
    precio: Optional[float] = None
    foto_url: Optional[str] = None


class PlazaOut(BaseModel):
    id: int
    nombre: str
    direccion: Optional[str] = None
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    activo: bool

    class Config:
        from_attributes = True


class PlazaUpdate(BaseModel):
    nombre: Optional[str] = None
    direccion: Optional[str] = None
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    activo: Optional[bool] = None


class PlazaCreate(BaseModel):
    nombre: str
    direccion: Optional[str] = None
    latitud: Optional[float] = None
    longitud: Optional[float] = None


class ViajeUbicacionOut(BaseModel):
    id: int
    id_plaza: Optional[int] = None
    plaza: Optional[PlazaOut] = None
    latitud: float
    longitud: float
    direccion: Optional[str] = None
    foto_url: Optional[str] = None
    activa: bool

    class Config:
        from_attributes = True


class ViajeUbicacionCreate(BaseModel):
    id_plaza: Optional[int] = None
    latitud: float
    longitud: float
    direccion: Optional[str] = None
    foto_url: Optional[str] = None


class ViajeUbicacionUpdate(BaseModel):
    id_plaza: Optional[int] = None
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    direccion: Optional[str] = None
    foto_url: Optional[str] = None


class OfertaFlashOut(BaseModel):
    id: int
    id_viaje_producto: int
    descuento_porcentaje: float
    precio_oferta: float
    cantidad_limite: Optional[float] = None
    activa: bool

    class Config:
        from_attributes = True


class ProductoFotoOut(BaseModel):
    id: int
    url: str
    orden: int

    class Config:
        from_attributes = True


class ViajeProductoOut(BaseModel):
    id: int
    id_producto: int
    producto: Optional[ProductoOut] = None
    id_calidad: Optional[int] = None
    precio: float
    cantidad_inicial: float
    cantidad_disponible: float
    activo: bool
    fotos: list[ProductoFotoOut] = []
    ofertas: list[OfertaFlashOut] = []

    class Config:
        from_attributes = True


class OfertaFlashFullOut(BaseModel):
    id: int
    descuento_porcentaje: float
    precio_oferta: float
    cantidad_limite: Optional[float] = None
    activa: Optional[bool] = True
    viaje_producto: Optional["ViajeProductoFullOut"] = None

    class Config:
        from_attributes = True


class ViajeProductoFullOut(BaseModel):
    id: int
    precio: float
    cantidad_disponible: float
    producto: Optional[ProductoOut] = None
    viaje: Optional["ViajeMiniOut"] = None

    class Config:
        from_attributes = True


class ViajeMiniOut(BaseModel):
    id: int
    fecha_viaje: date
    notas: Optional[str] = None
    ubicaciones: list[ViajeUbicacionOut] = []
    campesino: Optional[UsuarioOut] = None

    class Config:
        from_attributes = True


class ViajeProductoCreate(BaseModel):
    id_producto: int
    id_calidad: Optional[int] = None
    precio: float
    cantidad_inicial: float
    fotos: list[str] = []


class ViajeOut(BaseModel):
    id: int
    id_campesino: int
    campesino: Optional[UsuarioOut] = None
    fecha_viaje: date
    hora_inicio: Optional[time] = None
    hora_fin: Optional[time] = None
    notas: Optional[str] = None
    activo: bool
    ubicaciones: list[ViajeUbicacionOut] = []
    productos: list[ViajeProductoOut] = []
    created_at: datetime

    class Config:
        from_attributes = True


class ViajeCreate(BaseModel):
    fecha_viaje: date
    hora_inicio: Optional[time] = None
    hora_fin: Optional[time] = None
    notas: Optional[str] = None
    ubicaciones: list[ViajeUbicacionCreate] = []
    productos: list[ViajeProductoCreate] = []


class ViajeUpdate(BaseModel):
    fecha_viaje: Optional[date] = None
    hora_inicio: Optional[time] = None
    hora_fin: Optional[time] = None
    notas: Optional[str] = None
    activo: Optional[bool] = None


class PreordenOut(BaseModel):
    id: int
    id_viaje_producto: int
    id_consumidor: int
    cantidad: float
    estado: str
    viaje_producto: Optional[ViajeProductoOut] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PreordenCreate(BaseModel):
    id_viaje_producto: int
    cantidad: float


class ReseniaOut(BaseModel):
    id: int
    id_autor: int
    id_destino: int
    id_viaje: Optional[int] = None
    puntuacion: int
    comentario: Optional[str] = None
    respuesta: Optional[str] = None
    reportada: bool
    autor: Optional[UsuarioOut] = None
    destino: Optional[UsuarioOut] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ReseniaCreate(BaseModel):
    id_destino: int
    id_viaje: Optional[int] = None
    puntuacion: int
    comentario: Optional[str] = None

    @field_validator("puntuacion")
    @classmethod
    def validar_puntuacion(cls, v):
        if v < 1 or v > 5:
            raise ValueError("La puntuación debe estar entre 1 y 5")
        return v


class OfertaFlashCreate(BaseModel):
    descuento_porcentaje: float
    cantidad_limite: Optional[float] = None


class MapaFiltros(BaseModel):
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    radio_km: Optional[float] = 10
    id_categoria: Optional[int] = None
    id_producto: Optional[int] = None
    fecha: Optional[date] = None


class UsuarioRegister(BaseModel):
    nombres: str
    apellidos: str
    cedula: str
    email: str = ""
    celular: str
    password: str
    tipo: str = "consumidor"
    foto_cedula: str | None = None

    @field_validator("cedula")
    @classmethod
    def validar_cedula(cls, v):
        if not v.strip():
            raise ValueError("La cédula es obligatoria")
        return v.strip()

    @field_validator("celular")
    @classmethod
    def validar_celular(cls, v):
        if len(v) < 7:
            raise ValueError("El celular debe tener al menos 7 dígitos")
        return v

    @field_validator("password")
    @classmethod
    def validar_password(cls, v):
        if len(v) < 6:
            raise ValueError("La contraseña debe tener al menos 6 caracteres")
        return v

    @field_validator("tipo")
    @classmethod
    def validar_tipo(cls, v):
        if v not in ("campesino", "consumidor"):
            raise ValueError('El tipo debe ser "campesino" o "consumidor"')
        return v


class CambioPassword(BaseModel):
    password_actual: str
    password_nueva: str

    @field_validator("password_nueva")
    @classmethod
    def validar_nueva(cls, v):
        if len(v) < 6:
            raise ValueError("La nueva contraseña debe tener al menos 6 caracteres")
        return v


class TicketCreate(BaseModel):
    asunto: str
    mensaje: str


class TicketRespuestaCreate(BaseModel):
    mensaje: str


class TicketRespuestaOut(BaseModel):
    id: int
    id_ticket: int
    id_autor: int
    mensaje: str
    created_at: datetime
    autor: Optional[UsuarioOut] = None

    class Config:
        from_attributes = True


class TicketOut(BaseModel):
    id: int
    id_remitente: int
    asunto: str
    mensaje: str
    estado: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    remitente: Optional[UsuarioOut] = None
    respuestas: list[TicketRespuestaOut] = []

    class Config:
        from_attributes = True


class ChatConversacionCreate(BaseModel):
    nombre: str
    email: str = ""
    cedula: str = ""


class ChatMensajeCreate(BaseModel):
    mensaje: str


class ChatMensajeOut(BaseModel):
    id: int
    id_conversacion: int
    mensaje: str
    es_admin: bool
    id_admin: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ChatConversacionOut(BaseModel):
    id: int
    nombre: str
    email: str
    cedula: str
    id_usuario: Optional[int] = None
    session_token: str
    estado: str
    id_admin_asignado: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    mensajes: list[ChatMensajeOut] = []

    class Config:
        from_attributes = True


class ChatConversacionMiniOut(BaseModel):
    id: int
    nombre: str
    email: str
    cedula: str
    estado: str
    id_admin_asignado: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


OfertaFlashFullOut.model_rebuild()
ViajeProductoFullOut.model_rebuild()
ViajeMiniOut.model_rebuild()
