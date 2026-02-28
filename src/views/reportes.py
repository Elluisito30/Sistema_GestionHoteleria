import streamlit as st
import pandas as pd
from datetime import date, timedelta, datetime
import plotly.express as px
from config.database import db
from utils.pdf_generator import PDFGenerator, sanitize_text
from utils.logger import logger

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

COLORES_GRAFICOS = ['#5B8DB8','#A8D8EA','#9DB4C7','#68D391','#F6AD55','#FC8181','#B794F4']


# =============================================================================
# Helpers UI
# =============================================================================
def _get_pdf_data(pdf):
    pdf_output = pdf.output(dest='S')
    if isinstance(pdf_output, bytearray):
        return bytes(pdf_output)
    elif hasattr(pdf_output, 'encode'):
        return pdf_output.encode('latin1')
    return pdf_output


def _css():
    st.markdown(f"""
    <style>
    .stApp {{ background-color: #0d1b36; }}
    label, .stSelectbox label, .stDateInput label {{
        color: {C['muted']} !important;
        font-size: 0.82rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}
    .stSelectbox > div > div {{
        background: rgba(255,255,255,0.06) !important;
        border: 1px solid {C['border']} !important;
        border-radius: 8px !important;
        color: {C['text']} !important;
    }}
    .stDateInput input {{
        background: rgba(255,255,255,0.06) !important;
        border: 1px solid {C['border']} !important;
        border-radius: 8px !important;
        color: {C['text']} !important;
    }}
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
    [data-testid="stMetricDelta"] {{ font-size: 0.8rem !important; }}
    .stButton > button[kind="primary"],
    .stFormSubmitButton > button,
    .stDownloadButton > button {{
        background: linear-gradient(135deg, {C['mid']}, {C['primary']}) !important;
        color: white !important;
        border: none !important;
        border-radius: 9px !important;
        font-weight: 600 !important;
        transition: all 0.2s !important;
    }}
    .stButton > button[kind="primary"]:hover,
    .stDownloadButton > button:hover {{
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 18px rgba(91,141,184,0.35) !important;
    }}
    [data-testid="stInfo"] {{
        background: rgba(91,141,184,0.12) !important;
        border: 1px solid rgba(91,141,184,0.3) !important;
        border-radius: 10px !important;
        color: {C['accent']} !important;
    }}
    [data-testid="stInfo"] * {{ color: {C['accent']} !important; }}
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
    hr {{ border-color: {C['border']} !important; }}
    [data-testid="stMarkdownContainer"] p {{ color: {C['text']} !important; }}
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
        font-size: 0.85rem !important;
    }}
    </style>
    """, unsafe_allow_html=True)


def _seccion(emoji, titulo):
    st.markdown(
        f'<div style="display:flex; align-items:center; gap:0.6rem; margin:1.25rem 0 0.75rem;">'
        f'<span style="font-size:1.2rem;">{emoji}</span>'
        f'<span style="font-size:1rem; font-weight:700; color:{C["accent"]};">{titulo}</span>'
        f'</div>', unsafe_allow_html=True
    )


def _caption(texto):
    st.markdown(
        f'<div style="color:{C["muted"]}; font-size:0.82rem; margin-bottom:1rem;">{texto}</div>',
        unsafe_allow_html=True
    )


def _card_info(texto, tipo="info"):
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
        f'{texto}</div>', unsafe_allow_html=True
    )


# =============================================================================
# Helpers PDF (eliminan duplicación de encabezados)
# =============================================================================
def _pdf_header(pdf, subtitulo, fecha_inicio, fecha_fin):
    """Encabezado estándar para todos los reportes PDF."""
    pdf.add_page()

    pdf.set_font('Arial', 'B', 22)
    pdf.set_text_color(91, 141, 184)
    pdf.cell(0, 15, sanitize_text('Hotel Mirador Andino'), 0, 1, 'C')

    pdf.set_font('Arial', 'I', 12)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 8, sanitize_text(subtitulo), 0, 1, 'C')
    pdf.ln(8)

    pdf.set_draw_color(91, 141, 184)
    pdf.set_line_width(1)
    pdf.line(30, pdf.get_y(), 180, pdf.get_y())
    pdf.set_line_width(0.2)
    pdf.line(30, pdf.get_y() + 2, 180, pdf.get_y() + 2)
    pdf.ln(10)

    pdf.set_fill_color(240, 240, 240)
    pdf.set_draw_color(91, 141, 184)
    pdf.rect(30, pdf.get_y(), 150, 12, 'FD')
    pdf.set_xy(30, pdf.get_y())
    pdf.set_font('Arial', 'B', 10)
    pdf.set_text_color(44, 74, 127)
    pdf.cell(40, 12, sanitize_text('Período:'), 0, 0, 'L')
    pdf.set_font('Arial', '', 10)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(110, 12,
             sanitize_text(f'{fecha_inicio.strftime("%d/%m/%Y")} - {fecha_fin.strftime("%d/%m/%Y")}'),
             0, 1, 'L')
    pdf.ln(8)

    pdf.set_font('Arial', 'I', 9)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 6, sanitize_text(f'Generado: {datetime.now().strftime("%d/%m/%Y %H:%M")}'), 0, 1, 'R')
    pdf.ln(8)


