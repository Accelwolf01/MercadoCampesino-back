-- ============================================================
-- MERCADOCAMPESINO - Inicialización de Base de Datos
-- PostgreSQL
-- ============================================================

-- ============================================================
-- ELIMINAR TODO Y RECREAR (solo para desarrollo)
-- ============================================================
DROP TABLE IF EXISTS chat_mensajes CASCADE;
DROP TABLE IF EXISTS chat_conversaciones CASCADE;
DROP TABLE IF EXISTS producto_fotos CASCADE;
DROP TABLE IF EXISTS ofertas_flash CASCADE;
DROP TABLE IF EXISTS resenias CASCADE;
DROP TABLE IF EXISTS preordenes CASCADE;
DROP TABLE IF EXISTS viaje_productos CASCADE;
DROP TABLE IF EXISTS viaje_ubicaciones CASCADE;
DROP TABLE IF EXISTS ticket_respuestas CASCADE;
DROP TABLE IF EXISTS tickets CASCADE;
DROP TABLE IF EXISTS viajes CASCADE;
DROP TABLE IF EXISTS plazas CASCADE;
DROP TABLE IF EXISTS productos CASCADE;
DROP TABLE IF EXISTS calidades CASCADE;
DROP TABLE IF EXISTS categorias CASCADE;
DROP TABLE IF EXISTS usuarios CASCADE;
DROP TABLE IF EXISTS perfiles_permisos CASCADE;
DROP TABLE IF EXISTS permisos CASCADE;
DROP TABLE IF EXISTS perfiles CASCADE;

-- ============================================================
-- TABLAS
-- ============================================================

-- Perfiles (roles)
CREATE TABLE perfiles (
  id         SERIAL       PRIMARY KEY,
  nombre     VARCHAR(50)  NOT NULL UNIQUE,
  descripcion TEXT,
  activo     BOOLEAN      NOT NULL DEFAULT TRUE,
  created_at TIMESTAMP    NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP    NOT NULL DEFAULT NOW()
);

-- Permisos individuales
CREATE TABLE permisos (
  id          SERIAL       PRIMARY KEY,
  nombre      VARCHAR(100) NOT NULL UNIQUE,
  codigo      VARCHAR(100) NOT NULL UNIQUE,
  descripcion TEXT,
  created_at  TIMESTAMP    NOT NULL DEFAULT NOW()
);

-- Relacin muchos a muchos: perfil -> permisos
CREATE TABLE perfiles_permisos (
  id_perfil  INT NOT NULL REFERENCES perfiles(id) ON DELETE CASCADE,
  id_permiso INT NOT NULL REFERENCES permisos(id) ON DELETE CASCADE,
  PRIMARY KEY (id_perfil, id_permiso)
);

-- Usuarios
CREATE TABLE usuarios (
  id              SERIAL       PRIMARY KEY,
  nombres         VARCHAR(100) NOT NULL,
  apellidos       VARCHAR(100) NOT NULL,
  cedula          VARCHAR(20)  NOT NULL UNIQUE,
  email           VARCHAR(150) NOT NULL DEFAULT '',
  celular         VARCHAR(15)  NOT NULL UNIQUE,
  password_hash   TEXT         NOT NULL,
  id_perfil       INT          NOT NULL REFERENCES perfiles(id),
  email_verificado BOOLEAN     NOT NULL DEFAULT FALSE,
  celular_verificado BOOLEAN   NOT NULL DEFAULT FALSE,
  foto_cedula     TEXT,                  -- ruta/imagen de la cédula para verificacin
  verificado_por_admin BOOLEAN NOT NULL DEFAULT FALSE,
  puntos_confianza INT        NOT NULL DEFAULT 100,
  activo          BOOLEAN      NOT NULL DEFAULT TRUE,
  created_at      TIMESTAMP    NOT NULL DEFAULT NOW(),
  updated_at      TIMESTAMP    NOT NULL DEFAULT NOW()
);

-- ============================================================
-- PERMISOS DISPONIBLES DEL SISTEMA
-- ============================================================

