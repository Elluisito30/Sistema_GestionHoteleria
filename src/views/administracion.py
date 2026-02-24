"""Vista de administración del sistema"""
import streamlit as st
import pandas as pd
from datetime import date, timedelta, datetime
from config.database import db
from models.usuario import Usuario
from models.habitacion import Habitacion
from models.reserva import Reserva
from models.huesped import Huesped
from models.factura import Factura
from controllers.reserva_controller import ReservaController
from controllers.factura_controller import FacturaController
from utils.auth import Auth
from utils.logger import logger
from utils.permissions import Permission  # 👈 NUEVO

# ── Paleta (misma que el resto) ────────────────────────────────────────────────
C = {
    'dark':      '#1a2744',
    'dark2':     '#0F2044',
    'mid':       '#2c4a7f',
    'primary':   '#5B8DB8',
    'secondary': '#9DB4C7',
    'accent':    '#A8D8EA',
    'text':      '#E2E8F0',
    'muted':     '#9DB4C7',
    'border':    'rgba(157,180,199,0.25)',
    'card_bg':   'rgba(255,255,255,0.05)',
    'success':   '#68D391',
    'warning':   '#F6AD55',
    'danger':    '#FC8181',
    'purple':    '#B794F4',
}


def _css():
    st.markdown(f"""
    <style>
    .stApp {{ background-color: #0d1b36; }}

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        background: rgba(255,255,255,0.04);
        border-radius: 12px;
        padding: 0.3rem;
        border: 1px solid {C['border']};
        gap: 0.2rem;
        flex-wrap: wrap;
    }}
    .stTabs [data-baseweb="tab"] {{
        background: transparent;
        color: {C['muted']} !important;
        border-radius: 8px;
        font-weight: 500;
        font-size: 0.82rem;
        padding: 0.45rem 0.85rem;
        border: none;
    }}
    .stTabs [aria-selected="true"] {{
        background: {C['mid']} !important;
        color: {C['accent']} !important;
        font-weight: 600;
    }}
    .stTabs [data-baseweb="tab-panel"] {{ padding-top: 1.25rem; }}

    /* Labels */
    label, .stTextInput label, .stDateInput label,
    .stSelectbox label, .stNumberInput label,
    .stTextArea label, .stCheckbox label {{
        color: {C['muted']} !important;
        font-size: 0.82rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }}

    /* Inputs */
    .stTextInput input, .stTextArea textarea,
    .stDateInput input, .stNumberInput input {{
        background: rgba(255,255,255,0.06) !important;
        border: 1px solid {C['border']} !important;
        border-radius: 8px !important;
        color: {C['text']} !important;
        font-size: 0.92rem !important;
    }}
    .stTextInput input:focus, .stTextArea textarea:focus {{
        border-color: {C['primary']} !important;
        box-shadow: 0 0 0 2px rgba(91,141,184,0.2) !important;
    }}

    /* Selectbox */
    .stSelectbox > div > div {{
        background: rgba(255,255,255,0.06) !important;
        border: 1px solid {C['border']} !important;
        border-radius: 8px !important;
        color: {C['text']} !important;
    }}

    /* Radio */
    [data-testid="stSidebar"] .stRadio > div {{ gap: 0.25rem !important; }}
    .stRadio label {{
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid {C['border']} !important;
        border-radius: 8px !important;
        padding: 0.4rem 0.9rem !important;
        color: {C['muted']} !important;
        font-size: 0.85rem !important;
        text-transform: none !important;
        letter-spacing: 0 !important;
        font-weight: 500 !important;
    }}

    /* Checkbox */
    .stCheckbox label {{
        color: {C['text']} !important;
        text-transform: none !important;
        letter-spacing: 0 !important;
        font-size: 0.9rem !important;
        font-weight: 400 !important;
    }}

    /* Botones */
    .stButton > button[kind="primary"],
    .stFormSubmitButton > button,
    .stDownloadButton > button {{
        background: linear-gradient(135deg, {C['mid']}, {C['primary']}) !important;
        color: white !important;
        border: none !important;
        border-radius: 9px !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        transition: all 0.2s !important;
    }}
    .stButton > button[kind="primary"]:hover,
    .stDownloadButton > button:hover {{
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 18px rgba(91,141,184,0.35) !important;
    }}
    .stButton > button:not([kind="primary"]) {{
        background: rgba(255,255,255,0.06) !important;
        border: 1px solid {C['border']} !important;
        color: {C['text']} !important;
        border-radius: 9px !important;
        font-weight: 500 !important;
    }}
    
    /* Botones deshabilitados */
    .stButton > button:disabled {{
        opacity: 0.5 !important;
        cursor: not-allowed !important;
    }}

    /* Métricas */
    [data-testid="stMetric"] {{
        background: {C['card_bg']};
        border: 1px solid {C['border']};
        border-radius: 12px;
        padding: 1rem 1.25rem !important;
    }}
    [data-testid="stMetricLabel"] {{
        color: {C['muted']} !important;
        font-size: 0.75rem !important;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }}
    [data-testid="stMetricValue"] {{
        color: {C['text']} !important;
        font-size: 1.5rem !important;
        font-weight: 700 !important;
    }}

    /* Alerts */
    [data-testid="stSuccess"] {{
        background: rgba(104,211,145,0.12) !important;
        border: 1px solid rgba(104,211,145,0.3) !important;
        border-radius: 10px !important;
    }}
    [data-testid="stSuccess"] * {{ color: {C['success']} !important; }}
    [data-testid="stError"] {{
        background: rgba(252,129,129,0.12) !important;
        border: 1px solid rgba(252,129,129,0.3) !important;
        border-radius: 10px !important;
    }}
    [data-testid="stError"] * {{ color: {C['danger']} !important; }}
    [data-testid="stWarning"] {{
        background: rgba(246,173,85,0.12) !important;
        border: 1px solid rgba(246,173,85,0.3) !important;
        border-radius: 10px !important;
    }}
    [data-testid="stWarning"] * {{ color: {C['warning']} !important; }}
    [data-testid="stInfo"] {{
        background: rgba(91,141,184,0.12) !important;
        border: 1px solid rgba(91,141,184,0.3) !important;
        border-radius: 10px !important;
    }}
    [data-testid="stInfo"] * {{ color: {C['accent']} !important; }}

    /* Dataframe */
    [data-testid="stDataFrame"] {{
        border: 1px solid {C['border']} !important;
        border-radius: 12px !important;
        overflow: hidden;
    }}

    /* Markdown texto */
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] li {{
        color: {C['text']} !important;
    }}
    [data-testid="stMarkdownContainer"] strong {{
        color: {C['accent']} !important;
    }}

    hr {{ border-color: {C['border']} !important; }}

    /* ── Proteger sidebar ── */
    [data-testid="stSidebar"] {{
        background-color: #1a2744 !important;
    }}
    [data-testid="stSidebar"] * {{
        color: #ffffff !important;
    }}
    [data-testid="stSidebar"] .stRadio label {{
        color: #9DB4C7 !important;
        background: transparent !important;
        border: none !important;
        text-transform: none !important;
        letter-spacing: 0 !important;
        font-size: 0.92rem !important;
        font-weight: 500 !important;
        padding: 0.4rem 0.5rem !important;
    }}
    [data-testid="stSidebar"] .stButton > button {{
        background: transparent !important;
        border: 1px solid rgba(239,68,68,0.4) !important;
        color: #FC8181 !important;
        border-radius: 8px !important;
        text-transform: none !important;
        letter-spacing: 0 !important;
        font-size: 0.85rem !important;
    }}

    /* 👇 NUEVO: Badge de permisos */
    .permission-badge {{
        display: inline-block;
        background: rgba(91,141,184,0.15);
        border: 1px solid rgba(91,141,184,0.3);
        color: {C['accent']} !important;
        padding: 0.2rem 0.75rem;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 600;
        margin-left: 0.5rem;
    }}
    
    /* 👇 NUEVO: Modo solo lectura */
    .readonly-mode {{
        opacity: 0.7;
        pointer-events: none;
    }}
    </style>
    """, unsafe_allow_html=True)


