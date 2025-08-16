import streamlit as st
import pandas as pd
import pyodbc
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

# Configuración de conexión a SQL Server
@st.cache_resource
def init_connection():
    """Inicializa la conexión a SQL Server"""
    try:
        # Configurar según tu instancia de SQL Server
        connection_string = """
        Driver={ODBC Driver 17 for SQL Server};
        Server=localhost;
        Database=TallerAutomotriz;
        Trusted_Connection=yes;
        """
        return pyodbc.connect(connection_string)
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None

# Funciones de base de datos
def ejecutar_procedimiento(procedure_name, params=None):
    """Ejecuta un procedimiento almacenado"""
    conn = init_connection()
    if conn:
        try:
            cursor = conn.cursor()
            if params:
                cursor.execute(f"EXEC {procedure_name} {','.join(['?' for _ in params])}", params)
            else:
                cursor.execute(f"EXEC {procedure_name}")
            
            # Si es una consulta SELECT
            try:
                result = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                return pd.DataFrame(result, columns=columns)
            except:
                conn.commit()
                return True
        except Exception as e:
            st.error(f"Error ejecutando procedimiento: {e}")
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
    
    .btn-primary {
        background: linear-gradient(45deg, #2E86AB, #A23B72);
        color: white;
        padding: 10px 20px;
        border-radius: 5px;
        text-decoration: none;
        display: inline-block;
        margin: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# Inicialización de estado de sesión
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_type' not in st.session_state:
    st.session_state.user_type = None
if 'page' not in st.session_state:
    st.session_state.page = 'Inicio'

# Sidebar de navegación
def sidebar_navigation():
    st.sidebar.markdown("## 🔧 Taller Automotriz")
    st.sidebar.markdown("### Navegación")
    
    # Opciones para todos los usuarios
    pages = ['Inicio', 'Servicios', 'Agendar Cita', 'Mis Citas']
    
    # Opciones adicionales para administradores
    if st.session_state.authenticated and st.session_state.user_type == 'admin':
        pages.extend(['Panel Admin', 'Clientes', 'Inventario', 'Reportes'])
    
    selected_page = st.sidebar.selectbox("Ir a:", pages)
    
    # Botones de autenticación
    st.sidebar.markdown("---")
    if not st.session_state.authenticated:
        if st.sidebar.button("🔐 Login Admin"):
            st.session_state.page = 'Login'
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
    
    # Header principal
    st.markdown('<h1 class="main-header">🔧 Taller Automotriz San Isidro</h1>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        <div class="info-box">
        <h3>🚗 Bienvenido a nuestro taller</h3>
        <p>Somos especialistas en reparación y mantenimiento automotriz con más de 15 años de experiencia. 
        Ofrecemos servicios de calidad con tecnología de punta y personal altamente capacitado.</p>
        
        <h4>🕒 Horarios de Atención:</h4>
        <ul>
        <li><strong>Lunes a Viernes:</strong> 8:00 AM - 6:00 PM</li>
        <li><strong>Sábados:</strong> 8:00 AM - 2:00 PM</li>
        <li><strong>Domingos:</strong> Cerrado</li>
        </ul>
        
        <h4>📍 Ubicación:</h4>
        <p>Av. Petit Thouars 1234, San Isidro, Lima</p>
        <p>📞 <strong>Teléfono:</strong> (01) 555-0123</p>
        <p>📧 <strong>Email:</strong> info@tallersanisidro.com</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Botón para agendar cita
        if st.button("📅 AGENDAR CITA AHORA", key="agendar_inicio"):
            st.session_state.page = 'Agendar Cita'
            st.experimental_rerun()
    
    with col2:
        # Mapa de Google Maps
        st.markdown("### 📍 Nuestra Ubicación")
        
        # Coordenadas de San Isidro, Lima
        lat, lon = -12.0986, -77.0428
        
        m = folium.Map(location=[lat, lon], zoom_start=16)
        folium.Marker(
            [lat, lon],
            popup="Taller Automotriz San Isidro",
            tooltip="Nuestra ubicación",
            icon=folium.Icon(color='red', icon='wrench', prefix='fa')
        ).add_to(m)
        
        folium_static(m, width=400, height=300)
    
    # Servicios destacados
    st.markdown("---")
    st.markdown("## 🛠️ Nuestros Servicios Principales")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="service-card">
        <h4>🔧 Mantenimiento Preventivo</h4>
        <p>Cambio de aceite, filtros, revisión general</p>
        <strong>Desde S/. 120</strong>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="service-card">
        <h4>⚡ Sistema Eléctrico</h4>
        <p>Batería, alternador, sistema de encendido</p>
        <strong>Desde S/. 80</strong>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="service-card">
        <h4>🛞 Frenos y Suspensión</h4>
        <p>Pastillas, discos, amortiguadores</p>
        <strong>Desde S/. 150</strong>
        </div>
        """, unsafe_allow_html=True)

# Página de servicios
def pagina_servicios():
    st.title("🛠️ Nuestros Servicios")
    
    # Obtener servicios de la base de datos
    servicios_df = ejecutar_procedimiento("sp_obtener_servicios")
    
    if isinstance(servicios_df, pd.DataFrame) and not servicios_df.empty:
        col1, col2 = st.columns(2)
        
        for idx, servicio in servicios_df.iterrows():
            with col1 if idx % 2 == 0 else col2:
                with st.expander(f"🔧 {servicio['nombre']}"):
                    st.write(f"**Descripción:** {servicio['descripcion']}")
                    st.write(f"**Precio:** S/. {servicio['precio']:.2f}")
                    st.write(f"**Duración estimada:** {servicio['duracion_horas']} horas")
    else:
        st.info("No hay servicios disponibles en este momento.")

# Página de agendar cita
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
            
            # Obtener servicios disponibles
            servicios_df = ejecutar_procedimiento("sp_obtener_servicios")
            if isinstance(servicios_df, pd.DataFrame) and not servicios_df.empty:
                servicio_options = dict(zip(servicios_df['nombre'], servicios_df['id']))
                servicio = st.selectbox("Servicio solicitado *", options=list(servicio_options.keys()))
                servicio_id = servicio_options[servicio]
            else:
                st.error("No se pudieron cargar los servicios")
                return
            
            fecha_cita = st.date_input("Fecha de la cita *", min_value=date.today())
            
            # Horarios disponibles
            horarios = ["08:00", "09:00", "10:00", "11:00", "14:00", "15:00", "16:00", "17:00"]
            hora_cita = st.selectbox("Hora *", horarios)
            
            descripcion = st.text_area("Descripción del problema")
        
        submitted = st.form_submit_button("📅 Confirmar Cita")
        
        if submitted:
            if nombre and telefono and marca and modelo:
                # Crear cliente y vehículo si no existen
                params_cliente = [nombre, telefono, email]
                cliente_result = ejecutar_procedimiento("sp_crear_cliente", params_cliente)
                
                if cliente_result:
                    # Crear cita
                    datetime_cita = datetime.combine(fecha_cita, datetime.strptime(hora_cita, "%H:%M").time())
                    params_cita = [servicio_id, datetime_cita, descripcion, "Pendiente"]
                    
                    cita_result = ejecutar_procedimiento("sp_crear_cita", params_cita)
                    
                    if cita_result:
                        st.success("✅ Cita agendada exitosamente!")
                        st.balloons()
                    else:
                        st.error("Error al agendar la cita")
                else:
                    st.error("Error al registrar el cliente")
            else:
                st.error("Por favor complete todos los campos obligatorios (*)")

# Página de login
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
                # Verificar credenciales (simplificado para el ejemplo)
                if username == "admin" and password == "admin123":
                    st.session_state.authenticated = True
                    st.session_state.user_type = 'admin'
                    st.success("✅ Inicio de sesión exitoso")
                    st.experimental_rerun()
                else:
                    st.error("❌ Credenciales incorrectas")

# Panel administrativo
def panel_admin():
    st.title("👨‍💼 Panel de Administración")
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
        <h3>📅</h3>
        <h2>25</h2>
        <p>Citas Hoy</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
        <h3>👥</h3>
        <h2>156</h2>
        <p>Clientes Activos</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
        <h3>💰</h3>
        <h2>S/. 5,240</h2>
        <p>Ingresos Hoy</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
        <h3>📦</h3>
        <h2>12</h2>
        <p>Items Bajo Stock</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Calendario y citas del día
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📅 Citas de Hoy")
        
        # Simulación de citas (reemplazar con consulta real)
        citas_hoy = pd.DataFrame({
            'Hora': ['08:00', '09:30', '11:00', '14:00', '16:00'],
            'Cliente': ['Juan Pérez', 'María González', 'Carlos López', 'Ana Martín', 'Pedro Ruiz'],
            'Servicio': ['Mantenimiento', 'Frenos', 'Cambio Aceite', 'Revisión', 'Batería'],
            'Estado': ['Confirmado', 'Pendiente', 'En Proceso', 'Completado', 'Confirmado']
        })
        
        st.dataframe(citas_hoy, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Estado de Citas")
        
        # Gráfico de estados
        estados = ['Confirmado', 'Pendiente', 'En Proceso', 'Completado']
        valores = [12, 5, 3, 5]
        
        fig = px.pie(values=valores, names=estados, title="Distribución de Estados")
        st.plotly_chart(fig, use_container_width=True)

# Página de inventario
def pagina_inventario():
    st.title("📦 Gestión de Inventario")
    
    tab1, tab2, tab3 = st.tabs(["Ver Inventario", "Agregar Item", "Stock Bajo"])
    
    with tab1:
        st.subheader("Lista de Inventario")
        
        # Simulación de inventario
        inventario = pd.DataFrame({
            'ID': [1, 2, 3, 4, 5],
            'Producto': ['Aceite 5W30', 'Filtro de Aire', 'Pastillas de Freno', 'Batería 12V', 'Bujías'],
            'Categoría': ['Lubricantes', 'Filtros', 'Frenos', 'Eléctrico', 'Encendido'],
            'Stock': [15, 8, 3, 12, 25],
            'Mínimo': [10, 5, 5, 8, 20],
            'Precio': [45.0, 35.0, 120.0, 280.0, 15.0]
        })
        
        st.dataframe(inventario, use_container_width=True)
    
    with tab2:
        st.subheader("Agregar Nuevo Item")
        
        with st.form("form_inventario"):
            col1, col2 = st.columns(2)
            
            with col1:
                nombre = st.text_input("Nombre del Producto")
                categoria = st.selectbox("Categoría", 
                                       ["Lubricantes", "Filtros", "Frenos", "Eléctrico", "Encendido", "Otros"])
                precio = st.number_input("Precio Unitario", min_value=0.0, step=0.1)
            
            with col2:
                stock_inicial = st.number_input("Stock Inicial", min_value=0, step=1)
                stock_minimo = st.number_input("Stock Mínimo", min_value=0, step=1)
                proveedor = st.text_input("Proveedor")
            
            if st.form_submit_button("Agregar Item"):
                if nombre and categoria and precio > 0:
                    st.success(f"✅ Item '{nombre}' agregado exitosamente")
                else:
                    st.error("Complete todos los campos requeridos")
    
    with tab3:
        st.subheader("🚨 Items con Stock Bajo")
        
        stock_bajo = inventario[inventario['Stock'] < inventario['Mínimo']]
        
        if not stock_bajo.empty:
            st.warning(f"⚠️ Hay {len(stock_bajo)} items con stock bajo:")
            st.dataframe(stock_bajo, use_container_width=True)
        else:
            st.success("✅ Todos los items tienen stock suficiente")

# Función principal
def main():
    load_css()
    
    # Navegación
    if st.session_state.page == 'Login':
        pagina_login()
    else:
        selected_page = sidebar_navigation()
        
        # Routing de páginas
        if selected_page == 'Inicio':
            pagina_inicio()
        elif selected_page == 'Servicios':
            pagina_servicios()
        elif selected_page == 'Agendar Cita':
            pagina_agendar_cita()
        elif selected_page == 'Panel Admin' and st.session_state.authenticated:
            panel_admin()
        elif selected_page == 'Inventario' and st.session_state.authenticated:
            pagina_inventario()
        elif selected_page in ['Panel Admin', 'Clientes', 'Inventario', 'Reportes'] and not st.session_state.authenticated:
            st.warning("🔐 Debe iniciar sesión como administrador para acceder a esta sección")
            pagina_login()
        else:
            pagina_inicio()

if __name__ == "__main__":
    main()