INSERT INTO permisos (nombre, codigo, descripcion) VALUES
  -- SUPERADMIN
  ('Configurar sistema',           'configurar_sistema',       'Cambiar variables globales del sistema'),
  ('Gestionar API keys',           'gestionar_api_keys',       'Administrar claves de servicios externos'),
  ('Gestionar roles',              'gestionar_roles',          'Crear, editar y eliminar perfiles y permisos'),
  ('Ver logs',                     'ver_logs',                 'Ver registro de actividades del sistema'),
  ('Gestionar respaldos',          'gestionar_respaldos',      'Generar y descargar respaldos de BD'),
  ('Activar mantenimiento',        'activar_mantenimiento',    'Poner la plataforma en modo mantenimiento'),

  -- ADMIN
  ('Gestionar usuarios',           'gestionar_usuarios',       'Activar, bloquear, ver historial de usuarios'),
  ('Verificar campesinos',         'verificar_campesinos',     'Aprobar foto de cédula de campesinos'),
  ('Gestionar categorias',         'gestionar_categorias',     'CRUD de categorías de productos y calidades'),
  ('Moderar reseñas',              'moderar_resenias',         'Eliminar reseñas inapropiadas'),
  ('Gestionar plazas',             'gestionar_plazas',         'Agregar o desactivar plazas de mercado'),
  ('Ver reportes',                 'ver_reportes',             'Exportar reportes de ventas y usuarios'),
  ('Resolver disputas',            'resolver_disputas',        'Mediar entre campesino y comprador'),

  -- CAMPESINO
  ('Publicar viajes',              'publicar_viajes',          'Crear publicaciones de viaje anticipado'),
  ('Editar precios y stock',       'editar_precios_stock',     'Cambiar precios y cantidades en vivo'),
  ('Gestionar inventario',         'gestionar_inventario',     'Administrar productos y calidades'),
  ('Ver preórdenes',               'ver_preordenes',           'Ver pedidos apartados por consumidores'),
  ('Activar ofertas flash',        'activar_ofertas',          'Activar remates con descuento'),
  ('Marcar ubicación',             'marcar_ubicacion',         'Señalar el puesto en el mapa'),
  ('Ver historial de ventas',      'ver_historial_ventas',     'Consultar ventas realizadas'),
  ('Responder reseñas',            'responder_resenias',       'Responder a reseñas de compradores'),

  -- CONSUMIDOR
  ('Ver mapa',                     'ver_mapa',                 'Ver campesinos activos en el mapa'),
  ('Explorar productos',           'explorar_productos',       'Buscar y filtrar productos disponibles'),
  ('Realizar preórden',            'realizar_preorden',        'Apartar productos antes de ir a la plaza'),
  ('Dejar reseña',                 'dejar_resenia',            'Calificar y comentar al campesino'),
  ('Ver historial de compras',     'ver_historial_compras',    'Consultar pedidos realizados');

-- ============================================================
-- PERFILES DEL SISTEMA
-- ============================================================

INSERT INTO perfiles (nombre, descripcion) VALUES
  ('superadmin',   'Desarrollador con acceso total al sistema'),
  ('administrador','Encargado de gestionar usuarios, moderar y ver reportes'),
  ('campesino',    'Agricultor que vende sus productos en las plazas'),
  ('consumidor',   'Comprador que busca productos frescos directo del campo'),
  ('bloqueado',    'Usuario suspendido. Puede iniciar sesin pero no puede hacer nada');

-- ============================================================
-- ASIGNAR PERMISOS A CADA PERFIL
-- ============================================================

-- SUPERADMIN: todos los permisos
INSERT INTO perfiles_permisos (id_perfil, id_permiso)
SELECT (SELECT id FROM perfiles WHERE nombre = 'superadmin'), id FROM permisos;

-- ADMINISTRADOR
INSERT INTO perfiles_permisos (id_perfil, id_permiso)
SELECT (SELECT id FROM perfiles WHERE nombre = 'administrador'), id FROM permisos
WHERE codigo IN (
  'gestionar_usuarios',
  'verificar_campesinos',
  'gestionar_categorias',
  'moderar_resenias',
  'gestionar_plazas',
  'ver_reportes',
  'resolver_disputas',
  'realizar_preorden',
  'dejar_resenia'
);