def _pdf_section_title(pdf, titulo):
    """Título de sección con fondo azul estándar."""
    pdf.set_fill_color(91, 141, 184)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 12, sanitize_text(titulo), 1, 1, 'C', 1)
    pdf.ln(5)


def _pdf_kv_rows(pdf, filas):
    """Tabla de 2 columnas (etiqueta | valor) con filas alternas."""
    pdf.set_font('Arial', '', 11)
    pdf.set_text_color(0, 0, 0)
    for i, (label, valor) in enumerate(filas):
        pdf.set_fill_color(250, 250, 250) if i % 2 == 0 else pdf.set_fill_color(240, 240, 240)
        pdf.cell(80, 10, sanitize_text(label), 1, 0, 'L', 1)
        pdf.cell(110, 10, sanitize_text(valor), 1, 1, 'R', 1)
    pdf.ln(10)


def _pdf_table_header(pdf, columnas):
    """Cabecera de tabla con fondo azul."""
    pdf.set_font('Arial', 'B', 9)
    pdf.set_fill_color(91, 141, 184)
    pdf.set_text_color(255, 255, 255)
    for texto, ancho in columnas:
        pdf.cell(ancho, 10, sanitize_text(texto), 1, 0, 'C', 1)
    pdf.ln()


def _pdf_footer(pdf):
    """Línea decorativa al final del reporte."""
    pdf.ln(5)
    pdf.set_draw_color(91, 141, 184)
    pdf.set_line_width(0.5)
    pdf.line(20, pdf.get_y(), 190, pdf.get_y())


# =============================================================================
def show():
    _css()

    st.markdown(
        f'<h2 style="color:{C["accent"]}; font-weight:700; margin-bottom:1.25rem; font-size:1.4rem;">'
        f'📈 Reportes y Estadísticas</h2>',
        unsafe_allow_html=True
    )

    col_tipo, col_periodo, col_f1, col_f2 = st.columns([2, 1.5, 1.5, 1.5])

    with col_tipo:
        tipo_reporte = st.selectbox(
            "Tipo de reporte",
            ["Ocupación", "Ingresos", "Reservas", "Análisis de Huéspedes", "Rendimiento Hotelero"]
        )

    with col_periodo:
        periodo = st.selectbox("Período", ["Hoy", "Esta semana", "Este mes", "Personalizado"])

    fecha_inicio = fecha_fin = date.today()

    if periodo == "Esta semana":
        fecha_inicio = date.today() - timedelta(days=date.today().weekday())
    elif periodo == "Este mes":
        fecha_inicio = date.today().replace(day=1)
    elif periodo == "Personalizado":
        with col_f1:
            fecha_inicio = st.date_input("Desde", value=date.today() - timedelta(days=30))
        with col_f2:
            fecha_fin = st.date_input("Hasta", value=date.today())

    st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)

    if   tipo_reporte == "Ocupación":             mostrar_reporte_ocupacion(fecha_inicio, fecha_fin)
    elif tipo_reporte == "Ingresos":              mostrar_reporte_ingresos(fecha_inicio, fecha_fin)
    elif tipo_reporte == "Reservas":              mostrar_reporte_reservas(fecha_inicio, fecha_fin)
    elif tipo_reporte == "Análisis de Huéspedes": mostrar_reporte_huespedes(fecha_inicio, fecha_fin)
    elif tipo_reporte == "Rendimiento Hotelero":  mostrar_reporte_kpis(fecha_inicio, fecha_fin)


