import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, date
from config.database import db
from utils.permissions import Permission

# ── Paleta consistente con el sidebar ──────────────────────────────────────────
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

PLOTLY_LAYOUT = dict(
    paper_bgcolor='#1a2744',
    plot_bgcolor='#1e2f54',
    font=dict(color='#E2E8F0', family='Inter, sans-serif'),
    title_font=dict(color='#A8D8EA', size=14),
    xaxis=dict(
        gridcolor='rgba(157,180,199,0.15)',
        linecolor='rgba(157,180,199,0.3)',
        tickfont=dict(color='#9DB4C7'),
        title_font=dict(color='#9DB4C7'),
    ),
    yaxis=dict(
        gridcolor='rgba(157,180,199,0.15)',
        linecolor='rgba(157,180,199,0.3)',
        tickfont=dict(color='#9DB4C7'),
        title_font=dict(color='#9DB4C7'),
    ),
    legend=dict(
        bgcolor='rgba(255,255,255,0.05)',
        bordercolor='rgba(157,180,199,0.2)',
        font=dict(color='#E2E8F0'),
    ),
    margin=dict(l=16, r=16, t=40, b=16),
)


def _card(contenido_html: str) -> None:
    st.markdown(
        f'<div style="background:{C["card_bg"]}; border:1px solid {C["border"]}; '
        f'border-radius:14px; padding:1.25rem 1.5rem; margin-bottom:0.5rem;">'
        f'{contenido_html}</div>',
        unsafe_allow_html=True
    )


def _seccion(emoji: str, titulo: str) -> None:
    st.markdown(
        f'<div style="display:flex; align-items:center; gap:0.6rem; margin:1.5rem 0 0.75rem;">'
        f'<span style="font-size:1.25rem;">{emoji}</span>'
        f'<span style="font-size:1.05rem; font-weight:700; color:{C["accent"]}; letter-spacing:0.02em;">{titulo}</span>'
        f'</div>',
        unsafe_allow_html=True
    )


def _metrica(label: str, valor: str, delta: str = "", delta_ok: bool = True) -> None:
    delta_html = ""
    if delta:
        color = C['success'] if delta_ok else C['danger']
        arrow = "▲" if delta_ok else "▼"
        delta_html = (
            f'<div style="font-size:0.78rem; color:{color}; margin-top:0.2rem; font-weight:600;">'
            f'{arrow} {delta}</div>'
        )
    st.markdown(
        f'<div style="background:{C["card_bg"]}; border:1px solid {C["border"]}; '
        f'border-radius:12px; padding:1.1rem 1.25rem;">'
        f'<div style="font-size:0.72rem; font-weight:600; color:{C["muted"]}; '
        f'text-transform:uppercase; letter-spacing:0.08em; margin-bottom:0.4rem;">{label}</div>'
        f'<div style="font-size:1.6rem; font-weight:700; color:{C["text"]}; line-height:1.1;">{valor}</div>'
        f'{delta_html}'
        f'</div>',
        unsafe_allow_html=True
    )


def _get_ocupacion_hoy() -> dict:
    """Devuelve ocupadas, total y porcentaje de ocupación actual."""
    with db.get_cursor() as cursor:
        cursor.execute("""
            SELECT
                COUNT(DISTINCT CASE
                    WHEN r.fecha_check_in <= CURRENT_DATE
                    AND r.fecha_check_out > CURRENT_DATE
                    THEN r.habitacion_id
                END) as ocupadas_hoy,
                COUNT(h.id) as total_habitaciones
            FROM habitaciones h
            LEFT JOIN reservas r ON h.id = r.habitacion_id
                AND r.estado IN ('confirmada', 'completada')
                AND r.fecha_check_in <= CURRENT_DATE
                AND r.fecha_check_out > CURRENT_DATE
            WHERE h.activa = true
        """)
        result = cursor.fetchone()
    ocupadas  = result['ocupadas_hoy'] or 0
    total     = result['total_habitaciones'] or 1
    porcentaje = (ocupadas / total * 100)
    return {'ocupadas': ocupadas, 'total': total, 'porcentaje': porcentaje}