-- CAMPESINO
INSERT INTO perfiles_permisos (id_perfil, id_permiso)
SELECT (SELECT id FROM perfiles WHERE nombre = 'campesino'), id FROM permisos
WHERE codigo IN (
  'publicar_viajes',
  'editar_precios_stock',
  'gestionar_inventario',
  'ver_preordenes',
  'activar_ofertas',
  'marcar_ubicacion',
  'ver_historial_ventas',
  'responder_resenias',
  'ver_mapa',
  'realizar_preorden',
  'dejar_resenia'
);

-- CONSUMIDOR
INSERT INTO perfiles_permisos (id_perfil, id_permiso)
SELECT (SELECT id FROM perfiles WHERE nombre = 'consumidor'), id FROM permisos
WHERE codigo IN (
  'ver_mapa',
  'explorar_productos',
  'realizar_preorden',
  'dejar_resenia',
  'ver_historial_compras'
);

-- BLOQUEADO: no recibe ningn permiso (perfil vaco)

-- ============================================================
-- USUARIOS SUPERADMIN POR DEFECTO
-- ============================================================
-- La contrasea para ambos es: SuperAdmin2026!
-- Hash generado con bcrypt
-- En produccin CAMBIAR estas contraseas inmediatamente.

INSERT INTO usuarios (nombres, apellidos, cedula, email, celular, password_hash, id_perfil, email_verificado, celular_verificado, verificado_por_admin)
VALUES
  (
    'Superadmin',
    'Principal',
    '0000000001',
    'superadmin@mercadocampesino.co',
    '3000000001',
    '$2b$12$mRO5h0bo4Zw27kuPFpe4xO6Tj76xpzq77Jhf3tTSO.zkEKyJYs5VK',
    (SELECT id FROM perfiles WHERE nombre = 'superadmin'),
    TRUE, TRUE, TRUE
  ),
  (
    'Superadmin',
    'Secundario',
    '0000000002',
    'superadmin2@mercadocampesino.co',
    '3000000002',
    '$2b$12$mRO5h0bo4Zw27kuPFpe4xO6Tj76xpzq77Jhf3tTSO.zkEKyJYs5VK',
    (SELECT id FROM perfiles WHERE nombre = 'superadmin'),
    TRUE, TRUE, TRUE
  );

-- Admin de prueba (contraseña: SuperAdmin2026!)
INSERT INTO usuarios (nombres, apellidos, cedula, email, celular, password_hash, id_perfil, email_verificado, celular_verificado, verificado_por_admin)
VALUES (
  'Admin',
  'Principal',
  '0000000003',
  'admin@mercadocampesino.co',
  '3000000003',
  '$2b$12$mRO5h0bo4Zw27kuPFpe4xO6Tj76xpzq77Jhf3tTSO.zkEKyJYs5VK',
  (SELECT id FROM perfiles WHERE nombre = 'administrador'),
  TRUE, TRUE, TRUE
);

-- ============================================================
-- TABLAS DE NEGOCIO
-- ============================================================

-- Categoras de productos (ej: tubrculos, hortalizas, frutas, lcteos)
CREATE TABLE categorias (
  id          SERIAL       PRIMARY KEY,
  nombre      VARCHAR(100) NOT NULL UNIQUE,
  descripcion TEXT,
  activo      BOOLEAN      NOT NULL DEFAULT TRUE,
  created_at  TIMESTAMP    NOT NULL DEFAULT NOW()
);

-- Calidades del producto (ej: primera, segunda, tercera)
CREATE TABLE calidades (
  id          SERIAL       PRIMARY KEY,
  nombre      VARCHAR(50)  NOT NULL UNIQUE,
  descripcion TEXT,
  activo      BOOLEAN      NOT NULL DEFAULT TRUE,
  created_at  TIMESTAMP    NOT NULL DEFAULT NOW()
);

-- Productos del catlogo general (ej: papa, yuca, zanahoria)
CREATE TABLE productos (
  id            SERIAL       PRIMARY KEY,
  nombre        VARCHAR(100) NOT NULL,
  id_categoria  INT          REFERENCES categorias(id),
  id_creador    INT          REFERENCES usuarios(id),
  unidad        VARCHAR(20)  NOT NULL DEFAULT 'kg',   -- kg, libra, unidad, atado
  precio        NUMERIC(12,2),                        -- precio base del producto
  foto_url      TEXT,
  activo        BOOLEAN      NOT NULL DEFAULT TRUE,
  created_at    TIMESTAMP    NOT NULL DEFAULT NOW()
);

