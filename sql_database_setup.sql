-- Script para crear la base de datos del Taller Automotriz
-- SQL Server

-- Crear la base de datos
CREATE DATABASE TallerAutomotriz;
GO

USE TallerAutomotriz;
GO

-- Tabla de Clientes
CREATE TABLE Clientes (
    id INT IDENTITY(1,1) PRIMARY KEY,
    nombre NVARCHAR(100) NOT NULL,
    telefono NVARCHAR(20) NOT NULL,
    email NVARCHAR(100),
    direccion NVARCHAR(200),
    fecha_registro DATETIME DEFAULT GETDATE(),
    activo BIT DEFAULT 1
);

-- Tabla de Vehículos
CREATE TABLE Vehiculos (
    id INT IDENTITY(1,1) PRIMARY KEY,
    cliente_id INT FOREIGN KEY REFERENCES Clientes(id),
    marca NVARCHAR(50) NOT NULL,
    modelo NVARCHAR(50) NOT NULL,
    año INT NOT NULL,
    placa NVARCHAR(10),
    color NVARCHAR(30),
    kilometraje INT,
    fecha_registro DATETIME DEFAULT GETDATE()
);

-- Tabla de Servicios
CREATE TABLE Servicios (
    id INT IDENTITY(1,1) PRIMARY KEY,
    nombre NVARCHAR(100) NOT NULL,
    descripcion NVARCHAR(500),
    precio DECIMAL(10,2) NOT NULL,
    duracion_horas DECIMAL(4,2) DEFAULT 1.0,
    activo BIT DEFAULT 1
);

-- Tabla de Citas
CREATE TABLE Citas (
    id INT IDENTITY(1,1) PRIMARY KEY,
    cliente_id INT FOREIGN KEY REFERENCES Clientes(id),
    vehiculo_id INT FOREIGN KEY REFERENCES Vehiculos(id),
    servicio_id INT FOREIGN KEY REFERENCES Servicios(id),
    fecha_hora DATETIME NOT NULL,
    descripcion_problema NVARCHAR(500),
    estado NVARCHAR(20) DEFAULT 'Pendiente', -- Pendiente, Confirmado, En Proceso, Completado, Cancelado
    observaciones NVARCHAR(500),
    costo_total DECIMAL(10,2),
    fecha_creacion DATETIME DEFAULT GETDATE(),
    fecha_actualizacion DATETIME DEFAULT GETDATE()
);

-- Tabla de Inventario
CREATE TABLE Inventario (
    id INT IDENTITY(1,1) PRIMARY KEY,
    nombre NVARCHAR(100) NOT NULL,
    categoria NVARCHAR(50) NOT NULL,
    descripcion NVARCHAR(300),
    stock_actual INT NOT NULL DEFAULT 0,
    stock_minimo INT NOT NULL DEFAULT 1,
    precio_unitario DECIMAL(10,2) NOT NULL,
    proveedor NVARCHAR(100),
    fecha_actualizacion DATETIME DEFAULT GETDATE(),
    activo BIT DEFAULT 1
);

-- Tabla de Usuarios (para autenticación)
CREATE TABLE Usuarios (
    id INT IDENTITY(1,1) PRIMARY KEY,
    username NVARCHAR(50) UNIQUE NOT NULL,
    password_hash NVARCHAR(64) NOT NULL,
    nombre NVARCHAR(100) NOT NULL,
    email NVARCHAR(100),
    tipo NVARCHAR(20) DEFAULT 'admin', -- admin, empleado
    activo BIT DEFAULT 1,
    fecha_creacion DATETIME DEFAULT GETDATE()
);

-- Tabla de Movimientos de Inventario
CREATE TABLE MovimientosInventario (
    id INT IDENTITY(1,1) PRIMARY KEY,
    inventario_id INT FOREIGN KEY REFERENCES Inventario(id),
    tipo_movimiento NVARCHAR(10) NOT NULL, -- ENTRADA, SALIDA
    cantidad INT NOT NULL,
    motivo NVARCHAR(100),
    fecha DATETIME DEFAULT GETDATE(),
    usuario_id INT
);

-- ================================
-- PROCEDIMIENTOS ALMACENADOS
-- ================================