def _seccion(emoji: str, titulo: str):
    st.markdown(
        f'<div style="display:flex; align-items:center; gap:0.6rem; margin:1.25rem 0 0.75rem;">'
        f'<span style="font-size:1.2rem;">{emoji}</span>'
        f'<span style="font-size:1rem; font-weight:700; color:{C["accent"]};">{titulo}</span>'
        f'</div>',
        unsafe_allow_html=True
    )


def _card_info(texto: str, tipo: str = "info"):
    colores = {
        "info":    (C['primary'],  'rgba(91,141,184,0.12)'),
        "success": (C['success'],  'rgba(104,211,145,0.12)'),
        "warning": (C['warning'],  'rgba(246,173,85,0.12)'),
        "danger":  (C['danger'],   'rgba(252,129,129,0.12)'),
    }
    color, bg = colores.get(tipo, colores['info'])
    st.markdown(
        f'<div style="background:{bg}; border:1px solid {color}40; border-radius:10px; '
        f'padding:0.85rem 1.1rem; color:{color}; font-size:0.9rem; margin:0.5rem 0;">'
        f'{texto}</div>',
        unsafe_allow_html=True
    )


def _divider():
    st.markdown(f'<hr style="border-color:{C["border"]}; margin:1.5rem 0;">', unsafe_allow_html=True)


def _check_permission(permission: Permission) -> bool:
    """Helper para verificar permisos"""
    perm_checker = st.session_state.get('permission_checker', None)
    return perm_checker and perm_checker.can(permission)