-- Plazas de mercado predefinidas (opcional, el campesino puede poner ubicación libre)
CREATE TABLE plazas (
  id          SERIAL       PRIMARY KEY,
  nombre      VARCHAR(150) NOT NULL UNIQUE,
  direccion   TEXT,
  latitud     DECIMAL(10,7),
  longitud    DECIMAL(10,7),
  activo      BOOLEAN      NOT NULL DEFAULT TRUE,
  created_at  TIMESTAMP    NOT NULL DEFAULT NOW()
);

-- Viajes: cada publicación anticipada del campesino
CREATE TABLE viajes (
  id              SERIAL       PRIMARY KEY,
  id_campesino    INT          NOT NULL REFERENCES usuarios(id),
  fecha_viaje     DATE         NOT NULL,
  hora_inicio     TIME,                              -- desde cundo atiende
  hora_fin        TIME,                              -- hasta cundo atiende
  notas           TEXT,                               -- informacin adicional
  activo          BOOLEAN      NOT NULL DEFAULT TRUE,
  created_at      TIMESTAMP    NOT NULL DEFAULT NOW(),
  updated_at      TIMESTAMP    NOT NULL DEFAULT NOW()
);

-- Ubicaciones del viaje (el campesino puede tener varias en el da si se mueve)
-- Soporta tanto plaza predefinida como ubicación libre en el mapa
CREATE TABLE viaje_ubicaciones (
  id          SERIAL       PRIMARY KEY,
  id_viaje    INT          NOT NULL REFERENCES viajes(id) ON DELETE CASCADE,
  id_plaza    INT          REFERENCES plazas(id),     -- NULL si es ubicación libre
  latitud     DECIMAL(10,7) NOT NULL,                 -- siempre se guarda
  longitud    DECIMAL(10,7) NOT NULL,                 -- siempre se guarda
  direccion   TEXT,                                    -- direccin escrita o descripción del lugar
  foto_url    TEXT,                                     -- foto opcional del puesto/ubicación
  activa      BOOLEAN      NOT NULL DEFAULT TRUE,      -- cul es la ubicación actual
  created_at  TIMESTAMP    NOT NULL DEFAULT NOW()
);

-- Productos que el campesino lleva en ese viaje, con precio por calidad
CREATE TABLE viaje_productos (
  id            SERIAL       PRIMARY KEY,
  id_viaje      INT          NOT NULL REFERENCES viajes(id) ON DELETE CASCADE,
  id_producto   INT          NOT NULL REFERENCES productos(id),
  id_calidad    INT          REFERENCES calidades(id),
  precio        DECIMAL(12,2) NOT NULL,               -- precio por unidad
  cantidad_inicial DECIMAL(12,2) NOT NULL,             -- cunto llev
  cantidad_disponible DECIMAL(12,2) NOT NULL,          -- cunto queda
  activo        BOOLEAN      NOT NULL DEFAULT TRUE,
  created_at    TIMESTAMP    NOT NULL DEFAULT NOW(),
  updated_at    TIMESTAMP    NOT NULL DEFAULT NOW()
);

-- Fotos de cada producto en el viaje (mximo 5 por producto)
CREATE TABLE producto_fotos (
  id                  SERIAL       PRIMARY KEY,
  id_viaje_producto   INT          NOT NULL REFERENCES viaje_productos(id) ON DELETE CASCADE,
  url                 TEXT         NOT NULL,
  orden               INT          NOT NULL DEFAULT 0,
  created_at          TIMESTAMP    NOT NULL DEFAULT NOW()
);

-- Preórdenes: apartados que hacen los consumidores
CREATE TABLE preordenes (
  id                SERIAL       PRIMARY KEY,
  id_viaje_producto INT          NOT NULL REFERENCES viaje_productos(id),
  id_consumidor     INT          NOT NULL REFERENCES usuarios(id),
  cantidad          DECIMAL(12,2) NOT NULL,
  estado            VARCHAR(20)  NOT NULL DEFAULT 'pendiente',  -- pendiente, entregado, no_retiro, cancelado
  created_at        TIMESTAMP    NOT NULL DEFAULT NOW(),
  updated_at        TIMESTAMP    NOT NULL DEFAULT NOW()
);

