-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 10-08-2024 a las 04:00:55
-- Versión del servidor: 10.4.32-MariaDB
-- Versión de PHP: 8.1.25

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `proyecto_is1`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `almacenes`
--

CREATE TABLE `almacenes` (
  `id_almacenes` int(11) NOT NULL,
  `nombre` varchar(255) DEFAULT NULL,
  `direccion` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `almacenes`
--

INSERT INTO `almacenes` (`id_almacenes`, `nombre`, `direccion`) VALUES
(6, 'sdas', 'Olancho'),
(7, 'dasdads', 'Tegucigalpa'),
(8, 'sdsadas', 'Colon');

--
-- Disparadores `almacenes`
--
DELIMITER $$
CREATE TRIGGER `after_delete_almacenes` BEFORE DELETE ON `almacenes` FOR EACH ROW BEGIN
    INSERT INTO historicos_almacenes (id_almacenes, acciones, fecha, descripcion)
    VALUES (OLD.id_almacenes, 'Eliminación', NOW(), CONCAT('Se ha eliminado el almacén con ID ', OLD.id_almacenes));
END
$$
DELIMITER ;
DELIMITER $$
CREATE TRIGGER `after_insert_almacenes` AFTER INSERT ON `almacenes` FOR EACH ROW BEGIN
    INSERT INTO historicos_almacenes (id_almacenes, acciones, fecha, descripcion)
    VALUES (NEW.id_almacenes, 'Inserción', NOW(), CONCAT('Se ha añadido el almacén con ID ', NEW.id_almacenes));
END
$$
DELIMITER ;
DELIMITER $$
CREATE TRIGGER `after_update_almacenes` AFTER UPDATE ON `almacenes` FOR EACH ROW BEGIN
    INSERT INTO historicos_almacenes (id_almacenes, acciones, fecha, descripcion)
    VALUES (NEW.id_almacenes, 'Actualización', NOW(), CONCAT('Se ha actualizado el almacén con ID ', NEW.id_almacenes, ': nombre cambiado a "', NEW.nombre, '" y dirección cambiada a "', NEW.direccion, '".'));
END
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `capacitacion`
--

CREATE TABLE `capacitacion` (
  `id_capacitacion` int(11) NOT NULL,
  `id_empleado` int(11) DEFAULT NULL,
  `tema` varchar(100) DEFAULT NULL,
  `fecha_capacitacion` datetime DEFAULT NULL,
  `duracion` int(11) DEFAULT NULL,
  `resultado` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `capacitacion`
--

INSERT INTO `capacitacion` (`id_capacitacion`, `id_empleado`, `tema`, `fecha_capacitacion`, `duracion`, `resultado`) VALUES
(2, 9, 'Entrenamiento', '2024-08-13 18:33:00', 2, 5),
(3, 11, 'Entrenamiento', '2024-08-22 18:34:00', 3, 5);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `categorias`
--

CREATE TABLE `categorias` (
  `id_categoria` int(11) NOT NULL,
  `nombre_categoria` varchar(20) NOT NULL,
  `Descripcion` varchar(40) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `categorias`
--

INSERT INTO `categorias` (`id_categoria`, `nombre_categoria`, `Descripcion`) VALUES
(3, 'Ropa y Accesorios', 'Vestimenta y accesorios de moda para hom'),
(7, 'Libros y Música', 'Libros, música, instrumentos y accesorio'),
(10, 'Oficina y Papelería', 'Artículos de oficina, papelería y sumini'),
(11, 'Bebidas', 'soda, cafe, Te'),
(15, 'Electrodomesticos', 'Computadoras');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `cliente`
--

CREATE TABLE `cliente` (
  `id_cliente` int(10) NOT NULL,
  `nombre` varchar(50) NOT NULL,
  `apellido` varchar(50) NOT NULL,
  `fecha_nacimiento` date NOT NULL,
  `email` varchar(50) NOT NULL,
  `telefono` varchar(10) NOT NULL,
  `direccion` varchar(100) NOT NULL,
  `fecha_registro` date NOT NULL,
  `tipo` varchar(50) NOT NULL,
  `documento` varchar(14) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `cliente`
--

INSERT INTO `cliente` (`id_cliente`, `nombre`, `apellido`, `fecha_nacimiento`, `email`, `telefono`, `direccion`, `fecha_registro`, `tipo`, `documento`) VALUES
(26, 'joseph', 'joestar', '2004-02-21', 'joseph@gmail.com', '3125-8765', 'col.felon', '2005-08-28', 'DNI ', '0801-1998-9876'),
(27, 'Gustavo ', 'Hernandez', '1999-08-02', 'Gustavo@gmail.com', '96187469', 'col.miraflores', '2024-08-01', 'DNI ', '0801-1999-9876');

--
-- Disparadores `cliente`
--
DELIMITER $$
CREATE TRIGGER `after_delete_clientes` BEFORE DELETE ON `cliente` FOR EACH ROW BEGIN
    INSERT INTO historicos_clientes (id_cliente, acciones, fecha, descripcion)
    VALUES (OLD.id_cliente, 'Eliminación', NOW(), CONCAT('Se ha eliminado el cliente con ID ', OLD.id_cliente));
END
$$
DELIMITER ;
DELIMITER $$
CREATE TRIGGER `after_insert_clientes` AFTER INSERT ON `cliente` FOR EACH ROW BEGIN
    INSERT INTO historicos_clientes (id_cliente, acciones, fecha, descripcion)
    VALUES (NEW.id_cliente, 'Inserción', NOW(), CONCAT('Se ha añadido el cliente con ID ', NEW.id_cliente));
END
$$
DELIMITER ;
DELIMITER $$
CREATE TRIGGER `after_insertar_cliente` AFTER INSERT ON `cliente` FOR EACH ROW BEGIN
    INSERT INTO documentacion_clientes (nombre, apellido, tipo, documento, fecha_nacimiento)
    VALUES (NEW.nombre, NEW.apellido, NEW.tipo, NEW.documento, NEW.fecha_nacimiento);
END
$$
DELIMITER ;
DELIMITER $$
CREATE TRIGGER `after_update_clientes` AFTER UPDATE ON `cliente` FOR EACH ROW BEGIN
    INSERT INTO historicos_clientes (id_cliente, acciones, fecha, descripcion)
    VALUES (NEW.id_cliente, 'Actualización', NOW(), CONCAT('Se ha actualizado el cliente con ID ', NEW.id_cliente));
END
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `detalles_de_factura`
--

CREATE TABLE `detalles_de_factura` (
  `id_detalle` int(11) NOT NULL,
  `id_factura` int(11) DEFAULT NULL,
  `id_producto` int(100) DEFAULT NULL,
  `id_pedido` int(11) DEFAULT NULL,
  `cantidad` varchar(50) DEFAULT NULL,
  `precio_unitario` float DEFAULT NULL,
  `subtotal` decimal(10,0) DEFAULT NULL,
  `total` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `detalle_de_compra_cliente`
--

CREATE TABLE `detalle_de_compra_cliente` (
  `id_detalle` int(11) NOT NULL,
  `id_pedido` int(11) DEFAULT NULL,
  `id_producto` int(11) DEFAULT NULL,
  `cantidad` int(50) NOT NULL,
  `precio_unitario` decimal(10,0) DEFAULT NULL,
  `subtotal` decimal(10,0) DEFAULT NULL,
  `id_impuesto` int(11) DEFAULT NULL,
  `total` decimal(10,0) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `detalle_de_compra_proveedor`
--

CREATE TABLE `detalle_de_compra_proveedor` (
  `id_detalle` int(11) NOT NULL,
  `id_pedido` int(11) DEFAULT NULL,
  `id_producto` int(11) DEFAULT NULL,
  `cantidad` int(50) NOT NULL,
  `precio_unitario` decimal(10,0) DEFAULT NULL,
  `id_impuesto` int(11) DEFAULT NULL,
  `subtotal` decimal(10,0) DEFAULT NULL,
  `total` decimal(10,0) DEFAULT NULL,
  `id_estado` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `detalle_de_compra_proveedor`
--

INSERT INTO `detalle_de_compra_proveedor` (`id_detalle`, `id_pedido`, `id_producto`, `cantidad`, `precio_unitario`, `id_impuesto`, `subtotal`, `total`, `id_estado`) VALUES
(16, 17, 37, 2, 200, 6, 400, 400, NULL);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `devoluciones_compras`
--

CREATE TABLE `devoluciones_compras` (
  `id_devolucion` int(11) NOT NULL,
  `id_pedido` int(11) NOT NULL,
  `id_detalle` int(11) NOT NULL,
  `fecha_devolucion` date NOT NULL,
  `motivo` varchar(255) NOT NULL,
  `cantidad_devuelta` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `devoluciones_compras`
--

INSERT INTO `devoluciones_compras` (`id_devolucion`, `id_pedido`, `id_detalle`, `fecha_devolucion`, `motivo`, `cantidad_devuelta`) VALUES
(6, 17, 16, '2024-08-23', 'camisas llenas de termitas', 1),
(7, 17, 16, '2024-08-11', 'camisas llenas de termitas', 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `devoluciones_ventas`
--

CREATE TABLE `devoluciones_ventas` (
  `id_devolucion` int(11) NOT NULL,
  `id_pedido` int(11) NOT NULL,
  `id_detalle` int(11) NOT NULL,
  `fecha_devolucion` date NOT NULL,
  `motivo` varchar(255) NOT NULL,
  `cantidad_devuelta` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `devoluciones_ventas`
--

INSERT INTO `devoluciones_ventas` (`id_devolucion`, `id_pedido`, `id_detalle`, `fecha_devolucion`, `motivo`, `cantidad_devuelta`) VALUES
(1, 1, 3, '2024-08-23', 'Equipamiento dañado', 2);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `distribucion_almacenes`
--

CREATE TABLE `distribucion_almacenes` (
  `id_distribucion` int(11) NOT NULL,
  `id_almacenes` int(11) DEFAULT NULL,
  `id_producto` int(11) DEFAULT NULL,
  `cantidad` int(11) DEFAULT NULL,
  `fecha` date DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `documentacion_clientes`
--

CREATE TABLE `documentacion_clientes` (
  `id_documentoc` int(11) NOT NULL,
  `nombre` text NOT NULL,
  `apellido` text NOT NULL,
  `tipo` text NOT NULL,
  `documento` int(16) NOT NULL,
  `fecha_nacimiento` date NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `documentacion_clientes`
--

INSERT INTO `documentacion_clientes` (`id_documentoc`, `nombre`, `apellido`, `tipo`, `documento`, `fecha_nacimiento`) VALUES
(5, 'Dante', 'Valladares', 'DNI ', 2147483647, '2024-08-02'),
(6, 'Gustavo ', 'Hernandez', 'DNI ', 801, '1999-08-02');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `documento_empleado`
--

CREATE TABLE `documento_empleado` (
  `id_documento` int(11) NOT NULL,
  `nombre` varchar(30) NOT NULL,
  `apellido` varchar(30) NOT NULL,
  `tipo` varchar(50) NOT NULL,
  `documento` varchar(14) NOT NULL,
  `fecha_nacimiento` date DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `documento_empleado`
--

INSERT INTO `documento_empleado` (`id_documento`, `nombre`, `apellido`, `tipo`, `documento`, `fecha_nacimiento`) VALUES
(1, 'Juan', 'Pérez', 'DNI', '12345678', '1985-04-23'),
(2, 'Ana', 'Gómez', 'Pasaporte', 'A1234567', '1990-06-17'),
(3, 'Carlos', 'López', 'RTN', '123456789', '1982-11-30'),
(4, 'María', 'Torres', 'DNI', '87654321', '1987-09-15'),
(5, 'Luis', 'Fernández', 'Pasaporte', 'B7654321', '1978-03-22'),
(6, 'Carmen', 'Martínez', 'RTN', '234567890', '1995-07-10'),
(7, 'Antonio', 'Sánchez', 'DNI', '34567890', '1983-12-05'),
(8, 'Laura', 'Romero', 'Pasaporte', 'C3456789', '1992-10-25'),
(9, 'Javier', 'Ruiz', 'RTN', '456789012', '1981-05-14'),
(10, 'Isabel', 'Hernández', 'DNI', '56789012', '1993-01-09'),
(11, 'Pedro', 'García', 'Pasaporte', 'D5678901', '1989-08-08'),
(12, 'Sonia', 'Jiménez', 'RTN', '678901234', '1977-04-12'),
(13, 'Diego', 'Gil', 'DNI', '78901234', '1986-06-20'),
(14, 'Elena', 'Ortiz', 'Pasaporte', 'E7890123', '1991-11-18'),
(15, 'Francisco', 'Castillo', 'RTN', '890123456', '1984-02-28');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `empleados`
--

CREATE TABLE `empleados` (
  `id_empleado` int(6) NOT NULL,
  `nombre` varchar(30) NOT NULL,
  `apellido` varchar(30) NOT NULL,
  `fecha_nacimiento` date NOT NULL,
  `id_puesto` varchar(50) NOT NULL,
  `fecha_contratacion` date NOT NULL,
  `sucursal` varchar(50) NOT NULL,
  `email` varchar(50) NOT NULL,
  `telefono` varchar(15) NOT NULL,
  `tipo` varchar(50) NOT NULL,
  `documento` varchar(14) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `empleados`
--

INSERT INTO `empleados` (`id_empleado`, `nombre`, `apellido`, `fecha_nacimiento`, `id_puesto`, `fecha_contratacion`, `sucursal`, `email`, `telefono`, `tipo`, `documento`) VALUES
(1, 'José', 'Ramírez', '1980-01-15', 'Gerente', '2020-03-01', 'Sucursal A', 'jose.ramirez@example.com', '555-1234', '', '1234567890'),
(2, 'Laura', 'Martínez', '1985-06-20', 'Vendedora', '2021-05-15', 'Sucursal B', 'laura.martinez@example.com', '555-5678', '', '0987654321'),
(3, 'Carlos', 'López', '1990-09-12', 'Cajero', '2019-08-20', 'Sucursal C', 'carlos.lopez@example.com', '555-8765', '', '1122334455'),
(4, 'Ana', 'García', '1988-03-05', 'Jefa de almacén', '2018-01-10', 'Sucursal D', 'ana.garcia@example.com', '555-3456', '', '2233445566'),
(5, 'Juan', 'Torres', '1992-11-25', 'Supervisor', '2022-02-18', 'Sucursal E', 'juan.torres@example.com', '555-6543', '', '3344556677'),
(6, 'Marta', 'Gómez', '1985-08-30', 'Recepcionista', '2020-10-05', 'Sucursal F', 'marta.gomez@example.com', '555-4321', '', '4455667788'),
(7, 'Pedro', 'Fernández', '1991-07-14', 'Contador', '2019-12-12', 'Sucursal G', 'pedro.fernandez@example.com', '555-5432', '', '5566778899'),
(8, 'Lucía', 'Díaz', '1982-04-20', 'Administradora', '2017-06-22', 'Sucursal H', 'lucia.diaz@example.com', '555-8764', '', '6677889900'),
(9, 'Jorge', 'Morales', '1993-10-18', 'Analista', '2021-11-11', 'Sucursal I', 'jorge.morales@example.com', '555-9876', '', '7788990011'),
(11, 'Andrés', 'Vega', '1994-05-05', 'Ingeniero', '2020-07-07', 'Sucursal K', 'andres.vega@example.com', '555-7890', '', '9900112233'),
(12, 'Laura', 'Navarro', '1989-09-09', 'Diseñadora', '2019-03-15', 'Sucursal L', 'laura.navarro@example.com', '555-8901', '', '1011122334'),
(13, 'Rafael', 'Hernández', '1986-06-22', 'Técnico', '2021-08-08', 'Sucursal M', 'rafael.hernandez@example.com', '555-9012', '', '1213141516'),
(14, 'Sofía', 'Castillo', '1995-01-19', 'Programadora', '2022-03-03', 'Sucursal N', 'sofia.castillo@example.com', '555-1235', '', '1415161718');

--
-- Disparadores `empleados`
--
DELIMITER $$
CREATE TRIGGER `after_empleado_insert` AFTER INSERT ON `empleados` FOR EACH ROW BEGIN
    INSERT INTO historicos_empleados (
        id_empleado, 
        acciones, 
        fecha, 
        descripcion
    ) VALUES (
        NEW.id_empleado, 
        'Insertar', 
        NOW(), 
        CONCAT('Se ha insertado el empleado: ', NEW.nombre, ' ', NEW.apellido, 
               ' con puesto: ', NEW.id_puesto, 
               ', fecha de nacimiento: ', NEW.fecha_nacimiento, 
               ', sucursal: ', NEW.sucursal, 
               ', email: ', NEW.email, 
               ', teléfono: ', NEW.telefono, 
               ', tipo: ', NEW.tipo, 
               ', documento: ', NEW.documento)
    );
END
$$
DELIMITER ;
DELIMITER $$
CREATE TRIGGER `after_empleado_update` AFTER UPDATE ON `empleados` FOR EACH ROW BEGIN
    INSERT INTO historicos_empleados (
        id_empleado, 
        acciones, 
        fecha, 
        descripcion
    ) VALUES (
        NEW.id_empleado, 
        'Actualizar', 
        NOW(), 
        CONCAT('Se ha actualizado el empleado: ', OLD.nombre, ' ', OLD.apellido, 
               ' de puesto: ', OLD.id_puesto, 
               ' a: ', NEW.id_puesto, 
               ', de fecha de nacimiento: ', OLD.fecha_nacimiento, 
               ' a: ', NEW.fecha_nacimiento, 
               ', en sucursal: ', OLD.sucursal, 
               ' a: ', NEW.sucursal, 
               ', email: ', OLD.email, 
               ' a: ', NEW.email, 
               ', teléfono: ', OLD.telefono, 
               ' a: ', NEW.telefono, 
               ', tipo: ', OLD.tipo, 
               ' a: ', NEW.tipo, 
               ', documento: ', OLD.documento, 
               ' a: ', NEW.documento)
    );
END
$$
DELIMITER ;
DELIMITER $$
CREATE TRIGGER `before_delete_empleado` BEFORE DELETE ON `empleados` FOR EACH ROW BEGIN
    INSERT INTO historicos_empleados (
        id_empleado, 
        acciones, 
        fecha, 
        descripcion
    ) VALUES (
        OLD.id_empleado, 
        'Eliminar', 
        NOW(), 
        CONCAT('Se ha eliminado el empleado: ', OLD.nombre, ' ', OLD.apellido, 
               ' con puesto: ', OLD.id_puesto, 
               ', fecha de nacimiento: ', OLD.fecha_nacimiento, 
               ', sucursal: ', OLD.sucursal, 
               ', email: ', OLD.email, 
               ', teléfono: ', OLD.telefono, 
               ', tipo: ', OLD.tipo, 
               ', documento: ', OLD.documento)
    );
END
$$
DELIMITER ;
DELIMITER $$
CREATE TRIGGER `insertar_documentacion` AFTER INSERT ON `empleados` FOR EACH ROW BEGIN
    INSERT INTO documento_empleados (
        nombre,
        apellido,
        tipo,
        documento,
        fecha_nacimiento,
        telefono,
        email,
        fecha_propuesta
    ) VALUES (
        NEW.nombre,
        NEW.apellido,
        NEW.tipo,
        NEW.documento,
        NEW.fecha_nacimiento,
        NEW.telefono,
        NEW.email,
        CURDATE()
    );
END
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `equipo`
--

CREATE TABLE `equipo` (
  `id_equipo` int(11) NOT NULL,
  `tipo` varchar(10) NOT NULL,
  `Modelo` varchar(10) NOT NULL,
  `numero_serie` varchar(20) NOT NULL,
  `estado` varchar(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `equipo`
--

INSERT INTO `equipo` (`id_equipo`, `tipo`, `Modelo`, `numero_serie`, `estado`) VALUES
(3, 'Router', 'TP-Link Ar', 'SN1122334455', 'Activo'),
(4, 'Monitor', 'Samsung S2', 'SN2233445566', 'Inactivo'),
(5, 'Teclado', 'Logitech K', 'SN3344556677', 'Activo'),
(6, 'Mouse', 'Logitech M', 'SN4455667788', 'Activo'),
(8, 'Cámara', 'Canon EOS ', 'SN6677889900', 'Activo'),
(9, 'Tablet', 'iPad Air', 'SN7788990011', 'Activo'),
(10, 'Switch', 'Cisco SG30', 'SN8899001122', 'Inactivo'),
(11, 'Disco Duro', 'Seagate Ba', 'SN9900112233', 'Activo'),
(12, 'Laptop', 'MacBook Pr', 'SN1011122334', 'Activo'),
(13, 'Smartphone', 'iPhone 12', 'SN1213141516', 'Inactivo'),
(14, 'Altavoz', 'JBL Flip 4', 'SN1415161718', 'Activo'),
(15, 'Consola', 'PS5', 'SN1617181920', 'Activo'),
(3030, 'mecanico', 'nuevo', '3659', 'bueno');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `estado`
--

CREATE TABLE `estado` (
  `id_estado` int(11) NOT NULL,
  `nombre_estado` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `estado`
--

INSERT INTO `estado` (`id_estado`, `nombre_estado`) VALUES
(1, 'En Proceso'),
(2, 'Recibido'),
(3, 'Rechazado'),
(4, 'Cancelado');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `factura`
--

CREATE TABLE `factura` (
  `id_factura` int(11) NOT NULL,
  `id_cliente` int(11) DEFAULT NULL,
  `id_sar` int(11) DEFAULT NULL,
  `fecha_emision` datetime NOT NULL,
  `total` decimal(10,0) DEFAULT NULL,
  `id_metodo` int(11) DEFAULT NULL,
  `id_estado` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `garantia`
--

CREATE TABLE `garantia` (
  `id_garantia` int(11) NOT NULL,
  `duracion` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `garantia`
--

INSERT INTO `garantia` (`id_garantia`, `duracion`) VALUES
(1, '1 Semana'),
(2, '1 mes'),
(3, '6 meses'),
(4, '1 años'),
(5, '5 años');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `historial_de_pagos`
--

CREATE TABLE `historial_de_pagos` (
  `id_pago` int(11) NOT NULL,
  `id_cliente` int(11) DEFAULT NULL,
  `id_factura` int(11) DEFAULT NULL,
  `fecha_pago` datetime DEFAULT NULL,
  `monto` decimal(10,0) DEFAULT NULL,
  `id_metodo` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `historicos_almacenes`
--

CREATE TABLE `historicos_almacenes` (
  `id_historicos` int(11) NOT NULL,
  `id_almacenes` int(11) DEFAULT NULL,
  `acciones` varchar(100) NOT NULL,
  `fecha` timestamp NOT NULL DEFAULT current_timestamp(),
  `descripcion` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `historicos_almacenes`
--

INSERT INTO `historicos_almacenes` (`id_historicos`, `id_almacenes`, `acciones`, `fecha`, `descripcion`) VALUES
(1, NULL, 'Inserción', '2024-08-02 16:23:40', 'Se ha añadido el almacén con ID 2'),
(2, NULL, 'Actualización', '2024-08-02 16:30:32', 'Se ha actualizado el almacén con ID 2: nombre cambiado a \"Almacén Principal\" y dirección cambiada a '),
(3, NULL, 'Eliminación', '2024-08-02 16:31:34', 'Se ha eliminado el almacén con ID 2'),
(4, NULL, 'Inserción', '2024-08-03 02:55:50', 'Se ha añadido el almacén con ID 3'),
(5, NULL, 'Actualización', '2024-08-03 02:56:34', 'Se ha actualizado el almacén con ID 3: nombre cambiado a \"Almacem\" y dirección cambiada a \"Cortes\".'),
(6, NULL, 'Eliminación', '2024-08-03 04:27:46', 'Se ha eliminado el almacén con ID 3'),
(8, NULL, 'Inserción', '2024-08-09 22:05:06', 'Se ha añadido el almacén con ID 4'),
(10, NULL, 'Eliminación', '2024-08-09 22:06:01', 'Se ha eliminado el almacén con ID 1'),
(11, NULL, 'Inserción', '2024-08-09 22:07:33', 'Se ha añadido el almacén con ID 5'),
(12, 6, 'Inserción', '2024-08-10 01:39:54', 'Se ha añadido el almacén con ID 6'),
(13, 7, 'Inserción', '2024-08-10 01:40:45', 'Se ha añadido el almacén con ID 7'),
(14, 8, 'Inserción', '2024-08-10 01:52:13', 'Se ha añadido el almacén con ID 8'),
(15, NULL, 'Eliminación', '2024-08-10 01:58:20', 'Se ha eliminado el almacén con ID 4'),
(16, NULL, 'Eliminación', '2024-08-10 01:58:23', 'Se ha eliminado el almacén con ID 5');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `historicos_clientes`
--

CREATE TABLE `historicos_clientes` (
  `id_historico` int(11) NOT NULL,
  `acciones` varchar(100) DEFAULT NULL,
  `fecha` timestamp NOT NULL DEFAULT current_timestamp(),
  `descripcion` varchar(100) DEFAULT NULL,
  `id_cliente` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `historicos_clientes`
--

INSERT INTO `historicos_clientes` (`id_historico`, `acciones`, `fecha`, `descripcion`, `id_cliente`) VALUES
(1, 'Inserción', '2024-08-03 00:41:57', 'Se ha añadido el cliente con ID 26', 26),
(2, 'Eliminación', '2024-08-03 02:09:28', 'Se ha eliminado el cliente con ID 1', NULL),
(3, 'Eliminación', '2024-08-03 02:09:28', 'Se ha eliminado el cliente con ID 2', NULL),
(4, 'Eliminación', '2024-08-03 02:09:28', 'Se ha eliminado el cliente con ID 3', NULL),
(5, 'Eliminación', '2024-08-03 02:09:28', 'Se ha eliminado el cliente con ID 4', NULL),
(6, 'Eliminación', '2024-08-03 02:09:28', 'Se ha eliminado el cliente con ID 5', NULL),
(7, 'Eliminación', '2024-08-03 02:09:28', 'Se ha eliminado el cliente con ID 6', NULL),
(8, 'Eliminación', '2024-08-03 02:09:28', 'Se ha eliminado el cliente con ID 7', NULL),
(9, 'Eliminación', '2024-08-03 02:09:28', 'Se ha eliminado el cliente con ID 8', NULL),
(10, 'Eliminación', '2024-08-03 02:09:28', 'Se ha eliminado el cliente con ID 9', NULL),
(11, 'Eliminación', '2024-08-03 02:09:28', 'Se ha eliminado el cliente con ID 10', NULL),
(12, 'Eliminación', '2024-08-03 02:09:28', 'Se ha eliminado el cliente con ID 11', NULL),
(13, 'Eliminación', '2024-08-03 02:09:28', 'Se ha eliminado el cliente con ID 12', NULL),
(14, 'Eliminación', '2024-08-03 02:09:28', 'Se ha eliminado el cliente con ID 13', NULL),
(15, 'Eliminación', '2024-08-03 02:09:28', 'Se ha eliminado el cliente con ID 14', NULL),
(16, 'Eliminación', '2024-08-03 02:09:28', 'Se ha eliminado el cliente con ID 15', NULL),
(17, 'Eliminación', '2024-08-03 02:09:28', 'Se ha eliminado el cliente con ID 16', NULL),
(18, 'Eliminación', '2024-08-03 02:09:28', 'Se ha eliminado el cliente con ID 17', NULL),
(19, 'Eliminación', '2024-08-03 02:09:28', 'Se ha eliminado el cliente con ID 18', NULL),
(20, 'Eliminación', '2024-08-03 02:09:28', 'Se ha eliminado el cliente con ID 19', NULL),
(21, 'Eliminación', '2024-08-03 02:09:28', 'Se ha eliminado el cliente con ID 20', NULL),
(22, 'Eliminación', '2024-08-03 02:09:28', 'Se ha eliminado el cliente con ID 21', NULL),
(23, 'Eliminación', '2024-08-03 02:09:28', 'Se ha eliminado el cliente con ID 22', NULL),
(24, 'Eliminación', '2024-08-03 02:09:28', 'Se ha eliminado el cliente con ID 23', NULL),
(25, 'Eliminación', '2024-08-03 02:09:28', 'Se ha eliminado el cliente con ID 24', NULL),
(26, 'Eliminación', '2024-08-03 02:09:28', 'Se ha eliminado el cliente con ID 25', NULL),
(27, 'Inserción', '2024-08-03 13:29:45', 'Se ha añadido el cliente con ID 27', 27);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `historicos_devolucion`
--

CREATE TABLE `historicos_devolucion` (
  `id_historico` int(11) NOT NULL,
  `id_devolucion` int(11) DEFAULT NULL,
  `acciones` varchar(100) NOT NULL,
  `fecha` timestamp NOT NULL DEFAULT current_timestamp(),
  `descripcion` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `historicos_empleados`
--

CREATE TABLE `historicos_empleados` (
  `id_historico` int(11) NOT NULL,
  `id_empleado` int(11) DEFAULT NULL,
  `acciones` varchar(100) DEFAULT NULL,
  `fecha` timestamp NOT NULL DEFAULT current_timestamp(),
  `descripcion` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `historicos_empleados`
--

INSERT INTO `historicos_empleados` (`id_historico`, `id_empleado`, `acciones`, `fecha`, `descripcion`) VALUES
(3, NULL, 'INSERT', '2024-08-01 03:23:09', 'Empleado insertado'),
(4, NULL, 'UPDATE', '2024-08-01 03:23:34', 'Empleado actualizado'),
(5, NULL, 'Eliminar', '2024-08-01 16:18:27', 'Empleado eliminado'),
(6, NULL, 'Eliminar', '2024-08-01 17:30:46', 'Se ha eliminado el empleado: Juan Carlos Pérez con puesto: Supervisor, fecha de nacimiento: 1990-06-');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `historicos_impuestos`
--

CREATE TABLE `historicos_impuestos` (
  `id_historico` int(11) NOT NULL,
  `id_impuesto` int(11) DEFAULT NULL,
  `acciones` varchar(100) NOT NULL,
  `fecha` timestamp NOT NULL DEFAULT current_timestamp(),
  `descripcion` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `historicos_impuestos`
--

INSERT INTO `historicos_impuestos` (`id_historico`, `id_impuesto`, `acciones`, `fecha`, `descripcion`) VALUES
(1, NULL, 'Insertar', '2024-08-01 03:48:14', 'Se ha insertado un impuesto: IVA con tasa: 0.15'),
(2, NULL, 'Actualizar', '2024-08-01 03:48:45', 'Se ha actualizado el impuesto: IVA Modificado de tasa: 0.15 a: 0.18'),
(4, NULL, 'Eliminar', '2024-08-01 03:50:05', 'Se ha eliminado el impuesto: IVA Modificado con tasa: 0.18'),
(5, NULL, 'Insertar', '2024-08-03 01:09:30', 'Se ha insertado un impuesto: IVA con tasa: 15.00'),
(6, NULL, 'Insertar', '2024-08-03 01:09:30', 'Se ha insertado un impuesto: ISR con tasa: 25.00'),
(7, NULL, 'Insertar', '2024-08-03 01:09:30', 'Se ha insertado un impuesto: ISV con tasa: 12.00'),
(8, 5, 'Insertar', '2024-08-03 02:30:24', 'Se ha insertado un impuesto: ISV con tasa: 0.18'),
(9, NULL, 'Eliminar', '2024-08-03 02:30:39', 'Se ha eliminado el impuesto: ISV con tasa: 12.00'),
(10, NULL, 'Eliminar', '2024-08-03 02:30:42', 'Se ha eliminado el impuesto: IVA con tasa: 15.00'),
(11, NULL, 'Eliminar', '2024-08-03 02:30:46', 'Se ha eliminado el impuesto: ISR con tasa: 25.00'),
(12, 6, 'Insertar', '2024-08-03 02:30:55', 'Se ha insertado un impuesto: ISV con tasa: 0.15'),
(13, 5, 'Actualizar', '2024-08-03 03:05:29', 'Se ha actualizado el impuesto: ISV de tasa: 0.18 a: 18.00'),
(14, 5, 'Actualizar', '2024-08-03 03:13:29', 'Se ha actualizado el impuesto: ISV de tasa: 18.00 a: 0.18'),
(15, 5, 'Actualizar', '2024-08-08 18:52:57', 'Se ha actualizado el impuesto: ISV de tasa: 0 a: 18');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `historicos_productos`
--

CREATE TABLE `historicos_productos` (
  `id_historico` int(11) NOT NULL,
  `id_producto` int(11) DEFAULT NULL,
  `accion` varchar(255) DEFAULT NULL,
  `fecha` timestamp NOT NULL DEFAULT current_timestamp(),
  `descripcion` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `historicos_productos`
--

INSERT INTO `historicos_productos` (`id_historico`, `id_producto`, `accion`, `fecha`, `descripcion`) VALUES
(1, NULL, 'Eliminar', '2024-08-01 03:53:45', 'Se ha eliminado el producto: tacos adidas con precio: 3000.00'),
(2, NULL, 'Actualizar', '2024-08-01 03:54:03', 'Se ha actualizado el producto: pastilla panadol de precio: 5.00 a: 6.00'),
(3, NULL, 'Eliminar', '2024-08-02 02:05:44', 'Se ha eliminado el producto: fallout 4 con precio: 2500.00'),
(4, NULL, 'Insertar', '2024-08-02 14:10:35', 'Se ha insertado el producto: Producto Prueba 2 con precio original: 150.00'),
(8, NULL, 'Insertar', '2024-08-02 15:43:30', 'Se ha insertado el producto: Producto A con precio original: 50.00'),
(9, NULL, 'Insertar', '2024-08-02 15:43:30', 'Se ha insertado el producto: Producto E con precio original: 60.00'),
(10, 37, 'Insertar', '2024-08-03 01:09:49', 'Se ha insertado el producto: Estufa de Gas con precio original: 10000.00'),
(11, 37, 'Actualizar', '2024-08-03 01:09:59', 'Se ha actualizado el producto: Estufa de Gas de precio: 10000.00 a: 10000.00'),
(12, 37, 'Actualizar', '2024-08-03 01:12:21', 'Se ha actualizado el producto: Camisas Polo de precio: 10000.00 a: 200.00'),
(13, 37, 'Actualizar', '2024-08-03 01:12:34', 'Se ha actualizado el producto: Camisas Polo de precio: 200.00 a: 200.00'),
(15, NULL, 'Eliminar', '2024-08-03 03:34:34', 'Se ha eliminado el producto: crema depiladora con precio: 500.00'),
(16, NULL, 'Eliminar', '2024-08-03 03:34:34', 'Se ha eliminado el producto: Bad bunny con precio: 350.00'),
(17, NULL, 'Eliminar', '2024-08-03 03:34:34', 'Se ha eliminado el producto: camisa polo con precio: 600.00'),
(18, NULL, 'Eliminar', '2024-08-03 03:34:34', 'Se ha eliminado el producto: Reloj con precio: 1500.00'),
(19, NULL, 'Eliminar', '2024-08-03 03:34:34', 'Se ha eliminado el producto: pantalon con precio: 800.00'),
(20, NULL, 'Eliminar', '2024-08-03 03:34:34', 'Se ha eliminado el producto: Tennis nike con precio: 2500.00'),
(21, NULL, 'Eliminar', '2024-08-03 03:34:34', 'Se ha eliminado el producto: pastilla panadol con precio: 6.00'),
(22, NULL, 'Eliminar', '2024-08-03 03:34:34', 'Se ha eliminado el producto: Computadora dell con precio: 5000.00'),
(23, NULL, 'Eliminar', '2024-08-03 03:34:34', 'Se ha eliminado el producto: medias  con precio: 200.00'),
(24, NULL, 'Eliminar', '2024-08-03 03:34:34', 'Se ha eliminado el producto: Producto Prueba 2 con precio: 150.00'),
(25, NULL, 'Eliminar', '2024-08-03 03:34:34', 'Se ha eliminado el producto: Producto A con precio: 50.00'),
(26, NULL, 'Eliminar', '2024-08-03 03:34:34', 'Se ha eliminado el producto: Producto E con precio: 60.00'),
(27, NULL, 'Insertar', '2024-08-03 03:45:07', 'Se ha insertado el producto: Estufa de Gas con precio original: 10000.00'),
(28, 37, 'Actualizar', '2024-08-03 03:45:37', 'Se ha actualizado el producto: Camisas Polo de precio: 200.00 a: 200.00'),
(29, NULL, 'Eliminar', '2024-08-03 03:58:31', 'Se ha eliminado el producto: Estufa de Gas con precio: 10000.00'),
(30, 39, 'Insertar', '2024-08-03 06:07:27', 'Se ha insertado el producto: Estufa de Gas con precio original: 10000.00'),
(31, 40, 'Insertar', '2024-08-03 13:46:57', 'Se ha insertado el producto: Telefono con precio original: 10000.00');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `ideas_mejora`
--

CREATE TABLE `ideas_mejora` (
  `id_mejora` int(7) NOT NULL,
  `documento` varchar(13) NOT NULL,
  `fecha_propuesta` date NOT NULL,
  `descripcion_idea` text NOT NULL,
  `estado` varchar(50) NOT NULL,
  `fecha_implementacion` date NOT NULL,
  `descripcion_implementacion` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `impuesto`
--

CREATE TABLE `impuesto` (
  `id_impuesto` int(11) NOT NULL,
  `tipo_impuesto` varchar(40) NOT NULL,
  `tasa_impuesto` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `impuesto`
--

INSERT INTO `impuesto` (`id_impuesto`, `tipo_impuesto`, `tasa_impuesto`) VALUES
(5, 'ISV', 18),
(6, 'ISV', 0);

--
-- Disparadores `impuesto`
--
DELIMITER $$
CREATE TRIGGER `after_insert_impuesto` AFTER INSERT ON `impuesto` FOR EACH ROW BEGIN
    INSERT INTO historicos_impuestos (
        id_impuesto, 
        acciones, 
        fecha, 
        descripcion
    ) VALUES (
        NEW.id_impuesto, 
        'Insertar', 
        NOW(), 
        CONCAT('Se ha insertado un impuesto: ', NEW.tipo_impuesto, ' con tasa: ', NEW.tasa_impuesto)
    );
END
$$
DELIMITER ;
DELIMITER $$
CREATE TRIGGER `after_update_impuesto` AFTER UPDATE ON `impuesto` FOR EACH ROW BEGIN
    INSERT INTO historicos_impuestos (
        id_impuesto, 
        acciones, 
        fecha, 
        descripcion
    ) VALUES (
        NEW.id_impuesto, 
        'Actualizar', 
        NOW(), 
        CONCAT('Se ha actualizado el impuesto: ', NEW.tipo_impuesto, ' de tasa: ', OLD.tasa_impuesto, ' a: ', NEW.tasa_impuesto)
    );
END
$$
DELIMITER ;
DELIMITER $$
CREATE TRIGGER `before_delete_impuesto` BEFORE DELETE ON `impuesto` FOR EACH ROW BEGIN
    INSERT INTO historicos_impuestos (
        id_impuesto, 
        acciones, 
        fecha, 
        descripcion
    ) VALUES (
        OLD.id_impuesto, 
        'Eliminar', 
        NOW(), 
        CONCAT('Se ha eliminado el impuesto: ', OLD.tipo_impuesto, ' con tasa: ', OLD.tasa_impuesto)
    );
END
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `inventario`
--

CREATE TABLE `inventario` (
  `id_inventario` int(100) NOT NULL,
  `id_producto` int(11) DEFAULT NULL,
  `id_categoria` int(11) DEFAULT NULL,
  `cantidad_en_stock` int(100) NOT NULL,
  `stock_minimo` int(100) NOT NULL,
  `stock_maximo` int(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `inventario`
--

INSERT INTO `inventario` (`id_inventario`, `id_producto`, `id_categoria`, `cantidad_en_stock`, `stock_minimo`, `stock_maximo`) VALUES
(20, 37, 3, 22, 0, 1000),
(22, 39, 15, 10, 0, 1000),
(23, 40, 15, 2, 0, 1000);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `mantenimiento_equipo`
--

CREATE TABLE `mantenimiento_equipo` (
  `id_mantenimiento` int(11) NOT NULL,
  `id_equipo` int(11) NOT NULL,
  `fecha` date NOT NULL,
  `tipo` varchar(20) NOT NULL,
  `detalles` varchar(20) NOT NULL,
  `estado` varchar(20) NOT NULL,
  `documento` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `mantenimiento_equipo`
--

INSERT INTO `mantenimiento_equipo` (`id_mantenimiento`, `id_equipo`, `fecha`, `tipo`, `detalles`, `estado`, `documento`) VALUES
(5, 3030, '2024-08-15', 'electrico', 'ocupo cambio de cier', 'medio', '0801567890124');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `metodo_de_pago`
--

CREATE TABLE `metodo_de_pago` (
  `id_metodo` int(11) NOT NULL,
  `nombre` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `metodo_de_pago`
--

INSERT INTO `metodo_de_pago` (`id_metodo`, `nombre`) VALUES
(1, 'Tarjeta de Credito');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `pedido_de_compra_cliente`
--

CREATE TABLE `pedido_de_compra_cliente` (
  `id_pedido` int(11) NOT NULL,
  `numero_factura` varchar(20) DEFAULT NULL,
  `id_cliente` int(11) DEFAULT NULL,
  `fecha_pedido` date DEFAULT NULL,
  `fecha_entrega_estimada` date DEFAULT NULL,
  `fecha_entrega` date DEFAULT NULL,
  `id_metodo` int(11) DEFAULT NULL,
  `id_estado` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `pedido_de_compra_cliente`
--

INSERT INTO `pedido_de_compra_cliente` (`id_pedido`, `numero_factura`, `id_cliente`, `fecha_pedido`, `fecha_entrega_estimada`, `fecha_entrega`, `id_metodo`, `id_estado`) VALUES
(4, 'FAC-02-01-989687', 27, '2024-08-10', '2024-08-14', NULL, 1, 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `pedido_de_compra_proveedor`
--

CREATE TABLE `pedido_de_compra_proveedor` (
  `id_pedido` int(11) NOT NULL,
  `id_proveedor` int(11) DEFAULT NULL,
  `numero_factura` varchar(20) DEFAULT NULL,
  `fecha_pedido` date DEFAULT NULL,
  `fecha_entrega_estimada` date DEFAULT NULL,
  `fecha_entrega` date DEFAULT NULL,
  `id_metodo` int(11) DEFAULT NULL,
  `id_estado` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `pedido_de_compra_proveedor`
--

INSERT INTO `pedido_de_compra_proveedor` (`id_pedido`, `id_proveedor`, `numero_factura`, `fecha_pedido`, `fecha_entrega_estimada`, `fecha_entrega`, `id_metodo`, `id_estado`) VALUES
(14, 8, 'FAC-01-02-202408', '2024-08-10', '2024-08-21', '2024-08-22', 1, 1),
(17, 4, NULL, '2024-08-10', '2024-08-13', NULL, 1, 1);

--
-- Disparadores `pedido_de_compra_proveedor`
--
DELIMITER $$
CREATE TRIGGER `actualizar_inventario` AFTER UPDATE ON `pedido_de_compra_proveedor` FOR EACH ROW BEGIN
    -- Verifica si el estado del pedido ha cambiado a "recibido"
    IF NEW.id_estado = 2 AND OLD.id_estado = 1 THEN
        -- Aumenta la cantidad en el inventario por los detalles de compra relacionados
        UPDATE inventario
        SET cantidad_en_stock = cantidad_en_stock + (
            SELECT SUM(cantidad)
            FROM detalle_de_compra_proveedor
            WHERE id_pedido = NEW.id_pedido
        )
        WHERE id_producto IN (
            SELECT id_producto
            FROM detalle_de_compra_proveedor
            WHERE id_pedido = NEW.id_pedido
        );
    END IF;
END
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `producto`
--

CREATE TABLE `producto` (
  `id_producto` int(100) NOT NULL,
  `nombre` varchar(50) NOT NULL,
  `id_categoria` int(11) DEFAULT NULL,
  `id_proveedor` int(11) DEFAULT NULL,
  `original_precio` decimal(10,2) DEFAULT NULL,
  `id_impuesto` int(11) DEFAULT NULL,
  `id_promocion` int(100) DEFAULT NULL,
  `id_garantia` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `producto`
--

INSERT INTO `producto` (`id_producto`, `nombre`, `id_categoria`, `id_proveedor`, `original_precio`, `id_impuesto`, `id_promocion`, `id_garantia`) VALUES
(37, 'Camisas Polo', 3, 1, 200.00, 5, 11, 1),
(39, 'Estufa de Gas', 15, 9, 10000.00, 5, 11, 2),
(40, 'Telefono', 15, 7, 10000.00, 5, 11, 1);

--
-- Disparadores `producto`
--
DELIMITER $$
CREATE TRIGGER `after_insert_producto` AFTER INSERT ON `producto` FOR EACH ROW BEGIN
    INSERT INTO historicos_productos (
        id_producto, 
        accion, 
        fecha, 
        descripcion
    ) VALUES (
        NEW.id_producto, 
        'Insertar', 
        NOW(), 
        CONCAT('Se ha insertado el producto: ', NEW.nombre, ' con precio original: ', NEW.original_precio)
    );
END
$$
DELIMITER ;
DELIMITER $$
CREATE TRIGGER `after_product_insert` AFTER INSERT ON `producto` FOR EACH ROW BEGIN
    INSERT INTO inventario (id_producto, id_categoria, cantidad_en_stock, stock_minimo, stock_maximo)
    VALUES (NEW.id_producto, NEW.id_categoria, 0, 0, 1000);
END
$$
DELIMITER ;
DELIMITER $$
CREATE TRIGGER `after_update_producto` AFTER UPDATE ON `producto` FOR EACH ROW BEGIN
    INSERT INTO historicos_productos (
        id_producto, 
        accion, 
        fecha, 
        descripcion
    ) VALUES (
        NEW.id_producto, 
        'Actualizar', 
        NOW(), 
        CONCAT('Se ha actualizado el producto: ', NEW.nombre, ' de precio: ', OLD.original_precio, ' a: ', NEW.original_precio)
    );
END
$$
DELIMITER ;
DELIMITER $$
CREATE TRIGGER `before_delete_producto` BEFORE DELETE ON `producto` FOR EACH ROW BEGIN
    INSERT INTO historicos_productos (
        id_producto, 
        accion, 
        fecha, 
        descripcion
    ) VALUES (
        OLD.id_producto, 
        'Eliminar', 
        NOW(), 
        CONCAT('Se ha eliminado el producto: ', OLD.nombre, ' con precio: ', OLD.original_precio)
    );
END
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `promocion`
--

CREATE TABLE `promocion` (
  `id_promocion` int(100) NOT NULL,
  `nombre` varchar(50) NOT NULL,
  `valor` decimal(50,2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `promocion`
--

INSERT INTO `promocion` (`id_promocion`, `nombre`, `valor`) VALUES
(11, 'Descuento de 5%', 0.05),
(12, 'Descuento de 10%', 0.10),
(13, 'Descuento de 15%', 0.15),
(14, 'Descuento de 20%', 0.20),
(15, 'Descuento de 25%', 0.25),
(16, 'Descuento de 30%', 0.30),
(17, 'Descuento de 40%', 0.40),
(18, 'Descuento de 50%', 0.50);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `proveedores`
--

CREATE TABLE `proveedores` (
  `id_proveedor` int(11) NOT NULL,
  `Nombre_del_proveedor` varchar(50) NOT NULL,
  `Producto_Servicio` text NOT NULL,
  `Historial_de_desempeño` text NOT NULL,
  `nombre_compañia` varchar(20) NOT NULL,
  `Telefono` varchar(10) NOT NULL,
  `Ciudad` varchar(20) NOT NULL,
  `tipo` varchar(50) NOT NULL,
  `Documento` varchar(13) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `proveedores`
--

INSERT INTO `proveedores` (`id_proveedor`, `Nombre_del_proveedor`, `Producto_Servicio`, `Historial_de_desempeño`, `nombre_compañia`, `Telefono`, `Ciudad`, `tipo`, `Documento`) VALUES
(1, 'Ana López', 'Electrónica', 'A', 'Tech Innovators', '123-456-78', 'Ciudad A', 'Proveedor', '123456789'),
(2, 'Carlos Martínez', 'Ropa', 'B', 'Fashion Hub', '098-765-43', 'Ciudad B', 'Proveedor', '987654321'),
(3, 'Beatriz Gómez', 'Juguetes', 'C', 'Toy World', '456-789-01', 'Ciudad C', 'Proveedor', '456789123'),
(4, 'David Fernández', 'Electrodomésticos', 'A', 'Home Appliances', '321-654-09', 'Ciudad D', 'Proveedor', '321654987'),
(5, 'Elena Rodríguez', 'Muebles', 'B', 'Furniture Land', '789-012-34', 'Ciudad E', 'Proveedor', '789012345'),
(6, 'Francisco Hernández', 'Deportes', 'C', 'Sport Center', '654-321-09', 'Ciudad F', 'Proveedor', '654321098'),
(7, 'Gabriela Ruiz', 'Libros', 'A', 'Book Haven', '012-345-67', 'Ciudad G', 'Proveedor', '012345678'),
(8, 'Héctor Jiménez', 'Jardinería', 'B', 'Garden Supplies', '987-654-32', 'Ciudad H', 'Proveedor', '987654321'),
(9, 'Isabel Vargas', 'Oficina', 'C', 'Office Solutions', '123-789-45', 'Ciudad I', 'Proveedor', '123789456'),
(10, 'Juan Pérez', 'Alimentos', 'A', 'Food Distributors', '654-789-12', 'Ciudad J', 'Proveedor', '654789123'),
(11, 'sadasdsd', 'dasdadsd', 'Medio', 'pollos chepita', '2282-6399', 'Tegus', 'RTN', '0801200010203'),
(12, 'David Hernandez', 'pollo asado', 'Bueno', 'pollo campero', '2235-5980', 'tamaluipa', 'RTN', '0801199812345');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `puesto_de_trabajo`
--

CREATE TABLE `puesto_de_trabajo` (
  `id_puesto` int(11) NOT NULL,
  `id_documento` int(11) DEFAULT NULL,
  `fecha` datetime NOT NULL,
  `hora_inicio` time NOT NULL,
  `hora_fin` time NOT NULL,
  `puesto_trabajo` varchar(50) DEFAULT NULL,
  `salario` decimal(10,0) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `puesto_de_trabajo`
--

INSERT INTO `puesto_de_trabajo` (`id_puesto`, `id_documento`, `fecha`, `hora_inicio`, `hora_fin`, `puesto_trabajo`, `salario`) VALUES
(1, 3, '2024-08-03 00:00:00', '07:00:00', '14:00:00', 'empresario', 5000);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `sar`
--

CREATE TABLE `sar` (
  `id_sar` int(11) NOT NULL,
  `rtn` varchar(16) NOT NULL,
  `cai` varchar(50) NOT NULL,
  `fecha_emision` datetime NOT NULL,
  `fecha_vencimiento` datetime NOT NULL,
  `rango_inicial` int(11) NOT NULL,
  `rango_final` int(11) NOT NULL,
  `id_sucursal` int(11) DEFAULT NULL,
  `secuencial` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `seguimiento_de_envio`
--

CREATE TABLE `seguimiento_de_envio` (
  `id_seguimiento` int(11) NOT NULL,
  `id_pedido` int(11) DEFAULT NULL,
  `fecha_envio` datetime DEFAULT NULL,
  `fecha_entrega_estimada` datetime DEFAULT NULL,
  `fecha_entrega_real` datetime DEFAULT NULL,
  `estado` varchar(100) NOT NULL,
  `id_transportista` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `sucursales`
--

CREATE TABLE `sucursales` (
  `id_sucursal` int(11) NOT NULL,
  `Ciudad` varchar(20) NOT NULL,
  `Telefono` varchar(9) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `sucursales`
--

INSERT INTO `sucursales` (`id_sucursal`, `Ciudad`, `Telefono`) VALUES
(1, 'Sucursal Central', '1689-4568'),
(2, 'Sucursal Norte', '2345-6789'),
(3, 'Sucursal Sur', '3456-7890'),
(4, 'Sucursal Este', '4567-8901'),
(5, 'Sucursal Oeste', '5678-9012'),
(6, 'Sucursal Playa', '6789-0123'),
(7, 'Sucursal Montaña', '7890-1234'),
(8, 'Sucursal Río', '8901-2345'),
(9, 'Sucursal Centro Hist', '9012-3456'),
(10, 'Sucursal Aeropuerto', '0123-4567'),
(19, 'Sucursal XY', '9618-7469');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `transportistas`
--

CREATE TABLE `transportistas` (
  `id_transportista` int(11) NOT NULL,
  `nombre_empresa` varchar(40) NOT NULL,
  `Telefono` varchar(15) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `transportistas`
--

INSERT INTO `transportistas` (`id_transportista`, `nombre_empresa`, `Telefono`) VALUES
(1, 'Transporte chipita', '9654-8969');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuarios`
--

CREATE TABLE `usuarios` (
  `id_usuario` int(100) NOT NULL,
  `primer_nombre` varchar(20) NOT NULL,
  `primer_apellido` varchar(20) NOT NULL,
  `correo` varchar(50) NOT NULL,
  `password` varchar(50) NOT NULL,
  `usuario_activo` int(100) NOT NULL,
  `super_usuario` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `usuarios`
--

INSERT INTO `usuarios` (`id_usuario`, `primer_nombre`, `primer_apellido`, `correo`, `password`, `usuario_activo`, `super_usuario`) VALUES
(10, 'Joshua', 'Martinez', 'joshuamartinez8723@gmail.com', 'scrypt:32768:8:1$i0FUw5cQLYcODDLJ$2b94d6db9f9aa32e', 1, 1);

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `almacenes`
--
ALTER TABLE `almacenes`
  ADD PRIMARY KEY (`id_almacenes`);

--
-- Indices de la tabla `capacitacion`
--
ALTER TABLE `capacitacion`
  ADD PRIMARY KEY (`id_capacitacion`),
  ADD KEY `capacitacion_FK` (`id_empleado`);

--
-- Indices de la tabla `categorias`
--
ALTER TABLE `categorias`
  ADD PRIMARY KEY (`id_categoria`);

--
-- Indices de la tabla `cliente`
--
ALTER TABLE `cliente`
  ADD PRIMARY KEY (`id_cliente`);

--
-- Indices de la tabla `detalles_de_factura`
--
ALTER TABLE `detalles_de_factura`
  ADD PRIMARY KEY (`id_detalle`),
  ADD KEY `detalles_de_factura_FK` (`id_factura`),
  ADD KEY `detalles_de_factura_FK_1` (`id_producto`),
  ADD KEY `detalles_de_factura_FK_2` (`id_pedido`);

--
-- Indices de la tabla `detalle_de_compra_cliente`
--
ALTER TABLE `detalle_de_compra_cliente`
  ADD PRIMARY KEY (`id_detalle`),
  ADD KEY `detalle_de_compra_cliente_FK` (`id_pedido`);

--
-- Indices de la tabla `detalle_de_compra_proveedor`
--
ALTER TABLE `detalle_de_compra_proveedor`
  ADD PRIMARY KEY (`id_detalle`),
  ADD KEY `detalle_de_compra_proveedor_FK` (`id_pedido`),
  ADD KEY `detalle_de_compra_proveedor_FK_1` (`id_estado`),
  ADD KEY `detalle_de_compra_proveedor_FK_2` (`id_producto`);

--
-- Indices de la tabla `devoluciones_compras`
--
ALTER TABLE `devoluciones_compras`
  ADD PRIMARY KEY (`id_devolucion`),
  ADD KEY `devoluciones_compra_FK` (`id_detalle`),
  ADD KEY `devoluciones_compra_FK_1` (`id_pedido`);

--
-- Indices de la tabla `devoluciones_ventas`
--
ALTER TABLE `devoluciones_ventas`
  ADD PRIMARY KEY (`id_devolucion`),
  ADD KEY `devoluciones_ventas_FK` (`id_detalle`),
  ADD KEY `devoluciones_ventas_FK_1` (`id_pedido`);

--
-- Indices de la tabla `distribucion_almacenes`
--
ALTER TABLE `distribucion_almacenes`
  ADD PRIMARY KEY (`id_distribucion`),
  ADD KEY `distribucion_almacenes_FK` (`id_producto`),
  ADD KEY `distribucion_almacenes_FK_1` (`id_almacenes`);

--
-- Indices de la tabla `documentacion_clientes`
--
ALTER TABLE `documentacion_clientes`
  ADD PRIMARY KEY (`id_documentoc`);

--
-- Indices de la tabla `documento_empleado`
--
ALTER TABLE `documento_empleado`
  ADD PRIMARY KEY (`id_documento`),
  ADD UNIQUE KEY `documento` (`documento`);

--
-- Indices de la tabla `empleados`
--
ALTER TABLE `empleados`
  ADD PRIMARY KEY (`id_empleado`);

--
-- Indices de la tabla `equipo`
--
ALTER TABLE `equipo`
  ADD PRIMARY KEY (`id_equipo`);

--
-- Indices de la tabla `estado`
--
ALTER TABLE `estado`
  ADD PRIMARY KEY (`id_estado`);

--
-- Indices de la tabla `factura`
--
ALTER TABLE `factura`
  ADD PRIMARY KEY (`id_factura`),
  ADD KEY `factura_FK` (`id_cliente`),
  ADD KEY `factura_FK_1` (`id_sar`),
  ADD KEY `factura_FK_2` (`id_estado`);

--
-- Indices de la tabla `garantia`
--
ALTER TABLE `garantia`
  ADD PRIMARY KEY (`id_garantia`);

--
-- Indices de la tabla `historial_de_pagos`
--
ALTER TABLE `historial_de_pagos`
  ADD PRIMARY KEY (`id_pago`),
  ADD KEY `historial_de_pagos_FK` (`id_cliente`),
  ADD KEY `historial_de_pagos_FK_1` (`id_factura`),
  ADD KEY `historial_de_pagos_FK_2` (`id_metodo`);

--
-- Indices de la tabla `historicos_almacenes`
--
ALTER TABLE `historicos_almacenes`
  ADD PRIMARY KEY (`id_historicos`),
  ADD KEY `historicos_almacenes_FK` (`id_almacenes`);

--
-- Indices de la tabla `historicos_clientes`
--
ALTER TABLE `historicos_clientes`
  ADD PRIMARY KEY (`id_historico`),
  ADD KEY `historicos_clientes_FK` (`id_cliente`);

--
-- Indices de la tabla `historicos_devolucion`
--
ALTER TABLE `historicos_devolucion`
  ADD PRIMARY KEY (`id_historico`),
  ADD KEY `historicos_devolucion_FK` (`id_devolucion`);

--
-- Indices de la tabla `historicos_empleados`
--
ALTER TABLE `historicos_empleados`
  ADD PRIMARY KEY (`id_historico`),
  ADD KEY `historicos_empleados_FK` (`id_empleado`);

--
-- Indices de la tabla `historicos_impuestos`
--
ALTER TABLE `historicos_impuestos`
  ADD PRIMARY KEY (`id_historico`),
  ADD KEY `historicos_impuestos_FK` (`id_impuesto`);

--
-- Indices de la tabla `historicos_productos`
--
ALTER TABLE `historicos_productos`
  ADD PRIMARY KEY (`id_historico`),
  ADD KEY `historicos_productos_FK` (`id_producto`);

--
-- Indices de la tabla `ideas_mejora`
--
ALTER TABLE `ideas_mejora`
  ADD PRIMARY KEY (`id_mejora`);

--
-- Indices de la tabla `impuesto`
--
ALTER TABLE `impuesto`
  ADD PRIMARY KEY (`id_impuesto`);

--
-- Indices de la tabla `inventario`
--
ALTER TABLE `inventario`
  ADD PRIMARY KEY (`id_inventario`),
  ADD KEY `inventario_FK` (`id_producto`),
  ADD KEY `inventario_FK_1` (`id_categoria`);

--
-- Indices de la tabla `mantenimiento_equipo`
--
ALTER TABLE `mantenimiento_equipo`
  ADD PRIMARY KEY (`id_mantenimiento`),
  ADD KEY `mantenimiento_equipo_FK` (`id_equipo`);

--
-- Indices de la tabla `metodo_de_pago`
--
ALTER TABLE `metodo_de_pago`
  ADD PRIMARY KEY (`id_metodo`);

--
-- Indices de la tabla `pedido_de_compra_cliente`
--
ALTER TABLE `pedido_de_compra_cliente`
  ADD PRIMARY KEY (`id_pedido`),
  ADD KEY `pedido_de_compra_cliente__FK` (`id_cliente`),
  ADD KEY `pedido_de_compra_cliente__FK_2` (`id_metodo`),
  ADD KEY `pedido_de_compra_cliente__FK_1` (`id_estado`);

--
-- Indices de la tabla `pedido_de_compra_proveedor`
--
ALTER TABLE `pedido_de_compra_proveedor`
  ADD PRIMARY KEY (`id_pedido`),
  ADD KEY `pedido_de_compra_proveedor__FK_1` (`id_proveedor`),
  ADD KEY `pedido_de_compra_proveedor__FK_2` (`id_metodo`),
  ADD KEY `pedido_de_compra_proveedor__FK` (`id_estado`);

--
-- Indices de la tabla `producto`
--
ALTER TABLE `producto`
  ADD PRIMARY KEY (`id_producto`),
  ADD KEY `producto_FK` (`id_categoria`),
  ADD KEY `producto_FK_1` (`id_proveedor`),
  ADD KEY `producto_FK_2` (`id_impuesto`),
  ADD KEY `producto_FK_3` (`id_promocion`),
  ADD KEY `producto_FK_4` (`id_garantia`);

--
-- Indices de la tabla `promocion`
--
ALTER TABLE `promocion`
  ADD PRIMARY KEY (`id_promocion`);

--
-- Indices de la tabla `proveedores`
--
ALTER TABLE `proveedores`
  ADD PRIMARY KEY (`id_proveedor`);

--
-- Indices de la tabla `puesto_de_trabajo`
--
ALTER TABLE `puesto_de_trabajo`
  ADD PRIMARY KEY (`id_puesto`),
  ADD KEY `puesto_de_trabajo_FK` (`id_documento`);

--
-- Indices de la tabla `sar`
--
ALTER TABLE `sar`
  ADD PRIMARY KEY (`id_sar`),
  ADD KEY `sar_FK` (`id_sucursal`);

--
-- Indices de la tabla `seguimiento_de_envio`
--
ALTER TABLE `seguimiento_de_envio`
  ADD PRIMARY KEY (`id_seguimiento`),
  ADD KEY `seguimiento_de_envio_FK` (`id_pedido`),
  ADD KEY `seguimiento_de_envio_FK_1` (`id_transportista`);

--
-- Indices de la tabla `sucursales`
--
ALTER TABLE `sucursales`
  ADD PRIMARY KEY (`id_sucursal`);

--
-- Indices de la tabla `transportistas`
--
ALTER TABLE `transportistas`
  ADD PRIMARY KEY (`id_transportista`);

--
-- Indices de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  ADD PRIMARY KEY (`id_usuario`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `almacenes`
--
ALTER TABLE `almacenes`
  MODIFY `id_almacenes` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT de la tabla `capacitacion`
--
ALTER TABLE `capacitacion`
  MODIFY `id_capacitacion` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT de la tabla `categorias`
--
ALTER TABLE `categorias`
  MODIFY `id_categoria` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=16;

--
-- AUTO_INCREMENT de la tabla `cliente`
--
ALTER TABLE `cliente`
  MODIFY `id_cliente` int(10) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=28;

--
-- AUTO_INCREMENT de la tabla `detalles_de_factura`
--
ALTER TABLE `detalles_de_factura`
  MODIFY `id_detalle` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `detalle_de_compra_cliente`
--
ALTER TABLE `detalle_de_compra_cliente`
  MODIFY `id_detalle` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT de la tabla `detalle_de_compra_proveedor`
--
ALTER TABLE `detalle_de_compra_proveedor`
  MODIFY `id_detalle` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=17;

--
-- AUTO_INCREMENT de la tabla `devoluciones_compras`
--
ALTER TABLE `devoluciones_compras`
  MODIFY `id_devolucion` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT de la tabla `devoluciones_ventas`
--
ALTER TABLE `devoluciones_ventas`
  MODIFY `id_devolucion` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT de la tabla `distribucion_almacenes`
--
ALTER TABLE `distribucion_almacenes`
  MODIFY `id_distribucion` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=21;

--
-- AUTO_INCREMENT de la tabla `documentacion_clientes`
--
ALTER TABLE `documentacion_clientes`
  MODIFY `id_documentoc` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT de la tabla `documento_empleado`
--
ALTER TABLE `documento_empleado`
  MODIFY `id_documento` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=16;

--
-- AUTO_INCREMENT de la tabla `empleados`
--
ALTER TABLE `empleados`
  MODIFY `id_empleado` int(6) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=17;

--
-- AUTO_INCREMENT de la tabla `equipo`
--
ALTER TABLE `equipo`
  MODIFY `id_equipo` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3031;

--
-- AUTO_INCREMENT de la tabla `estado`
--
ALTER TABLE `estado`
  MODIFY `id_estado` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT de la tabla `factura`
--
ALTER TABLE `factura`
  MODIFY `id_factura` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `garantia`
--
ALTER TABLE `garantia`
  MODIFY `id_garantia` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT de la tabla `historial_de_pagos`
--
ALTER TABLE `historial_de_pagos`
  MODIFY `id_pago` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `historicos_almacenes`
--
ALTER TABLE `historicos_almacenes`
  MODIFY `id_historicos` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=17;

--
-- AUTO_INCREMENT de la tabla `historicos_clientes`
--
ALTER TABLE `historicos_clientes`
  MODIFY `id_historico` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=28;

--
-- AUTO_INCREMENT de la tabla `historicos_devolucion`
--
ALTER TABLE `historicos_devolucion`
  MODIFY `id_historico` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `historicos_empleados`
--
ALTER TABLE `historicos_empleados`
  MODIFY `id_historico` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT de la tabla `historicos_impuestos`
--
ALTER TABLE `historicos_impuestos`
  MODIFY `id_historico` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=16;

--
-- AUTO_INCREMENT de la tabla `historicos_productos`
--
ALTER TABLE `historicos_productos`
  MODIFY `id_historico` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=32;

--
-- AUTO_INCREMENT de la tabla `ideas_mejora`
--
ALTER TABLE `ideas_mejora`
  MODIFY `id_mejora` int(7) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT de la tabla `impuesto`
--
ALTER TABLE `impuesto`
  MODIFY `id_impuesto` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT de la tabla `inventario`
--
ALTER TABLE `inventario`
  MODIFY `id_inventario` int(100) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=24;

--
-- AUTO_INCREMENT de la tabla `mantenimiento_equipo`
--
ALTER TABLE `mantenimiento_equipo`
  MODIFY `id_mantenimiento` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT de la tabla `metodo_de_pago`
--
ALTER TABLE `metodo_de_pago`
  MODIFY `id_metodo` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT de la tabla `pedido_de_compra_cliente`
--
ALTER TABLE `pedido_de_compra_cliente`
  MODIFY `id_pedido` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT de la tabla `pedido_de_compra_proveedor`
--
ALTER TABLE `pedido_de_compra_proveedor`
  MODIFY `id_pedido` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=18;

--
-- AUTO_INCREMENT de la tabla `producto`
--
ALTER TABLE `producto`
  MODIFY `id_producto` int(100) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=41;

--
-- AUTO_INCREMENT de la tabla `promocion`
--
ALTER TABLE `promocion`
  MODIFY `id_promocion` int(100) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=20;

--
-- AUTO_INCREMENT de la tabla `proveedores`
--
ALTER TABLE `proveedores`
  MODIFY `id_proveedor` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;

--
-- AUTO_INCREMENT de la tabla `puesto_de_trabajo`
--
ALTER TABLE `puesto_de_trabajo`
  MODIFY `id_puesto` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT de la tabla `sar`
--
ALTER TABLE `sar`
  MODIFY `id_sar` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `sucursales`
--
ALTER TABLE `sucursales`
  MODIFY `id_sucursal` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=20;

--
-- AUTO_INCREMENT de la tabla `transportistas`
--
ALTER TABLE `transportistas`
  MODIFY `id_transportista` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  MODIFY `id_usuario` int(100) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `capacitacion`
--
ALTER TABLE `capacitacion`
  ADD CONSTRAINT `capacitacion_FK` FOREIGN KEY (`id_empleado`) REFERENCES `empleados` (`id_empleado`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Filtros para la tabla `detalles_de_factura`
--
ALTER TABLE `detalles_de_factura`
  ADD CONSTRAINT `detalles_de_factura_FK` FOREIGN KEY (`id_factura`) REFERENCES `factura` (`id_factura`) ON UPDATE CASCADE,
  ADD CONSTRAINT `detalles_de_factura_FK_1` FOREIGN KEY (`id_producto`) REFERENCES `producto` (`id_producto`) ON UPDATE CASCADE,
  ADD CONSTRAINT `detalles_de_factura_FK_2` FOREIGN KEY (`id_pedido`) REFERENCES `pedido_de_compra_cliente` (`id_pedido`) ON UPDATE CASCADE;

--
-- Filtros para la tabla `detalle_de_compra_cliente`
--
ALTER TABLE `detalle_de_compra_cliente`
  ADD CONSTRAINT `detalle_de_compra_cliente_FK` FOREIGN KEY (`id_pedido`) REFERENCES `pedido_de_compra_cliente` (`id_pedido`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Filtros para la tabla `detalle_de_compra_proveedor`
--
ALTER TABLE `detalle_de_compra_proveedor`
  ADD CONSTRAINT `detalle_de_compra_proveedor_FK` FOREIGN KEY (`id_pedido`) REFERENCES `pedido_de_compra_proveedor` (`id_pedido`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `detalle_de_compra_proveedor_FK_1` FOREIGN KEY (`id_estado`) REFERENCES `estado` (`id_estado`) ON UPDATE CASCADE,
  ADD CONSTRAINT `detalle_de_compra_proveedor_FK_2` FOREIGN KEY (`id_producto`) REFERENCES `producto` (`id_producto`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Filtros para la tabla `devoluciones_compras`
--
ALTER TABLE `devoluciones_compras`
  ADD CONSTRAINT `devoluciones_compra_FK` FOREIGN KEY (`id_detalle`) REFERENCES `detalle_de_compra_proveedor` (`id_detalle`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `devoluciones_compra_FK_1` FOREIGN KEY (`id_pedido`) REFERENCES `pedido_de_compra_proveedor` (`id_pedido`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Filtros para la tabla `distribucion_almacenes`
--
ALTER TABLE `distribucion_almacenes`
  ADD CONSTRAINT `distribucion_almacenes_FK` FOREIGN KEY (`id_producto`) REFERENCES `producto` (`id_producto`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `distribucion_almacenes_FK_1` FOREIGN KEY (`id_almacenes`) REFERENCES `almacenes` (`id_almacenes`) ON UPDATE CASCADE;

--
-- Filtros para la tabla `factura`
--
ALTER TABLE `factura`
  ADD CONSTRAINT `factura_FK` FOREIGN KEY (`id_cliente`) REFERENCES `cliente` (`id_cliente`) ON UPDATE CASCADE,
  ADD CONSTRAINT `factura_FK_1` FOREIGN KEY (`id_sar`) REFERENCES `sar` (`id_sar`) ON UPDATE CASCADE,
  ADD CONSTRAINT `factura_FK_2` FOREIGN KEY (`id_estado`) REFERENCES `estado` (`id_estado`) ON UPDATE CASCADE;

--
-- Filtros para la tabla `historial_de_pagos`
--
ALTER TABLE `historial_de_pagos`
  ADD CONSTRAINT `historial_de_pagos_FK` FOREIGN KEY (`id_cliente`) REFERENCES `cliente` (`id_cliente`) ON UPDATE CASCADE,
  ADD CONSTRAINT `historial_de_pagos_FK_1` FOREIGN KEY (`id_factura`) REFERENCES `factura` (`id_factura`) ON UPDATE CASCADE,
  ADD CONSTRAINT `historial_de_pagos_FK_2` FOREIGN KEY (`id_metodo`) REFERENCES `metodo_de_pago` (`id_metodo`) ON UPDATE CASCADE;

--
-- Filtros para la tabla `historicos_almacenes`
--
ALTER TABLE `historicos_almacenes`
  ADD CONSTRAINT `historicos_almacenes_FK` FOREIGN KEY (`id_almacenes`) REFERENCES `almacenes` (`id_almacenes`) ON DELETE SET NULL ON UPDATE CASCADE;

--
-- Filtros para la tabla `historicos_clientes`
--
ALTER TABLE `historicos_clientes`
  ADD CONSTRAINT `historicos_clientes_FK` FOREIGN KEY (`id_cliente`) REFERENCES `cliente` (`id_cliente`) ON DELETE SET NULL ON UPDATE CASCADE;

--
-- Filtros para la tabla `historicos_empleados`
--
ALTER TABLE `historicos_empleados`
  ADD CONSTRAINT `historicos_empleados_FK` FOREIGN KEY (`id_empleado`) REFERENCES `empleados` (`id_empleado`) ON DELETE SET NULL ON UPDATE CASCADE;

--
-- Filtros para la tabla `historicos_impuestos`
--
ALTER TABLE `historicos_impuestos`
  ADD CONSTRAINT `historicos_impuestos_FK` FOREIGN KEY (`id_impuesto`) REFERENCES `impuesto` (`id_impuesto`) ON DELETE SET NULL ON UPDATE CASCADE;

--
-- Filtros para la tabla `historicos_productos`
--
ALTER TABLE `historicos_productos`
  ADD CONSTRAINT `historicos_productos_FK` FOREIGN KEY (`id_producto`) REFERENCES `producto` (`id_producto`) ON DELETE SET NULL ON UPDATE CASCADE;

--
-- Filtros para la tabla `inventario`
--
ALTER TABLE `inventario`
  ADD CONSTRAINT `inventario_FK` FOREIGN KEY (`id_producto`) REFERENCES `producto` (`id_producto`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `inventario_FK_1` FOREIGN KEY (`id_categoria`) REFERENCES `categorias` (`id_categoria`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Filtros para la tabla `mantenimiento_equipo`
--
ALTER TABLE `mantenimiento_equipo`
  ADD CONSTRAINT `mantenimiento_equipo_FK` FOREIGN KEY (`id_equipo`) REFERENCES `equipo` (`id_equipo`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Filtros para la tabla `pedido_de_compra_cliente`
--
ALTER TABLE `pedido_de_compra_cliente`
  ADD CONSTRAINT `pedido_de_compra_cliente__FK` FOREIGN KEY (`id_cliente`) REFERENCES `cliente` (`id_cliente`) ON UPDATE CASCADE,
  ADD CONSTRAINT `pedido_de_compra_cliente__FK_1` FOREIGN KEY (`id_estado`) REFERENCES `estado` (`id_estado`) ON UPDATE CASCADE,
  ADD CONSTRAINT `pedido_de_compra_cliente__FK_2` FOREIGN KEY (`id_metodo`) REFERENCES `metodo_de_pago` (`id_metodo`) ON UPDATE CASCADE;

--
-- Filtros para la tabla `pedido_de_compra_proveedor`
--
ALTER TABLE `pedido_de_compra_proveedor`
  ADD CONSTRAINT `pedido_de_compra_proveedor__FK` FOREIGN KEY (`id_estado`) REFERENCES `estado` (`id_estado`) ON UPDATE CASCADE,
  ADD CONSTRAINT `pedido_de_compra_proveedor__FK_1` FOREIGN KEY (`id_proveedor`) REFERENCES `proveedores` (`id_proveedor`) ON UPDATE CASCADE,
  ADD CONSTRAINT `pedido_de_compra_proveedor__FK_2` FOREIGN KEY (`id_metodo`) REFERENCES `metodo_de_pago` (`id_metodo`) ON UPDATE CASCADE;

--
-- Filtros para la tabla `producto`
--
ALTER TABLE `producto`
  ADD CONSTRAINT `producto_FK` FOREIGN KEY (`id_categoria`) REFERENCES `categorias` (`id_categoria`) ON DELETE SET NULL ON UPDATE CASCADE,
  ADD CONSTRAINT `producto_FK_1` FOREIGN KEY (`id_proveedor`) REFERENCES `proveedores` (`id_proveedor`) ON DELETE SET NULL,
  ADD CONSTRAINT `producto_FK_2` FOREIGN KEY (`id_impuesto`) REFERENCES `impuesto` (`id_impuesto`) ON DELETE SET NULL ON UPDATE CASCADE,
  ADD CONSTRAINT `producto_FK_3` FOREIGN KEY (`id_promocion`) REFERENCES `promocion` (`id_promocion`) ON DELETE SET NULL ON UPDATE CASCADE,
  ADD CONSTRAINT `producto_FK_4` FOREIGN KEY (`id_garantia`) REFERENCES `garantia` (`id_garantia`) ON DELETE SET NULL ON UPDATE CASCADE;

--
-- Filtros para la tabla `puesto_de_trabajo`
--
ALTER TABLE `puesto_de_trabajo`
  ADD CONSTRAINT `puesto_de_trabajo_FK` FOREIGN KEY (`id_documento`) REFERENCES `documento_empleado` (`id_documento`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Filtros para la tabla `sar`
--
ALTER TABLE `sar`
  ADD CONSTRAINT `sar_FK` FOREIGN KEY (`id_sucursal`) REFERENCES `sucursales` (`id_sucursal`) ON UPDATE CASCADE;

--
-- Filtros para la tabla `seguimiento_de_envio`
--
ALTER TABLE `seguimiento_de_envio`
  ADD CONSTRAINT `seguimiento_de_envio_FK` FOREIGN KEY (`id_pedido`) REFERENCES `pedido_de_compra_cliente` (`id_pedido`) ON UPDATE CASCADE,
  ADD CONSTRAINT `seguimiento_de_envio_FK_1` FOREIGN KEY (`id_transportista`) REFERENCES `transportistas` (`id_transportista`) ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