# =============================================================================
def show():
    _css()
    
    perm_checker = st.session_state.get('permission_checker', None)
    if not perm_checker:
        st.error("Error de permisos")
        return

    # Verificar si tiene acceso a administración
    if not perm_checker.can(Permission.CONFIG_VIEW):
        _card_info("⛔ No tienes permisos para acceder al módulo de Administración", "danger")
        st.stop()

    st.markdown(
        f'<h2 style="color:{C["accent"]}; font-weight:700; margin-bottom:1rem; font-size:1.4rem;">'
        f'⚙️ Administración del Sistema'
        f'<span class="permission-badge">{st.session_state.role.title()}</span></h2>',
        unsafe_allow_html=True
    )

    # 👇 NUEVO: Determinar qué tabs mostrar según permisos
    tabs_disponibles = []
    tab_funciones = []
    
    # Usuarios - solo admin
    if perm_checker.can(Permission.USER_VIEW_ALL):
        tabs_disponibles.append("👥 Usuarios")
        tab_funciones.append(mostrar_gestion_usuarios)
    
    # Habitaciones - admin y gerente
    if perm_checker.can(Permission.ROOM_VIEW):
        tabs_disponibles.append("🛏️ Habitaciones")
        tab_funciones.append(mostrar_gestion_habitaciones)
    
    # Reservas - todos (pero con restricciones)
    if perm_checker.can(Permission.BOOKING_VIEW_ALL):
        tabs_disponibles.append("📋 Reservas")
        tab_funciones.append(mostrar_gestion_reservas)
    
    # Huéspedes - todos
    tabs_disponibles.append("👤 Huéspedes")
    tab_funciones.append(mostrar_gestion_huespedes)
    
    # Facturas - según permisos
    if perm_checker.can(Permission.INVOICE_VIEW):
        tabs_disponibles.append("🧾 Facturas")
        tab_funciones.append(mostrar_gestion_facturas)
    
    # Tipos Habitación - solo lectura para todos
    tabs_disponibles.append("🛏️ Tipos Hab.")
    tab_funciones.append(mostrar_tipos_habitacion)
    
    # Sistema - solo admin
    if perm_checker.can(Permission.CONFIG_EDIT):
        tabs_disponibles.append("📊 Sistema")
        tab_funciones.append(mostrar_estado_sistema)

    # Crear tabs
    tab_objects = st.tabs(tabs_disponibles)
    
    # Ejecutar función correspondiente
    for i, tab in enumerate(tab_objects):
        with tab:
            tab_funciones[i]()


# =============================================================================
def mostrar_gestion_usuarios():
    _seccion("👥", "Gestión de Usuarios")
    
    perm_checker = st.session_state.get('permission_checker', None)
    puede_crear = perm_checker and perm_checker.can(Permission.USER_CREATE)
    puede_editar = perm_checker and perm_checker.can(Permission.USER_EDIT)
    puede_eliminar = perm_checker and perm_checker.can(Permission.USER_DELETE)

    usuarios = Usuario.get_all(solo_activos=False)
    if usuarios:
        df = pd.DataFrame(usuarios)
        df['activo'] = df['activo'].apply(lambda x: "✅ Activo" if x else "❌ Inactivo")
        df['rol'] = df['rol'].str.capitalize()
        if 'ultimo_acceso' in df.columns:
            df['ultimo_acceso'] = pd.to_datetime(df['ultimo_acceso'], errors='coerce')
            df['ultimo_acceso'] = df['ultimo_acceso'].dt.strftime('%d/%m/%Y %H:%M').fillna('-')

        cols = [c for c in ['username','nombre_completo','email','rol','activo','ultimo_acceso'] if c in df.columns]
        st.dataframe(df[cols], use_container_width=True, hide_index=True,
            column_config={"username":"Usuario","nombre_completo":"Nombre","rol":"Rol",
                           "activo":"Estado","ultimo_acceso":"Último acceso"})

        # 👇 NUEVO: Solo admin puede crear usuarios
        if puede_crear:
            _divider()
            _seccion("➕", "Crear Nuevo Usuario")
            with st.form("form_nuevo_usuario"):
                col1, col2 = st.columns(2)
                with col1:
                    username        = st.text_input("Usuario *")
                    nombre_completo = st.text_input("Nombre completo *")
                with col2:
                    email    = st.text_input("Email *")
                    rol      = st.selectbox("Rol", ["recepcionista","gerente","admin"])
                password = st.text_input("Contraseña *", type="password")

                if st.form_submit_button("Crear usuario", type="primary"):
                    if not all([username, nombre_completo, email, password]):
                        st.error("Complete todos los campos obligatorios")
                    else:
                        r = crear_usuario(username, nombre_completo, email, rol, password)
                        if r['success']:
                            st.success("Usuario creado correctamente")
                            st.rerun()
                        else:
                            st.error(r['error'])
        else:
            _card_info("ℹ️ Modo solo lectura - No tienes permisos para crear usuarios", "info")
    else:
        _card_info("📭 No hay usuarios registrados", "info")


