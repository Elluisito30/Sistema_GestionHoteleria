import streamlit as st
import pandas as pd
from datetime import date, timedelta, datetime
import plotly.express as px
import time

from controllers.reserva_controller import ReservaController
from controllers.habitacion_controller import HabitacionController
from controllers.huesped_controller import HuespedController
from models.reserva import Reserva
from config.database import db
from utils.logger import logger
from utils.permissions import Permission
from utils.pdf_generator import PDFGenerator

# ── Paleta (misma que dashboard) ───────────────────────────────────────────────
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
}

def _get_pdf_data(pdf):
    """Convierte la salida del PDF a bytes para descargar"""
    pdf_output = pdf.output(dest='S')
    if isinstance(pdf_output, bytearray):
        return bytes(pdf_output)
    elif hasattr(pdf_output, 'encode'):
        return pdf_output.encode('latin1')
    else:
        return pdf_output

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
        gap: 0.25rem;
    }}
    .stTabs [data-baseweb="tab"] {{
        background: transparent;
        color: {C['muted']} !important;
        border-radius: 8px;
        font-weight: 500;
        font-size: 0.88rem;
        padding: 0.5rem 1rem;
        border: none;
    }}
    .stTabs [aria-selected="true"] {{
        background: {C['mid']} !important;
        color: {C['accent']} !important;
        font-weight: 600;
    }}
    .stTabs [data-baseweb="tab-panel"] {{
        padding-top: 1.25rem;
    }}

    /* Labels e inputs */
    label, .stTextInput label, .stDateInput label,
    .stSelectbox label, .stNumberInput label, .stTextArea label {{
        color: {C['muted']} !important;
        font-size: 0.82rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}
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

    /* Botones primarios */
    .stButton > button[kind="primary"],
    .stFormSubmitButton > button {{
        background: linear-gradient(135deg, {C['mid']}, {C['primary']}) !important;
        color: white !important;
        border: none !important;
        border-radius: 9px !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        letter-spacing: 0.03em !important;
        transition: all 0.2s !important;
    }}
    .stButton > button[kind="primary"]:hover,
    .stFormSubmitButton > button:hover {{
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 18px rgba(91,141,184,0.35) !important;
    }}

    /* Botones secundarios */
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

    /* Alerts */
    [data-testid="stSuccess"] {{
        background: rgba(104,211,145,0.12) !important;
        border: 1px solid rgba(104,211,145,0.3) !important;
        border-radius: 10px !important;
        color: {C['success']} !important;
    }}
    [data-testid="stError"] {{
        background: rgba(252,129,129,0.12) !important;
        border: 1px solid rgba(252,129,129,0.3) !important;
        border-radius: 10px !important;
        color: {C['danger']} !important;
    }}
    [data-testid="stWarning"] {{
        background: rgba(246,173,85,0.12) !important;
        border: 1px solid rgba(246,173,85,0.3) !important;
        border-radius: 10px !important;
        color: {C['warning']} !important;
    }}
    [data-testid="stInfo"] {{
        background: rgba(91,141,184,0.12) !important;
        border: 1px solid rgba(91,141,184,0.3) !important;
        border-radius: 10px !important;
        color: {C['accent']} !important;
    }}
    [data-testid="stSuccess"] *, [data-testid="stError"] *,
    [data-testid="stWarning"] *, [data-testid="stInfo"] * {{
        color: inherit !important;
    }}

    /* Dataframe */
    [data-testid="stDataFrame"] {{
        border: 1px solid {C['border']} !important;
        border-radius: 12px !important;
        overflow: hidden;
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
        font-size: 1.6rem !important;
        font-weight: 700 !important;
    }}

    /* Spinner */
    .stSpinner > div {{ border-top-color: {C['primary']} !important; }}

    /* Markdown headers dentro de vistas */
    [data-testid="stMarkdownContainer"] h3,
    [data-testid="stMarkdownContainer"] h4 {{
        color: {C['accent']} !important;
        background: transparent !important;
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

    /* 👇 Badge de permisos */
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
        "info":    (C['primary'],   'rgba(91,141,184,0.12)'),
        "success": (C['success'],   'rgba(104,211,145,0.12)'),
        "warning": (C['warning'],   'rgba(246,173,85,0.12)'),
        "danger":  (C['danger'],    'rgba(252,129,129,0.12)'),
    }
    color, bg = colores.get(tipo, colores['info'])
    st.markdown(
        f'<div style="background:{bg}; border:1px solid {color}40; border-radius:10px; '
        f'padding:0.85rem 1.1rem; color:{color}; font-size:0.9rem; margin:0.5rem 0;">'
        f'{texto}</div>',
        unsafe_allow_html=True
    )


def show():
    _css()
    
    # Inicializar contadores para limpiar inputs
    if 'checkin_counter' not in st.session_state:
        st.session_state.checkin_counter = 0
    if 'checkout_counter' not in st.session_state:
        st.session_state.checkout_counter = 0
    
    # Inicializar índice de habitación seleccionada
    if 'habitacion_idx' not in st.session_state:
        st.session_state.habitacion_idx = 0
    
    # Inicializar estado de búsqueda de habitaciones
    if 'busqueda_realizada' not in st.session_state:
        st.session_state.busqueda_realizada = False
    if 'habitaciones_encontradas' not in st.session_state:
        st.session_state.habitaciones_encontradas = []
    if 'fecha_check_in_actual' not in st.session_state:
        st.session_state.fecha_check_in_actual = date.today()
    if 'fecha_check_out_actual' not in st.session_state:
        st.session_state.fecha_check_out_actual = date.today() + timedelta(days=1)
    if 'tipo_seleccionado' not in st.session_state:
        st.session_state.tipo_seleccionado = "Todos"
    if 'capacidad_seleccionada' not in st.session_state:
        st.session_state.capacidad_seleccionada = 2
    
    # Inicializar estado de búsqueda de huéspedes
    if 'busqueda_huesped_realizada' not in st.session_state:
        st.session_state.busqueda_huesped_realizada = False
    if 'resultados_huesped' not in st.session_state:
        st.session_state.resultados_huesped = []
    
    # Inicializar caché de reservas activas
    if 'reservas_activas_cache' not in st.session_state:
        st.session_state.reservas_activas_cache = None
    
    # Obtener permission checker
    perm_checker = st.session_state.get('permission_checker', None)
    if not perm_checker:
        st.error("Error de permisos")
        return

    st.markdown(
        f'<h2 style="color:{C["accent"]}; font-weight:700; margin-bottom:1rem; font-size:1.4rem;">'
        f'🛎️ Módulo de Recepción'
        f'<span class="permission-badge">{st.session_state.role.title()}</span></h2>',
        unsafe_allow_html=True
    )

    # Determinar qué tabs mostrar según permisos
    tabs_disponibles = []
    tab_funciones = []
    
    # Buscar Disponibilidad - todos pueden ver
    tabs_disponibles.append("🔍 Buscar Disponibilidad")
    tab_funciones.append(mostrar_busqueda_disponibilidad)
    
    # Reservas Activas - todos pueden ver
    if perm_checker.can_any([Permission.BOOKING_VIEW_OWN, Permission.BOOKING_VIEW_ALL]):
        tabs_disponibles.append("📋 Reservas Activas")
        tab_funciones.append(mostrar_reservas_activas)
    
    # 👇 NUEVA PESTAÑA: Huéspedes Alojados Ahora
    tabs_disponibles.append("🏨 Alojados Ahora")
    tab_funciones.append(mostrar_alojados_ahora)
    
    # Check-in/Check-out - solo si puede crear reservas o check-in
    if perm_checker.can_any([Permission.BOOKING_CREATE, Permission.BOOKING_EDIT]):
        tabs_disponibles.append("✅ Check-in / Check-out")
        tab_funciones.append(mostrar_check_in_out)
    
    # Registrar Huésped - todos pueden (pero con limitaciones)
    tabs_disponibles.append("👤 Registrar Huésped")
    tab_funciones.append(mostrar_registro_huesped)
    
    # Crear tabs
    tab_objects = st.tabs(tabs_disponibles)
    
    # Ejecutar función correspondiente
    for i, tab in enumerate(tab_objects):
        with tab:
            tab_funciones[i]()


def mostrar_busqueda_disponibilidad():
    _seccion("🔍", "Buscar Habitaciones Disponibles")
    
    # Verificar si puede crear reservas
    perm_checker = st.session_state.permission_checker
    puede_reservar = perm_checker.can(Permission.BOOKING_CREATE)

    # ===== FORMULARIO DE BÚSQUEDA =====
    with st.form("form_busqueda_principal"):
        col1, col2, col3 = st.columns(3)
        with col1:
            fecha_check_in = st.date_input(
                "Check-in", 
                min_value=date.today(), 
                value=st.session_state.fecha_check_in_actual,
                key="busqueda_checkin_form"
            )
        with col2:
            fecha_check_out = st.date_input(
                "Check-out",
                min_value=fecha_check_in + timedelta(days=1),
                value=fecha_check_in + timedelta(days=1),
                key="busqueda_checkout_form"
            )
        with col3:
            capacidad = st.number_input(
                "Capacidad (personas)", 
                min_value=1, 
                value=st.session_state.capacidad_seleccionada,
                key="busqueda_capacidad_form"
            )

        col4, col5 = st.columns(2)
        with col4:
            tipo_habitacion = st.selectbox(
                "Tipo de Habitación",
                options=["Todos", "Individual", "Doble", "Suite", "Familiar", "Presidencial"],
                index=["Todos", "Individual", "Doble", "Suite", "Familiar", "Presidencial"].index(st.session_state.tipo_seleccionado),
                key="busqueda_tipo_form"
            )
        with col5:
            st.markdown("<br>", unsafe_allow_html=True)
            buscar = st.form_submit_button("🔍 Buscar Habitaciones", type="primary", use_container_width=True)

    # ===== PROCESAR BÚSQUEDA =====
    if buscar:
        with st.spinner("Buscando disponibilidad..."):
            tipo_map = {"Individual": 1, "Doble": 2, "Suite": 3, "Familiar": 4, "Presidencial": 5}
            tipo_id = tipo_map.get(tipo_habitacion) if tipo_habitacion != "Todos" else None

            habitaciones = ReservaController.buscar_disponibilidad(
                fecha_check_in, fecha_check_out, tipo_id, capacidad
            )
            
            # Guardar en session_state
            st.session_state.busqueda_realizada = True
            st.session_state.habitaciones_encontradas = habitaciones
            st.session_state.fecha_check_in_actual = fecha_check_in
            st.session_state.fecha_check_out_actual = fecha_check_out
            st.session_state.tipo_seleccionado = tipo_habitacion
            st.session_state.capacidad_seleccionada = capacidad
            st.session_state.habitacion_idx = 0  # Resetear índice de habitación
            st.session_state.busqueda_huesped_realizada = False  # Resetear búsqueda de huésped
            
            st.rerun()

    # ===== MOSTRAR RESULTADOS DE BÚSQUEDA =====
    if st.session_state.busqueda_realizada:
        habitaciones = st.session_state.habitaciones_encontradas
        
        if habitaciones:
            _card_info(f"✅ Se encontraron <strong>{len(habitaciones)}</strong> habitaciones disponibles", "success")

            df = pd.DataFrame(habitaciones)
            df_display = df[['numero','tipo_nombre','piso','tarifa_calculada','metros_cuadrados','tiene_vista']].copy()
            df_display.columns = ['Habitación','Tipo','Piso','Tarifa/Día (S/)','m²','Vista']
            df_display['Tarifa/Día (S/)'] = df_display['Tarifa/Día (S/)'].apply(lambda x: f"S/ {x:,.2f}")
            df_display['Vista'] = df_display['Vista'].apply(lambda x: "✅ Sí" if x else "❌ No")

            st.dataframe(df_display, use_container_width=True, hide_index=True)

            # ===== SECCIÓN DE RESERVA =====
            if puede_reservar:
                _seccion("📝", "Realizar Reserva")

                # Preparar opciones de habitación
                opciones_habitacion = {
                    f"{h['numero']} - {h['tipo_nombre']} (S/ {h['tarifa_calculada']:,.2f}/día)": h
                    for h in habitaciones
                }
                
                opciones_lista = list(opciones_habitacion.keys())
                # Eliminar duplicados por si acaso
                opciones_lista = list(dict.fromkeys(opciones_lista))
                
                # Asegurar índice válido
                if st.session_state.habitacion_idx >= len(opciones_lista):
                    st.session_state.habitacion_idx = 0
                
                # SELECTOR DE HABITACIÓN (NO CAUSA RERUN)
                col_sel, col_btn = st.columns([5, 1])
                
                with col_sel:
                    seleccion = st.selectbox(
                        "Seleccionar habitación", 
                        opciones_lista,
                        index=st.session_state.habitacion_idx,
                        key="selector_hab_final"
                    )
                    # Actualizar índice SIN rerun
                    nuevo_idx = opciones_lista.index(seleccion)
                    if nuevo_idx != st.session_state.habitacion_idx:
                        st.session_state.habitacion_idx = nuevo_idx
                
                with col_btn:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("🔄 Limpiar", key="btn_limpiar_hab_final"):
                        st.session_state.habitacion_idx = 0
                        st.rerun()
                
                # Obtener habitación seleccionada
                habitacion = opciones_habitacion[seleccion]
                
                # ===== BÚSQUEDA DE HUÉSPED =====
                st.markdown("### 👤 Datos del Huésped")
                
                # Campo de búsqueda
                termino_busqueda = st.text_input(
                    "Buscar huésped por documento o email",
                    placeholder="Ingrese DNI, pasaporte o email...",
                    key="busqueda_huesped_input_final"
                )
                
                # Botón de búsqueda
                col_buscar, col_espacio = st.columns([1, 5])
                with col_buscar:
                    buscar_huesped = st.button("🔍 Buscar", key="btn_buscar_huesped_final", use_container_width=True)
                
                if buscar_huesped and termino_busqueda:
                    with st.spinner("Buscando..."):
                        resultados = HuespedController.buscar(termino_busqueda)
                        st.session_state.busqueda_huesped_realizada = True
                        st.session_state.resultados_huesped = resultados
                        st.rerun()
                
                # Mostrar resultados si existen
                huesped_id = None
                if st.session_state.busqueda_huesped_realizada and st.session_state.resultados_huesped:
                    resultados = st.session_state.resultados_huesped
                    if resultados:
                        opciones_huesped = {
                            f"{h['nombre']} {h['apellido']} - {h['numero_documento']}": h
                            for h in resultados
                        }
                        opciones_lista_huesped = list(opciones_huesped.keys())
                        
                        # Selector de huésped (sin mensaje de cantidad)
                        seleccion_huesped = st.selectbox(
                            "Seleccionar huésped",
                            opciones_lista_huesped,
                            key="selector_huesped_final"
                        )
                        
                        if seleccion_huesped:
                            huesped_id = opciones_huesped[seleccion_huesped]['id']
                            
                            # Botón para limpiar búsqueda (más pequeño y discreto)
                            if st.button("✕ Limpiar búsqueda", key="btn_limpiar_busqueda_huesped"):
                                st.session_state.busqueda_huesped_realizada = False
                                st.session_state.resultados_huesped = []
                                st.rerun()
                    else:
                        st.warning("No se encontraron huéspedes. Complete los datos para uno nuevo.")
                        if st.button("↺ Intentar de nuevo", key="btn_reintentar_final"):
                            st.session_state.busqueda_huesped_realizada = False
                            st.rerun()
                
                # Línea separadora
                st.markdown("---")
                
                # FORMULARIO DE RESERVA
                with st.form(key="form_reserva_final"):
                    
                    # Datos del nuevo huésped (solo si no se seleccionó uno existente)
                    if not huesped_id:
                        st.markdown("### 📝 Registrar Nuevo Huésped")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            nombre = st.text_input("Nombres *", key="nombre_final")
                            documento = st.text_input("Documento *", key="doc_final")
                            email = st.text_input("Email", key="email_final")
                        
                        with col2:
                            apellido = st.text_input("Apellidos *", key="apellido_final")
                            telefono = st.text_input("Teléfono *", key="tel_final")
                    else:
                        # Si hay huésped seleccionado, no mostrar el formulario de registro
                        # Solo mostrar un mensaje discreto
                        st.info(f"Huésped seleccionado: {seleccion_huesped}")
                        # Campos ocultos con valores vacíos
                        nombre = apellido = documento = telefono = ""
                    
                    st.markdown("### 🏨 Detalles de la Reserva")
                    col3, col4, col5 = st.columns(3)
                    
                    with col3:
                        adultos = st.number_input("Adultos", min_value=1, value=2, key="adultos_final")
                    
                    with col4:
                        ninos = st.number_input("Niños", min_value=0, value=0, key="ninos_final")
                    
                    with col5:
                        total_dias = (st.session_state.fecha_check_out_actual - st.session_state.fecha_check_in_actual).days
                        # Convertir Decimal a float
                        tarifa_float = float(habitacion['tarifa_calculada']) if hasattr(habitacion['tarifa_calculada'], 'item') else float(habitacion['tarifa_calculada'])
                        total_estancia = tarifa_float * total_dias
                        st.metric("Total estancia", f"S/ {total_estancia:,.2f}", f"{total_dias} días")
                    
                    notas = st.text_area("Notas adicionales", key="notas_final")
                    
                    submitted = st.form_submit_button("✅ Confirmar Reserva", type="primary", use_container_width=True)
                    
                    if submitted:
                        # Validaciones
                        if not huesped_id and not all([nombre, apellido, documento, telefono]):
                            st.error("Complete todos los campos obligatorios (*) o busque un huésped existente")
                        else:
                            # ===== NUEVA VALIDACIÓN DE CAPACIDAD =====
                            total_personas = adultos + ninos
                            capacidad_maxima = habitacion.get('capacidad_maxima', 0)
                            
                            if total_personas > capacidad_maxima:
                                st.error(f"⚠️ La habitación {habitacion['numero']} ({habitacion['tipo_nombre']}) tiene capacidad máxima de {capacidad_maxima} personas. Has seleccionado {total_personas} personas.")
                                st.stop()
                            
                            # Crear huésped si no existe
                            if not huesped_id:
                                nuevo = HuespedController.crear_huesped({
                                    'nombre': nombre, 'apellido': apellido,
                                    'tipo_documento': 'DNI', 'numero_documento': documento,
                                    'email': email, 'telefono': telefono
                                })
                                if nuevo['success']:
                                    huesped_id = nuevo['huesped_id']
                                else:
                                    st.error(nuevo['error'])
                                    st.stop()
                            
                            # Crear reserva
                            resultado = ReservaController.crear_reserva(
                                {
                                    'huesped_id': huesped_id,
                                    'fecha_check_in': st.session_state.fecha_check_in_actual,
                                    'fecha_check_out': st.session_state.fecha_check_out_actual,
                                    'numero_adultos': adultos,
                                    'numero_ninos': ninos,
                                    'habitacion_id': habitacion['id'],
                                    'tarifa_total': total_estancia,
                                    'notas': notas
                                },
                                st.session_state.user['id']
                            )
                            
                            if resultado['success']:
                                st.success(f"✅ Reserva creada — Código: **{resultado['codigo_reserva']}**")
                                logger.info(f"Reserva creada: {resultado['codigo_reserva']}")
                                st.balloons()
                                # Limpiar después de reserva exitosa
                                st.session_state.busqueda_realizada = False
                                st.session_state.busqueda_huesped_realizada = False
                                st.session_state.habitacion_idx = 0
                                # Limpiar caché de reservas activas
                                if 'reservas_activas_cache' in st.session_state:
                                    st.session_state.reservas_activas_cache = None
                                st.rerun()
                            else:
                                st.error(f"Error: {resultado['error']}")
            else:
                _card_info("ℹ️ No tienes permisos para crear reservas. Consulta con un supervisor.", "info")
        else:
            _card_info("⚠️ No hay habitaciones disponibles para los criterios seleccionados", "warning")
            if st.button("🔄 Nueva búsqueda", key="btn_nueva_busqueda"):
                st.session_state.busqueda_realizada = False
                st.rerun()


def mostrar_reservas_activas():
    _seccion("📋", "Reservas Activas")
    
    perm_checker = st.session_state.permission_checker
    puede_cancelar = perm_checker.can(Permission.BOOKING_CANCEL)
    puede_editar = perm_checker.can(Permission.BOOKING_EDIT)
    puede_ver_factura = perm_checker.can(Permission.INVOICE_VIEW)

    # ===== USAR CACHÉ PARA OPTIMIZAR =====
    # Si no hay caché o se forzó recarga, obtener datos frescos
    if st.session_state.reservas_activas_cache is None:
        reservas = Reserva.get_activas()
        st.session_state.reservas_activas_cache = reservas
    else:
        reservas = st.session_state.reservas_activas_cache

    if reservas:
        df = pd.DataFrame(reservas)
        df['fecha_check_in']  = pd.to_datetime(df['fecha_check_in']).dt.strftime('%d/%m/%Y')
        df['fecha_check_out'] = pd.to_datetime(df['fecha_check_out']).dt.strftime('%d/%m/%Y')

        # Filtrar columnas según permisos
        columnas_base = ['codigo_reserva','huesped_nombre','huesped_apellido',
                        'fecha_check_in','fecha_check_out','habitacion_numero','estado']
        
        if perm_checker.can(Permission.BOOKING_VIEW_ALL):
            # Puede ver todas las reservas
            df_display = df[columnas_base].copy()
        else:
            # Solo ve reservas propias o básicas
            if 'created_by' in df.columns:
                df = df[df['created_by'] == st.session_state.user['id']]
            df_display = df[columnas_base].copy()
        
        df_display.columns = ['Código','Nombre','Apellido','Check-in','Check-out','Habitación','Estado']

        def color_estado(val):
            colores = {
                'confirmada': f'background-color:rgba(104,211,145,0.15); color:{C["success"]}',
                'completada': f'background-color:rgba(91,141,184,0.15); color:{C["accent"]}',
                'cancelada':  f'background-color:rgba(252,129,129,0.15); color:{C["danger"]}',
            }
            return colores.get(val, '')

        try:
            st.dataframe(
                df_display.style.map(color_estado, subset=['Estado']),
                use_container_width=True, hide_index=True
            )
        except AttributeError:
            st.dataframe(
                df_display.style.applymap(color_estado, subset=['Estado']),
                use_container_width=True, hide_index=True
            )

        # Acciones según permisos
        _seccion("⚡", "Acciones")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            codigo_buscar = st.text_input("Buscar reserva por código", key="buscar_reserva_accion")
        
        if codigo_buscar:
            reserva = Reserva.get_by_codigo(codigo_buscar)
            if reserva:
                _card_info(f"✅ Reserva encontrada: <strong>{reserva['huesped_nombre']} {reserva['huesped_apellido']}</strong>", "success")
                
                # Mostrar acciones disponibles
                col_a, col_b, col_c = st.columns(3)
                
                with col_a:
                    if puede_editar:
                        if st.button("✏️ Editar Reserva", key=f"editar_{reserva['id']}", use_container_width=True):
                            st.session_state[f"show_edit_{reserva['id']}"] = not st.session_state.get(f"show_edit_{reserva['id']}", False)
                            # Cerrar otros expanders
                            st.session_state[f"show_cancel_{reserva['id']}"] = False
                            st.session_state[f"show_factura_{reserva['id']}"] = False
                            st.rerun()
                
                with col_b:
                    if puede_cancelar:
                        if st.button("❌ Cancelar Reserva", key=f"cancelar_{reserva['id']}", use_container_width=True):
                            st.session_state[f"show_cancel_{reserva['id']}"] = not st.session_state.get(f"show_cancel_{reserva['id']}", False)
                            # Cerrar otros expanders
                            st.session_state[f"show_edit_{reserva['id']}"] = False
                            st.session_state[f"show_factura_{reserva['id']}"] = False
                            st.rerun()
                
                with col_c:
                    if puede_ver_factura:
                        if st.button("🧾 Ver Factura", key=f"factura_{reserva['id']}", use_container_width=True):
                            st.session_state[f"show_factura_{reserva['id']}"] = not st.session_state.get(f"show_factura_{reserva['id']}", False)
                            # Cerrar otros expanders
                            st.session_state[f"show_edit_{reserva['id']}"] = False
                            st.session_state[f"show_cancel_{reserva['id']}"] = False
                            st.rerun()
                
                # ===== EDITAR RESERVA (CORREGIDO - AHORA ACTUALIZA BD Y REFRESCA TABLA) =====
                if st.session_state.get(f"show_edit_{reserva['id']}", False):
                    with st.expander(f"✏️ Editar reserva {reserva['codigo_reserva']}", expanded=True):
                        with st.form(f"form_editar_{reserva['id']}"):
                            col1, col2 = st.columns(2)
                            with col1:
                                nueva_fecha_in = st.date_input(
                                    "Nueva fecha check-in", 
                                    value=reserva['fecha_check_in'],
                                    min_value=date.today(),
                                    key=f"edit_in_{reserva['id']}"
                                )
                                nuevos_adultos = st.number_input(
                                    "Adultos", 
                                    min_value=1, 
                                    value=reserva['numero_adultos'],
                                    key=f"edit_adultos_{reserva['id']}"
                                )
                            with col2:
                                nueva_fecha_out = st.date_input(
                                    "Nueva fecha check-out", 
                                    value=reserva['fecha_check_out'],
                                    min_value=nueva_fecha_in + timedelta(days=1),
                                    key=f"edit_out_{reserva['id']}"
                                )
                                nuevos_ninos = st.number_input(
                                    "Niños", 
                                    min_value=0, 
                                    value=reserva['numero_ninos'],
                                    key=f"edit_ninos_{reserva['id']}"
                                )
                            
                            motivo_edicion = st.text_area("Motivo de la modificación", key=f"motivo_edit_{reserva['id']}")
                            
                            # CORRECCIÓN: Convertir Decimal a float
                            dias = (nueva_fecha_out - nueva_fecha_in).days
                            tarifa_original = float(reserva['tarifa_total']) if hasattr(reserva['tarifa_total'], 'item') else float(reserva['tarifa_total'])
                            nueva_tarifa = tarifa_original  # Simplificado
                            
                            st.info(f"Tarifa original: S/ {tarifa_original:,.2f} | Nueva tarifa estimada: S/ {nueva_tarifa:,.2f}")
                            
                            # Columnas para botones
                            _, col_confirm, _ = st.columns([1, 4, 1])
                            with col_confirm:
                                confirmar = st.form_submit_button("✅ Confirmar cambios", type="primary", use_container_width=True)
                            
                            if confirmar:
                                if not motivo_edicion:
                                    st.error("Debes ingresar un motivo para la modificación")
                                else:
                                    # ===== VERIFICAR DISPONIBILIDAD ANTES DE ACTUALIZAR =====
                                    with db.get_cursor() as cursor:
                                        cursor.execute("""
                                            SELECT verificar_disponibilidad(%s, %s, %s, %s) as disponible
                                        """, (reserva['habitacion_id'], nueva_fecha_in, nueva_fecha_out, reserva['id']))
                                        result = cursor.fetchone()
                                        
                                        if not result['disponible']:
                                            st.error("❌ La habitación no está disponible para las nuevas fechas seleccionadas")
                                            st.stop()
                                    
                                    # ===== ACTUALIZACIÓN REAL EN BD =====
                                    try:
                                        with db.get_cursor() as cursor:
                                            cursor.execute("""
                                                UPDATE reservas 
                                                SET fecha_check_in = %s,
                                                    fecha_check_out = %s,
                                                    numero_adultos = %s,
                                                    numero_ninos = %s,
                                                    notas = %s,
                                                    updated_at = CURRENT_TIMESTAMP
                                                WHERE id = %s
                                                RETURNING id
                                            """, (nueva_fecha_in, nueva_fecha_out, nuevos_adultos, nuevos_ninos, 
                                                  motivo_edicion, reserva['id']))
                                            
                                            # Registrar en historial
                                            cursor.execute("""
                                                INSERT INTO historial_estados_reserva 
                                                (reserva_id, estado_anterior, estado_nuevo, usuario_id, motivo)
                                                VALUES (%s, %s, %s, %s, %s)
                                            """, (reserva['id'], reserva['estado'], reserva['estado'], 
                                                  st.session_state.user['id'], motivo_edicion))
                                            
                                            st.success("✅ Reserva modificada exitosamente")
                                            st.info(f"Cambios guardados: {nuevos_adultos} adultos, {nuevos_ninos} niños")
                                            
                                            # ===== LIMPIAR ESTADO Y FORZAR RECARGA DE DATOS =====
                                            st.session_state[f"show_edit_{reserva['id']}"] = False
                                            
                                            # 👇 FORZAR RECARGA DE LA TABLA
                                            st.session_state.reservas_activas_cache = None
                                            
                                            st.rerun()
                                    except Exception as e:
                                        st.error(f"Error al actualizar: {str(e)}")
                
                # ===== CANCELAR RESERVA =====
                if st.session_state.get(f"show_cancel_{reserva['id']}", False):
                    with st.expander(f"❌ Cancelar reserva {reserva['codigo_reserva']}", expanded=True):
                        with st.form(f"form_cancelar_{reserva['id']}"):
                            motivo = st.text_area("Motivo de cancelación", key=f"motivo_{reserva['id']}")
                            
                            # Solo admin/gerente ven opción de reembolso
                            aplicar_reembolso = False
                            if perm_checker.can(Permission.BOOKING_CANCEL_REFUND):
                                aplicar_reembolso = st.checkbox("Aplicar reembolso", key=f"reembolso_{reserva['id']}")
                            
                            # Columnas con proporciones
                            _, col_confirm, _ = st.columns([1, 4, 1])
                            with col_confirm:
                                confirmar = st.form_submit_button("✅ Confirmar cancelación", type="primary", use_container_width=True)
                            
                            if confirmar:
                                if not motivo:
                                    st.error("Debes ingresar un motivo de cancelación")
                                else:
                                    resultado = ReservaController.cancelar_reserva(
                                        reserva['id'], 
                                        motivo,
                                        st.session_state.user['id'],
                                        aplicar_reembolso
                                    )
                                    if resultado['success']:
                                        st.success("✅ Reserva cancelada exitosamente")
                                        st.balloons()
                                        st.session_state[f"show_cancel_{reserva['id']}"] = False
                                        # Forzar recarga de la tabla
                                        st.session_state.reservas_activas_cache = None
                                        st.rerun()
                                    else:
                                        st.error(f"Error: {resultado['error']}")
                
                # ===== VER FACTURA (CORREGIDO - AHORA SE ACTUALIZA DESPUÉS DE CREAR) =====
                if st.session_state.get(f"show_factura_{reserva['id']}", False):
                    with st.expander(f"🧾 Factura de {reserva['codigo_reserva']}", expanded=True):
                        # Buscar factura existente - SIEMPRE CONSULTA FRESCA
                        with db.get_cursor() as cursor:
                            cursor.execute("""
                                SELECT f.*, df.concepto, df.cantidad, df.precio_unitario, df.importe, df.tipo,
                                       h.nombre as huesped_nombre, h.apellido as huesped_apellido,
                                       h.numero_documento as huesped_documento
                                FROM facturas f
                                LEFT JOIN detalle_factura df ON f.id = df.factura_id
                                JOIN huespedes h ON f.huesped_id = h.id
                                WHERE f.reserva_id = %s
                                ORDER BY f.id, df.id
                            """, (reserva['id'],))
                            facturas_data = cursor.fetchall()
                        
                        if facturas_data:
                            # Mostrar factura existente
                            factura = facturas_data[0]
                            
                            # Información de la factura
                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown(f"**Número:** {factura['numero_factura']}")
                                st.markdown(f"**Fecha emisión:** {pd.to_datetime(factura['fecha_emision']).strftime('%d/%m/%Y %H:%M')}")
                                st.markdown(f"**Estado:** {factura['estado'].upper()}")
                            with col2:
                                st.markdown(f"**Huésped:** {factura['huesped_nombre']} {factura['huesped_apellido']}")
                                st.markdown(f"**Documento:** {factura['huesped_documento']}")
                                if factura.get('metodo_pago'):
                                    st.markdown(f"**Método pago:** {factura['metodo_pago'].capitalize()}")
                            
                            st.markdown("---")
                            st.markdown("**DETALLE**")
                            
                            # Crear tabla de detalle
                            detalle_items = []
                            for item in facturas_data:
                                if item.get('concepto'):
                                    detalle_items.append({
                                        'Concepto': item['concepto'],
                                        'Cantidad': item['cantidad'],
                                        'P. Unitario': f"S/ {float(item['precio_unitario']):,.2f}",
                                        'Importe': f"S/ {float(item['importe']):,.2f}"
                                    })
                            
                            if detalle_items:
                                df_detalle = pd.DataFrame(detalle_items)
                                st.dataframe(df_detalle, use_container_width=True, hide_index=True)
                            
                            # Mostrar totales
                            col_t1, col_t2, col_t3 = st.columns(3)
                            with col_t1:
                                st.metric("Subtotal", f"S/ {float(factura['subtotal']):,.2f}")
                            with col_t2:
                                st.metric("Impuestos", f"S/ {float(factura['impuestos']):,.2f}")
                            with col_t3:
                                st.metric("TOTAL", f"S/ {float(factura['total']):,.2f}")
                            
                            # Botón para generar PDF
                            col_pdf, col_close = st.columns(2)
                            with col_pdf:
                                if st.button("📄 Generar Factura PDF", key=f"pdf_{reserva['id']}", use_container_width=True):
                                    with st.spinner("Generando PDF..."):
                                        pdf = PDFGenerator()
                                        
                                        # Preparar datos para el PDF
                                        factura_data = {
                                            'numero_factura': factura['numero_factura'],
                                            'fecha_emision': factura['fecha_emision'],
                                            'huesped_nombre': factura['huesped_nombre'],
                                            'huesped_apellido': factura['huesped_apellido'],
                                            'huesped_documento': factura['huesped_documento'],
                                            'reserva_id': reserva['id'],
                                            'codigo_reserva': reserva['codigo_reserva'],
                                            'subtotal': float(factura['subtotal']),
                                            'impuestos': float(factura['impuestos']),
                                            'total': float(factura['total']),
                                            'metodo_pago': factura.get('metodo_pago'),
                                            'notas': factura.get('notas')
                                        }
                                        
                                        # Detalle items
                                        detalle_items_pdf = []
                                        for item in facturas_data:
                                            if item.get('concepto'):
                                                detalle_items_pdf.append({
                                                    'concepto': item['concepto'],
                                                    'cantidad': item['cantidad'],
                                                    'precio_unitario': float(item['precio_unitario']),
                                                    'importe': float(item['importe'])
                                                })
                                        
                                        pdf.create_invoice_pdf(factura_data, detalle_items_pdf)
                                        pdf_data = _get_pdf_data(pdf)
                                        
                                        st.download_button(
                                            "📥 Descargar Factura PDF", 
                                            data=pdf_data,
                                            file_name=f"factura_{factura['numero_factura']}.pdf",
                                            mime="application/pdf",
                                            key=f"download_{reserva['id']}"
                                        )
                            with col_close:
                                if st.button("❌ Cerrar", key=f"close_factura_{reserva['id']}", use_container_width=True):
                                    st.session_state[f"show_factura_{reserva['id']}"] = False
                                    st.rerun()
                        else:
                            # No hay factura, opción para crear una
                            st.info("No hay factura asociada a esta reserva")
                            
                            # CORRECCIÓN: Convertir Decimal a float
                            dias = (reserva['fecha_check_out'] - reserva['fecha_check_in']).days
                            subtotal = float(reserva['tarifa_total']) if hasattr(reserva['tarifa_total'], 'item') else float(reserva['tarifa_total'])
                            impuestos = subtotal * 0.18
                            total = subtotal + impuestos
                            
                            with st.form(f"form_crear_factura_{reserva['id']}"):
                                st.markdown("**Crear nueva factura**")
                                
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.markdown(f"**Subtotal:** S/ {subtotal:,.2f}")
                                    st.markdown(f"**Días:** {dias}")
                                with col2:
                                    st.markdown(f"**Impuestos (18%):** S/ {impuestos:,.2f}")
                                    st.markdown(f"**TOTAL:** S/ {total:,.2f}")
                                
                                metodo_pago = st.selectbox(
                                    "Método de pago",
                                    options=["", "efectivo", "tarjeta", "transferencia"],
                                    key=f"metodo_pago_{reserva['id']}"
                                )
                                
                                _, col_crear, _ = st.columns([1, 4, 1])
                                with col_crear:
                                    crear = st.form_submit_button("✅ Crear Factura", type="primary", use_container_width=True)
                                
                                if crear:
                                    # Insertar nueva factura
                                    with db.get_cursor() as cursor:
                                        # Generar número de factura
                                        cursor.execute("SELECT nextval('facturas_numero_seq')")
                                        factura_id = cursor.fetchone()['nextval']
                                        numero = f"FAC-{datetime.now().strftime('%Y%m%d')}-{factura_id}"
                                        
                                        cursor.execute("""
                                            INSERT INTO facturas 
                                            (numero_factura, huesped_id, reserva_id, fecha_emision,
                                             subtotal, impuestos, total, estado, metodo_pago)
                                            VALUES (%s, %s, %s, CURRENT_TIMESTAMP, %s, %s, %s, %s, %s)
                                            RETURNING id
                                        """, (numero, reserva['huesped_id'], reserva['id'],
                                              subtotal, impuestos, total,
                                              'pagada' if metodo_pago else 'pendiente',
                                              metodo_pago if metodo_pago else None))
                                        
                                        factura_id = cursor.fetchone()['id']
                                        
                                        # Insertar detalle
                                        cursor.execute("""
                                            INSERT INTO detalle_factura 
                                            (factura_id, concepto, cantidad, precio_unitario, importe, tipo)
                                            VALUES (%s, %s, %s, %s, %s, %s)
                                        """, (factura_id, 
                                              f"Alojamiento - {dias} noches - Hab {reserva['habitacion_numero']}", 
                                              1, subtotal, subtotal, 'alojamiento'))
                                        
                                        st.success(f"✅ Factura {numero} creada correctamente")
                                        
                                        # ===== CORRECCIÓN IMPORTANTE =====
                                        # Cerrar el expander actual y forzar recarga
                                        st.session_state[f"show_factura_{reserva['id']}"] = False
                                        # Pequeña pausa para asegurar que la BD se actualice
                                        time.sleep(0.5)
                                        st.rerun()
            else:
                _card_info("⚠️ Reserva no encontrada", "warning")
    else:
        _card_info("📭 No hay reservas activas en este momento", "info")


# =============================================================================
# FUNCIÓN: Mostrar huéspedes alojados actualmente
# =============================================================================
def mostrar_alojados_ahora():
    """Muestra los huéspedes que están actualmente en el hotel"""
    _seccion("🏨", "Huéspedes Alojados Ahora")
    
    # Obtener huéspedes alojados
    alojados = Reserva.get_alojados_ahora()
    
    if alojados:
        df = pd.DataFrame(alojados)
        
        # Formatear fechas
        df['fecha_check_in'] = pd.to_datetime(df['fecha_check_in']).dt.strftime('%d/%m/%Y %H:%M')
        df['fecha_check_out_estimado'] = pd.to_datetime(df['fecha_check_out']).dt.strftime('%d/%m/%Y')
        
        # Preparar columnas para mostrar
        df_display = df[['codigo_reserva', 'huesped_nombre', 'huesped_apellido',
                         'habitacion_numero', 'fecha_check_in', 'fecha_check_out_estimado']].copy()
        df_display.columns = ['Código', 'Nombre', 'Apellido', 'Habitación', 
                              'Check-in (real)', 'Check-out (estimado)']
        
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        
        # Estadísticas
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total huéspedes alojados", len(alojados))
        with col2:
            # Habitaciones ocupadas únicas
            habitaciones_ocupadas = df['habitacion_id'].nunique() if 'habitacion_id' in df.columns else len(alojados)
            st.metric("Habitaciones ocupadas", habitaciones_ocupadas)
        with col3:
            # Próximos check-outs (mañana)
            manana = date.today() + timedelta(days=1)
            prox_checkouts = df[pd.to_datetime(df['fecha_check_out']).dt.date == manana].shape[0] if 'fecha_check_out' in df.columns else 0
            st.metric("Check-outs mañana", prox_checkouts)
        
        # Opción para hacer check-out rápido
        _seccion("⚡", "Check-out Rápido")
        
        # Crear lista de opciones para el selectbox
        opciones_checkout = []
        for _, row in df.iterrows():
            opciones_checkout.append(
                f"{row['codigo_reserva']} - {row['huesped_nombre']} {row['huesped_apellido']} (Hab {row['habitacion_numero']})"
            )
        
        if opciones_checkout:
            col_sel, col_btn = st.columns([3, 1])
            with col_sel:
                seleccion = st.selectbox("Seleccionar huésped para check-out", opciones_checkout, key="checkout_rapido_sel")
            
            with col_btn:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🔴 Procesar Check-out", type="primary", use_container_width=True):
                    # Extraer código de reserva
                    codigo = seleccion.split(" - ")[0]
                    
                    # Buscar la reserva
                    reserva = Reserva.get_by_codigo(codigo)
                    if reserva:
                        # Guardar en sesión para mostrar el expander
                        st.session_state[f"show_checkout_{reserva['id']}"] = True
                        st.rerun()
            
            # Mostrar formulario de check-out si se seleccionó
            for _, row in df.iterrows():
                if st.session_state.get(f"show_checkout_{row['id']}", False):
                    with st.expander(f"🔴 Check-out: {row['codigo_reserva']} - {row['huesped_nombre']} {row['huesped_apellido']}", expanded=True):
                        with st.form(f"form_checkout_rapido_{row['id']}"):
                            st.markdown(f"**Habitación:** {row['habitacion_numero']}")
                            st.markdown(f"**Check-in:** {row['fecha_check_in']}")
                            st.markdown(f"**Check-out estimado:** {row['fecha_check_out_estimado']}")
                            
                            observaciones = st.text_area("Observaciones del check-out", key=f"obs_{row['id']}")
                            
                            # Opciones de descuento según permisos
                            perm_checker = st.session_state.permission_checker
                            if perm_checker.can(Permission.INVOICE_DISCOUNT):
                                aplicar_descuento = st.checkbox("Aplicar descuento", key=f"desc_{row['id']}")
                                if aplicar_descuento:
                                    max_descuento = 20 if not perm_checker.can(Permission.INVOICE_DISCOUNT_HIGH) else 50
                                    descuento = st.slider("Porcentaje de descuento", 0, max_descuento, 0, key=f"desc_slider_{row['id']}")
                            
                            col_conf, col_canc = st.columns(2)
                            with col_conf:
                                confirmar = st.form_submit_button("✅ Confirmar Check-out", type="primary", use_container_width=True)
                            with col_canc:
                                cancelar = st.form_submit_button("❌ Cancelar", use_container_width=True)
                            
                            if confirmar:
                                resultado = ReservaController.check_out(
                                    row['id'],
                                    row['habitacion_id'],
                                    st.session_state.user['id'],
                                    observaciones if observaciones else None
                                )
                                if resultado['success']:
                                    st.success("✅ Check-out realizado exitosamente")
                                    st.balloons()
                                    st.session_state[f"show_checkout_{row['id']}"] = False
                                    st.rerun()
                                else:
                                    st.error(resultado['error'])
                            
                            if cancelar:
                                st.session_state[f"show_checkout_{row['id']}"] = False
                                st.rerun()
    else:
        _card_info("🏨 No hay huéspedes alojados en este momento", "info")


def mostrar_check_in_out():
    _seccion("✅", "Check-in / Check-out")
    
    perm_checker = st.session_state.permission_checker
    puede_checkin = perm_checker.can(Permission.BOOKING_EDIT)
    puede_checkout = perm_checker.can(Permission.BOOKING_EDIT)

    if not puede_checkin and not puede_checkout:
        _card_info("⛔ No tienes permisos para realizar check-in/check-out", "danger")
        return

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            f'<div style="background:{C["card_bg"]}; border:1px solid {C["border"]}; '
            f'border-radius:14px; padding:1.5rem; margin-bottom:1rem;">'
            f'<div style="color:{C["accent"]}; font-weight:700; font-size:1rem; margin-bottom:1rem;">🟢 Check-in</div>',
            unsafe_allow_html=True
        )
        
        if puede_checkin:
            # Usar contador para limpiar input
            checkin_key = f"checkin_codigo_{st.session_state.checkin_counter}"
            
            with st.form("form_checkin"):
                codigo_reserva = st.text_input("Código de reserva", key=checkin_key)
                submitted = st.form_submit_button("Procesar Check-in", type="primary", use_container_width=True)

                if submitted and codigo_reserva:
                    reserva = Reserva.get_by_codigo(codigo_reserva)
                    if reserva:
                        if reserva['estado'] == 'confirmada':
                            resultado = ReservaController.check_in(
                                reserva['id'], reserva['habitacion_id'], st.session_state.user['id']
                            )
                            if resultado['success']:
                                st.success("✅ Check-in realizado exitosamente")
                                st.session_state.checkin_counter += 1
                                # Limpiar caché de reservas activas
                                st.session_state.reservas_activas_cache = None
                                st.rerun()
                            else:
                                st.error(resultado['error'])
                        else:
                            st.warning(f"La reserva no está en estado confirmada")
                    else:
                        st.error("Reserva no encontrada")
        else:
            _card_info("⛔ No tienes permiso para realizar check-in", "danger")
        
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown(
            f'<div style="background:{C["card_bg"]}; border:1px solid {C["border"]}; '
            f'border-radius:14px; padding:1.5rem; margin-bottom:1rem;">'
            f'<div style="color:{C["warning"]}; font-weight:700; font-size:1rem; margin-bottom:1rem;">🔴 Check-out</div>',
            unsafe_allow_html=True
        )
        
        if puede_checkout:
            checkout_key = f"checkout_codigo_{st.session_state.checkout_counter}"
            
            with st.form("form_checkout"):
                codigo_reserva_out = st.text_input("Código de reserva", key=checkout_key)
                
                if perm_checker.can(Permission.INVOICE_DISCOUNT):
                    aplicar_descuento = st.checkbox("Aplicar descuento", key="aplicar_descuento")
                    if aplicar_descuento:
                        max_descuento = 20 if not perm_checker.can(Permission.INVOICE_DISCOUNT_HIGH) else 50
                        descuento = st.slider("Porcentaje de descuento", 0, max_descuento, 0, key="descuento_slider")
                
                observaciones = st.text_area("Observaciones", key="checkout_obs")
                submitted_out = st.form_submit_button("Procesar Check-out", type="primary", use_container_width=True)

                if submitted_out and codigo_reserva_out:
                    reserva = Reserva.get_by_codigo(codigo_reserva_out)
                    if reserva:
                        with db.get_cursor() as cursor:
                            cursor.execute("SELECT * FROM alojamientos WHERE reserva_id = %s", (reserva['id'],))
                            alojamiento = cursor.fetchone()

                        if alojamiento:
                            if not alojamiento.get('fecha_check_out'):
                                resultado = ReservaController.check_out(
                                    reserva['id'], reserva['habitacion_id'],
                                    st.session_state.user['id'],
                                    observaciones if observaciones else None
                                )
                                if resultado['success']:
                                    st.success("✅ Check-out realizado exitosamente")
                                    st.info("Habitación liberada")
                                    st.session_state.checkout_counter += 1
                                    # Limpiar caché de reservas activas
                                    st.session_state.reservas_activas_cache = None
                                    st.rerun()
                                else:
                                    st.error(resultado['error'])
                            else:
                                st.warning("Check-out ya realizado")
                        else:
                            st.error("No se encontró check-in")
                    else:
                        st.error("Reserva no encontrada")
        else:
            _card_info("⛔ No tienes permiso para realizar check-out", "danger")
        
        st.markdown("</div>", unsafe_allow_html=True)


def mostrar_registro_huesped():
    _seccion("👤", "Registrar Nuevo Huésped")
    
    perm_checker = st.session_state.permission_checker
    puede_crear = perm_checker.can(Permission.USER_CREATE)

    if not puede_crear:
        _card_info("⛔ No tienes permisos para registrar nuevos huéspedes", "danger")
        return

    # Sistema de limpieza
    if 'huesped_counter' not in st.session_state:
        st.session_state.huesped_counter = 0
    
    form_key = f"form_huesped_{st.session_state.huesped_counter}"

    st.markdown(
        f'<div style="background:{C["card_bg"]}; border:1px solid {C["border"]}; '
        f'border-radius:14px; padding:1.5rem;">',
        unsafe_allow_html=True
    )

    with st.form(form_key):
        st.markdown("### 📋 Datos Personales")
        
        col1, col2 = st.columns(2)

        with col1:
            nombre = st.text_input("Nombres *", placeholder="Ej: Juan Carlos", key=f"nombre_{st.session_state.huesped_counter}")
            tipo_documento = st.selectbox("Tipo de Documento *", options=["DNI", "Pasaporte", "Carné de Extranjería", "Otro"], key=f"tipo_doc_{st.session_state.huesped_counter}")
            numero_documento = st.text_input("Número de Documento *", placeholder="Ej: 12345678", key=f"num_doc_{st.session_state.huesped_counter}")
            fecha_nacimiento = st.date_input("Fecha de Nacimiento", max_value=date.today(), min_value=date(1900, 1, 1), value=date(1980, 1, 1), key=f"fecha_nac_{st.session_state.huesped_counter}")

        with col2:
            apellido = st.text_input("Apellidos *", placeholder="Ej: Pérez Gómez", key=f"apellido_{st.session_state.huesped_counter}")
            nacionalidad = st.selectbox("Nacionalidad *", options=["Peruana", "Argentina", "Boliviana", "Brasileña", "Chilena", "Colombiana", "Ecuatoriana", "Española", "Estadounidense", "Mexicana", "Otro"], index=0, key=f"nacionalidad_{st.session_state.huesped_counter}")
            email = st.text_input("Correo Electrónico", placeholder="ejemplo@correo.com", key=f"email_{st.session_state.huesped_counter}")
            telefono = st.text_input("Teléfono / Celular *", placeholder="Ej: 987654321", key=f"telefono_{st.session_state.huesped_counter}")

        st.markdown("---")
        st.markdown("### 🌍 Lugar de Origen")
        
        col3, col4 = st.columns(2)

        with col3:
            pais_origen = st.selectbox("País de Origen *", options=["Perú", "Argentina", "Bolivia", "Brasil", "Chile", "Colombia", "Ecuador", "España", "Estados Unidos", "México", "Otro"], index=0, key=f"pais_{st.session_state.huesped_counter}")
            ciudad_origen = st.text_input("Ciudad de Origen *", placeholder="Ej: Lima, Arequipa, Buenos Aires...", key=f"ciudad_{st.session_state.huesped_counter}")

        with col4:
            direccion = st.text_input("Dirección (calle y número)", placeholder="Ej: Av. Arequipa 123", key=f"direccion_{st.session_state.huesped_counter}")
            
            distrito = None
            if pais_origen == "Perú":
                distrito = st.text_input("Distrito (opcional)", placeholder="Ej: Miraflores, Wanchaq...", key=f"distrito_{st.session_state.huesped_counter}")
            else:
                st.info("Para otros países, el distrito no es necesario.")
            
            codigo_postal = st.text_input("Código Postal (opcional)", placeholder="Ej: 15074", key=f"cp_{st.session_state.huesped_counter}")

        st.markdown("---")
        st.markdown("### 💬 Información Adicional")
        
        preferencias = st.text_area("Preferencias / Observaciones", placeholder="Ej: Alergias, preferencias de habitación...", key=f"preferencias_{st.session_state.huesped_counter}")

        acepta_terminos = st.checkbox("Confirmo que los datos ingresados son correctos", key=f"terminos_{st.session_state.huesped_counter}")

        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            submitted = st.form_submit_button("💾 Registrar Huésped", type="primary", use_container_width=True)

        if submitted:
            errores = []
            if not nombre:
                errores.append("Nombres")
            if not apellido:
                errores.append("Apellidos")
            if not numero_documento:
                errores.append("Número de Documento")
            if not telefono:
                errores.append("Teléfono")
            if not ciudad_origen:
                errores.append("Ciudad de Origen")
            
            if errores:
                st.error(f"❌ Campos obligatorios: {', '.join(errores)}")
            elif not acepta_terminos:
                st.error("❌ Debes confirmar que los datos son correctos")
            else:
                datos_huesped = {
                    'nombre': nombre, 'apellido': apellido,
                    'tipo_documento': tipo_documento, 'numero_documento': numero_documento,
                    'fecha_nacimiento': fecha_nacimiento, 'nacionalidad': nacionalidad,
                    'email': email if email else None, 'telefono': telefono,
                    'pais_origen': pais_origen, 'ciudad_origen': ciudad_origen,
                    'direccion': direccion if direccion else None,
                    'distrito': distrito if distrito else None,
                    'codigo_postal': codigo_postal if codigo_postal else None,
                    'preferencias': preferencias if preferencias else None
                }
                
                resultado = HuespedController.crear_huesped(datos_huesped)
                
                if resultado['success']:
                    st.success("✅ Huésped registrado exitosamente")
                    st.balloons()
                    st.session_state.huesped_counter += 1
                    st.rerun()
                else:
                    st.error(f"Error: {resultado['error']}")

    st.markdown("</div>", unsafe_allow_html=True)