-- Reseñas mutuas entre campesino y consumidor
CREATE TABLE resenias (
  id                  SERIAL       PRIMARY KEY,
  id_autor            INT          NOT NULL REFERENCES usuarios(id),
  id_destino          INT          NOT NULL REFERENCES usuarios(id),
  id_viaje            INT          REFERENCES viajes(id),
  puntuacion          INT          NOT NULL CHECK (puntuacion >= 1 AND puntuacion <= 5),
  comentario          TEXT,
  respuesta           TEXT,                               -- respuesta del reseñado
  reportada           BOOLEAN      NOT NULL DEFAULT FALSE,
  created_at          TIMESTAMP    NOT NULL DEFAULT NOW()
);

-- Ofertas flash: remates de ltimo momento con descuento
CREATE TABLE ofertas_flash (
  id                SERIAL       PRIMARY KEY,
  id_viaje_producto INT          NOT NULL REFERENCES viaje_productos(id),
  descuento_porcentaje DECIMAL(5,2) NOT NULL,             -- ej: 30 (30% de descuento)
  precio_oferta     DECIMAL(12,2) NOT NULL,               -- precio ya con descuento
  cantidad_limite   DECIMAL(12,2),                        -- NULL = sin lmite
  activa            BOOLEAN      NOT NULL DEFAULT TRUE,
  created_at        TIMESTAMP    NOT NULL DEFAULT NOW(),
  updated_at        TIMESTAMP    NOT NULL DEFAULT NOW()
);

-- Tickets de soporte: canal de comunicacin usuario -> administrador
CREATE TABLE tickets (
  id            SERIAL       PRIMARY KEY,
  id_remitente  INT          NOT NULL REFERENCES usuarios(id),
  asunto        VARCHAR(200) NOT NULL,
  mensaje       TEXT         NOT NULL,
  estado        VARCHAR(20)  NOT NULL DEFAULT 'abierto',  -- abierto, en_progreso, finalizado
  created_at    TIMESTAMP    NOT NULL DEFAULT NOW(),
  updated_at    TIMESTAMP    NOT NULL DEFAULT NOW()
);

-- Respuestas/avances en cada ticket
CREATE TABLE ticket_respuestas (
  id          SERIAL       PRIMARY KEY,
  id_ticket   INT          NOT NULL REFERENCES tickets(id) ON DELETE CASCADE,
  id_autor    INT          NOT NULL REFERENCES usuarios(id),
  mensaje     TEXT         NOT NULL,
  created_at  TIMESTAMP    NOT NULL DEFAULT NOW()
);

-- Chat en vivo
CREATE TABLE chat_conversaciones (
  id                SERIAL       PRIMARY KEY,
  nombre            VARCHAR(200) NOT NULL,
  email             VARCHAR(200) NOT NULL DEFAULT '',
  cedula            VARCHAR(20)  NOT NULL DEFAULT '',
  id_usuario        INT          REFERENCES usuarios(id),
  session_token     VARCHAR(100) NOT NULL,
  estado            VARCHAR(20)  NOT NULL DEFAULT 'abierto',
  id_admin_asignado INT          REFERENCES usuarios(id),
  created_at        TIMESTAMP    NOT NULL DEFAULT NOW(),
  updated_at        TIMESTAMP    NOT NULL DEFAULT NOW()
);

CREATE TABLE chat_mensajes (
  id                SERIAL       PRIMARY KEY,
  id_conversacion   INT          NOT NULL REFERENCES chat_conversaciones(id) ON DELETE CASCADE,
  mensaje           TEXT         NOT NULL,
  es_admin          BOOLEAN      NOT NULL DEFAULT FALSE,
  id_admin          INT          REFERENCES usuarios(id),
  created_at        TIMESTAMP    NOT NULL DEFAULT NOW()
);

-- ============================================================
-- DATOS INICIALES
-- ============================================================

INSERT INTO calidades (nombre, descripcion) VALUES
  ('primera',  'Producto de la mejor calidad, sin imperfecciones, tamao uniforme'),
  ('segunda',  'Producto de buena calidad, pequeas imperfecciones estticas'),
  ('tercera',  'Producto apto para consumo, imperfecciones visibles, ideal para procesar');