-- SP para crear un cliente
GO
CREATE PROCEDURE sp_crear_cliente
    @nombre NVARCHAR(100),
    @telefono NVARCHAR(20),
    @email NVARCHAR(100) = NULL,
    @direccion NVARCHAR(200) = NULL
AS
BEGIN
    BEGIN TRY
        INSERT INTO Clientes (nombre, telefono, email, direccion)
        VALUES (@nombre, @telefono, @email, @direccion);
        
        SELECT SCOPE_IDENTITY() as cliente_id, 'Cliente creado exitosamente' as mensaje;
    END TRY
    BEGIN CATCH
        SELECT 0 as cliente_id, ERROR_MESSAGE() as mensaje;
    END CATCH
END
GO

-- SP para crear un vehículo
CREATE PROCEDURE sp_crear_vehiculo
    @cliente_id INT,
    @marca NVARCHAR(50),
    @modelo NVARCHAR(50),
    @año INT,
    @placa NVARCHAR(10) = NULL,
    @color NVARCHAR(30) = NULL
AS
BEGIN
    BEGIN TRY
        INSERT INTO Vehiculos (cliente_id, marca, modelo, año, placa, color)
        VALUES (@cliente_id, @marca, @modelo, @año, @placa, @color);
        
        SELECT SCOPE_IDENTITY() as vehiculo_id, 'Vehículo registrado exitosamente' as mensaje;
    END TRY
    BEGIN CATCH
        SELECT 0 as vehiculo_id, ERROR_MESSAGE() as mensaje;
    END CATCH
END
GO

-- SP para obtener servicios
CREATE PROCEDURE sp_obtener_servicios
AS
BEGIN
    SELECT id, nombre, descripcion, precio, duracion_horas
    FROM Servicios
    WHERE activo = 1
    ORDER BY nombre;
END
GO

-- SP para crear una cita
CREATE PROCEDURE sp_crear_cita
    @cliente_id INT,
    @vehiculo_id INT,
    @servicio_id INT,
    @fecha_hora DATETIME,
    @descripcion_problema NVARCHAR(500) = NULL
AS
BEGIN
    BEGIN TRY
        -- Verificar disponibilidad (opcional)
        IF EXISTS (
            SELECT 1 FROM Citas 
            WHERE fecha_hora = @fecha_hora 
            AND estado NOT IN ('Cancelado')
        )
        BEGIN
            SELECT 0 as cita_id, 'Ya existe una cita en esa fecha y hora' as mensaje;
            RETURN;
        END
        
        INSERT INTO Citas (cliente_id, vehiculo_id, servicio_id, fecha_hora, descripcion_problema)
        VALUES (@cliente_id, @vehiculo_id, @servicio_id, @fecha_hora, @descripcion_problema);
        
        SELECT SCOPE_IDENTITY() as cita_id, 'Cita creada exitosamente' as mensaje;
    END TRY
    BEGIN CATCH
        SELECT 0 as cita_id, ERROR_MESSAGE() as mensaje;
    END CATCH
END
GO

-- SP para obtener citas
CREATE PROCEDURE sp_obtener_citas
    @fecha_inicio DATE = NULL,
    @fecha_fin DATE = NULL,
    @estado NVARCHAR(20) = NULL
AS
BEGIN
    SELECT 
        c.id,
        cl.nombre as cliente_nombre,
        cl.telefono,
        v.marca,
        v.modelo,
        v.placa,
        s.nombre as servicio,
        c.fecha_hora,
        c.estado,
        c.descripcion_problema,
        c.costo_total,
        s.precio as precio_base
    FROM Citas c
    INNER JOIN Clientes cl ON c.cliente_id = cl.id
    INNER JOIN Vehiculos v ON c.vehiculo_id = v.id
    INNER JOIN Servicios s ON c.servicio_id = s.id
    WHERE 
        (@fecha_inicio IS NULL OR CAST(c.fecha_hora AS DATE) >= @fecha_inicio)
        AND (@fecha_fin IS NULL OR CAST(c.fecha_hora AS DATE) <= @fecha_fin)
        AND (@estado IS NULL OR c.estado = @estado)
    ORDER BY c.fecha_hora;
END
GO

