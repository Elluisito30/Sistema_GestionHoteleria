# Debe ser lo primero: evita UnicodeDecodeError al conectar a PostgreSQL
import os
os.environ.setdefault('PGCLIENTENCODING', 'LATIN1')

import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

from config.settings import settings
from utils.auth import Auth
from utils.logger import logger
from utils.permissions import PermissionChecker, Permission, RoleManager  # 👈 NUEVO
from views import recepcion, administracion, dashboard, reportes

# =============================================================================
# 🏨 IDENTIDAD DEL HOTEL
# =============================================================================

HOTEL = {
    'nombre':    'Hotel Mirador Andino',
    'tagline':   'Desde las alturas del Cusco, una experiencia única',
    'emoji':     '🏔️',
    'direccion': 'Av. El Sol 456, Cusco, Perú',
    'email':     'reservas@hotelmiradorandino.pe',
    'telefono':  '(084) 234-567',
    'web':       'www.hotelmiradorandino.pe',
}

# =============================================================================
# 🎨 COLORES
# =============================================================================

COLORS = {
    'primary':        '#5B8DB8',
    'secondary':      '#9DB4C7',
    'accent':         '#A8C8B8',
    'bg_main':        '#F0F4F8',
    'bg_card':        '#FFFFFF',
    'bg_sidebar':     '#1a2744',
    'text_primary':   '#2D3748',
    'text_secondary': '#4A5568',
    'text_light':     '#718096',
    'border':         '#E2E8F0',
}