def crear_usuario(username, nombre_completo, email, rol, password):
    try:
        if Usuario.get_by_username(username):
            return {'success': False, 'error': 'El nombre de usuario ya existe'}
        password_hash = Auth.hash_password(password)
        with db.get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO usuarios (username, password_hash, nombre_completo, email, rol)
                VALUES (%s, %s, %s, %s, %s) RETURNING id
            """, (username, password_hash, nombre_completo, email, rol))
            result = cursor.fetchone()
            if result:
                logger.info(f"Usuario creado: {username}")
                return {'success': True, 'id': result['id']}
        return {'success': False, 'error': 'No se pudo crear el usuario'}
    except Exception as e:
        logger.error(f"Error creando usuario: {e}")
        return {'success': False, 'error': str(e)}


# =============================================================================
def mostrar_tipos_habitacion():
    _seccion("🛏️", "Tipos de Habitación")

    with db.get_cursor() as cursor:
        cursor.execute("""
            SELECT id, nombre, descripcion, capacidad_maxima
            FROM tipos_habitacion ORDER BY capacidad_maxima
        """)
        tipos = cursor.fetchall()

    if tipos:
        st.dataframe(pd.DataFrame(tipos), use_container_width=True, hide_index=True,
            column_config={"id":"ID","nombre":"Nombre",
                           "descripcion":"Descripción","capacidad_maxima":"Capacidad máx."})
    else:
        _card_info("📭 No hay tipos de habitación registrados", "info")


# =============================================================================
def mostrar_estado_sistema():
    _seccion("📊", "Estado del Sistema")
    
    perm_checker = st.session_state.get('permission_checker', None)
    puede_editar = perm_checker and perm_checker.can(Permission.CONFIG_EDIT)

    with db.get_cursor() as cursor:
        cursor.execute("SELECT COUNT(*) as total FROM habitaciones WHERE activa = true")
        habitaciones = cursor.fetchone()['total']
        cursor.execute("SELECT COUNT(*) as total FROM huespedes")
        huespedes = cursor.fetchone()['total']
        cursor.execute("SELECT COUNT(*) as total FROM reservas WHERE estado NOT IN ('cancelada')")
        reservas_activas = cursor.fetchone()['total']
        cursor.execute("SELECT COUNT(*) as total FROM facturas WHERE estado = 'pendiente'")
        facturas_pendientes = cursor.fetchone()['total']

    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Habitaciones activas",    habitaciones)
    with col2: st.metric("Huéspedes registrados",   huespedes)
    with col3: st.metric("Reservas activas",         reservas_activas)
    with col4: st.metric("Facturas pendientes",      facturas_pendientes)

    # 👇 NUEVO: Configuración adicional solo para admin
    if puede_editar:
        _divider()
        _seccion("⚙️", "Configuración del Sistema")
        
        with st.form("form_config_sistema"):
            col1, col2 = st.columns(2)
            with col1:
                nombre_hotel = st.text_input("Nombre del Hotel", "Hotel Mirador Andino")
                email_contacto = st.text_input("Email de contacto", "reservas@hotelmiradorandino.pe")
            with col2:
                telefono = st.text_input("Teléfono", "(084) 234-567")
                direccion = st.text_input("Dirección", "Av. El Sol 456, Cusco, Perú")
            
            politicas = st.text_area("Políticas de cancelación", 
                                     "Cancelación gratuita hasta 24h antes del check-in")
            
            if st.form_submit_button("💾 Guardar Configuración", type="primary"):
                st.success("Configuración guardada (simulado)")
    else:
        _card_info("ℹ️ Modo solo lectura - Contacta al administrador para cambios", "info")

    _divider()
    st.markdown(
        f'<div style="color:{C["muted"]}; font-size:0.8rem; text-align:center;">'
        f'Sistema de Gestión Hotelera — Versión 1.0</div>',
        unsafe_allow_html=True
    )


# =============================================================================
def mostrar_gestion_habitaciones():
    _seccion("🛏️", "Gestión de Habitaciones")
    
    perm_checker = st.session_state.get('permission_checker', None)
    puede_editar = perm_checker and perm_checker.can(Permission.ROOM_EDIT)
    puede_crear = perm_checker and perm_checker.can(Permission.ROOM_CREATE)
    puede_cambiar_tarifas = perm_checker and perm_checker.can(Permission.ROOM_CHANGE_RATES)

    col1, col2, col3 = st.columns(3)
    with col1:
        mostrar_inactivas = st.checkbox("Mostrar inactivas", value=False)
    with col2:
        filtro_piso = st.selectbox("Filtrar por piso", ["Todos"] + [str(i) for i in range(1, 11)])
    with col3:
        filtro_estado = st.selectbox("Filtrar por estado",
            ["Todos","Disponible","Ocupada","Mantenimiento","Reservada","Limpieza"])

    habitaciones = Habitacion.get_all(activas_only=not mostrar_inactivas)

    if habitaciones:
        df = pd.DataFrame(habitaciones)
        if filtro_piso != "Todos":
            df = df[df['piso'] == int(filtro_piso)]
        if filtro_estado != "Todos":
            df = df[df['estado_nombre'].str.lower() == filtro_estado.lower()]

        df['activa']       = df['activa'].apply(lambda x: "✅" if x else "❌")
        df['tiene_vista']  = df['tiene_vista'].apply(lambda x: "✅" if x else "❌")
        df['tiene_balcon'] = df['tiene_balcon'].apply(lambda x: "✅" if x else "❌")
        df['tarifa_base']  = df['tarifa_base'].apply(lambda x: f"€ {x:,.2f}")

        ev_hab = st.dataframe(
            df[['numero','piso','tipo_nombre','estado_nombre','tarifa_base','metros_cuadrados','activa']],
            use_container_width=True, hide_index=True,
            column_config={"numero":"Número","piso":"Piso","tipo_nombre":"Tipo",
                           "estado_nombre":"Estado","tarifa_base":"Tarifa",
                           "metros_cuadrados":"m²","activa":"Activa"},
            on_select="rerun", selection_mode="single-row"
        )
        sel = (ev_hab.selection.rows if hasattr(ev_hab,'selection') and ev_hab.selection else None) or []

        # 👇 NUEVO: Edición solo con permisos
        if sel and sel[0] < len(df) and puede_editar:
            hab = habitaciones[sel[0]]
            _divider()
            _seccion("✏️", f"Editar Habitación {hab['numero']}")
            with st.form("form_editar_habitacion"):
                col1, col2 = st.columns(2)
                with col1:
                    nuevo_estado = st.selectbox("Estado",
                        [(1,"Disponible"),(2,"Ocupada"),(3,"Mantenimiento"),(4,"Reservada"),(5,"Limpieza")],
                        index=hab['estado_id']-1, format_func=lambda x: x[1])
                    
                    # 👇 NUEVO: Restricción para cambiar tarifas
                    if puede_cambiar_tarifas:
                        nueva_tarifa = st.number_input("Tarifa base (€)", min_value=0.0,
                            value=float(hab['tarifa_base']), step=10.0)
                    else:
                        nueva_tarifa = float(hab['tarifa_base'])
                        st.info(f"Tarifa actual: € {nueva_tarifa:,.2f} (solo lectura)")
                    
                    activa = st.checkbox("Habitación activa", value=hab['activa'])
                with col2:
                    tiene_vista   = st.checkbox("Tiene vista",   value=hab['tiene_vista'])
                    tiene_balcon  = st.checkbox("Tiene balcón",  value=hab['tiene_balcon'])
                    metros = st.number_input("m²", min_value=0.0,
                        value=float(hab.get('metros_cuadrados') or 0), step=0.5)
                notas = st.text_area("Notas", value=hab.get('notas','') or '')

                if st.form_submit_button("💾 Guardar Cambios", type="primary"):
                    h = Habitacion(id=hab['id'], numero=hab['numero'], piso=hab['piso'],
                        tipo_habitacion_id=hab['tipo_habitacion_id'], estado_id=nuevo_estado[0],
                        tarifa_base=nueva_tarifa, tiene_vista=tiene_vista, tiene_balcon=tiene_balcon,
                        metros_cuadrados=metros or None, notas=notas or None, activa=activa)
                    if h.save():
                        st.success("Habitación actualizada correctamente")
                        st.rerun()
                    else:
                        st.error("Error al actualizar la habitación")

        # 👇 NUEVO: Crear nueva habitación solo con permisos
        if puede_crear:
            _divider()
            _seccion("➕", "Nueva Habitación")
            with st.form("form_nueva_habitacion"):
                col1, col2 = st.columns(2)
                with col1:
                    numero    = st.text_input("Número *")
                    piso      = st.number_input("Piso *", min_value=1, max_value=20, value=1)
                    tipo_id   = st.selectbox("Tipo *",
                        [(1,"Individual"),(2,"Doble"),(3,"Suite"),(4,"Familiar"),(5,"Presidencial")],
                        format_func=lambda x: x[1])
                with col2:
                    tarifa_base = st.number_input("Tarifa base (€) *", min_value=0.0, value=100.0, step=10.0)
                    metros      = st.number_input("m²", min_value=0.0, value=20.0, step=0.5)
                    estado_id   = st.selectbox("Estado inicial",
                        [(1,"Disponible"),(2,"Ocupada"),(3,"Mantenimiento"),(4,"Reservada"),(5,"Limpieza")],
                        format_func=lambda x: x[1])
                tiene_vista  = st.checkbox("Tiene vista")
                tiene_balcon = st.checkbox("Tiene balcón")
                notas        = st.text_area("Notas")

                if st.form_submit_button("Crear habitación", type="primary"):
                    if not numero:
                        st.error("El número de habitación es obligatorio")
                    else:
                        h = Habitacion(numero=numero, piso=piso, tipo_habitacion_id=tipo_id[0],
                            estado_id=estado_id[0], tarifa_base=tarifa_base,
                            tiene_vista=tiene_vista, tiene_balcon=tiene_balcon,
                            metros_cuadrados=metros or None, notas=notas or None, activa=True)
                        if h.save():
                            st.success(f"Habitación {numero} creada correctamente")
                            st.rerun()
                        else:
                            st.error("Error al crear la habitación")
        else:
            if not puede_editar:
                _card_info("ℹ️ Modo solo lectura - No tienes permisos de edición", "info")
    else:
        _card_info("📭 No hay habitaciones registradas", "info")


# =============================================================================
def mostrar_gestion_reservas():
    _seccion("📋", "Gestión de Reservas")
    
    perm_checker = st.session_state.get('permission_checker', None)
    puede_cancelar = perm_checker and perm_checker.can(Permission.BOOKING_CANCEL)

    col1, col2 = st.columns(2)
    with col1:
        filtro_estado = st.selectbox("Filtrar por estado",
            ["Todas","Confirmada","Completada","Cancelada","No Show"])
    with col2:
        fecha_filtro = st.date_input("Filtrar por fecha check-in", value=None)

    reservas = Reserva.get_by_fechas(fecha_filtro, fecha_filtro + timedelta(days=30)) \
        if fecha_filtro else Reserva.get_activas()

    if reservas:
        df = pd.DataFrame(reservas)
        if filtro_estado != "Todas":
            df = df[df['estado'].str.lower() == filtro_estado.lower()]

        df['fecha_check_in']  = pd.to_datetime(df['fecha_check_in']).dt.strftime('%d/%m/%Y')
        df['fecha_check_out'] = pd.to_datetime(df['fecha_check_out']).dt.strftime('%d/%m/%Y')
        df['tarifa_total']    = df['tarifa_total'].apply(lambda x: f"€ {x:,.2f}")

        st.dataframe(
            df[['codigo_reserva','huesped_nombre','huesped_apellido','habitacion_numero',
                'fecha_check_in','fecha_check_out','tarifa_total','estado']],
            use_container_width=True, hide_index=True,
            column_config={"codigo_reserva":"Código","huesped_nombre":"Nombre",
                           "huesped_apellido":"Apellido","habitacion_numero":"Habitación",
                           "fecha_check_in":"Check-in","fecha_check_out":"Check-out",
                           "tarifa_total":"Total","estado":"Estado"}
        )

        # 👇 NUEVO: Cancelación solo con permisos
        if puede_cancelar:
            _divider()
            _seccion("⚡", "Cancelar Reserva")
            with st.form("form_cancelar_reserva"):
                codigo_cancelar = st.text_input("Código de reserva a cancelar")
                motivo = st.text_area("Motivo de cancelación")
                
                # Opción de reembolso según permisos
                tiene_reembolso = perm_checker and perm_checker.can(Permission.BOOKING_CANCEL_REFUND)
                if tiene_reembolso:
                    aplicar_reembolso = st.checkbox("Aplicar reembolso")
                
                if st.form_submit_button("Cancelar Reserva", type="primary"):
                    if codigo_cancelar and motivo:
                        reserva = Reserva.get_by_codigo(codigo_cancelar)
                        if reserva:
                            r = Reserva(id=reserva['id'])
                            if r.cancelar(motivo, st.session_state.user.get('id')):
                                st.success("Reserva cancelada correctamente")
                                if tiene_reembolso and aplicar_reembolso:
                                    st.info("Procesando reembolso...")
                                st.rerun()
                            else:
                                st.error("Error al cancelar la reserva")
                        else:
                            st.error("Reserva no encontrada")
                    else:
                        st.warning("Complete el código y el motivo")
        else:
            _card_info("ℹ️ No tienes permisos para cancelar reservas", "info")
    else:
        _card_info("📭 No hay reservas para mostrar", "info")


# =============================================================================
def mostrar_gestion_huespedes():
    _seccion("👤", "Gestión de Huéspedes")
    
    perm_checker = st.session_state.get('permission_checker', None)
    puede_editar = perm_checker and perm_checker.can(Permission.USER_EDIT)
    puede_marcar_vip = perm_checker and perm_checker.can(Permission.USER_EDIT)

    busqueda = st.text_input("🔍 Buscar huésped (documento, nombre, email)", key="busqueda_huesped")

    if busqueda:
        huespedes = Huesped.buscar(busqueda)
    else:
        with db.get_cursor() as cursor:
            cursor.execute("SELECT * FROM huespedes ORDER BY nombre, apellido LIMIT 100")
            huespedes = cursor.fetchall()

    if huespedes:
        df = pd.DataFrame(huespedes)
        df['es_vip'] = df['es_vip'].apply(lambda x: "⭐ VIP" if x else "")
        cols = [c for c in ['nombre','apellido','numero_documento','email','telefono','nacionalidad','es_vip'] if c in df.columns]

        ev_hue = st.dataframe(df[cols], use_container_width=True, hide_index=True,
            column_config={"nombre":"Nombre","apellido":"Apellido","numero_documento":"Documento",
                           "email":"Email","telefono":"Teléfono","nacionalidad":"Nacionalidad","es_vip":"VIP"},
            on_select="rerun", selection_mode="single-row")
        sel = (ev_hue.selection.rows if hasattr(ev_hue,'selection') and ev_hue.selection else None) or []

        # 👇 NUEVO: Edición solo con permisos
        if sel and sel[0] < len(df) and puede_editar:
            h = huespedes[sel[0]]
            _divider()
            _seccion("✏️", f"Editar: {h['nombre']} {h['apellido']}")
            with st.form("form_editar_huesped"):
                col1, col2 = st.columns(2)
                with col1:
                    nombre      = st.text_input("Nombre",    value=h.get('nombre',''))
                    apellido    = st.text_input("Apellido",  value=h.get('apellido',''))
                    documento   = st.text_input("Documento", value=h.get('numero_documento',''))
                    email       = st.text_input("Email",     value=h.get('email',''))
                with col2:
                    telefono    = st.text_input("Teléfono",     value=h.get('telefono',''))
                    nacionalidad= st.text_input("Nacionalidad", value=h.get('nacionalidad',''))
                    # 👇 NUEVO: Marcar VIP según permisos
                    es_vip      = st.checkbox("Huésped VIP",   value=h.get('es_vip', False), 
                                              disabled=not puede_marcar_vip)

                if st.form_submit_button("💾 Actualizar Huésped", type="primary"):
                    huesped = Huesped(id=h['id'], nombre=nombre, apellido=apellido,
                        numero_documento=documento, email=email, telefono=telefono,
                        nacionalidad=nacionalidad, es_vip=es_vip)
                    if huesped.save():
                        st.success("Huésped actualizado correctamente")
                        st.rerun()
                    else:
                        st.error("Error al actualizar el huésped")

        # Estadísticas
        _divider()
        col1, col2, col3 = st.columns(3)
        with col1: st.metric("Total huéspedes", len(df))
        with col2:
            vip = df['es_vip'].str.contains("VIP", na=False).sum() if 'es_vip' in df.columns else 0
            st.metric("Huéspedes VIP", vip)
        with col3:
            if 'nacionalidad' in df.columns:
                st.metric("Nacionalidades", df['nacionalidad'].nunique())
    else:
        _card_info("📭 No se encontraron huéspedes", "info")


# =============================================================================
def mostrar_gestion_facturas():
    _seccion("🧾", "Gestión de Facturas")
    
    perm_checker = st.session_state.get('permission_checker', None)
    puede_crear = perm_checker and perm_checker.can(Permission.INVOICE_CREATE)
    puede_anular = perm_checker and perm_checker.can(Permission.INVOICE_VOID)
    puede_descuento = perm_checker and perm_checker.can(Permission.INVOICE_DISCOUNT)

    col1, col2 = st.columns(2)
    with col1:
        filtro_estado = st.selectbox("Filtrar por estado",
            ["Todas","Pendiente","Pagada","Cancelada","Reembolsada"])
    with col2:
        fecha_filtro = st.date_input("Desde", value=date.today() - timedelta(days=30))

    facturas = Factura.get_por_rango_fechas(fecha_filtro, date.today())

    if facturas:
        df = pd.DataFrame(facturas)
        if filtro_estado != "Todas":
            df = df[df['estado'].str.lower() == filtro_estado.lower()]

        df_num = pd.DataFrame(facturas)  # numérico para resumen
        df['fecha_emision'] = pd.to_datetime(df['fecha_emision']).dt.strftime('%d/%m/%Y')
        df['total']    = df['total'].apply(lambda x: f"€ {x:,.2f}")
        df['subtotal'] = df['subtotal'].apply(lambda x: f"€ {x:,.2f}")

        ev_fac = st.dataframe(
            df[['numero_factura','huesped_nombre','fecha_emision','subtotal','impuestos','total','metodo_pago','estado']],
            use_container_width=True, hide_index=True,
            column_config={"numero_factura":"Número","huesped_nombre":"Huésped",
                           "fecha_emision":"Fecha","subtotal":"Subtotal",
                           "impuestos":"Impuestos","total":"Total",
                           "metodo_pago":"Método","estado":"Estado"},
            on_select="rerun", selection_mode="single-row"
        )
        sel = (ev_fac.selection.rows if hasattr(ev_fac,'selection') and ev_fac.selection else None) or []

        if sel and sel[0] < len(facturas):
            fac = facturas[sel[0]]
            _divider()
            _seccion("🧾", f"Detalle — Factura {fac['numero_factura']}")

            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Huésped:** {fac.get('huesped_nombre','N/A')}")
                st.markdown(f"**Fecha:** {pd.to_datetime(fac['fecha_emision']).strftime('%d/%m/%Y')}")
                st.markdown(f"**Estado:** {fac['estado'].capitalize()}")
            with col2:
                st.markdown(f"**Subtotal:** € {fac['subtotal']:,.2f}")
                st.markdown(f"**Impuestos:** € {fac['impuestos']:,.2f}")
                st.markdown(f"**Total:** € {fac['total']:,.2f}")
                if fac.get('metodo_pago'):
                    st.markdown(f"**Método pago:** {fac['metodo_pago'].capitalize()}")

            # 👇 NUEVO: Botones de acción según permisos
            col_a, col_b, col_c = st.columns(3)
            
            with col_a:
                if puede_anular and fac['estado'] != 'cancelada':
                    if st.button("❌ Anular Factura", type="primary"):
                        st.warning("¿Confirmar anulación?")
            
            with col_b:
                if st.button("📄 Ver Detalle"):
                    with db.get_cursor() as cursor:
                        cursor.execute("""
                            SELECT concepto, cantidad, precio_unitario, importe, tipo
                            FROM detalle_factura WHERE factura_id = %s
                        """, (fac['id'],))
                        detalle = cursor.fetchall()

                    if detalle:
                        st.dataframe(pd.DataFrame(detalle), use_container_width=True, hide_index=True)
            
            with col_c:
                if st.button("📥 Generar PDF"):
                    from utils.pdf_generator import PDFGenerator
                    with st.spinner("Generando PDF..."):
                        with db.get_cursor() as cursor:
                            cursor.execute("""
                                SELECT concepto, cantidad, precio_unitario, importe, tipo
                                FROM detalle_factura WHERE factura_id = %s
                            """, (fac['id'],))
                            detalle = cursor.fetchall()
                        
                        pdf = PDFGenerator()
                        pdf.create_invoice_pdf(fac, detalle)
                        pdf_data = pdf.output(dest='S').encode('latin1')
                        st.download_button("📥 Descargar Factura PDF", data=pdf_data,
                            file_name=f"factura_{fac['numero_factura']}.pdf",
                            mime="application/pdf")

        # ── Resumen financiero ────────────────────────────────────────────────
        _divider()
        col1, col2, col3 = st.columns(3)
        with col1:
            pend = df_num[df_num['estado']=='pendiente']['total'].sum() if 'estado' in df_num.columns else 0
            st.metric("Total Pendiente", f"€ {pend:,.2f}")
        with col2:
            pagado = df_num[df_num['estado']=='pagada']['total'].sum() if 'estado' in df_num.columns else 0
            st.metric("Total Pagado", f"€ {pagado:,.2f}")
        with col3:
            st.metric("Total Facturas", len(df))

        # 👇 NUEVO: Crear nueva factura solo con permisos
        if puede_crear:
            _divider()
            _seccion("➕", "Crear Nueva Factura")

            opcion = st.radio("Tipo", ["Desde reserva (automático)","Manual"], horizontal=True)

            if opcion == "Desde reserva (automático)":
                codigo_reserva = st.text_input("Código de reserva *", key="auto_reserva")

                if 'servicios_factura' not in st.session_state:
                    st.session_state.servicios_factura = []

                _seccion("🛎️", "Servicios Adicionales (opcional)")
                with db.get_cursor() as cursor:
                    cursor.execute("SELECT id, nombre, precio_base, categoria FROM servicios WHERE activo = true")
                    servicios_disp = cursor.fetchall()

                if servicios_disp:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        serv_sel = st.selectbox("Seleccionar servicio",
                            [""] + [f"{s['nombre']} - €{s['precio_base']:.2f}" for s in servicios_disp],
                            key="sel_servicio")
                    with col2:
                        cant_serv = st.number_input("Cantidad", min_value=1, value=1, key="cant_servicio")
                    with col3:
                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.button("➕ Agregar", key="add_servicio"):
                            if serv_sel:
                                info = next(s for s in servicios_disp if f"{s['nombre']} - €{s['precio_base']:.2f}" == serv_sel)
                                st.session_state.servicios_factura.append({
                                    'concepto': info['nombre'], 'cantidad': cant_serv,
                                    'precio_unitario': info['precio_base'], 'tipo': info['categoria']
                                })
                                st.success(f"Servicio agregado: {info['nombre']}")
                                st.rerun()

                if st.session_state.servicios_factura:
                    for idx, serv in enumerate(st.session_state.servicios_factura):
                        col1, col2 = st.columns([5, 1])
                        with col1:
                            st.markdown(
                                f'<div style="color:{C["text"]}; font-size:0.88rem; padding:0.3rem 0;">'
                                f'• {serv["concepto"]} ×{serv["cantidad"]} = '
                                f'€{serv["precio_unitario"] * serv["cantidad"]:,.2f}</div>',
                                unsafe_allow_html=True
                            )
                        with col2:
                            if st.button("❌", key=f"del_{idx}"):
                                st.session_state.servicios_factura.pop(idx)
                                st.rerun()

                metodo_pago = st.selectbox("Método de pago", ["","efectivo","tarjeta","transferencia"], key="auto_pago")
                notas = st.text_area("Notas", key="auto_notas")

                if st.button("Crear Factura Automática", type="primary", key="crear_auto"):
                    if codigo_reserva:
                        reserva = Reserva.get_by_codigo(codigo_reserva)
                        if reserva:
                            servicios = st.session_state.servicios_factura or None
                            resultado = FacturaController.crear_factura_desde_reserva(reserva['id'], servicios)
                            if resultado['success']:
                                if metodo_pago:
                                    FacturaController.marcar_pagada(resultado['factura_id'], metodo_pago)
                                st.success(f"Factura {resultado['numero_factura']} creada correctamente")
                                fi, fo = reserva['fecha_check_in'], reserva['fecha_check_out']
                                if isinstance(fi, str):
                                    fi = datetime.strptime(fi,'%Y-%m-%d').date()
                                    fo = datetime.strptime(fo,'%Y-%m-%d').date()
                                st.info(f"Se calcularon {(fo-fi).days} noche(s) automáticamente")
                                st.session_state.servicios_factura = []
                                st.rerun()
                            else:
                                st.error(resultado.get('error','Error al crear la factura'))
                        else:
                            st.error("Reserva no encontrada")
                    else:
                        st.warning("Ingrese un código de reserva")

            else:
                with st.form("form_factura_manual"):
                    col1, col2 = st.columns(2)
                    with col1:
                        codigo_reserva = st.text_input("Código de reserva (opcional)", key="manual_reserva")
                        subtotal       = st.number_input("Subtotal (€)", min_value=0.0, value=0.0, step=10.0)
                    with col2:
                        impuestos   = st.number_input("Impuestos (€)", min_value=0.0, value=0.0, step=1.0)
                        metodo_pago = st.selectbox("Método de pago", ["","efectivo","tarjeta","transferencia"], key="manual_pago")
                    notas = st.text_area("Notas", key="manual_notas")

                    if st.form_submit_button("Crear Factura Manual", type="primary"):
                        if codigo_reserva:
                            reserva = Reserva.get_by_codigo(codigo_reserva)
                            if reserva:
                                datos = {
                                    'huesped_id': reserva['huesped_id'],
                                    'reserva_id': reserva['id'],
                                    'subtotal': subtotal, 'impuestos': impuestos,
                                    'total': subtotal + impuestos,
                                    'metodo_pago': metodo_pago or None,
                                    'estado': 'pagada' if metodo_pago else 'pendiente',
                                    'notas': notas or None,
                                    'detalle': [{'concepto': f'Alojamiento - Reserva {codigo_reserva}',
                                                 'cantidad': 1, 'precio_unitario': subtotal,
                                                 'importe': subtotal, 'tipo': 'alojamiento'}]
                                }
                                r = FacturaController.crear_factura(datos)
                                if r['success']:
                                    st.success(f"Factura {r['numero_factura']} creada correctamente")
                                    st.rerun()
                                else:
                                    st.error(r.get('error','Error al crear la factura'))
                            else:
                                st.error("Reserva no encontrada")
                        else:
                            st.warning("Ingrese un código de reserva")
    else:
        _card_info("📭 No hay facturas para mostrar", "info")