-- SP para actualizar estado de cita
CREATE PROCEDURE sp_actualizar_estado_cita
    @cita_id INT,
    @nuevo_estado NVARCHAR(20),
    @observaciones NVARCHAR(500) = NULL,
    @costo_total DECIMAL(10,2) = NULL
AS
BEGIN
    BEGIN TRY
        UPDATE Citas 
        SET 
            estado = @nuevo_estado,
            observaciones = ISNULL(@observaciones, observaciones),
            costo_total = ISNULL(@costo_total, costo_total),
            fecha_actualizacion = GETDATE()
        WHERE id = @cita_id;
        
        SELECT 'Estado actualizado exitosamente' as mensaje;
    END TRY
    BEGIN CATCH
        SELECT ERROR_MESSAGE() as mensaje;
    END CATCH
END
GO

-- SP para obtener inventario
CREATE PROCEDURE sp_obtener_inventario
    @categoria NVARCHAR(50) = NULL,
    @stock_bajo BIT = 0
AS
BEGIN
    SELECT 
        id,
        nombre,
        categoria,
        descripcion,
        stock_actual,
        stock_minimo,
        precio_unitario,
        proveedor,
        fecha_actualizacion,
        CASE WHEN stock_actual <= stock_minimo THEN 1 ELSE 0 END as es_stock_bajo
    FROM Inventario
    WHERE 
        activo = 1
        AND (@categoria IS NULL OR categoria = @categoria)
        AND (@stock_bajo = 0 OR stock_actual <= stock_minimo)
    ORDER BY 
        CASE WHEN stock_actual <= stock_minimo THEN 0 ELSE 1 END,
        nombre;
END
GO

-- SP para agregar item al inventario
CREATE PROCEDURE sp_agregar_inventario
    @nombre NVARCHAR(100),
    @categoria NVARCHAR(50),
    @descripcion NVARCHAR(300) = NULL,
    @stock_inicial INT = 0,
    @stock_minimo INT = 1,
    @precio_unitario DECIMAL(10,2),
    @proveedor NVARCHAR(100) = NULL
AS
BEGIN
    BEGIN TRY
        INSERT INTO Inventario (nombre, categoria, descripcion, stock_actual, stock_minimo, precio_unitario, proveedor)
        VALUES (@nombre, @categoria, @descripcion, @stock_inicial, @stock_minimo, @precio_unitario, @proveedor);
        
        DECLARE @inventario_id INT = SCOPE_IDENTITY();
        
        -- Registrar movimiento inicial si hay stock
        IF @stock_inicial > 0
        BEGIN
            INSERT INTO MovimientosInventario (inventario_id, tipo_movimiento, cantidad, motivo)
            VALUES (@inventario_id, 'ENTRADA', @stock_inicial, 'Stock inicial');
        END
        
        SELECT @inventario_id as inventario_id, 'Item agregado exitosamente' as mensaje;
    END TRY
    BEGIN CATCH
        SELECT 0 as inventario_id, ERROR_MESSAGE() as mensaje;
    END CATCH
END
GO

-- SP para actualizar stock
CREATE PROCEDURE sp_actualizar_stock
    @inventario_id INT,
    @tipo_movimiento NVARCHAR(10), -- ENTRADA o SALIDA
    @cantidad INT,
    @motivo NVARCHAR(100) = NULL,
    @usuario_id INT = NULL
AS
BEGIN
    BEGIN TRY
        BEGIN TRANSACTION;
        
        -- Validar que el item existe
        IF NOT EXISTS (SELECT 1 FROM Inventario WHERE id = @inventario_id AND activo = 1)
        BEGIN
            ROLLBACK TRANSACTION;
            SELECT 'Item no encontrado' as mensaje;
            RETURN;
        END
        
        -- Para salidas, verificar stock suficiente
        IF @tipo_movimiento = 'SALIDA'
        BEGIN
            DECLARE @stock_actual INT;
            SELECT @stock_actual = stock_actual FROM Inventario WHERE id = @inventario_id;
            
            IF @stock_actual < @cantidad
            BEGIN
                ROLLBACK TRANSACTION;
                SELECT 'Stock insuficiente' as mensaje;
                RETURN;
            END
        END
        
        -- Actualizar stock
        IF @tipo_movimiento = 'ENTRADA'
        BEGIN
            UPDATE Inventario 
            SET stock_actual = stock_actual + @cantidad,
                fecha_actualizacion = GETDATE()
            WHERE id = @inventario_id;
        END
        ELSE IF @tipo_movimiento = 'SALIDA'
        BEGIN
            UPDATE Inventario 
            SET stock_actual = stock_actual - @cantidad,
                fecha_actualizacion = GETDATE()
            WHERE id = @inventario_id;
        END
        
        -- Registrar movimiento
        INSERT INTO MovimientosInventario (inventario_id, tipo_movimiento, cantidad, motivo, usuario_id)
        VALUES (@inventario_id, @tipo_movimiento, @cantidad, @motivo, @usuario_id);
        
        COMMIT TRANSACTION;
        SELECT 'Stock actualizado exitosamente' as mensaje;
    END TRY
    BEGIN CATCH
        ROLLBACK TRANSACTION;
        SELECT ERROR_MESSAGE() as mensaje;
    END CATCH