def _get_reservas_futuras() -> int:
    """Reservas confirmadas con check-in en el futuro."""
    with db.get_cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*) as total FROM reservas
            WHERE estado = 'confirmada' AND fecha_check_in > CURRENT_DATE
        """)
        return cursor.fetchone()['total']


def show():
    perm_checker = st.session_state.get('permission_checker', None)
    if not perm_checker:
        st.error("Error de permisos")
        return

    st.markdown(f"""
    <style>
    .stApp {{ background-color: #0d1b36; }}

    [data-testid="stSidebar"] {{ background-color: #1a2744 !important; }}
    [data-testid="stSidebar"] * {{ color: #ffffff !important; }}
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

    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] li {{ color: {C['text']} !important; }}

    [data-testid="stInfo"] {{
        background: rgba(91,141,184,0.12) !important;
        border: 1px solid rgba(91,141,184,0.3) !important;
        border-radius: 10px !important;
        color: {C['text']} !important;
    }}
    [data-testid="stInfo"] * {{ color: {C['text']} !important; }}

    [data-testid="stDataFrame"] {{
        border: 1px solid {C['border']} !important;
        border-radius: 12px !important;
        overflow: hidden;
    }}

    .stPlotlyChart {{
        background: transparent !important;
        border-radius: 14px !important;
        border: 1px solid {C['border']} !important;
        overflow: hidden;
    }}

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

    hr {{ border-color: {C['border']} !important; }}
    </style>
    """, unsafe_allow_html=True)

    st.markdown(
        f'<h2 style="color:{C["accent"]}; font-weight:700; margin-bottom:1.25rem; font-size:1.4rem;">'
        f'📊 Panel de Gestión Hotelera'
        f'<span class="permission-badge">{st.session_state.role.title()}</span></h2>',
        unsafe_allow_html=True
    )

    # ── Datos compartidos ──────────────────────────────────────────────────────
    ocup             = _get_ocupacion_hoy()
    reservas_futuras = _get_reservas_futuras()

    # ═══════════════════════════════════════════════════════════════════════════
    # KPIs PRINCIPALES
    # ═══════════════════════════════════════════════════════════════════════════
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        _metrica("Ocupación Hoy",
                 f"{ocup['ocupadas']}/{ocup['total']}",
                 f"{ocup['porcentaje']:.1f}%",
                 ocup['porcentaje'] > 50)

    with col2:
        if perm_checker.can(Permission.DASHBOARD_VIEW_KPI_ALL):
            with db.get_cursor() as cursor:
                cursor.execute("""
                    SELECT COALESCE(SUM(total), 0) as ingresos_hoy
                    FROM facturas
                    WHERE DATE(fecha_emision) = CURRENT_DATE AND estado = 'pagada'
                """)
                result = cursor.fetchone()
            _metrica("Ingresos Hoy", f"S/ {result['ingresos_hoy']:,.2f}")
        else:
            with db.get_cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) as total FROM alojamientos
                    WHERE DATE(fecha_check_in) = CURRENT_DATE
                """)
                result = cursor.fetchone()
            _metrica("Check-ins Hoy", str(result['total'] or 0))

    with col3:
        if perm_checker.can(Permission.DASHBOARD_VIEW_KPI_ALL):
            with db.get_cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) as total FROM alojamientos
                    WHERE DATE(fecha_check_in) = CURRENT_DATE
                """)
                result = cursor.fetchone()
            _metrica("Check-ins Hoy", str(result['total'] or 0))
        else:
            with db.get_cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) as total FROM alojamientos
                    WHERE DATE(fecha_check_out) = CURRENT_DATE
                """)
                result = cursor.fetchone()
            _metrica("Check-outs Hoy", str(result['total'] or 0))

    with col4:
        _metrica("Reservas Futuras", str(reservas_futuras))

    st.markdown("<div style='height:0.75rem;'></div>", unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════════════════════════
    # KPIs SECUNDARIOS
    # ═══════════════════════════════════════════════════════════════════════════
    col1, col2, col3 = st.columns(3)

    if perm_checker.can(Permission.DASHBOARD_VIEW_KPI_ALL):
        with col1:
            with db.get_cursor() as cursor:
                cursor.execute("""
                    SELECT COALESCE(AVG(fecha_check_out - fecha_check_in), 0) as estancia_promedio
                    FROM reservas
                    WHERE fecha_check_out >= CURRENT_DATE - INTERVAL '30 days'
                    AND estado = 'completada'
                """)
                result = cursor.fetchone()
            _metrica("Estancia Promedio", f"{float(result['estancia_promedio'] or 0):.1f} días")

        with col2:
            with db.get_cursor() as cursor:
                cursor.execute("""
                    WITH stats AS (
                        SELECT
                            (SELECT COUNT(*) FROM habitaciones WHERE activa = true) as total_hab,
                            COALESCE(SUM(total), 0) as ingresos,
                            EXTRACT(DAY FROM DATE_TRUNC('month', CURRENT_DATE + INTERVAL '1 month')
                                - DATE_TRUNC('month', CURRENT_DATE)) as dias_mes
                        FROM facturas
                        WHERE estado = 'pagada'
                        AND DATE_TRUNC('month', fecha_emision) = DATE_TRUNC('month', CURRENT_DATE)
                    )
                    SELECT ingresos / NULLIF(total_hab * dias_mes, 0) as revpar FROM stats
                """)
                result = cursor.fetchone()
            _metrica("RevPAR (Mes Actual)", f"S/ {float(result['revpar'] or 0):,.2f}")

        with col3:
            with db.get_cursor() as cursor:
                cursor.execute("""
                    SELECT COALESCE(SUM(total), 0) as ingresos_mes FROM facturas
                    WHERE estado = 'pagada'
                    AND DATE_TRUNC('month', fecha_emision) = DATE_TRUNC('month', CURRENT_DATE)
                """)
                result = cursor.fetchone()
            _metrica("Ingresos del Mes", f"S/ {result['ingresos_mes']:,.2f}")

    else:
        with col1:
            with db.get_cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) as total FROM alojamientos
                    WHERE DATE(fecha_check_in) = CURRENT_DATE
                """)
                result = cursor.fetchone()
            _metrica("Huéspedes Hoy", str(result['total'] or 0))

        with col2:
            with db.get_cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) as total FROM habitaciones
                    WHERE estado_id = (SELECT id FROM estados_habitacion WHERE nombre = 'disponible')
                    AND activa = true
                """)
                result = cursor.fetchone()
            _metrica("Habitaciones Libres", str(result['total'] or 0))

        with col3:
            with db.get_cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) as total FROM habitaciones
                    WHERE estado_id = (SELECT id FROM estados_habitacion WHERE nombre = 'mantenimiento')
                """)
                result = cursor.fetchone()
            _metrica("En Mantenimiento", str(result['total'] or 0))

    # ═══════════════════════════════════════════════════════════════════════════
    # GRÁFICOS
    # ═══════════════════════════════════════════════════════════════════════════
    st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        _seccion("📈", "Ocupación — Últimos 7 días")
        with db.get_cursor() as cursor:
            cursor.execute("""
                WITH fechas AS (
                    SELECT generate_series(
                        CURRENT_DATE - INTERVAL '6 days',
                        CURRENT_DATE, '1 day'::interval
                    )::date as fecha
                )
                SELECT f.fecha, COUNT(DISTINCT r.habitacion_id) as habitaciones_ocupadas
                FROM fechas f
                LEFT JOIN reservas r ON
                    r.fecha_check_in <= f.fecha AND r.fecha_check_out > f.fecha
                    AND r.estado IN ('confirmada', 'completada')
                GROUP BY f.fecha ORDER BY f.fecha
            """)
            datos = cursor.fetchall()

        df = pd.DataFrame(datos)
        if not df.empty:
            fig = px.line(df, x='fecha', y='habitaciones_ocupadas', markers=True,
                          color_discrete_sequence=[C['accent']])
            fig.update_traces(
                line=dict(width=2.5, color=C['accent']),
                marker=dict(size=8, color=C['primary'], line=dict(color=C['accent'], width=2)),
                fill='tozeroy',
                fillcolor='rgba(168,216,234,0.1)',
            )
            fig.update_layout(**PLOTLY_LAYOUT, height=320,
                              xaxis_title="Fecha", yaxis_title="Habitaciones",
                              showlegend=False, title="")
            st.plotly_chart(fig, use_container_width=True)
        else:
            _card(f'<p style="color:{C["muted"]}; text-align:center; padding:2rem 0;">Sin datos disponibles</p>')

    with col2:
        if perm_checker.can(Permission.REPORT_VIEW_FINANCIAL):
            _seccion("💰", "Ingresos por Tipo de Habitación")
            with db.get_cursor() as cursor:
                cursor.execute("""
                    SELECT th.nombre as tipo_habitacion, SUM(df.importe) as ingresos
                    FROM detalle_factura df
                    JOIN facturas f ON df.factura_id = f.id
                    JOIN reservas r ON f.reserva_id = r.id
                    JOIN habitaciones h ON r.habitacion_id = h.id
                    JOIN tipos_habitacion th ON h.tipo_habitacion_id = th.id
                    WHERE f.fecha_emision >= CURRENT_DATE - INTERVAL '30 days'
                    AND df.tipo = 'alojamiento'
                    GROUP BY th.nombre ORDER BY ingresos DESC
                """)
                datos = cursor.fetchall()

            if datos:
                df = pd.DataFrame(datos)
                fig = px.pie(df, values='ingresos', names='tipo_habitacion', hole=0.45,
                             color_discrete_sequence=['#5B8DB8','#A8D8EA','#9DB4C7',
                                                      '#68D391','#F6AD55','#FC8181'])
                fig.update_traces(
                    textposition='inside', textinfo='percent+label',
                    textfont=dict(color='white', size=12),
                    marker=dict(line=dict(color=C['dark'], width=2)),
                )
                fig.update_layout(**PLOTLY_LAYOUT, height=320, showlegend=True, title="")
                st.plotly_chart(fig, use_container_width=True)
            else:
                _card(f'<p style="color:{C["muted"]}; text-align:center; padding:2rem 0;">Sin datos del último mes</p>')

        else:
            _seccion("✅", "Check-ins por Día")
            with db.get_cursor() as cursor:
                cursor.execute("""
                    WITH fechas AS (
                        SELECT generate_series(
                            CURRENT_DATE - INTERVAL '6 days',
                            CURRENT_DATE, '1 day'::interval
                        )::date as fecha
                    )
                    SELECT f.fecha, COUNT(a.id) as check_ins
                    FROM fechas f
                    LEFT JOIN alojamientos a ON DATE(a.fecha_check_in) = f.fecha
                    GROUP BY f.fecha ORDER BY f.fecha
                """)
                datos = cursor.fetchall()

            if datos:
                df = pd.DataFrame(datos)
                fig = px.bar(df, x='fecha', y='check_ins',
                             color_discrete_sequence=[C['success']])
                fig.update_traces(
                    marker=dict(color=C['success'], line=dict(color=C['accent'], width=1))
                )
                fig.update_layout(**PLOTLY_LAYOUT, height=320,
                                  xaxis_title="Fecha", yaxis_title="Check-ins",
                                  showlegend=False, title="")
                st.plotly_chart(fig, use_container_width=True)
            else:
                _card(f'<p style="color:{C["muted"]}; text-align:center; padding:2rem 0;">Sin datos disponibles</p>')

    # ═══════════════════════════════════════════════════════════════════════════
    # PRÓXIMOS CHECK-INS
    # ═══════════════════════════════════════════════════════════════════════════
    _seccion("📅", "Próximos Check-ins — 7 días")

    with db.get_cursor() as cursor:
        cursor.execute("""
            SELECT
                r.codigo_reserva,
                h.nombre || ' ' || h.apellido as huesped,
                r.fecha_check_in,
                r.fecha_check_out,
                hab.numero as habitacion,
                (r.fecha_check_out - r.fecha_check_in) as noches
            FROM reservas r
            JOIN huespedes h ON r.huesped_id = h.id
            JOIN habitaciones hab ON r.habitacion_id = hab.id
            WHERE r.fecha_check_in BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '7 days'
            AND r.estado = 'confirmada'
            ORDER BY r.fecha_check_in
        """)
        proximos = cursor.fetchall()

    if proximos:
        df = pd.DataFrame(proximos)
        df['fecha_check_in']  = pd.to_datetime(df['fecha_check_in']).dt.strftime('%d/%m/%Y')
        df['fecha_check_out'] = pd.to_datetime(df['fecha_check_out']).dt.strftime('%d/%m/%Y')
        st.dataframe(df, use_container_width=True, hide_index=True,
            column_config={
                "codigo_reserva": "Código",
                "huesped":        "Huésped",
                "fecha_check_in": "Check-in",
                "fecha_check_out":"Check-out",
                "habitacion":     "Habitación",
                "noches":         "Noches",
            })
    else:
        st.markdown(
            f'<div style="background:rgba(91,141,184,0.1); border:1px solid rgba(91,141,184,0.3); '
            f'border-radius:10px; padding:1rem 1.5rem; color:{C["muted"]}; font-size:0.9rem; '
            f'margin-bottom:2rem;">'
            f'📭 No hay check-ins programados para los próximos 7 días</div>',
            unsafe_allow_html=True
        )