from sqlalchemy.orm import Session
from app.models import Perfil, Permiso, perfiles_permisos, Usuario, Categoria
from app.database import engine, Base
import bcrypt


def init_db():
    Base.metadata.create_all(bind=engine)


PERMISOS_FALTANTES = [
    {"nombre": "Realizar preorden", "codigo": "realizar_preorden", "descripcion": "Apartar productos antes de ir a la plaza"},
    {"nombre": "Ver preordenes", "codigo": "ver_preordenes", "descripcion": "Ver pedidos apartados por consumidores"},
    {"nombre": "Dejar resena", "codigo": "dejar_resenia", "descripcion": "Calificar y comentar al campesino"},
    {"nombre": "Ver historial compras", "codigo": "ver_historial_compras", "descripcion": "Consultar pedidos realizados"},
]


def _agregar_permisos_faltantes(db: Session):
    for pdata in PERMISOS_FALTANTES:
        existente = db.query(Permiso).filter(Permiso.codigo == pdata["codigo"]).first()
        if not existente:
            permiso = Permiso(**pdata)
            db.add(permiso)
            db.flush()
            superadmin = db.query(Perfil).filter(Perfil.nombre == "superadmin").first()
            if superadmin:
                db.execute(perfiles_permisos.insert().values(id_perfil=superadmin.id, id_permiso=permiso.id))
            if pdata["codigo"] == "ver_preordenes":
                campesino = db.query(Perfil).filter(Perfil.nombre == "campesino").first()
                if campesino:
                    db.execute(perfiles_permisos.insert().values(id_perfil=campesino.id, id_permiso=permiso.id))
            if pdata["codigo"] == "realizar_preorden":
                for nombre in ("consumidor", "administrador", "campesino"):
                    p = db.query(Perfil).filter(Perfil.nombre == nombre).first()
                    if p:
                        db.execute(perfiles_permisos.insert().values(id_perfil=p.id, id_permiso=permiso.id))
            if pdata["codigo"] == "dejar_resenia":
                for nombre in ("consumidor", "administrador", "campesino"):
                    p = db.query(Perfil).filter(Perfil.nombre == nombre).first()
                    if p:
                        db.execute(perfiles_permisos.insert().values(id_perfil=p.id, id_permiso=permiso.id))
            if pdata["codigo"] == "ver_historial_compras":
                for nombre in ("consumidor", "administrador", "campesino"):
                    p = db.query(Perfil).filter(Perfil.nombre == nombre).first()
                    if p:
                        db.execute(perfiles_permisos.insert().values(id_perfil=p.id, id_permiso=permiso.id))
    db.commit()