INSERT INTO categorias (nombre, descripcion) VALUES
  ('Tubérculos y raíces', 'Papas, yuca, zanahoria, remolacha, etc.'),
  ('Hortalizas y verduras', 'Lechuga, tomate, cebolla, brcoli, etc.'),
  ('Frutas', 'Manzana, naranja, banano, fresa, etc.'),
  ('Lácteos', 'Leche, queso, yogur, etc.'),
  ('Huevos', 'Huevos de gallina, codorniz, etc.'),
  ('Legumbres y granos', 'Fríjol, lenteja, garbanzo, etc.'),
  ('Hierbas y aromáticas', 'Cilantro, perejil, hierbabuena, etc.'),
  ('Miel y derivados', 'Miel de abeja, propleo, polen, etc.');

INSERT INTO plazas (nombre, direccion, latitud, longitud) VALUES
  ('Plaza de Paloquemao',    'Cra. 19 #21-58, Bogotá',     4.6100000, -74.0800000),
  ('Plaza 7 de Agosto',      'Cl. 66 #12-40, Bogotá',      4.6500000, -74.0600000),
  ('Plaza Las Flores',       'Cra. 70 #1-20, Bogotá',       4.6300000, -74.1000000),
  ('Plaza de La Perseverancia', 'Cra. 5 #30-40, Bogotá',   4.6000000, -74.0700000),
  ('Plaza Samper Mendoza',   'Cl. 14 #1-60, Bogotá',        4.5900000, -74.0900000);

-- ============================================================
-- DATOS DE PRUEBA: productos catlogo y campesino de ejemplo
-- ============================================================

-- Campesino de prueba (contrasea: Campesino2026!)
INSERT INTO usuarios (nombres, apellidos, cedula, email, celular, password_hash, id_perfil, email_verificado, celular_verificado, verificado_por_admin)
VALUES (
  'Carlos',
  'Martínez',
  '123456789',
  'carlos@campesino.co',
  '3101234567',
  '$2b$12$mRO5h0bo4Zw27kuPFpe4xO6Tj76xpzq77Jhf3tTSO.zkEKyJYs5VK',
  (SELECT id FROM perfiles WHERE nombre = 'campesino'),
  TRUE, TRUE, TRUE
);

-- Consumidor de prueba (contrasea: Consumidor2026!)
INSERT INTO usuarios (nombres, apellidos, cedula, email, celular, password_hash, id_perfil, email_verificado, celular_verificado, verificado_por_admin)
VALUES (
  'Ana',
  'García',
  '987654321',
  'ana@consumidor.co',
  '3117654321',
  '$2b$12$mRO5h0bo4Zw27kuPFpe4xO6Tj76xpzq77Jhf3tTSO.zkEKyJYs5VK',
  (SELECT id FROM perfiles WHERE nombre = 'consumidor'),
  TRUE, TRUE, TRUE
);