st.set_page_config(
    page_title=HOTEL['nombre'],
    page_icon=HOTEL['emoji'],
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# 🎨 CSS (tu código CSS existente se mantiene igual)
# =============================================================================

st.markdown(f"""
    <style>
    /* ── Fondo general ── */
    .stApp {{
        background-color: {COLORS['bg_main']};
    }}

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {{
        background-color: {COLORS['bg_sidebar']};
        border-right: 1px solid #2d3748;
    }}
    [data-testid="stSidebar"] * {{
        color: #ffffff !important;
    }}
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {{
        color: #9DB4C7 !important;
    }}

    /* ── Header login ── */
    .main-header {{
        background: linear-gradient(135deg, #2c5282 0%, #3b6e9f 100%);
        padding: 1rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: -1rem;
        box-shadow: 0 4px 20px rgba(44, 82, 130, 0.3);
    }}
    .main-header h1 {{
        color: white !important;
        font-size: 2rem;
        font-weight: 600;
        margin: 0;
    }}
    .main-header .subtitle {{
        color: rgba(255,255,255,0.9) !important;
        font-size: 1.05rem;
        margin-top: 0.5rem;
    }}
    .main-header .hotel-name {{
        color: #A8D8EA !important;
        font-weight: 800;
        letter-spacing: 0.5px;
    }}

    /* ── Header de vistas autenticadas ── */
    .view-header {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 1rem 1.5rem;
        background: #FFFFFF;
        border-radius: 14px;
        border: 1px solid {COLORS['border']};
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        margin-bottom: 1.5rem;
    }}
    .view-header-left {{
        display: flex;
        align-items: center;
        gap: 1rem;
    }}
    .view-header-icon {{
        width: 48px;
        height: 48px;
        background: linear-gradient(135deg, {COLORS['primary']}, {COLORS['secondary']});
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.4rem;
        flex-shrink: 0;
    }}
    .view-header-title {{
        font-size: 1.3rem;
        font-weight: 700;
        color: {COLORS['text_primary']};
        margin: 0;
        line-height: 1.2;
    }}
    .view-header-sub {{
        font-size: 0.82rem;
        color: {COLORS['text_light']};
        margin-top: 0.15rem;
    }}
    .view-header-right {{
        text-align: right;
    }}
    .view-header-date {{
        font-size: 0.8rem;
        color: {COLORS['text_light']};
        letter-spacing: 0.02em;
    }}
    .view-header-hotel {{
        font-size: 0.85rem;
        font-weight: 600;
        color: {COLORS['primary']};
        margin-top: 0.2rem;
    }}

    /* ── Inputs login ── */
    .stTextInput > label,
    .stPasswordInput > label {{
        color: {COLORS['text_primary']} !important;
        font-weight: 600;
        font-size: 0.95rem;
    }}
    .stTextInput input,
    .stPasswordInput input {{
        background-color: white !important;
        color: {COLORS['text_primary']} !important;
        border: 2px solid {COLORS['border']} !important;
        border-radius: 10px !important;
        padding: 12px 16px !important;
    }}
    .stTextInput input:focus,
    .stPasswordInput input:focus {{
        border-color: {COLORS['primary']} !important;
        box-shadow: 0 0 0 3px rgba(91, 141, 184, 0.15) !important;
    }}

    /* ── Botones ── */
    .stButton > button {{
        background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['secondary']} 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 14px 36px !important;
        font-weight: 600 !important;
        font-size: 1.05rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(91, 141, 184, 0.4) !important;
        min-width: 180px;
    }}
    .stButton > button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(91, 141, 184, 0.4) !important;
    }}

    /* ── Métricas nativas de Streamlit ── */
    [data-testid="stMetric"] {{
        background: #FFFFFF;
        border: 1px solid {COLORS['border']};
        border-radius: 12px;
        padding: 1rem 1.25rem !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.04);
    }}
    [data-testid="stMetricLabel"] {{
        font-size: 0.8rem !important;
        font-weight: 600 !important;
        color: {COLORS['text_light']} !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}
    [data-testid="stMetricValue"] {{
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        color: {COLORS['text_primary']} !important;
    }}
    [data-testid="stMetricDelta"] {{
        font-size: 0.82rem !important;
    }}

    .stPlotlyChart {{
        background: transparent !important;
        border-radius: 14px !important;
        border: 1px solid rgba(157,180,199,0.25) !important;
        overflow: hidden;
    }}

    .js-plotly-plot {{
        background: transparent !important;
        border: 1px solid {COLORS['border']};
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 2px 6px rgba(0,0,0,0.04);
    }}

    /* ── Dataframe ── */
    [data-testid="stDataFrame"] {{
        border-radius: 10px !important;
        overflow: hidden;
        border: 1px solid {COLORS['border']} !important;
    }}

    /* ── Badge de permisos ── */
    .permission-badge {{
        display: inline-block;
        background: rgba(91, 141, 184, 0.15);
        color: {COLORS['primary']} !important;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 600;
        border: 1px solid rgba(91, 141, 184, 0.3);
        margin: 0.2rem;
    }}

    /* ── Animación ── */
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(12px); }}
        to   {{ opacity: 1; transform: translateY(0); }}
    }}
    .main > .block-container {{
        animation: fadeIn 0.4s ease-out;
    }}

    </style>
""", unsafe_allow_html=True)

# =============================================================================
# 🔄 INICIALIZACIÓN
# =============================================================================

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.role = None
    st.session_state.permission_checker = None  # 👈 NUEVO

# =============================================================================
# 🧭 SIDEBAR
# =============================================================================

with st.sidebar:
    st.markdown(f"""
        <div style="text-align:center; padding:2.5rem 1.5rem; background:linear-gradient(180deg,rgba(91,141,184,0.15) 0%,rgba(91,141,184,0.05) 100%); border-bottom:2px solid rgba(157,180,199,0.3); margin:-1rem -1rem 1.5rem -1rem;">
            <div style="font-size:3rem; margin-bottom:0.5rem; filter:drop-shadow(0 4px 8px rgba(91,141,184,0.3));">{HOTEL['emoji']}</div>
            <div style="color:#A8D8EA; font-weight:800; font-size:1.15rem; letter-spacing:0.5px; margin-bottom:0.2rem;">
                {HOTEL['nombre']}
            </div>
            <div style="color:#9DB4C7; font-size:0.75rem; letter-spacing:0.5px; font-style:italic;">
                {HOTEL['tagline']}
            </div>
        </div>
    """, unsafe_allow_html=True)

    if st.session_state.authenticated:
        user = st.session_state.user
        role_badges = {
            'admin':         ('👑 Administrador', '#9B8AA5'),
            'gerente':       ('💼 Gerente',        '#7A9BAC'),
            'recepcionista': ('🛎️ Recepción',     '#88B8A8'),
        }
        role_text, role_color = role_badges.get(st.session_state.role, ('👤 Usuario', '#718096'))

        st.markdown(f"""
            <div style="background:rgba(255,255,255,0.07); padding:1.25rem; border-radius:14px; border:1px solid rgba(157,180,199,0.2); margin-bottom:1.25rem;">
                <div style="display:flex; align-items:center; gap:0.875rem; margin-bottom:0.875rem;">
                    <div style="width:48px; height:48px; background:linear-gradient(135deg,{COLORS['primary']},{COLORS['secondary']}); border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:1.3rem; font-weight:700; color:white; flex-shrink:0;">
                        {user.get('nombre_completo', '?')[0].upper()}
                    </div>
                    <div style="flex:1; min-width:0;">
                        <div style="color:#FFFFFF !important; font-weight:700; font-size:0.92rem; margin-bottom:0.2rem; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">
                            {user.get('nombre_completo', 'Usuario')}
                        </div>
                        <div style="display:inline-block; background:{role_color}25; color:{role_color} !important; padding:0.15rem 0.55rem; border-radius:10px; font-size:0.73rem; font-weight:600; border:1px solid {role_color}40;">
                            {role_text}
                        </div>
                    </div>
                </div>
                <div style="font-size:0.78rem; border-top:1px solid rgba(255,255,255,0.08); padding-top:0.6rem; display:flex; align-items:center; gap:0.4rem; overflow:hidden;">
                    <span style="flex-shrink:0;">📧</span>
                    <span style="overflow:hidden; text-overflow:ellipsis; white-space:nowrap; color:#9DB4C7 !important;">
                        {user.get('email', 'N/A')}
                    </span>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # 👇 NUEVO: Mostrar badges de permisos (opcional, colapsable)
        with st.expander("🔑 Mis Permisos", expanded=False):
            perm_checker = st.session_state.permission_checker
            st.markdown(f"**Rol:** {st.session_state.role.title()}")
            
            permisos_destacados = []
            if perm_checker.can(Permission.REPORT_VIEW_FINANCIAL):
                permisos_destacados.append("📊 Reportes financieros")
            if perm_checker.can(Permission.BOOKING_CANCEL_REFUND):
                permisos_destacados.append("💰 Reembolsos")
            if perm_checker.can(Permission.INVOICE_DISCOUNT_HIGH):
                permisos_destacados.append("🏷️ Descuentos >20%")
            if perm_checker.can(Permission.USER_CREATE):
                permisos_destacados.append("👥 Gestión usuarios")
            if perm_checker.can(Permission.CONFIG_EDIT):
                permisos_destacados.append("⚙️ Configuración")
            
            if permisos_destacados:
                st.markdown("**Permisos destacados:**")
                for p in permisos_destacados:
                    st.markdown(f"✓ {p}")
            else:
                st.markdown("*Permisos básicos de operación*")

        st.markdown("""
            <div style="color:#9DB4C7; font-weight:600; font-size:0.75rem; text-transform:uppercase; letter-spacing:1px; margin-bottom:0.5rem; padding:0 0.25rem;">
                🧭 Navegación
            </div>
        """, unsafe_allow_html=True)

        # 👇 NUEVO: Menú dinámico basado en permisos
        menu_options = {}
        perm_checker = st.session_state.permission_checker
        
        if perm_checker.can(Permission.DASHBOARD_VIEW):
            menu_options["📊 Dashboard"] = dashboard
        
        if perm_checker.can(Permission.BOOKING_CREATE) or perm_checker.can(Permission.BOOKING_VIEW_OWN):
            menu_options["🛎️ Recepción"] = recepcion
        
        if perm_checker.can(Permission.REPORT_VIEW_BASIC):
            menu_options["📈 Reportes"] = reportes
        
        if perm_checker.can(Permission.CONFIG_VIEW):
            menu_options["⚙️ Administración"] = administracion

        # Si no hay opciones (no debería pasar), mostrar mensaje
        if not menu_options:
            st.warning("No tienes acceso a ningún módulo")
            menu_options = {"📊 Dashboard": dashboard}  # fallback

        selected = st.radio(
            "Navegación", 
            list(menu_options.keys()), 
            label_visibility="collapsed",
            key="nav_radio"
        )

        st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
        st.markdown("<div style='padding-top:1rem; border-top:1px solid rgba(157,180,199,0.2);'>", unsafe_allow_html=True)
        
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            Auth.logout()
            st.session_state.authenticated = False
            st.session_state.user = None
            st.session_state.role = None
            st.session_state.permission_checker = None
            for k in [x for x in st.session_state if x not in ('authenticated','user','role','permission_checker')]:
                del st.session_state[k]
            st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)

    else:
        st.markdown(f"""
            <div style="background:linear-gradient(135deg,rgba(255,255,255,0.08) 0%,rgba(255,255,255,0.03) 100%); padding:2rem 1.5rem; border-radius:16px; text-align:center; border:2px solid rgba(157,180,199,0.3); box-shadow:0 4px 15px rgba(0,0,0,0.2);">
                <div style="font-size:3rem; margin-bottom:1rem;">🔐</div>
                <h4 style="color:#ffffff; margin:0 0 0.5rem 0; font-weight:700; font-size:1.1rem;">Acceso Restringido</h4>
                <p style="color:#9DB4C7; font-size:0.9rem; margin:0; line-height:1.5;">
                    Personal autorizado<br>de <strong>{HOTEL['nombre']}</strong>
                </p>
            </div>
        """, unsafe_allow_html=True)

# =============================================================================
# 🎬 CONTENIDO PRINCIPAL
# =============================================================================

if not st.session_state.authenticated:
    # ── LOGIN ───────────────────────────────────────────────────
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown(f"""
            <div class="main-header">
                <h1>{HOTEL['emoji']} <span class="hotel-name">{HOTEL['nombre']}</span></h1>
                <p class="subtitle">{HOTEL['tagline']}</p>
                <p class="subtitle" style="font-size:0.9rem; opacity:0.8; margin-top:0.25rem;">
                    Sistema de Gestión — Reservas, operaciones y experiencia del huésped
                </p>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='height:1.5rem;'></div>", unsafe_allow_html=True)

        with st.form("login_form", clear_on_submit=True):
            username = st.text_input("👤 Usuario", placeholder="Ingresa tu nombre de usuario")
            password = st.text_input("🔒 Contraseña", type="password", placeholder="••••••••")
            st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
            col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
            with col_btn2:
                submitted = st.form_submit_button("✨ Ingresar", use_container_width=True)

            if submitted:
                if not username or not password:
                    st.error("⚠️ Completa todos los campos")
                else:
                    success, result = Auth.authenticate(username, password)
                    if success:
                        st.session_state.authenticated = True
                        st.session_state.user = result
                        st.session_state.role = result.get('rol')
                        # 👇 NUEVO: Inicializar permission checker
                        st.session_state.permission_checker = PermissionChecker(st.session_state.role)
                        logger.info(f"✅ Login exitoso: {username}")
                        st.rerun()
                    else:
                        st.error(f"❌ {result}")

else:
    # ── VISTAS AUTENTICADAS ───────────────────────────────────────────────────
    # Obtener título según módulo seleccionado
    titulos_modulos = {
        "📊 Dashboard": ("📊", "Panel de Control", "Resumen operativo del día"),
        "🛎️ Recepción": ("🛎️", "Recepción", "Check-in, check-out y reservas"),
        "📈 Reportes": ("📈", "Reportes", "Indicadores y estadísticas"),
        "⚙️ Administración": ("⚙️", "Administración", "Configuración del sistema"),
    }
    
    emoji_v, titulo, subtitulo = titulos_modulos.get(selected, ("🏨", HOTEL['nombre'], ""))
    nombre_usuario = st.session_state.user.get('nombre_completo', 'Usuario')
    fecha_hoy = datetime.now().strftime("%d/%m/%Y")

    # Header limpio y profesional para vistas autenticadas
    st.markdown(f"""
        <div class="view-header">
            <div class="view-header-left">
                <div class="view-header-icon">{emoji_v}</div>
                <div>
                    <div class="view-header-title">{titulo}</div>
                    <div class="view-header-sub">{subtitulo}</div>
                </div>
            </div>
            <div class="view-header-right">
                <div class="view-header-date">👤 {nombre_usuario} &nbsp;·&nbsp; {fecha_hoy}</div>
                <div class="view-header-hotel">{HOTEL['emoji']} {HOTEL['nombre']}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 👇 NUEVO: Verificar permisos antes de cargar cada vista
    try:
        if selected == "📊 Dashboard":
            if st.session_state.permission_checker.can(Permission.DASHBOARD_VIEW):
                dashboard.show()
            else:
                st.error("⛔ No tienes permisos para ver el Dashboard")
                
        elif selected == "🛎️ Recepción":
            if st.session_state.permission_checker.can_any([Permission.BOOKING_CREATE, Permission.BOOKING_VIEW_OWN]):
                recepcion.show()
            else:
                st.error("⛔ No tienes permisos para acceder a Recepción")
                
        elif selected == "📈 Reportes":
            if st.session_state.permission_checker.can(Permission.REPORT_VIEW_BASIC):
                reportes.show()
            else:
                st.error("⛔ No tienes permisos para ver Reportes")
                
        elif selected == "⚙️ Administración":
            if st.session_state.permission_checker.can(Permission.CONFIG_VIEW):
                administracion.show()
            else:
                st.error("⛔ No tienes permisos para acceder a Administración")
    except Exception as e:
        st.error(f"Error al cargar la vista: {str(e)}")
        logger.error(f"Error en navegación: {str(e)}")

# =============================================================================
# 🦶 FOOTER
# =============================================================================

st.markdown(
    f"""
    <div style="border-top:1px solid #3a3a5a; margin-top:1rem;">
        <div style="text-align:center; padding:1.5rem 0 0.5rem;">
            <div style="
                font-weight:800;
                font-size:1.15rem;
                color:#1a2744;
                margin-bottom:0.3rem;
                letter-spacing:0.5px;
            ">
                {HOTEL['nombre']}
            </div>
            <div style="
                color:#4A5568;
                font-size:0.82rem;
                font-style:italic;
                margin-bottom:0.75rem;
            ">
                {HOTEL['tagline']}
            </div>
            <div style="
                color:#4A5568;
                font-size:0.85rem;
            ">
                📍 {HOTEL['direccion']} &nbsp;|&nbsp; 
                ✉️ {HOTEL['email']} &nbsp;|&nbsp; 
                📞 {HOTEL['telefono']}
            </div>
            <div style="
                color:#718096;
                font-size:0.78rem;
                padding-top:0.75rem;
            ">
                &copy; 2026 {HOTEL['nombre']} — Todos los derechos reservados
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)