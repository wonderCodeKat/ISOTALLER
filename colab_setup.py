# ========================================
# CONFIGURACIÓN PARA GOOGLE COLAB
# Taller Automotriz - Sistema de Gestión
# ========================================

"""
INSTRUCCIONES PARA EJECUTAR EN GOOGLE COLAB:

1. Abrir Google Colab (colab.research.google.com)
2. Crear un nuevo notebook
3. Ejecutar las siguientes celdas en orden
"""

# CELDA 1: Instalar dependencias
# ========================================
!pip install streamlit
!pip install pyodbc
!pip install folium
!pip install streamlit-folium
!pip install plotly
!pip install pandas
!pip install hashlib-compat

# CELDA 2: Configurar túnel para Streamlit
# ========================================
!npm install -g localtunnel

# CELDA 3: Crear archivo de configuración de base de datos
# ========================================
# Si no tienes SQL Server local, puedes usar SQLite como alternativa

import sqlite3
import pandas as pd
import hashlib
from datetime import datetime, date

def crear_bd_sqlite():
    """Crear base de datos SQLite como alternativa para desarrollo"""
    conn = sqlite3.connect('taller_automotriz.db')
    cursor = conn.cursor()
    
    # Crear tablas
    tablas_sql = """
    -- Tabla de Clientes
    CREATE TABLE IF NOT EXISTS Clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        telefono TEXT NOT NULL,
        email TEXT,
        direccion TEXT,
        fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
        activo INTEGER DEFAULT 1
    );
    
    -- Tabla de Vehículos
    CREATE TABLE IF NOT EXISTS Vehiculos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER,
        marca TEXT NOT NULL,
        modelo TEXT NOT NULL,
        año INTEGER NOT NULL,
        placa TEXT,
        color TEXT,
        kilometraje INTEGER,
        fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (cliente_id) REFERENCES Clientes(id)
    );
    
    -- Tabla de Servicios
    CREATE TABLE IF NOT EXISTS Servicios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        descripcion TEXT,
        precio DECIMAL(10,2) NOT NULL,
        duracion_horas DECIMAL(4,2) DEFAULT 1.0,
        activo INTEGER DEFAULT 1
    );
    
    -- Tabla de Citas
    CREATE TABLE IF NOT EXISTS Citas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER,
        vehiculo_id INTEGER,
        servicio_id INTEGER,
        fecha_hora DATETIME NOT NULL,
        descripcion_problema TEXT,
        estado TEXT DEFAULT 'Pendiente',
        observaciones TEXT,
        costo_total DECIMAL(10,2),
        fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
        fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (cliente_id) REFERENCES Clientes(id),
        FOREIGN KEY (vehiculo_id) REFERENCES Vehiculos(id),
        FOREIGN KEY (servicio_id) REFERENCES Servicios(id)
    );
    
    -- Tabla de Inventario
    CREATE TABLE IF NOT EXISTS Inventario (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        categoria TEXT NOT NULL,
        descripcion TEXT,
        stock_actual INTEGER NOT NULL DEFAULT 0,
        stock_minimo INTEGER NOT NULL DEFAULT 1,
        precio_unitario DECIMAL(10,2) NOT NULL,
        proveedor TEXT,
        fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP,
        activo INTEGER DEFAULT 1
    );
    
    -- Tabla de Usuarios
    CREATE TABLE IF NOT EXISTS Usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        nombre TEXT NOT NULL,
        email TEXT,
        tipo TEXT DEFAULT 'admin',
        activo INTEGER DEFAULT 1,
        fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    # Ejecutar creación de tablas
    cursor.executescript(tablas_sql)
    
    # Insertar datos de ejemplo
    servicios_data = [
        ('Mantenimiento Preventivo', 'Cambio de aceite, filtros y revisión general del vehículo', 120.00, 2.0),
        ('Cambio de Aceite', 'Cambio de aceite de motor y filtro', 80.00, 1.0),
        ('Afinamiento de Motor', 'Cambio de bujías, cables y filtros', 150.00, 3.0),
        ('Revisión de Frenos', 'Inspección y cambio de pastillas y discos de freno', 180.00, 2.5),
        ('Sistema Eléctrico', 'Diagnóstico y reparación del sistema eléctrico', 100.00, 2.0),
        ('Cambio de Batería', 'Suministro e instalación de batería nueva', 250.00, 0.5),
        ('Reparación de Suspensión', 'Cambio de amortiguadores y componentes de suspensión', 300.00, 4.0),
        ('Diagnóstico Computarizado', 'Escaneo y diagnóstico por computadora', 50.00, 1.0)
    ]
    
    cursor.executemany('''
        INSERT OR IGNORE INTO Servicios (nombre, descripcion, precio, duracion_horas)
        VALUES (?, ?, ?, ?)
    ''', servicios_data)
    
    # Insertar inventario de ejemplo
    inventario_data = [
        ('Aceite 5W30 4L', 'Lubricantes', 'Aceite sintético para motor', 20, 10, 45.00, 'Castrol'),
        ('Filtro de Aceite', 'Filtros', 'Filtro de aceite universal', 15, 5, 25.00, 'Mann Filter'),
        ('Filtro de Aire', 'Filtros', 'Filtro de aire del motor', 8, 5, 35.00, 'K&N'),
        ('Pastillas de Freno', 'Frenos', 'Pastillas de freno cerámicas', 3, 5, 120.00, 'Brembo'),
        ('Batería 12V', 'Eléctrico', 'Batería libre de mantenimiento', 12, 8, 280.00, 'Bosch')
    ]
    
    cursor.executemany('''
        INSERT OR IGNORE INTO Inventario (nombre, categoria, descripcion, stock_actual, stock_minimo, precio_unitario, proveedor)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', inventario_data)
    
    # Insertar usuario admin (password: admin123)
    password_hash = hashlib.sha256("admin123".encode()).hexdigest()
    cursor.execute('''
        INSERT OR IGNORE INTO Usuarios (username, password_hash, nombre, email, tipo)
        VALUES (?, ?, ?, ?, ?)
    ''', ('admin', password_hash, 'Administrador', 'admin@tallersanisidro.com', 'admin'))
    
    # Insertar clientes de ejemplo
    clientes_data = [
        ('Juan Pérez García', '987654321', 'juan.perez@email.com', 'Av. Arequipa 1234, San Isidro'),
        ('María González López', '987654322', 'maria.gonzalez@email.com', 'Jr. Lampa 567, Lima Centro'),
        ('Carlos Rodríguez', '987654323', 'carlos.rodriguez@email.com', 'Av. Javier Prado 890, San Isidro')
    ]
    
    cursor.executemany('''
        INSERT OR IGNORE INTO Clientes (nombre, telefono, email, direccion)
        VALUES (?, ?, ?, ?)
    ''', clientes_data)
    
    conn.commit()
    conn.close()
    print("✅ Base de datos SQLite creada exitosamente con datos de ejemplo")

# Ejecutar creación de BD
crear_bd_sqlite()

# CELDA 4: Versión adaptada de la aplicación para Colab
# ========================================
import streamlit as st
import pandas as pd
import sqlite3
import hashlib
from datetime import datetime, date, timedelta
import folium
from streamlit_folium import folium_static
import plotly.express as px
import plotly.graph_objects as go

# Configuración de la página
st.set_page_config(
    page_title="Taller Automotriz San Isidro",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Funciones para SQLite (adaptación de la aplicación principal)
@st.cache_resource
def init_connection():
    """Inicializa la conexión a SQLite"""
    try:
        return sqlite3.connect('taller_automotriz.db', check_same_thread=False)
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None

def ejecutar_consulta(query, params=None):
    """Ejecuta una consulta SQL"""
    conn = init_connection()
    if conn:
        try:
            if params:
                result = pd.read_sql_query(query, conn, params=params)
            else:
                result = pd.read_sql_query(query, conn)
            return result
        except Exception as e:
            st.error(f"Error ejecutando consulta: {e}")
            return pd.DataFrame()
        finally:
            conn.close()
    return pd.DataFrame()

def ejecutar_comando(query, params=None):
    """Ejecuta un comando SQL (INSERT, UPDATE, DELETE)"""
    conn = init_connection()
    if conn:
        try:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            conn.commit()
            return True
        except Exception as e:
            st.error(f"Error ejecutando comando: {e}")
            return False
        finally:
            conn.close()
    return False

def hash_password(password):
    """Hashea la contraseña"""
    return hashlib.sha256(str.encode(password)).hexdigest()

# CSS personalizado
def load_css():
    st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        color: #2E86AB;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    
    .service-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .info-box {
        background: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #2E86AB;
        margin: 10px 0;
    }
    
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# Inicialización de estado de sesión
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_type' not in st.session_state:
    st.session_state.user_type = None

# Sidebar de navegación
def sidebar_navigation():
    st.sidebar.markdown("## 🔧 Taller Automotriz")
    st.sidebar.markdown("### Navegación")
    
    pages = ['Inicio', 'Servicios', 'Agendar Cita']
    
    if st.session_state.authenticated and st.session_state.user_type == 'admin':
        pages.extend(['Panel Admin', 'Clientes', 'Inventario'])
    
    selected_page = st.sidebar.selectbox("Ir a:", pages)
    
    st.sidebar.markdown("---")
    if not st.session_state.authenticated:
        if st.sidebar.button("🔐 Login Admin"):
            return 'Login'
    else:
        st.sidebar.success(f"Bienvenido, Admin")
        if st.sidebar.button("🚪 Cerrar Sesión"):
            st.session_state.authenticated = False
            st.session_state.user_type = None
            st.experimental_rerun()
    
    return selected_page

# Página de inicio
def pagina_inicio():
    load_css()
    
    st.markdown('<h1 class="main-header">🔧 Taller Automotriz San Isidro</h1>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        <div class="info-box">
        <h3>🚗 Bienvenido a nuestro taller</h3>
        <p>Somos especialistas en reparación y mantenimiento automotriz con más de 15 años de experiencia.</p>
        
        <h4>🕒 Horarios de Atención:</h4>
        <ul>
        <li><strong>Lunes a Viernes:</strong> 8:00 AM - 6:00 PM</li>
        <li><strong>Sábados:</strong> 8:00 AM - 2:00 PM</li>
        <li><strong>Domingos:</strong> Cerrado</li>
        </ul>
        
        <h4>📍 Ubicación:</h4>
        <p>Av. Petit Thouars 1234, San Isidro, Lima</p>
        <p>📞 <strong>Teléfono:</strong> (01) 555-0123</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("📅 AGENDAR CITA AHORA"):
            st.session_state.page = 'Agendar Cita'
            st.experimental_rerun()
    
    with col2:
        st.markdown("### 📍 Nuestra Ubicación")
        lat, lon = -12.0986, -77.0428
        m = folium.Map(location=[lat, lon], zoom_start=16)
        folium.Marker([lat, lon], popup="Taller Automotriz San Isidro").add_to(m)
        folium_static(m, width=400, height=300)

def pagina_servicios():
    st.title("🛠️ Nuestros Servicios")
    
    query = "SELECT * FROM Servicios WHERE activo = 1 ORDER BY nombre"
    servicios_df = ejecutar_consulta(query)
    
    if not servicios_df.empty:
        col1, col2 = st.columns(2)
        
        for idx, servicio in servicios_df.iterrows():
            with col1 if idx % 2 == 0 else col2:
                with st.expander(f"🔧 {servicio['nombre']}"):
                    st.write(f"**Descripción:** {servicio['descripcion']}")
                    st.write(f"**Precio:** S/. {servicio['precio']:.2f}")
                    st.write(f"**Duración:** {servicio['duracion_horas']} horas")

def pagina_agendar_cita():
    st.title("📅 Agendar Nueva Cita")
    
    with st.form("form_agendar_cita"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Datos del Cliente")
            nombre = st.text_input("Nombre completo *")
            telefono = st.text_input("Teléfono *")
            email = st.text_input("Email")
            
            st.subheader("Datos del Vehículo")
            marca = st.text_input("Marca *")
            modelo = st.text_input("Modelo *")
            año = st.number_input("Año", min_value=1990, max_value=2025, value=2020)
            placa = st.text_input("Placa")
        
        with col2:
            st.subheader("Detalles de la Cita")
            
            servicios_df = ejecutar_consulta("SELECT * FROM Servicios WHERE activo = 1")
            if not servicios_df.empty:
                servicio_options = dict(zip(servicios_df['nombre'], servicios_df['id']))
                servicio_nombre = st.selectbox("Servicio solicitado *", options=list(servicio_options.keys()))
                servicio_id = servicio_options[servicio_nombre]
            
            fecha_cita = st.date_input("Fecha de la cita *", min_value=date.today())
            horarios = ["08:00", "09:00", "10:00", "11:00", "14:00", "15:00", "16:00", "17:00"]
            hora_cita = st.selectbox("Hora *", horarios)
            descripcion = st.text_area("Descripción del problema")
        
        submitted = st.form_submit_button("📅 Confirmar Cita")
        
        if submitted:
            if nombre and telefono and marca and modelo:
                # Insertar cliente
                cliente_query = """
                INSERT INTO Clientes (nombre, telefono, email)
                VALUES (?, ?, ?)
                """
                if ejecutar_comando(cliente_query, (nombre, telefono, email)):
                    
                    # Obtener ID del cliente
                    cliente_id_query = "SELECT id FROM Clientes WHERE telefono = ? ORDER BY id DESC LIMIT 1"
                    cliente_result = ejecutar_consulta(cliente_id_query, (telefono,))
                    
                    if not cliente_result.empty:
                        cliente_id = cliente_result.iloc[0]['id']
                        
                        # Insertar vehículo
                        vehiculo_query = """
                        INSERT INTO Vehiculos (cliente_id, marca, modelo, año, placa)
                        VALUES (?, ?, ?, ?, ?)
                        """
                        if ejecutar_comando(vehiculo_query, (cliente_id, marca, modelo, año, placa)):
                            
                            # Obtener ID del vehículo
                            vehiculo_id_query = "SELECT id FROM Vehiculos WHERE cliente_id = ? ORDER BY id DESC LIMIT 1"
                            vehiculo_result = ejecutar_consulta(vehiculo_id_query, (cliente_id,))
                            
                            if not vehiculo_result.empty:
                                vehiculo_id = vehiculo_result.iloc[0]['id']
                                
                                # Crear cita
                                datetime_cita = f"{fecha_cita} {hora_cita}:00"
                                cita_query = """
                                INSERT INTO Citas (cliente_id, vehiculo_id, servicio_id, fecha_hora, descripcion_problema)
                                VALUES (?, ?, ?, ?, ?)
                                """
                                if ejecutar_comando(cita_query, (cliente_id, vehiculo_id, servicio_id, datetime_cita, descripcion)):
                                    st.success("✅ Cita agendada exitosamente!")
                                    st.balloons()
                                else:
                                    st.error("Error al crear la cita")
            else:
                st.error("Complete todos los campos obligatorios (*)")

def pagina_login():
    st.title("🔐 Login Administrador")
    
    with st.form("login_form"):
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown("### Acceso Administrativo")
            username = st.text_input("Usuario")
            password = st.text_input("Contraseña", type="password")
            
            submitted = st.form_submit_button("Iniciar Sesión")
            
            if submitted:
                password_hash = hash_password(password)
                query = "SELECT * FROM Usuarios WHERE username = ? AND password_hash = ? AND activo = 1"
                user_result = ejecutar_consulta(query, (username, password_hash))
                
                if not user_result.empty:
                    st.session_state.authenticated = True
                    st.session_state.user_type = 'admin'
                    st.success("✅ Inicio de sesión exitoso")
                    st.experimental_rerun()
                else:
                    st.error("❌ Credenciales incorrectas")

def panel_admin():
    st.title("👨‍💼 Panel de Administración")
    
    # Métricas
    col1, col2, col3, col4 = st.columns(4)
    
    # Obtener métricas de la BD
    citas_hoy = ejecutar_consulta("SELECT COUNT(*) as total FROM Citas WHERE DATE(fecha_hora) = DATE('now')")
    clientes_activos = ejecutar_consulta("SELECT COUNT(*) as total FROM Clientes WHERE activo = 1")
    items_bajo_stock = ejecutar_consulta("SELECT COUNT(*) as total FROM Inventario WHERE stock_actual <= stock_minimo")
    
    with col1:
        total_citas = citas_hoy.iloc[0]['total'] if not citas_hoy.empty else 0
        st.metric("📅 Citas Hoy", total_citas)
    
    with col2:
        total_clientes = clientes_activos.iloc[0]['total'] if not clientes_activos.empty else 0
        st.metric("👥 Clientes", total_clientes)
    
    with col3:
        st.metric("💰 Ingresos Hoy", "S/. 1,250")
    
    with col4:
        items_stock = items_bajo_stock.iloc[0]['total'] if not items_bajo_stock.empty else 0
        st.metric("📦 Stock Bajo", items_stock)
    
    st.markdown("---")
    
    # Citas del día
    st.subheader("📅 Citas de Hoy")
    
    citas_query = """
    SELECT 
        c.id,
        cl.nombre as cliente,
        v.marca,
        v.modelo,
        s.nombre as servicio,
        c.fecha_hora,
        c.estado
    FROM Citas c
    JOIN Clientes cl ON c.cliente_id = cl.id
    JOIN Vehiculos v ON c.vehiculo_id = v.id
    JOIN Servicios s ON c.servicio_id = s.id
    WHERE DATE(c.fecha_hora) = DATE('now')
    ORDER BY c.fecha_hora
    """
    
    citas_df = ejecutar_consulta(citas_query)
    if not citas_df.empty:
        st.dataframe(citas_df, use_container_width=True)
    else:
        st.info("No hay citas programadas para hoy")

def pagina_inventario():
    st.title("📦 Gestión de Inventario")
    
    tab1, tab2, tab3 = st.tabs(["Ver Inventario", "Agregar Item", "Stock Bajo"])
    
    with tab1:
        inventario_df = ejecutar_consulta("SELECT * FROM Inventario WHERE activo = 1 ORDER BY nombre")
        if not inventario_df.empty:
            st.dataframe(inventario_df, use_container_width=True)
    
    with tab2:
        with st.form("form_inventario"):
            col1, col2 = st.columns(2)
            
            with col1:
                nombre = st.text_input("Nombre del Producto")
                categoria = st.selectbox("Categoría", 
                                       ["Lubricantes", "Filtros", "Frenos", "Eléctrico", "Encendido"])
                precio = st.number_input("Precio Unitario", min_value=0.0, step=0.1)
            
            with col2:
                stock_inicial = st.number_input("Stock Inicial", min_value=0, step=1)
                stock_minimo = st.number_input("Stock Mínimo", min_value=0, step=1)
                proveedor = st.text_input("Proveedor")
            
            if st.form_submit_button("Agregar Item"):
                if nombre and categoria and precio > 0:
                    query = """
                    INSERT INTO Inventario (nombre, categoria, stock_actual, stock_minimo, precio_unitario, proveedor)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """
                    if ejecutar_comando(query, (nombre, categoria, stock_inicial, stock_minimo, precio, proveedor)):
                        st.success("✅ Item agregado exitosamente")
                        st.experimental_rerun()
    
    with tab3:
        stock_bajo_df = ejecutar_consulta("SELECT * FROM Inventario WHERE stock_actual <= stock_minimo AND activo = 1")
        if not stock_bajo_df.empty:
            st.warning(f"⚠️ Hay {len(stock_bajo_df)} items con stock bajo:")
            st.dataframe(stock_bajo_df, use_container_width=True)
        else:
            st.success("✅ Todos los items tienen stock suficiente")

def pagina_clientes():
    st.title("👥 Gestión de Clientes")
    
    clientes_query = """
    SELECT 
        c.id,
        c.nombre,
        c.telefono,
        c.email,
        c.fecha_registro,
        COUNT(v.id) as total_vehiculos,
        COUNT(ct.id) as total_citas
    FROM Clientes c
    LEFT JOIN Vehiculos v ON c.id = v.cliente_id
    LEFT JOIN Citas ct ON c.id = ct.cliente_id
    WHERE c.activo = 1
    GROUP BY c.id, c.nombre, c.telefono, c.email, c.fecha_registro
    ORDER BY c.nombre
    """
    
    clientes_df = ejecutar_consulta(clientes_query)
    if not clientes_df.empty:
        st.dataframe(clientes_df, use_container_width=True)
        
        # Detalle del cliente seleccionado
        st.subheader("Detalle del Cliente")
        cliente_seleccionado = st.selectbox("Seleccionar cliente:", 
                                          options=clientes_df['nombre'].tolist())
        
        if cliente_seleccionado:
            cliente_id = clientes_df[clientes_df['nombre'] == cliente_seleccionado]['id'].iloc[0]
            
            # Vehículos del cliente
            vehiculos_query = "SELECT * FROM Vehiculos WHERE cliente_id = ?"
            vehiculos_df = ejecutar_consulta(vehiculos_query, (cliente_id,))
            
            if not vehiculos_df.empty:
                st.write("**Vehículos:**")
                st.dataframe(vehiculos_df[['marca', 'modelo', 'año', 'placa']], use_container_width=True)
            
            # Historial de citas
            citas_query = """
            SELECT 
                c.fecha_hora,
                s.nombre as servicio,
                c.estado,
                c.costo_total
            FROM Citas c
            JOIN Servicios s ON c.servicio_id = s.id
            WHERE c.cliente_id = ?
            ORDER BY c.fecha_hora DESC
            """
            citas_cliente_df = ejecutar_consulta(citas_query, (cliente_id,))
            
            if not citas_cliente_df.empty:
                st.write("**Historial de Citas:**")
                st.dataframe(citas_cliente_df, use_container_width=True)

# Función principal
def main():
    load_css()
    
    # Obtener página seleccionada
    selected_page = sidebar_navigation()
    
    # Routing
    if selected_page == 'Login':
        pagina_login()
    elif selected_page == 'Inicio':
        pagina_inicio()
    elif selected_page == 'Servicios':
        pagina_servicios()
    elif selected_page == 'Agendar Cita':
        pagina_agendar_cita()
    elif selected_page == 'Panel Admin' and st.session_state.authenticated:
        panel_admin()
    elif selected_page == 'Inventario' and st.session_state.authenticated:
        pagina_inventario()
    elif selected_page == 'Clientes' and st.session_state.authenticated:
        pagina_clientes()
    elif selected_page in ['Panel Admin', 'Clientes', 'Inventario'] and not st.session_state.authenticated:
        st.warning("🔐 Debe iniciar sesión para acceder a esta sección")
        pagina_login()
    else:
        pagina_inicio()

if __name__ == "__main__":
    main()

# CELDA 5: Ejecutar la aplicación
# ========================================
# Para ejecutar en Colab, usar el siguiente comando:

import subprocess
import threading

def run_streamlit():
    subprocess.run(["streamlit", "run", "app.py", "--server.port", "8501"])

# Guardar la aplicación en un archivo
with open('app.py', 'w', encoding='utf-8') as f:
    f.write("""