-- Productos del catálogo (todos de Carlos Martínez, campesino)
INSERT INTO productos (nombre, id_categoria, id_creador, unidad, precio, foto_url) VALUES
  ('Papa criolla',    (SELECT id FROM categorias WHERE nombre = 'Tubérculos y raíces'), (SELECT id FROM usuarios WHERE cedula = '123456789'), 'kg',  3000, 'data:image/svg+xml;base64,'),
  ('Papa pastusa',    (SELECT id FROM categorias WHERE nombre = 'Tubérculos y raíces'), (SELECT id FROM usuarios WHERE cedula = '123456789'), 'kg',  2500, 'data:image/svg+xml;base64,'),
  ('Yuca',            (SELECT id FROM categorias WHERE nombre = 'Tubérculos y raíces'), (SELECT id FROM usuarios WHERE cedula = '123456789'), 'kg',  2000, 'data:image/svg+xml;base64,'),
  ('Zanahoria',       (SELECT id FROM categorias WHERE nombre = 'Tubérculos y raíces'), (SELECT id FROM usuarios WHERE cedula = '123456789'), 'kg',  2500, 'data:image/svg+xml;base64,'),
  ('Tomate chonto',   (SELECT id FROM categorias WHERE nombre = 'Hortalizas y verduras'), (SELECT id FROM usuarios WHERE cedula = '123456789'), 'kg', 4000, 'data:image/svg+xml;base64,'),
  ('Cebolla cabezona',(SELECT id FROM categorias WHERE nombre = 'Hortalizas y verduras'), (SELECT id FROM usuarios WHERE cedula = '123456789'), 'kg', 3500, 'data:image/svg+xml;base64,'),
  ('Lechuga crespa',  (SELECT id FROM categorias WHERE nombre = 'Hortalizas y verduras'), (SELECT id FROM usuarios WHERE cedula = '123456789'), 'unidad',2000, 'data:image/svg+xml;base64,'),
  ('Fresas',          (SELECT id FROM categorias WHERE nombre = 'Frutas'),              (SELECT id FROM usuarios WHERE cedula = '123456789'), 'kg',  8000, 'data:image/svg+xml;base64,'),
  ('Manzana',         (SELECT id FROM categorias WHERE nombre = 'Frutas'),              (SELECT id FROM usuarios WHERE cedula = '123456789'), 'kg',  5000, 'data:image/svg+xml;base64,'),
  ('Naranja',         (SELECT id FROM categorias WHERE nombre = 'Frutas'),              (SELECT id FROM usuarios WHERE cedula = '123456789'), 'kg',  3000, 'data:image/svg+xml;base64,'),
  ('Huevos de gallina',(SELECT id FROM categorias WHERE nombre = 'Huevos'),             (SELECT id FROM usuarios WHERE cedula = '123456789'), 'unidad',500, 'data:image/svg+xml;base64,'),
  ('Leche entera',    (SELECT id FROM categorias WHERE nombre = 'Lácteos'),             (SELECT id FROM usuarios WHERE cedula = '123456789'), 'litro', 4500, 'data:image/svg+xml;base64,'),
  ('Queso campesino', (SELECT id FROM categorias WHERE nombre = 'Lácteos'),             (SELECT id FROM usuarios WHERE cedula = '123456789'), 'kg',   12000, 'data:image/svg+xml;base64,'),
  ('Fríjol',          (SELECT id FROM categorias WHERE nombre = 'Legumbres y granos'),  (SELECT id FROM usuarios WHERE cedula = '123456789'), 'kg',  6000, 'data:image/svg+xml;base64,'),
  ('Cilantro',        (SELECT id FROM categorias WHERE nombre = 'Hierbas y aromáticas'), (SELECT id FROM usuarios WHERE cedula = '123456789'), 'atado', 1000, 'data:image/svg+xml;base64,');

-- Viaje de prueba (hoy)
INSERT INTO viajes (id_campesino, fecha_viaje, hora_inicio, hora_fin, notas)
VALUES (
  (SELECT id FROM usuarios WHERE email = 'carlos@campesino.co'),
  CURRENT_DATE, '06:00', '14:00',
  'Productos frescos directos de la finca'
);

-- Ubicación del viaje (Plaza de Paloquemao)
INSERT INTO viaje_ubicaciones (id_viaje, id_plaza, latitud, longitud, direccion)
VALUES (
  (SELECT id FROM viajes WHERE notas = 'Productos frescos directos de la finca'),
  (SELECT id FROM plazas WHERE nombre = 'Plaza de Paloquemao'),
  4.6100000, -74.0800000,
  'Cra. 19 #21-58, Bogotá'
);

-- Productos del viaje con precios
INSERT INTO viaje_productos (id_viaje, id_producto, precio, cantidad_inicial, cantidad_disponible)
SELECT
  (SELECT id FROM viajes WHERE notas = 'Productos frescos directos de la finca'),
  p.id,
  CASE p.nombre
    WHEN 'Papa criolla' THEN 3000
    WHEN 'Tomate chonto' THEN 4000
    WHEN 'Cebolla cabezona' THEN 3500
    WHEN 'Zanahoria' THEN 2500
    WHEN 'Fresas' THEN 8000
    WHEN 'Cilantro' THEN 1000
  END,
  50, 50
FROM productos p
WHERE p.nombre IN ('Papa criolla','Tomate chonto','Cebolla cabezona','Zanahoria','Fresas','Cilantro');

-- Ofertas flash activas
INSERT INTO ofertas_flash (id_viaje_producto, descuento_porcentaje, precio_oferta, cantidad_limite)
SELECT vp.id, 30, vp.precio * 0.7, 10
FROM viaje_productos vp
JOIN productos p ON vp.id_producto = p.id
WHERE p.nombre IN ('Papa criolla', 'Fresas');