END
GO

-- SP para obtener clientes
CREATE PROCEDURE sp_obtener_clientes
    @activos_solamente BIT = 1
AS
BEGIN
    SELECT 
        c.id,
        c.nombre,
        c.telefono,
        c.email,
        c.direccion,
        c.fecha_registro,
        COUNT(v.id) as total_vehiculos,
        COUNT(ct.id) as total_citas
    FROM Clientes c
    LEFT JOIN Vehiculos v ON c.id = v.cliente_id
    LEFT JOIN Citas ct ON c.id = ct.cliente_id
    WHERE (@activos_solamente = 0 OR c.activo = 1)
    GROUP BY c.id, c.nombre, c.telefono, c.email, c.direccion, c.fecha_registro
    ORDER BY c.nombre;
END
GO

-- SP para obtener vehículos de un cliente
CREATE PROCEDURE sp_obtener_vehiculos_cliente
    @cliente_id INT
AS
BEGIN
    SELECT 
        id,
        marca,
        modelo,
        año,
        placa,
        color,
        kilometraje,
        fecha_registro
    FROM Vehiculos
    WHERE cliente_id = @cliente_id
    ORDER BY fecha_registro DESC;
END
GO

-- SP para dashboard - métricas principales
CREATE PROCEDURE sp_dashboard_metricas
    @fecha DATE = NULL
AS
BEGIN
    IF @fecha IS NULL
        SET @fecha = CAST(GETDATE() AS DATE);
    
    -- Citas del día
    SELECT COUNT(*) as citas_hoy
    FROM Citas
    WHERE CAST(fecha_hora AS DATE) = @fecha
    AND estado NOT IN ('Cancelado');
    
    -- Total de clientes activos
    SELECT COUNT(*) as clientes_activos
    FROM Clientes
    WHERE activo = 1;
    
    -- Ingresos del día
    SELECT ISNULL(SUM(costo_total), 0) as ingresos_hoy
    FROM Citas
    WHERE CAST(fecha_hora AS DATE) = @fecha
    AND estado = 'Completado';
    
    -- Items con stock bajo
    SELECT COUNT(*) as items_stock_bajo
    FROM Inventario
    WHERE stock_actual <= stock_minimo
    AND activo = 1;
    
    -- Distribución de estados de citas del día
    SELECT 
        estado,
        COUNT(*) as cantidad
    FROM Citas
    WHERE CAST(fecha_hora AS DATE) = @fecha
    GROUP BY estado;
END
GO

-- SP para reportes de servicios más solicitados
CREATE PROCEDURE sp_reporte_servicios_populares
    @fecha_inicio DATE = NULL,
    @fecha_fin DATE = NULL,
    @top INT = 10
AS
BEGIN
    IF @fecha_inicio IS NULL
        SET @fecha_inicio = DATEADD(MONTH, -1, GETDATE());
    
    IF @fecha_fin IS NULL
        SET @fecha_fin = GETDATE();
    
    SELECT TOP (@top)
        s.nombre as servicio,
        COUNT(c.id) as total_citas,
        AVG(s.precio) as precio_promedio,
        SUM(ISNULL(c.costo_total, s.precio)) as ingresos_totales
    FROM Servicios s
    INNER JOIN Citas c ON s.id = c.servicio_id
    WHERE CAST(c.fecha_hora AS DATE) BETWEEN @fecha_inicio AND @fecha_fin
    GROUP BY s.id, s.nombre
    ORDER BY total_citas DESC;