# =============================================================================
def mostrar_reporte_ocupacion(fecha_inicio, fecha_fin):
    _seccion("📊", "Reporte de Ocupación")
    _caption(f"Período: {fecha_inicio.strftime('%d/%m/%Y')} — {fecha_fin.strftime('%d/%m/%Y')}")

    with db.get_cursor() as cursor:
        cursor.execute("""
            WITH fechas AS (
                SELECT generate_series(%s::date, %s::date, '1 day'::interval)::date as fecha
            )
            SELECT
                f.fecha,
                COUNT(DISTINCT CASE
                    WHEN r.fecha_check_in <= f.fecha AND r.fecha_check_out > f.fecha
                    AND r.estado IN ('confirmada','completada') THEN r.habitacion_id
                END) as habitaciones_ocupadas,
                COUNT(DISTINCT r.id) as reservas_activas,
                COALESCE(SUM(CASE
                    WHEN r.fecha_check_in <= f.fecha AND r.fecha_check_out > f.fecha
                    AND r.estado IN ('confirmada','completada') THEN 1
                END), 0) as huespedes
            FROM fechas f
            LEFT JOIN reservas r ON r.fecha_check_in <= f.fecha AND r.fecha_check_out > f.fecha
            GROUP BY f.fecha ORDER BY f.fecha
        """, (fecha_inicio, fecha_fin))
        datos = cursor.fetchall()

    if not datos:
        _card_info("📭 No hay datos de ocupación para el período seleccionado", "info")
        return

    df = pd.DataFrame(datos)
    for col in ['habitaciones_ocupadas', 'reservas_activas', 'huespedes']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    fig = px.bar(df, x='fecha', y='habitaciones_ocupadas',
                 color='habitaciones_ocupadas',
                 color_continuous_scale=[[0,'#2c4a7f'],[0.5,'#5B8DB8'],[1,'#A8D8EA']])
    fig.update_layout(**PLOTLY_LAYOUT, height=320, showlegend=False,
                      xaxis_title="Fecha", yaxis_title="Habitaciones Ocupadas",
                      coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

    _seccion("📋", "Detalle por Día")
    df_disp = df.copy()
    df_disp['fecha'] = pd.to_datetime(df_disp['fecha']).dt.strftime('%d/%m/%Y')
    df_disp.columns = ['Fecha','Habitaciones Ocupadas','Reservas Activas','Huéspedes']
    st.dataframe(df_disp, use_container_width=True, hide_index=True)

    col1, col2, col3 = st.columns(3)
    with col1: st.metric("Promedio Ocupación", f"{df['habitaciones_ocupadas'].mean():.1f} habs")
    with col2:
        max_v   = df['habitaciones_ocupadas'].max()
        dia_m   = df.loc[df['habitaciones_ocupadas'].idxmax(), 'fecha']
        dia_str = dia_m.strftime('%d/%m') if hasattr(dia_m, 'strftime') else str(dia_m)
        st.metric("Máxima Ocupación", f"{max_v:.0f}", f"({dia_str})")
    with col3: st.metric("Total Huéspedes", f"{df['huespedes'].sum():.0f}")

    st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
    if st.button("📄 Generar Reporte de Ocupación", type="primary", key="btn_pdf_ocupacion"):
        with st.spinner("Generando PDF..."):
            pdf = PDFGenerator()
            _pdf_header(pdf, 'Reporte de Ocupación', fecha_inicio, fecha_fin)
            _pdf_section_title(pdf, 'RESUMEN DE OCUPACIÓN')
            _pdf_kv_rows(pdf, [
                ('Promedio de Ocupación:', f'{df["habitaciones_ocupadas"].mean():.1f} habitaciones'),
                ('Máxima Ocupación:',      f'{df["habitaciones_ocupadas"].max():.0f} habitaciones'),
                ('Total Huéspedes:',       f'{df["huespedes"].sum():.0f}'),
                ('Días analizados:',       f'{len(df)}'),
            ])
            _pdf_section_title(pdf, 'DETALLE POR DÍA')
            _pdf_table_header(pdf, [('Fecha',45),('Habitaciones Ocupadas',55),('Reservas',45),('Huéspedes',45)])
            pdf.set_font('Arial', '', 9)
            pdf.set_text_color(0, 0, 0)
            for i, (_, row) in enumerate(df.iterrows()):
                pdf.set_fill_color(250,250,250) if i%2==0 else pdf.set_fill_color(240,240,240)
                fecha_str = row['fecha'].strftime('%d/%m/%Y') if hasattr(row['fecha'],'strftime') else str(row['fecha'])
                pdf.cell(45, 8, sanitize_text(fecha_str), 1, 0, 'C', 1)
                pdf.cell(55, 8, sanitize_text(str(int(row['habitaciones_ocupadas']))), 1, 0, 'C', 1)
                pdf.cell(45, 8, sanitize_text(str(int(row['reservas_activas']))), 1, 0, 'C', 1)
                pdf.cell(45, 8, sanitize_text(str(int(row['huespedes']))), 1, 1, 'C', 1)
            _pdf_footer(pdf)
            st.download_button("📥 Descargar Reporte de Ocupación", data=_get_pdf_data(pdf),
                file_name=f"reporte_ocupacion_{fecha_inicio:%Y%m%d}_{fecha_fin:%Y%m%d}.pdf",
                mime="application/pdf")


# =============================================================================
def mostrar_reporte_ingresos(fecha_inicio, fecha_fin):
    _seccion("💰", "Reporte de Ingresos")
    _caption(f"Período: {fecha_inicio.strftime('%d/%m/%Y')} — {fecha_fin.strftime('%d/%m/%Y')}")

    with db.get_cursor() as cursor:
        cursor.execute("""
            SELECT
                DATE(fecha_emision) as fecha,
                COUNT(DISTINCT id) as total_facturas,
                SUM(total) as ingresos,
                SUM(CASE WHEN metodo_pago='efectivo'     THEN total ELSE 0 END) as efectivo,
                SUM(CASE WHEN metodo_pago='tarjeta'      THEN total ELSE 0 END) as tarjeta,
                SUM(CASE WHEN metodo_pago='transferencia' THEN total ELSE 0 END) as transferencia
            FROM facturas
            WHERE DATE(fecha_emision) BETWEEN %s AND %s AND estado='pagada'
            GROUP BY DATE(fecha_emision) ORDER BY fecha
        """, (fecha_inicio, fecha_fin))
        datos = cursor.fetchall()

    if not datos:
        _card_info("📭 No hay datos de ingresos para el período seleccionado", "info")
        return

    df = pd.DataFrame(datos)
    for col in ['ingresos','efectivo','tarjeta','transferencia','total_facturas']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    fig = px.line(df, x='fecha', y=['ingresos','efectivo','tarjeta','transferencia'],
                  color_discrete_sequence=COLORES_GRAFICOS, markers=True)
    fig.update_layout(**PLOTLY_LAYOUT, height=320, xaxis_title="Fecha", yaxis_title="Ingresos (S/)")
    st.plotly_chart(fig, use_container_width=True)

    total_ing  = df['ingresos'].sum()
    total_fact = df['total_facturas'].sum()
    ticket     = total_ing / total_fact if total_fact > 0 else 0
    diario     = total_ing / len(df)    if len(df) > 0    else 0

    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Total Ingresos",       f"S/ {total_ing:,.2f}")
    with col2: st.metric("Total Facturas",        str(int(total_fact)))
    with col3: st.metric("Ticket Promedio",       f"S/ {ticket:,.2f}")
    with col4: st.metric("Ingreso Diario Prom.",  f"S/ {diario:,.2f}")

    _seccion("💳", "Distribución por Método de Pago")
    metodos = pd.DataFrame({
        'Método': ['Efectivo','Tarjeta','Transferencia'],
        'Total':  [df['efectivo'].sum(), df['tarjeta'].sum(), df['transferencia'].sum()]
    })
    fig_pie = px.pie(metodos, values='Total', names='Método',
                     color_discrete_sequence=COLORES_GRAFICOS, hole=0.45)
    fig_pie.update_traces(textposition='inside', textinfo='percent+label',
                          textfont=dict(color='white', size=12),
                          marker=dict(line=dict(color=C['dark'], width=2)))
    fig_pie.update_layout(**PLOTLY_LAYOUT, height=300, showlegend=True)
    st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
    if st.button("📄 Generar Reporte de Ingresos", type="primary", key="btn_pdf_ingresos"):
        with st.spinner("Generando PDF..."):
            pdf = PDFGenerator()
            _pdf_header(pdf, 'Reporte de Ingresos', fecha_inicio, fecha_fin)
            _pdf_section_title(pdf, 'RESUMEN FINANCIERO')
            _pdf_kv_rows(pdf, [
                ('Total Ingresos:',          f'S/ {total_ing:,.2f}'),
                ('Total Facturas:',          f'{int(total_fact)}'),
                ('Ticket Promedio:',         f'S/ {ticket:,.2f}'),
                ('Ingreso Diario Promedio:', f'S/ {diario:,.2f}'),
            ])
            _pdf_section_title(pdf, 'DISTRIBUCIÓN POR MÉTODO DE PAGO')
            _pdf_kv_rows(pdf, [
                ('Efectivo:',      f'S/ {df["efectivo"].sum():,.2f}'),
                ('Tarjeta:',       f'S/ {df["tarjeta"].sum():,.2f}'),
                ('Transferencia:', f'S/ {df["transferencia"].sum():,.2f}'),
            ])
            _pdf_section_title(pdf, 'DETALLE DIARIO')
            _pdf_table_header(pdf, [('Fecha',30),('Facturas',30),('Efectivo',35),
                                     ('Tarjeta',35),('Transf.',35),('Total',35)])
            pdf.set_font('Arial', '', 8)
            pdf.set_text_color(0, 0, 0)
            for i, (_, row) in enumerate(df.iterrows()):
                pdf.set_fill_color(250,250,250) if i%2==0 else pdf.set_fill_color(240,240,240)
                fecha_str = row['fecha'].strftime('%d/%m') if hasattr(row['fecha'],'strftime') else str(row['fecha'])
                pdf.cell(30, 7, sanitize_text(fecha_str), 1, 0, 'C', 1)
                pdf.cell(30, 7, sanitize_text(str(int(row['total_facturas']))), 1, 0, 'C', 1)
                pdf.cell(35, 7, sanitize_text(f"S/{row['efectivo']:,.0f}"), 1, 0, 'R', 1)
                pdf.cell(35, 7, sanitize_text(f"S/{row['tarjeta']:,.0f}"), 1, 0, 'R', 1)
                pdf.cell(35, 7, sanitize_text(f"S/{row['transferencia']:,.0f}"), 1, 0, 'R', 1)
                pdf.cell(35, 7, sanitize_text(f"S/{row['ingresos']:,.0f}"), 1, 1, 'R', 1)
            _pdf_footer(pdf)
            st.download_button("📥 Descargar Reporte de Ingresos", data=_get_pdf_data(pdf),
                file_name=f"reporte_ingresos_{fecha_inicio:%Y%m%d}_{fecha_fin:%Y%m%d}.pdf",
                mime="application/pdf")


# =============================================================================
def mostrar_reporte_reservas(fecha_inicio, fecha_fin):
    _seccion("📋", "Reporte de Reservas")
    _caption(f"Período: {fecha_inicio.strftime('%d/%m/%Y')} — {fecha_fin.strftime('%d/%m/%Y')}")

    with db.get_cursor() as cursor:
        cursor.execute("""
            SELECT
                r.codigo_reserva,
                r.fecha_reserva::date as fecha_reserva,
                r.fecha_check_in, r.fecha_check_out,
                r.tarifa_total, r.estado,
                h.nombre || ' ' || h.apellido as huesped,
                hab.numero as habitacion,
                th.nombre as tipo_habitacion
            FROM reservas r
            JOIN huespedes h ON r.huesped_id = h.id
            LEFT JOIN habitaciones hab ON r.habitacion_id = hab.id
            LEFT JOIN tipos_habitacion th ON hab.tipo_habitacion_id = th.id
            WHERE r.fecha_reserva::date BETWEEN %s AND %s
            ORDER BY r.fecha_reserva DESC
        """, (fecha_inicio, fecha_fin))
        datos = cursor.fetchall()

    if not datos:
        _card_info("📭 No hay reservas en el período seleccionado", "info")
        return

    df = pd.DataFrame(datos)
    df['tarifa_total']  = pd.to_numeric(df['tarifa_total'], errors='coerce').fillna(0)
    df['fecha_reserva'] = pd.to_datetime(df['fecha_reserva']).dt.strftime('%d/%m/%Y')
    df['fecha_check_in']  = pd.to_datetime(df['fecha_check_in']).dt.strftime('%d/%m/%Y')
    df['fecha_check_out'] = pd.to_datetime(df['fecha_check_out']).dt.strftime('%d/%m/%Y')

    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Total Reservas",  len(df))
    with col2: st.metric("Confirmadas",     len(df[df['estado']=='confirmada']))
    with col3: st.metric("Completadas",     len(df[df['estado']=='completada']))
    with col4: st.metric("Canceladas",      len(df[df['estado']=='cancelada']))

    st.dataframe(
        df[['codigo_reserva','huesped','habitacion','fecha_check_in','fecha_check_out','tarifa_total','estado']],
        use_container_width=True, hide_index=True,
        column_config={
            "codigo_reserva":"Código", "huesped":"Huésped", "habitacion":"Habitación",
            "fecha_check_in":"Check-in", "fecha_check_out":"Check-out",
            "tarifa_total":"Total (S/)", "estado":"Estado"
        }
    )

    _seccion("🥧", "Distribución por Estado")
    estado_counts = df['estado'].value_counts()
    fig = px.pie(values=estado_counts.values, names=estado_counts.index,
                 color_discrete_sequence=COLORES_GRAFICOS, hole=0.45)
    fig.update_traces(textposition='inside', textinfo='percent+label',
                      textfont=dict(color='white', size=12),
                      marker=dict(line=dict(color=C['dark'], width=2)))
    fig.update_layout(**PLOTLY_LAYOUT, height=300)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
    if st.button("📄 Generar Reporte de Reservas", type="primary", key="btn_pdf_reservas"):
        with st.spinner("Generando PDF..."):
            pdf = PDFGenerator()
            _pdf_header(pdf, 'Reporte de Reservas', fecha_inicio, fecha_fin)
            _pdf_section_title(pdf, 'RESUMEN DE RESERVAS')
            _pdf_kv_rows(pdf, [
                ('Total Reservas:', f'{len(df)}'),
                ('Confirmadas:',    f'{len(df[df["estado"]=="confirmada"])}'),
                ('Completadas:',    f'{len(df[df["estado"]=="completada"])}'),
                ('Canceladas:',     f'{len(df[df["estado"]=="cancelada"])}'),
            ])
            _pdf_section_title(pdf, 'DETALLE DE RESERVAS')
            _pdf_table_header(pdf, [('Código',25),('Huésped',45),('Check-in',25),
                                     ('Check-out',25),('Hab.',25),('Total',30),('Estado',25)])
            pdf.set_font('Arial', '', 8)
            pdf.set_text_color(0, 0, 0)
            for i, (_, row) in enumerate(df.iterrows()):
                pdf.set_fill_color(250,250,250) if i%2==0 else pdf.set_fill_color(240,240,240)
                pdf.cell(25, 7, sanitize_text(str(row['codigo_reserva'])), 1, 0, 'C', 1)
                pdf.cell(45, 7, sanitize_text(str(row['huesped'])[:20]), 1, 0, 'L', 1)
                pdf.cell(25, 7, sanitize_text(str(row['fecha_check_in'])), 1, 0, 'C', 1)
                pdf.cell(25, 7, sanitize_text(str(row['fecha_check_out'])), 1, 0, 'C', 1)
                pdf.cell(25, 7, sanitize_text(str(row['habitacion'])), 1, 0, 'C', 1)
                pdf.cell(30, 7, sanitize_text(f"S/{row['tarifa_total']:,.0f}"), 1, 0, 'R', 1)
                pdf.cell(25, 7, sanitize_text(str(row['estado'])), 1, 1, 'C', 1)
            _pdf_footer(pdf)
            st.download_button("📥 Descargar Reporte de Reservas", data=_get_pdf_data(pdf),
                file_name=f"reporte_reservas_{fecha_inicio:%Y%m%d}_{fecha_fin:%Y%m%d}.pdf",
                mime="application/pdf")


# =============================================================================
def mostrar_reporte_kpis(fecha_inicio, fecha_fin):
    _seccion("📊", "KPIs — Rendimiento Hotelero")
    _caption(f"Período: {fecha_inicio.strftime('%d/%m/%Y')} — {fecha_fin.strftime('%d/%m/%Y')}")

    with db.get_cursor() as cursor:
        cursor.execute("""
            WITH stats AS (
                SELECT
                    COUNT(DISTINCT r.id) as total_reservas,
                    COALESCE(SUM(r.tarifa_total), 0) as ingresos_totales,
                    COALESCE(AVG(r.fecha_check_out - r.fecha_check_in), 0) as estancia_promedio,
                    COUNT(DISTINCT r.huesped_id) as huespedes_unicos,
                    SUM(CASE WHEN r.estado='cancelada' THEN 1 ELSE 0 END) as cancelaciones
                FROM reservas r WHERE r.fecha_reserva::date BETWEEN %s AND %s
            ),
            habitaciones_stats AS (
                SELECT COUNT(*) as total_habitaciones, AVG(tarifa_base) as tarifa_promedio
                FROM habitaciones WHERE activa = true
            )
            SELECT s.*, h.total_habitaciones, h.tarifa_promedio,
                CASE WHEN s.total_reservas > 0
                    THEN (s.cancelaciones::DECIMAL / s.total_reservas * 100) ELSE 0
                END as tasa_cancelacion
            FROM stats s, habitaciones_stats h
        """, (fecha_inicio, fecha_fin))
        kpis = cursor.fetchone()

    if not kpis:
        _card_info("📭 No hay datos para el período seleccionado", "info")
        return

    estancia = float(kpis.get('estancia_promedio') or 0)
    dias_periodo = (fecha_fin - fecha_inicio).days + 1
    hab_disp = kpis['total_habitaciones'] * dias_periodo
    revpar   = float(kpis['ingresos_totales']) / hab_disp if hab_disp > 0 else 0

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Reservas",    kpis['total_reservas'])
        st.metric("Estancia Promedio", f"{estancia:.1f} días")
    with col2:
        st.metric("Ingresos Totales",  f"S/ {float(kpis['ingresos_totales']):,.2f}")
        st.metric("Huéspedes Únicos",  kpis['huespedes_unicos'])
    with col3:
        st.metric("Tasa Cancelación",  f"{float(kpis['tasa_cancelacion']):.1f}%")
        st.metric("Tarifa Promedio",   f"S/ {float(kpis['tarifa_promedio']):,.2f}")

    st.markdown(
        f'<div style="background:linear-gradient(135deg,{C["mid"]},{C["primary"]}22); '
        f'border:1px solid {C["primary"]}44; border-radius:12px; padding:1.25rem 1.5rem; '
        f'display:flex; align-items:center; justify-content:space-between; margin:1rem 0;">'
        f'<div>'
        f'<div style="color:{C["muted"]}; font-size:0.75rem; font-weight:600; '
        f'text-transform:uppercase; letter-spacing:0.08em;">RevPAR — Revenue per Available Room</div>'
        f'<div style="color:{C["accent"]}; font-size:2rem; font-weight:700; margin-top:0.25rem;">'
        f'S/ {revpar:,.2f}</div>'
        f'</div>'
        f'<div style="font-size:2.5rem; opacity:0.4;">🏨</div>'
        f'</div>',
        unsafe_allow_html=True
    )

    st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
    if st.button("📄 Generar Reporte de Rendimiento Hotelero", type="primary", key="btn_pdf_kpis"):
        with st.spinner("Generando PDF..."):
            pdf = PDFGenerator()
            _pdf_header(pdf, 'Reporte de Rendimiento Hotelero', fecha_inicio, fecha_fin)
            _pdf_section_title(pdf, 'INDICADORES CLAVE DE RENDIMIENTO (KPIs)')
            kpis_filas = [
                ('Total Reservas',    f'{kpis["total_reservas"]}'),
                ('Ingresos Totales',  f'S/ {float(kpis["ingresos_totales"]):,.2f}'),
                ('Estancia Promedio', f'{estancia:.1f} días'),
                ('Huéspedes Únicos',  f'{kpis["huespedes_unicos"]}'),
                ('Tasa Cancelación',  f'{float(kpis["tasa_cancelacion"]):.1f}%'),
                ('Tarifa Promedio',   f'S/ {float(kpis["tarifa_promedio"]):,.2f}'),
                ('RevPAR',            f'S/ {revpar:,.2f}'),
            ]
            # Centrar tabla de KPIs
            pdf.set_font('Arial', '', 11)
            pdf.set_text_color(0, 0, 0)
            for i, (metrica, valor) in enumerate(kpis_filas):
                pdf.set_fill_color(250,250,250) if i%2==0 else pdf.set_fill_color(240,240,240)
                pdf.set_x((210 - 140) / 2)
                pdf.cell(70, 10, sanitize_text(metrica), 1, 0, 'L', 1)
                pdf.cell(70, 10, sanitize_text(valor), 1, 1, 'R', 1)
            pdf.ln(10)
            pdf.set_font('Arial', 'B', 10)
            pdf.set_text_color(44, 74, 127)
            pdf.cell(0, 8, sanitize_text('Notas:'), 0, 1, 'L')
            pdf.set_font('Arial', '', 9)
            pdf.set_text_color(80, 80, 80)
            pdf.cell(0, 5, sanitize_text('• RevPAR: Revenue per Available Room'), 0, 1, 'L')
            pdf.cell(0, 5, sanitize_text(f'• Período analizado: {dias_periodo} días'), 0, 1, 'L')
            pdf.cell(0, 5, sanitize_text(f'• Total habitaciones: {kpis["total_habitaciones"]}'), 0, 1, 'L')
            _pdf_footer(pdf)
            st.download_button("📥 Descargar Reporte de Rendimiento", data=_get_pdf_data(pdf),
                file_name=f"reporte_rendimiento_{fecha_inicio:%Y%m%d}_{fecha_fin:%Y%m%d}.pdf",
                mime="application/pdf")


# =============================================================================
def mostrar_reporte_huespedes(fecha_inicio, fecha_fin):
    _seccion("👤", "Análisis de Huéspedes")
    _caption(f"Período: {fecha_inicio.strftime('%d/%m/%Y')} — {fecha_fin.strftime('%d/%m/%Y')}")

    with db.get_cursor() as cursor:
        cursor.execute("""
            SELECT
                h.id, h.nombre, h.apellido, h.numero_documento,
                h.email, h.nacionalidad, h.es_vip,
                h.created_at::date as fecha_registro,
                COUNT(r.id) as total_reservas,
                COALESCE(SUM(CASE WHEN r.estado != 'cancelada' THEN r.tarifa_total ELSE 0 END), 0) as total_consumido
            FROM huespedes h
            LEFT JOIN reservas r ON h.id = r.huesped_id
                AND r.fecha_reserva::date BETWEEN %s AND %s
            WHERE h.created_at::date BETWEEN %s AND %s
            GROUP BY h.id, h.nombre, h.apellido, h.numero_documento,
                     h.email, h.nacionalidad, h.es_vip, h.created_at
            ORDER BY total_reservas DESC, total_consumido DESC
        """, (fecha_inicio, fecha_fin, fecha_inicio, fecha_fin))
        datos = cursor.fetchall()

    if not datos:
        _card_info("📭 No hay datos de huéspedes para el período seleccionado", "info")
        return

    df = pd.DataFrame(datos)
    df['total_reservas']  = pd.to_numeric(df['total_reservas'],  errors='coerce').fillna(0)
    df['total_consumido'] = pd.to_numeric(df['total_consumido'], errors='coerce').fillna(0)
    df['fecha_registro']  = pd.to_datetime(df['fecha_registro']).dt.strftime('%d/%m/%Y')
    df['es_vip']          = df['es_vip'].apply(lambda x: "⭐ Sí" if x else "No")

    col1, col2, col3 = st.columns(3)
    with col1: st.metric("Nuevos Huéspedes",  len(df))
    with col2: st.metric("Total Reservas",     int(df['total_reservas'].sum()))
    with col3: st.metric("Ingresos Huéspedes", f"S/ {df['total_consumido'].sum():,.2f}")

    _seccion("🏆", "Top 10 Huéspedes por Consumo")
    top = df.nlargest(10, 'total_consumido')
    st.dataframe(
        top[['nombre','apellido','total_reservas','total_consumido','es_vip']],
        use_container_width=True, hide_index=True,
        column_config={
            "nombre":"Nombre", "apellido":"Apellido", "total_reservas":"Reservas",
            "total_consumido": st.column_config.NumberColumn("Total (S/)", format="S/ %.2f"),
            "es_vip":"VIP"
        }
    )

    if 'nacionalidad' in df.columns and df['nacionalidad'].notna().any():
        _seccion("🌍", "Huéspedes por Nacionalidad")
        nac_counts = df[df['nacionalidad'].notna()]['nacionalidad'].value_counts().head(10)
        fig = px.bar(x=nac_counts.index, y=nac_counts.values,
                     color=nac_counts.values,
                     color_continuous_scale=[[0,'#2c4a7f'],[0.5,'#5B8DB8'],[1,'#A8D8EA']])
        fig.update_layout(**PLOTLY_LAYOUT, height=300, xaxis_title="Nacionalidad",
                          yaxis_title="Cantidad", showlegend=False, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
    if st.button("📄 Generar Reporte de Huéspedes", type="primary", key="btn_pdf_huespedes"):
        with st.spinner("Generando PDF..."):
            pdf = PDFGenerator()
            _pdf_header(pdf, 'Reporte de Análisis de Huéspedes', fecha_inicio, fecha_fin)
            _pdf_section_title(pdf, 'RESUMEN EJECUTIVO')
            _pdf_kv_rows(pdf, [
                ('Nuevos Huéspedes:', f'{len(df)}'),
                ('Total Reservas:',   f'{int(df["total_reservas"].sum())}'),
                ('Ingresos Totales:', f'S/ {df["total_consumido"].sum():,.2f}'),
            ])
            _pdf_section_title(pdf, 'TOP 10 HUÉSPEDES POR CONSUMO')
            _pdf_table_header(pdf, [('Nombre',45),('Apellido',45),('Reservas',30),
                                     ('Total Consumido',45),('VIP',25)])
            pdf.set_font('Arial', '', 8)
            pdf.set_text_color(0, 0, 0)
            for i, (_, row) in enumerate(top.iterrows()):
                pdf.set_fill_color(250,250,250) if i%2==0 else pdf.set_fill_color(240,240,240)
                pdf.cell(45, 8, sanitize_text(row['nombre'][:25]), 1, 0, 'L', 1)
                pdf.cell(45, 8, sanitize_text(row['apellido'][:25]), 1, 0, 'L', 1)
                pdf.cell(30, 8, sanitize_text(str(int(row['total_reservas']))), 1, 0, 'C', 1)
                pdf.cell(45, 8, sanitize_text(f"S/ {row['total_consumido']:,.2f}"), 1, 0, 'R', 1)
                pdf.cell(25, 8, sanitize_text('Si' if '⭐' in str(row['es_vip']) else ''), 1, 1, 'C', 1)
            if 'nacionalidad' in df.columns and df['nacionalidad'].notna().any():
                pdf.ln(8)
                _pdf_section_title(pdf, 'DISTRIBUCIÓN POR NACIONALIDAD')
                nac_counts = df[df['nacionalidad'].notna()]['nacionalidad'].value_counts().head(5)
                _pdf_kv_rows(pdf, [(f'{pais}:', f'{cnt} huéspedes') for pais, cnt in nac_counts.items()])
            _pdf_footer(pdf)
            st.download_button("📥 Descargar Reporte de Huéspedes", data=_get_pdf_data(pdf),
                file_name=f"reporte_huespedes_{fecha_inicio:%Y%m%d}_{fecha_fin:%Y%m%d}.pdf",
                mime="application/pdf")