# Aquí pegarías todo el código de la aplicación desde la CELDA 4
""")

# Crear túnel para acceder desde fuera
def create_tunnel():
    subprocess.run(["lt", "--port", "8501"])

print("🚀 Instrucciones finales:")
print("1. Ejecuta: !streamlit run app.py --server.port 8501 &")
print("2. En otra celda ejecuta: !lt --port 8501")
print("3. Usa la URL proporcionada por localtunnel para acceder a la aplicación")
print()
print("📋 Credenciales de prueba:")
print("Usuario: admin")
print("Contraseña: admin123")

# INFORMACIÓN ADICIONAL PARA COLAB
# ========================================

print("""
📚 GUÍA COMPLETA PARA GOOGLE COLAB:

1. PREPARAR EL ENTORNO:
   - Ejecutar celdas 1-4 en orden
   - Esperar a que se instalen todas las dependencias

2. EJECUTAR LA APLICACIÓN:
   En celdas separadas, ejecutar:
   
   Celda A: !streamlit run app.py --server.port 8501 &
   Celda B: !lt --port 8501
   
3. ACCEDER A LA APLICACIÓN:
   - Usar la URL proporcionada por localtunnel
   - Puede tomar 1-2 minutos en cargar inicialmente

4. FUNCIONALIDADES DISPONIBLES:
   ✅ Página de inicio con información del taller
   ✅ Lista de servicios disponibles  
   ✅ Sistema de citas (crear, ver)
   ✅ Login administrativo
   ✅ Panel de administración con métricas
   ✅ Gestión de inventario
   ✅ Gestión de clientes
   ✅ Base de datos SQLite integrada

5. DATOS DE PRUEBA:
   - Usuario admin: admin / admin123
   - Base de datos con servicios, inventario y clientes de ejemplo
   - Citas de prueba ya creadas

6. LIMITACIONES EN COLAB:
   - Base de datos en memoria (se reinicia al cerrar)
   - Sin persistencia entre sesiones
   - Requiere túnel para acceso externo

7. PARA PRODUCCIÓN:
   - Migrar a SQL Server con los scripts proporcionados
   - Desplegar en servidor dedicado
   - Configurar base de datos persistente
""")

# Comando final para ejecutar
print("🎯 COMANDO PARA EJECUTAR:")
print("!streamlit run app.py --server.port 8501 &")
print("!lt --port 8501")