END
GO

-- SP para validar usuario (login)
CREATE PROCEDURE sp_validar_usuario
    @username NVARCHAR(50),
    @password_hash NVARCHAR(64)
AS
BEGIN
    SELECT 
        id,
        username,
        nombre,
        email,
        tipo
    FROM Usuarios
    WHERE username = @username 
    AND password_hash = @password_hash 
    AND activo = 1;
END
GO

-- SP para obtener movimientos de inventario
CREATE PROCEDURE sp_obtener_movimientos_inventario
    @inventario_id INT = NULL,
    @fecha_inicio DATE = NULL,
    @fecha_fin DATE = NULL
AS
BEGIN
    SELECT 
        m.id,
        i.nombre as producto,
        m.tipo_movimiento,
        m.cantidad,
        m.motivo,
        m.fecha,
        u.nombre as usuario
    FROM MovimientosInventario m
    INNER JOIN Inventario i ON m.inventario_id = i.id
    LEFT JOIN Usuarios u ON m.usuario_id = u.id
    WHERE 
        (@inventario_id IS NULL OR m.inventario_id = @inventario_id)
        AND (@fecha_inicio IS NULL OR CAST(m.fecha AS DATE) >= @fecha_inicio)
        AND (@fecha_fin IS NULL OR CAST(m.fecha AS DATE) <= @fecha_fin)
    ORDER BY m.fecha DESC;
END
GO

-- ================================
-- DATOS INICIALES
-- ================================

-- Insertar servicios base
INSERT INTO Servicios (nombre, descripcion, precio, duracion_horas) VALUES
('Mantenimiento Preventivo', 'Cambio de aceite, filtros y revisión general del vehículo', 120.00, 2.0),
('Cambio de Aceite', 'Cambio de aceite de motor y filtro', 80.00, 1.0),
('Afinamiento de Motor', 'Cambio de bujías, cables y filtros', 150.00, 3.0),
('Revisión de Frenos', 'Inspección y cambio de pastillas y discos de freno', 180.00, 2.5),
('Sistema Eléctrico', 'Diagnóstico y reparación del sistema eléctrico', 100.00, 2.0),
('Cambio de Batería', 'Suministro e instalación de batería nueva', 250.00, 0.5),
('Reparación de Suspensión', 'Cambio de amortiguadores y componentes de suspensión', 300.00, 4.0),
('Diagnóstico Computarizado', 'Escaneo y diagnóstico por computadora', 50.00, 1.0),
('Cambio de Llantas', 'Montaje y balanceo de llantas nuevas', 200.00, 1.5),
('Reparación de Transmisión', 'Diagnóstico y reparación de caja de cambios', 500.00, 6.0);

-- Insertar items de inventario base
INSERT INTO Inventario (nombre, categoria, descripcion, stock_actual, stock_minimo, precio_unitario, proveedor) VALUES
('Aceite 5W30 4L', 'Lubricantes', 'Aceite sintético para motor', 20, 10, 45.00, 'Castrol'),
('Filtro de Aceite', 'Filtros', 'Filtro de aceite universal', 15, 5, 25.00, 'Mann Filter'),
('Filtro de Aire', 'Filtros', 'Filtro de aire del motor', 8, 5, 35.00, 'K&N'),
('Pastillas de Freno Delanteras', 'Frenos', 'Pastillas de freno cerámicas', 3, 5, 120.00, 'Brembo'),
('Pastillas de Freno Traseras', 'Frenos', 'Pastillas de freno cerámicas', 4, 5, 100.00, 'Brembo'),
('Batería 12V 60Ah', 'Eléctrico', 'Batería libre de mantenimiento', 12, 8, 280.00, 'Bosch'),
('Bujías NGK', 'Encendido', 'Bujías de platino', 25, 20, 15.00, 'NGK'),
('Amortiguador Delantero', 'Suspensión', 'Amortiguador gas-oil', 6, 4, 180.00, 'Monroe'),
('Líquido de Frenos DOT4', 'Fluidos', 'Líquido de frenos sintético', 10, 5, 20.00, 'Castrol'),
('Refrigerante', 'Fluidos', 'Refrigerante universal', 8, 6, 30.00, 'Prestone');