def seed_data(db: Session):
    if db.query(Perfil).count() > 0:
        _agregar_permisos_faltantes(db)
        return

    perfiles_data = [
        {"nombre": "superadmin", "descripcion": "Superadministrador del sistema"},
        {"nombre": "administrador", "descripcion": "Administrador de la plataforma"},
        {"nombre": "campesino", "descripcion": "Campesino vendedor"},
        {"nombre": "consumidor", "descripcion": "Consumidor comprador"},
        {"nombre": "bloqueado", "descripcion": "Usuario bloqueado"},
    ]
    perfiles = {}
    for p in perfiles_data:
        perfil = Perfil(**p)
        db.add(perfil)
        db.flush()
        perfiles[p["nombre"]] = perfil

    permisos_data = [
        {"nombre": "Verificar usuarios", "codigo": "verificar_usuarios", "descripcion": "Verificar y aprobar nuevos usuarios"},
        {"nombre": "Gestionar categorias", "codigo": "gestionar_categorias", "descripcion": "Crear, activar y desactivar categorias"},
        {"nombre": "Gestionar perfiles", "codigo": "gestionar_perfiles", "descripcion": "Crear y modificar perfiles"},
        {"nombre": "Gestionar permisos", "codigo": "gestionar_permisos", "descripcion": "Asignar permisos a perfiles"},
        {"nombre": "Ver reportes", "codigo": "ver_reportes", "descripcion": "Ver reportes del sistema"},
        {"nombre": "Gestionar config", "codigo": "gestionar_config", "descripcion": "Gestionar configuracion del sistema"},
        {"nombre": "Realizar preorden", "codigo": "realizar_preorden", "descripcion": "Apartar productos antes de ir a la plaza"},
        {"nombre": "Ver preordenes", "codigo": "ver_preordenes", "descripcion": "Ver pedidos apartados por consumidores"},
    ]
    permisos = {}
    for perm in permisos_data:
        p = Permiso(**perm)
        db.add(p)
        db.flush()
        permisos[perm["codigo"]] = p

    db.execute(perfiles_permisos.insert().values([
        {"id_perfil": perfiles["superadmin"].id, "id_permiso": permisos["verificar_usuarios"].id},
        {"id_perfil": perfiles["superadmin"].id, "id_permiso": permisos["gestionar_categorias"].id},
        {"id_perfil": perfiles["superadmin"].id, "id_permiso": permisos["gestionar_perfiles"].id},
        {"id_perfil": perfiles["superadmin"].id, "id_permiso": permisos["gestionar_permisos"].id},
        {"id_perfil": perfiles["superadmin"].id, "id_permiso": permisos["ver_reportes"].id},
        {"id_perfil": perfiles["superadmin"].id, "id_permiso": permisos["gestionar_config"].id},
        {"id_perfil": perfiles["superadmin"].id, "id_permiso": permisos["realizar_preorden"].id},
        {"id_perfil": perfiles["superadmin"].id, "id_permiso": permisos["ver_preordenes"].id},
        {"id_perfil": perfiles["administrador"].id, "id_permiso": permisos["verificar_usuarios"].id},
        {"id_perfil": perfiles["administrador"].id, "id_permiso": permisos["gestionar_categorias"].id},
        {"id_perfil": perfiles["administrador"].id, "id_permiso": permisos["ver_reportes"].id},
        {"id_perfil": perfiles["campesino"].id, "id_permiso": permisos["ver_preordenes"].id},
        {"id_perfil": perfiles["consumidor"].id, "id_permiso": permisos["realizar_preorden"].id},
    ]))

    password_hash = bcrypt.hashpw(b"SuperAdmin2026!", bcrypt.gensalt()).decode()

    usuarios_data = [
        {"nombres": "Super", "apellidos": "Admin", "cedula": "0000000001", "email": "superadmin@mercadocampesino.co", "celular": "3000000001", "password_hash": password_hash, "id_perfil": perfiles["superadmin"].id, "activo": True, "verificado_por_admin": True},
        {"nombres": "Admin", "apellidos": "Principal", "cedula": "0000000002", "email": "admin@mercadocampesino.co", "celular": "3000000002", "password_hash": password_hash, "id_perfil": perfiles["administrador"].id, "activo": True, "verificado_por_admin": True},
        {"nombres": "Carlos", "apellidos": "Campesino", "cedula": "123456789", "email": "carlos@campesino.co", "celular": "3001111111", "password_hash": password_hash, "id_perfil": perfiles["campesino"].id, "activo": True, "verificado_por_admin": True},
        {"nombres": "Ana", "apellidos": "Consumidora", "cedula": "987654321", "email": "ana@consumidor.co", "celular": "3002222222", "password_hash": password_hash, "id_perfil": perfiles["consumidor"].id, "activo": True, "verificado_por_admin": True},
    ]
    for u in usuarios_data:
        db.add(Usuario(**u))

    categorias_data = [
        {"nombre": "Frutas", "descripcion": "Frutas frescas", "activo": True},
        {"nombre": "Verduras", "descripcion": "Verduras y hortalizas", "activo": True},
        {"nombre": "Lacteos", "descripcion": "Leche, queso, yogurt", "activo": True},
        {"nombre": "Huevos", "descripcion": "Huevos de campo", "activo": True},
        {"nombre": "Miel", "descripcion": "Miel de abeja pura", "activo": True},
        {"nombre": "Carnes", "descripcion": "Carnes frescas", "activo": True},
        {"nombre": "Granos", "descripcion": "Granos y legumbres", "activo": True},
        {"nombre": "Panaderia", "descripcion": "Pan artesanal", "activo": False},
    ]
    for cat in categorias_data:
        db.add(Categoria(**cat))

    db.commit()
