from sqlalchemy.orm import Session
from app.models import Perfil, Permiso, perfiles_permisos, Usuario, Categoria
from app.database import engine, Base
import bcrypt


def init_db():
    Base.metadata.create_all(bind=engine)


def seed_data(db: Session):
    if db.query(Perfil).count() > 0:
        return

    perfiles_data = [
        {"nombre": "superadmin", "descripcion": "Superadministrador del sistema"},
        {"nombre": "admin", "descripcion": "Administrador de la plataforma"},
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
        {"id_perfil": perfiles["admin"].id, "id_permiso": permisos["verificar_usuarios"].id},
        {"id_perfil": perfiles["admin"].id, "id_permiso": permisos["gestionar_categorias"].id},
        {"id_perfil": perfiles["admin"].id, "id_permiso": permisos["ver_reportes"].id},
    ]))

    password_hash = bcrypt.hashpw(b"SuperAdmin2026!", bcrypt.gensalt()).decode()

    usuarios_data = [
        {"nombre": "Super Admin", "email": "superadmin@mercadocampesino.co", "password": password_hash, "id_perfil": perfiles["superadmin"].id, "activo": True, "verificado_por_admin": True, "telefono": "3000000000"},
        {"nombre": "Carlos Campesino", "email": "carlos@campesino.co", "password": password_hash, "id_perfil": perfiles["campesino"].id, "activo": True, "verificado_por_admin": True, "telefono": "3001111111"},
        {"nombre": "Ana Consumidora", "email": "ana@consumidor.co", "password": password_hash, "id_perfil": perfiles["consumidor"].id, "activo": True, "verificado_por_admin": True, "telefono": "3002222222"},
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