-- Insertar usuario administrador (password: admin123)
INSERT INTO Usuarios (username, password_hash, nombre, email, tipo) VALUES
('admin', 'EE26B0DD4AF7E749AA1A8EE3C10AE9923F618980772E473F8819A5D4940E0DB27AC185F8A0E1D5F84F88BC887FD67B143732C304CC5FA9AD8E6F57F50028A8FF', 'Administrador', 'admin@tallersanisidro.com', 'admin');

-- Insertar algunos clientes de ejemplo
INSERT INTO Clientes (nombre, telefono, email, direccion) VALUES
('Juan Pérez García', '987654321', 'juan.perez@email.com', 'Av. Arequipa 1234, San Isidro'),
('María González López', '987654322', 'maria.gonzalez@email.com', 'Jr. Lampa 567, Lima Centro'),
('Carlos Rodríguez', '987654323', 'carlos.rodriguez@email.com', 'Av. Javier Prado 890, San Isidro'),
('Ana Martín Silva', '987654324', 'ana.martin@email.com', 'Calle Los Nogales 123, San Borja'),
('Pedro Ruiz Castro', '987654325', 'pedro.ruiz@email.com', 'Av. El Sol 456, Surco');

-- Insertar vehículos de ejemplo
INSERT INTO Vehiculos (cliente_id, marca, modelo, año, placa, color) VALUES
(1, 'Toyota', 'Corolla', 2018, 'ABC-123', 'Blanco'),
(2, 'Nissan', 'Sentra', 2019, 'DEF-456', 'Azul'),
(3, 'Hyundai', 'Accent', 2020, 'GHI-789', 'Rojo'),
(4, 'Chevrolet', 'Spark', 2017, 'JKL-012', 'Negro'),
(5, 'Kia', 'Rio', 2021, 'MNO-345', 'Gris');

-- Insertar algunas citas de ejemplo
INSERT INTO Citas (cliente_id, vehiculo_id, servicio_id, fecha_hora, descripcion_problema, estado) VALUES
(1, 1, 1, '2024-08-16 08:00:00', 'Mantenimiento programado', 'Confirmado'),
(2, 2, 4, '2024-08-16 09:30:00', 'Ruido en los frenos', 'Pendiente'),
(3, 3, 2, '2024-08-16 11:00:00', 'Cambio de aceite', 'En Proceso'),
(4, 4, 8, '2024-08-16 14:00:00', 'Check engine encendido', 'Completado'),
(5, 5, 6, '2024-08-16 16:00:00', 'Batería descargada', 'Confirmado');

-- ================================
-- ÍNDICES PARA MEJORAR PERFORMANCE
-- ================================

-- Índices en tablas principales
CREATE INDEX IX_Citas_FechaHora ON Citas(fecha_hora);
CREATE INDEX IX_Citas_Estado ON Citas(estado);
CREATE INDEX IX_Citas_ClienteId ON Citas(cliente_id);
CREATE INDEX IX_Vehiculos_ClienteId ON Vehiculos(cliente_id);
CREATE INDEX IX_Inventario_StockBajo ON Inventario(stock_actual, stock_minimo) WHERE activo = 1;
CREATE INDEX IX_MovimientosInventario_Fecha ON MovimientosInventario(fecha);

-- Vista para dashboard
CREATE VIEW vw_dashboard_resumen AS
SELECT 
    (SELECT COUNT(*) FROM Citas WHERE CAST(fecha_hora AS DATE) = CAST(GETDATE() AS DATE) AND estado NOT IN ('Cancelado')) as citas_hoy,
    (SELECT COUNT(*) FROM Clientes WHERE activo = 1) as clientes_activos,
    (SELECT ISNULL(SUM(costo_total), 0) FROM Citas WHERE CAST(fecha_hora AS DATE) = CAST(GETDATE() AS DATE) AND estado = 'Completado') as ingresos_hoy,
    (SELECT COUNT(*) FROM Inventario WHERE stock_actual <= stock_minimo AND activo = 1) as items_stock_bajo;
GO

PRINT 'Base de datos TallerAutomotriz creada exitosamente con todos los procedimientos almacenados y datos de ejemplo.';
        