from fpdf import FPDF
from datetime import datetime
import pandas as pd
import os

def sanitize_text(text):
    """Reemplaza caracteres especiales no soportados por Arial/Helvetica"""
    if text is None:
        return ""
    
    # Convertir a string si no lo es
    text = str(text)
    
    # Reemplazar caracteres problemáticos
    replacements = {
        '•': '-',           # bullet point por guión
        '€': 'S/',         # símbolo euro por S/
        '—': '-',           # guión largo por guión
        '"': '"',           # comillas
        "'": "'",           # apóstrofe
        '’': "'",           # apóstrofe curvo
        '“': '"',           # comillas curvas
        '”': '"',           # comillas curvas
        '–': '-',           # guión medio
        '…': '...',         # puntos suspensivos
        '⭐': '[VIP]',      # estrella por [VIP]
        '\u2b50': '[VIP]',  # estrella unicode por [VIP]
        '\u2022': '-',      # bullet point unicode
        '\u20ac': 'S/',    # símbolo euro unicode por S/
        '\u2014': '-',      # guión largo unicode
        '\u2013': '-',      # guión medio unicode
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    return text

class PDFGenerator(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        
    def header(self):
        # Logo
        self.set_font('Arial', 'B', 15)
        self.cell(80)
        self.cell(30, 10, sanitize_text('Hotel Mirador Andino'), 0, 0, 'C')
        self.ln(20)
        
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, sanitize_text(f'Página {self.page_no()}'), 0, 0, 'C')
    
    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, sanitize_text(title), 0, 1, 'L')
        self.ln(5)
    
    def chapter_body(self, body):
        self.set_font('Arial', '', 11)
        self.multi_cell(0, 5, sanitize_text(body))
        self.ln()
    
    def create_occupancy_report(self, df, fecha_inicio, fecha_fin):
        """Genera reporte PDF de ocupación"""
        self.add_page()
        
        # Título
        self.set_font('Arial', 'B', 20)
        self.set_text_color(91, 141, 184)
        self.cell(0, 15, sanitize_text('Hotel Mirador Andino'), 0, 1, 'C')
        
        self.set_font('Arial', 'I', 11)
        self.set_text_color(80, 80, 80)
        self.cell(0, 8, sanitize_text('Reporte de Ocupación'), 0, 1, 'C')
        self.ln(8)
        
        # Línea decorativa
        self.set_draw_color(91, 141, 184)
        self.set_line_width(0.5)
        self.line(20, self.get_y(), 190, self.get_y())
        self.ln(10)
        
        # Período
        self.set_fill_color(240, 240, 240)
        self.set_draw_color(91, 141, 184)
        self.rect(30, self.get_y(), 150, 12, 'FD')
        self.set_xy(30, self.get_y())
        self.set_font('Arial', 'B', 10)
        self.set_text_color(44, 74, 127)
        self.cell(40, 12, sanitize_text('Período:'), 0, 0, 'L')
        self.set_font('Arial', '', 10)
        self.set_text_color(0, 0, 0)
        self.cell(110, 12, sanitize_text(f'{fecha_inicio.strftime("%d/%m/%Y")} - {fecha_fin.strftime("%d/%m/%Y")}'), 0, 1, 'L')
        self.ln(8)
        
        # Fecha de generación
        self.set_font('Arial', 'I', 9)
        self.set_text_color(100, 100, 100)
        self.cell(0, 6, sanitize_text(f'Generado: {datetime.now().strftime("%d/%m/%Y %H:%M")}'), 0, 1, 'R')
        self.ln(8)
        
        # Título de tabla
        self.set_fill_color(91, 141, 184)
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 14)
        self.cell(0, 12, sanitize_text('RESUMEN DE OCUPACIÓN'), 1, 1, 'C', 1)
        self.ln(5)
        
        # Datos resumen
        self.set_font('Arial', '', 11)
        self.set_text_color(0, 0, 0)
        
        resumen_data = [
            ('Promedio de Ocupación:', f'{df["habitaciones_ocupadas"].mean():.1f} habitaciones'),
            ('Máxima Ocupación:', f'{df["habitaciones_ocupadas"].max():.0f} habitaciones'),
            ('Total Huéspedes:', f'{df["huespedes"].sum():.0f}'),
            ('Días analizados:', f'{len(df)}')
        ]
        
        for i, (label, valor) in enumerate(resumen_data):
            if i % 2 == 0:
                self.set_fill_color(250, 250, 250)
            else:
                self.set_fill_color(240, 240, 240)
            
            self.cell(80, 10, sanitize_text(label), 1, 0, 'L', 1)
            self.cell(110, 10, sanitize_text(valor), 1, 1, 'R', 1)
        
        self.ln(10)
        
        # Tabla de detalle diario
        self.set_fill_color(91, 141, 184)
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 14)
        self.cell(0, 12, sanitize_text('DETALLE POR DÍA'), 1, 1, 'C', 1)
        self.ln(5)
        
        # Cabecera de tabla
        self.set_font('Arial', 'B', 10)
        self.set_fill_color(91, 141, 184)
        self.set_text_color(255, 255, 255)
        self.cell(45, 10, sanitize_text('Fecha'), 1, 0, 'C', 1)
        self.cell(55, 10, sanitize_text('Habitaciones Ocupadas'), 1, 0, 'C', 1)
        self.cell(45, 10, sanitize_text('Reservas'), 1, 0, 'C', 1)
        self.cell(45, 10, sanitize_text('Huéspedes'), 1, 1, 'C', 1)
        
        # Datos
        self.set_font('Arial', '', 9)
        self.set_text_color(0, 0, 0)
        
        for i, (_, row) in enumerate(df.iterrows()):
            if i % 2 == 0:
                self.set_fill_color(250, 250, 250)
            else:
                self.set_fill_color(240, 240, 240)
            
            try:
                fecha_str = row['fecha'].strftime('%d/%m/%Y')
            except:
                fecha_str = str(row['fecha'])
            
            self.cell(45, 8, sanitize_text(fecha_str), 1, 0, 'C', 1)
            self.cell(55, 8, sanitize_text(str(int(row['habitaciones_ocupadas']))), 1, 0, 'C', 1)
            self.cell(45, 8, sanitize_text(str(int(row['reservas_activas']))), 1, 0, 'C', 1)
            self.cell(45, 8, sanitize_text(str(int(row['huespedes']))), 1, 1, 'C', 1)
        
        # Línea final decorativa
        self.ln(5)
        self.set_draw_color(91, 141, 184)
        self.set_line_width(0.5)
        self.line(20, self.get_y(), 190, self.get_y())
    
    def create_income_report(self, df, fecha_inicio, fecha_fin):
        """Genera reporte PDF de ingresos"""
        self.add_page()
        
        # Título
        self.set_font('Arial', 'B', 20)
        self.set_text_color(91, 141, 184)
        self.cell(0, 15, sanitize_text('Hotel Mirador Andino'), 0, 1, 'C')
        
        self.set_font('Arial', 'I', 11)
        self.set_text_color(80, 80, 80)
        self.cell(0, 8, sanitize_text('Reporte de Ingresos'), 0, 1, 'C')
        self.ln(8)
        
        # Línea decorativa
        self.set_draw_color(91, 141, 184)
        self.set_line_width(0.5)
        self.line(20, self.get_y(), 190, self.get_y())
        self.ln(10)
        
        # Período
        self.set_fill_color(240, 240, 240)
        self.set_draw_color(91, 141, 184)
        self.rect(30, self.get_y(), 150, 12, 'FD')
        self.set_xy(30, self.get_y())
        self.set_font('Arial', 'B', 10)
        self.set_text_color(44, 74, 127)
        self.cell(40, 12, sanitize_text('Período:'), 0, 0, 'L')
        self.set_font('Arial', '', 10)
        self.set_text_color(0, 0, 0)
        self.cell(110, 12, sanitize_text(f'{fecha_inicio.strftime("%d/%m/%Y")} - {fecha_fin.strftime("%d/%m/%Y")}'), 0, 1, 'L')
        self.ln(8)
        
        # Fecha de generación
        self.set_font('Arial', 'I', 9)
        self.set_text_color(100, 100, 100)
        self.cell(0, 6, sanitize_text(f'Generado: {datetime.now().strftime("%d/%m/%Y %H:%M")}'), 0, 1, 'R')
        self.ln(8)
        
        # Título de tabla
        self.set_fill_color(91, 141, 184)
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 14)
        self.cell(0, 12, sanitize_text('RESUMEN FINANCIERO'), 1, 1, 'C', 1)
        self.ln(5)
        
        total_ing = df['ingresos'].sum()
        total_fact = df['total_facturas'].sum()
        ticket = total_ing / total_fact if total_fact > 0 else 0
        diario = total_ing / len(df) if len(df) > 0 else 0
        
        # Datos resumen
        self.set_font('Arial', '', 11)
        self.set_text_color(0, 0, 0)
        
        resumen_data = [
            ('Total Ingresos:', f'S/ {total_ing:,.2f}'),
            ('Total Facturas:', f'{int(total_fact)}'),
            ('Ticket Promedio:', f'S/ {ticket:,.2f}'),
            ('Ingreso Diario Promedio:', f'S/ {diario:,.2f}')
        ]
        
        for i, (label, valor) in enumerate(resumen_data):
            if i % 2 == 0:
                self.set_fill_color(250, 250, 250)
            else:
                self.set_fill_color(240, 240, 240)
            
            self.cell(80, 10, sanitize_text(label), 1, 0, 'L', 1)
            self.cell(110, 10, sanitize_text(valor), 1, 1, 'R', 1)
        
        self.ln(10)
        
        # Distribución por método de pago
        self.set_fill_color(91, 141, 184)
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 14)
        self.cell(0, 12, sanitize_text('DISTRIBUCIÓN POR MÉTODO DE PAGO'), 1, 1, 'C', 1)
        self.ln(5)
        
        metodos_pago = [
            ('Efectivo:', f'S/ {df["efectivo"].sum():,.2f}'),
            ('Tarjeta:', f'S/ {df["tarjeta"].sum():,.2f}'),
            ('Transferencia:', f'S/ {df["transferencia"].sum():,.2f}')
        ]
        
        for i, (label, valor) in enumerate(metodos_pago):
            if i % 2 == 0:
                self.set_fill_color(250, 250, 250)
            else:
                self.set_fill_color(240, 240, 240)
            
            self.cell(80, 10, sanitize_text(label), 1, 0, 'L', 1)
            self.cell(110, 10, sanitize_text(valor), 1, 1, 'R', 1)
        
        self.ln(10)
        
        # Tabla de detalle diario
        self.set_fill_color(91, 141, 184)
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 14)
        self.cell(0, 12, sanitize_text('DETALLE DIARIO'), 1, 1, 'C', 1)
        self.ln(5)
        
        # Cabecera de tabla
        self.set_font('Arial', 'B', 9)
        self.set_fill_color(91, 141, 184)
        self.set_text_color(255, 255, 255)
        self.cell(30, 10, sanitize_text('Fecha'), 1, 0, 'C', 1)
        self.cell(30, 10, sanitize_text('Facturas'), 1, 0, 'C', 1)
        self.cell(35, 10, sanitize_text('Efectivo'), 1, 0, 'C', 1)
        self.cell(35, 10, sanitize_text('Tarjeta'), 1, 0, 'C', 1)
        self.cell(35, 10, sanitize_text('Transf.'), 1, 0, 'C', 1)
        self.cell(35, 10, sanitize_text('Total'), 1, 1, 'C', 1)
        
        # Datos
        self.set_font('Arial', '', 8)
        self.set_text_color(0, 0, 0)
        
        for i, (_, row) in enumerate(df.iterrows()):
            if i % 2 == 0:
                self.set_fill_color(250, 250, 250)
            else:
                self.set_fill_color(240, 240, 240)
            
            try:
                fecha_str = row['fecha'].strftime('%d/%m')
            except:
                fecha_str = str(row['fecha'])
            
            self.cell(30, 7, sanitize_text(fecha_str), 1, 0, 'C', 1)
            self.cell(30, 7, sanitize_text(str(int(row['total_facturas']))), 1, 0, 'C', 1)
            self.cell(35, 7, sanitize_text(f"S/{row['efectivo']:,.0f}"), 1, 0, 'R', 1)
            self.cell(35, 7, sanitize_text(f"S/{row['tarjeta']:,.0f}"), 1, 0, 'R', 1)
            self.cell(35, 7, sanitize_text(f"S/{row['transferencia']:,.0f}"), 1, 0, 'R', 1)
            self.cell(35, 7, sanitize_text(f"S/{row['ingresos']:,.0f}"), 1, 1, 'R', 1)
        
        # Línea final decorativa
        self.ln(5)
        self.set_draw_color(91, 141, 184)
        self.set_line_width(0.5)
        self.line(20, self.get_y(), 190, self.get_y())
    
    def create_reservations_report(self, df, fecha_inicio, fecha_fin):
        """Genera reporte PDF de reservas"""
        self.add_page()
        
        # Título
        self.set_font('Arial', 'B', 20)
        self.set_text_color(91, 141, 184)
        self.cell(0, 15, sanitize_text('Hotel Mirador Andino'), 0, 1, 'C')
        
        self.set_font('Arial', 'I', 11)
        self.set_text_color(80, 80, 80)
        self.cell(0, 8, sanitize_text('Reporte de Reservas'), 0, 1, 'C')
        self.ln(8)
        
        # Línea decorativa
        self.set_draw_color(91, 141, 184)
        self.set_line_width(0.5)
        self.line(20, self.get_y(), 190, self.get_y())
        self.ln(10)
        
        # Período
        self.set_fill_color(240, 240, 240)
        self.set_draw_color(91, 141, 184)
        self.rect(30, self.get_y(), 150, 12, 'FD')
        self.set_xy(30, self.get_y())
        self.set_font('Arial', 'B', 10)
        self.set_text_color(44, 74, 127)
        self.cell(40, 12, sanitize_text('Período:'), 0, 0, 'L')
        self.set_font('Arial', '', 10)
        self.set_text_color(0, 0, 0)
        self.cell(110, 12, sanitize_text(f'{fecha_inicio.strftime("%d/%m/%Y")} - {fecha_fin.strftime("%d/%m/%Y")}'), 0, 1, 'L')
        self.ln(8)
        
        # Fecha de generación
        self.set_font('Arial', 'I', 9)
        self.set_text_color(100, 100, 100)
        self.cell(0, 6, sanitize_text(f'Generado: {datetime.now().strftime("%d/%m/%Y %H:%M")}'), 0, 1, 'R')
        self.ln(8)
        
        # Título de tabla
        self.set_fill_color(91, 141, 184)
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 14)
        self.cell(0, 12, sanitize_text('RESUMEN DE RESERVAS'), 1, 1, 'C', 1)
        self.ln(5)
        
        # Datos resumen
        self.set_font('Arial', '', 11)
        self.set_text_color(0, 0, 0)
        
        resumen_data = [
            ('Total Reservas:', f'{len(df)}'),
            ('Confirmadas:', f'{len(df[df["estado"]=="confirmada"])}'),
            ('Completadas:', f'{len(df[df["estado"]=="completada"])}'),
            ('Canceladas:', f'{len(df[df["estado"]=="cancelada"])}')
        ]
        
        for i, (label, valor) in enumerate(resumen_data):
            if i % 2 == 0:
                self.set_fill_color(250, 250, 250)
            else:
                self.set_fill_color(240, 240, 240)
            
            self.cell(80, 10, sanitize_text(label), 1, 0, 'L', 1)
            self.cell(110, 10, sanitize_text(valor), 1, 1, 'R', 1)
        
        self.ln(10)
        
        # Distribución por estado
        self.set_fill_color(91, 141, 184)
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 14)
        self.cell(0, 12, sanitize_text('DISTRIBUCIÓN POR ESTADO'), 1, 1, 'C', 1)
        self.ln(5)
        
        estado_counts = df['estado'].value_counts()
        for i, (estado, count) in enumerate(estado_counts.items()):
            if i % 2 == 0:
                self.set_fill_color(250, 250, 250)
            else:
                self.set_fill_color(240, 240, 240)
            
            self.cell(80, 10, sanitize_text(f'{estado.capitalize()}'), 1, 0, 'L', 1)
            self.cell(110, 10, sanitize_text(str(count)), 1, 1, 'R', 1)
        
        self.ln(10)
        
        # Tabla de detalle de reservas
        self.set_fill_color(91, 141, 184)
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 14)
        self.cell(0, 12, sanitize_text('DETALLE DE RESERVAS'), 1, 1, 'C', 1)
        self.ln(5)
        
        # Cabecera de tabla
        self.set_font('Arial', 'B', 9)
        self.set_fill_color(91, 141, 184)
        self.set_text_color(255, 255, 255)
        self.cell(25, 10, sanitize_text('Código'), 1, 0, 'C', 1)
        self.cell(45, 10, sanitize_text('Huésped'), 1, 0, 'C', 1)
        self.cell(25, 10, sanitize_text('Check-in'), 1, 0, 'C', 1)
        self.cell(25, 10, sanitize_text('Check-out'), 1, 0, 'C', 1)
        self.cell(25, 10, sanitize_text('Habitación'), 1, 0, 'C', 1)
        self.cell(30, 10, sanitize_text('Total'), 1, 0, 'C', 1)
        self.cell(25, 10, sanitize_text('Estado'), 1, 1, 'C', 1)
        
        # Datos
        self.set_font('Arial', '', 8)
        self.set_text_color(0, 0, 0)
        
        for i, (_, row) in enumerate(df.iterrows()):
            if i % 2 == 0:
                self.set_fill_color(250, 250, 250)
            else:
                self.set_fill_color(240, 240, 240)
            
            self.cell(25, 7, sanitize_text(str(row['codigo_reserva'])), 1, 0, 'C', 1)
            self.cell(45, 7, sanitize_text(str(row['huesped'])[:20]), 1, 0, 'L', 1)
            self.cell(25, 7, sanitize_text(str(row['fecha_check_in'])), 1, 0, 'C', 1)
            self.cell(25, 7, sanitize_text(str(row['fecha_check_out'])), 1, 0, 'C', 1)
            self.cell(25, 7, sanitize_text(str(row['habitacion'])), 1, 0, 'C', 1)
            self.cell(30, 7, sanitize_text(f"S/{row['tarifa_total']:,.0f}"), 1, 0, 'R', 1)
            self.cell(25, 7, sanitize_text(str(row['estado'])), 1, 1, 'C', 1)
        
        # Línea final decorativa
        self.ln(5)
        self.set_draw_color(91, 141, 184)
        self.set_line_width(0.5)
        self.line(20, self.get_y(), 190, self.get_y())
    
    def create_invoice_pdf(self, factura_data, detalle_items):
        """Genera PDF de factura profesional"""
        self.add_page()
        
        # Encabezado con datos del hotel
        self.set_font('Arial', 'B', 22)
        self.set_text_color(91, 141, 184)
        self.cell(0, 15, sanitize_text('Hotel Mirador Andino'), 0, 1, 'C')
        
        self.set_font('Arial', 'I', 10)
        self.set_text_color(80, 80, 80)
        self.cell(0, 5, sanitize_text('Av. El Sol 456, Cusco, Perú'), 0, 1, 'C')
        self.cell(0, 5, sanitize_text('RUC: 20123456789 - Tel: (084) 234-567'), 0, 1, 'C')
        self.ln(5)
        
        # Línea decorativa
        self.set_draw_color(91, 141, 184)
        self.set_line_width(0.5)
        self.line(20, self.get_y(), 190, self.get_y())
        self.ln(10)
        
        # Título FACTURA
        self.set_font('Arial', 'B', 18)
        self.set_text_color(44, 74, 127)
        self.cell(0, 10, sanitize_text('FACTURA ELECTRÓNICA'), 0, 1, 'C')
        self.ln(5)
        
        # Número de factura y fecha
        self.set_font('Arial', 'B', 11)
        self.set_text_color(0, 0, 0)
        self.cell(50, 8, sanitize_text('N° Factura:'), 0, 0, 'L')
        self.set_font('Arial', '', 11)
        self.cell(70, 8, sanitize_text(factura_data.get('numero_factura', 'N/A')), 0, 0, 'L')
        
        self.set_font('Arial', 'B', 11)
        self.cell(30, 8, sanitize_text('Fecha:'), 0, 0, 'L')
        self.set_font('Arial', '', 11)
        fecha_emision = factura_data.get('fecha_emision', datetime.now())
        if isinstance(fecha_emision, str):
            try:
                fecha_emision = datetime.strptime(fecha_emision, '%Y-%m-%d')
            except:
                fecha_emision = datetime.now()
        self.cell(40, 8, sanitize_text(fecha_emision.strftime('%d/%m/%Y')), 0, 1, 'L')
        self.ln(8)
        
        # Datos del cliente
        self.set_fill_color(240, 240, 240)
        self.set_font('Arial', 'B', 12)
        self.set_text_color(44, 74, 127)
        self.cell(0, 10, sanitize_text('DATOS DEL CLIENTE'), 1, 1, 'L', 1)
        self.ln(2)
        
        self.set_font('Arial', '', 10)
        self.set_text_color(0, 0, 0)
        self.cell(40, 7, sanitize_text('Cliente:'), 0, 0, 'L')
        self.cell(150, 7, sanitize_text(f"{factura_data.get('huesped_nombre', '')} {factura_data.get('huesped_apellido', '')}"), 0, 1, 'L')
        
        self.cell(40, 7, sanitize_text('Documento:'), 0, 0, 'L')
        self.cell(150, 7, sanitize_text(factura_data.get('huesped_documento', 'N/A')), 0, 1, 'L')
        
        if factura_data.get('reserva_id'):
            self.cell(40, 7, sanitize_text('Reserva:'), 0, 0, 'L')
            self.cell(150, 7, sanitize_text(factura_data.get('codigo_reserva', 'N/A')), 0, 1, 'L')
        self.ln(5)
        
        # Tabla de detalle
        self.set_fill_color(91, 141, 184)
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 11)
        self.cell(80, 10, sanitize_text('Descripción'), 1, 0, 'C', 1)
        self.cell(25, 10, sanitize_text('Cant.'), 1, 0, 'C', 1)
        self.cell(35, 10, sanitize_text('P. Unit.'), 1, 0, 'C', 1)
        self.cell(50, 10, sanitize_text('Importe'), 1, 1, 'C', 1)
        
        # Detalle items
        self.set_font('Arial', '', 10)
        self.set_text_color(0, 0, 0)
        subtotal = 0
        
        for i, item in enumerate(detalle_items):
            if i % 2 == 0:
                self.set_fill_color(250, 250, 250)
            else:
                self.set_fill_color(240, 240, 240)
            
            concepto = item.get('concepto', '')[:40]
            cantidad = item.get('cantidad', 1)
            precio = float(item.get('precio_unitario', 0))
            importe = float(item.get('importe', precio * cantidad))
            subtotal += importe
            
            self.cell(80, 8, sanitize_text(concepto), 1, 0, 'L', 1)
            self.cell(25, 8, sanitize_text(str(cantidad)), 1, 0, 'C', 1)
            self.cell(35, 8, sanitize_text(f"S/ {precio:,.2f}"), 1, 0, 'R', 1)
            self.cell(50, 8, sanitize_text(f"S/ {importe:,.2f}"), 1, 1, 'R', 1)
        
        # Totales
        impuestos = float(factura_data.get('impuestos', 0))
        total = float(factura_data.get('total', subtotal + impuestos))
        
        self.ln(5)
        self.set_font('Arial', '', 11)
        self.cell(130, 8, sanitize_text('Subtotal:'), 0, 0, 'R')
        self.cell(60, 8, sanitize_text(f"S/ {subtotal:,.2f}"), 0, 1, 'R')
        
        self.cell(130, 8, sanitize_text('IGV (18%):'), 0, 0, 'R')
        self.cell(60, 8, sanitize_text(f"S/ {impuestos:,.2f}"), 0, 1, 'R')
        
        self.set_font('Arial', 'B', 14)
        self.set_text_color(44, 74, 127)
        self.cell(130, 10, sanitize_text('TOTAL:'), 0, 0, 'R')
        self.cell(60, 10, sanitize_text(f"S/ {total:,.2f}"), 0, 1, 'R')
        
        # Método de pago
        if factura_data.get('metodo_pago'):
            self.ln(5)
            self.set_font('Arial', '', 10)
            self.set_text_color(0, 0, 0)
            self.cell(0, 7, sanitize_text(f'Método de pago: {factura_data["metodo_pago"].capitalize()}'), 0, 1, 'L')
        
        # Notas
        if factura_data.get('notas'):
            self.ln(5)
            self.set_font('Arial', 'I', 9)
            self.set_text_color(100, 100, 100)
            self.multi_cell(0, 5, sanitize_text(f'Notas: {factura_data["notas"]}'))
        
        # Línea final
        self.ln(10)
        self.set_draw_color(91, 141, 184)
        self.set_line_width(0.5)
        self.line(20, self.get_y(), 190, self.get_y())
        
        # Pie de página
        self.ln(5)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 4, sanitize_text('Gracias por su preferencia'), 0, 1, 'C')
        self.cell(0, 4, sanitize_text('Esta factura es válida como comprobante de pago'), 0, 1, 'C')
    
    def create_kpi_report(self, kpis, fecha_inicio, fecha_fin, dias_periodo, revpar):
        """Genera reporte PDF de KPIs (Rendimiento Hotelero)"""
        self.add_page()
        
        # Encabezado
        self.set_font('Arial', 'B', 22)
        self.set_text_color(91, 141, 184)
        self.cell(0, 15, sanitize_text('Hotel Mirador Andino'), 0, 1, 'C')
        
        self.set_font('Arial', 'I', 12)
        self.set_text_color(80, 80, 80)
        self.cell(0, 8, sanitize_text('Reporte de Rendimiento Hotelero'), 0, 1, 'C')
        self.ln(8)
        
        # Línea decorativa doble
        self.set_draw_color(91, 141, 184)
        self.set_line_width(1)
        self.line(30, self.get_y(), 180, self.get_y())
        self.set_line_width(0.2)
        self.line(30, self.get_y() + 2, 180, self.get_y() + 2)
        self.ln(10)
        
        # Período
        self.set_fill_color(240, 240, 240)
        self.set_draw_color(91, 141, 184)
        self.rect(30, self.get_y(), 150, 12, 'FD')
        self.set_xy(30, self.get_y())
        self.set_font('Arial', 'B', 10)
        self.set_text_color(44, 74, 127)
        self.cell(40, 12, sanitize_text('Período:'), 0, 0, 'L')
        self.set_font('Arial', '', 10)
        self.set_text_color(0, 0, 0)
        self.cell(110, 12, sanitize_text(f'{fecha_inicio.strftime("%d/%m/%Y")} - {fecha_fin.strftime("%d/%m/%Y")}'), 0, 1, 'L')
        self.ln(8)
        
        # Fecha de generación
        self.set_font('Arial', 'I', 9)
        self.set_text_color(100, 100, 100)
        self.cell(0, 6, sanitize_text(f'Generado: {datetime.now().strftime("%d/%m/%Y %H:%M")}'), 0, 1, 'R')
        self.ln(8)
        
        # Título de tabla
        self.set_fill_color(91, 141, 184)
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 14)
        self.cell(0, 12, sanitize_text('INDICADORES CLAVE DE RENDIMIENTO (KPIs)'), 1, 1, 'C', 1)
        self.ln(5)
        
        # Preparar datos de KPIs
        estancia = kpis.get('estancia_promedio', 0)
        if estancia is None:
            estancia = 0
            
        kpis_data = [
            ('Total Reservas', f'{kpis["total_reservas"]}'),
            ('Ingresos Totales', f'S/ {float(kpis["ingresos_totales"]):,.2f}'),
            ('Estancia Promedio', f'{float(estancia):.1f} días'),
            ('Huéspedes Únicos', f'{kpis["huespedes_unicos"]}'),
            ('Tasa Cancelación', f'{float(kpis["tasa_cancelacion"]):.1f}%'),
            ('Tarifa Promedio', f'S/ {float(kpis["tarifa_promedio"]):,.2f}'),
            ('RevPAR', f'S/ {revpar:,.2f}')
        ]
        
        # Tabla de KPIs
        self.set_font('Arial', '', 11)
        self.set_text_color(0, 0, 0)
        
        for i, (metrica, valor) in enumerate(kpis_data):
            if i % 2 == 0:
                self.set_fill_color(250, 250, 250)
            else:
                self.set_fill_color(240, 240, 240)
            
            self.cell(90, 10, sanitize_text(metrica), 1, 0, 'L', 1)
            self.cell(90, 10, sanitize_text(valor), 1, 1, 'R', 1)
        
        self.ln(10)
        
        # Información adicional
        self.set_font('Arial', 'B', 10)
        self.set_text_color(44, 74, 127)
        self.cell(0, 8, sanitize_text('Notas:'), 0, 1, 'L')
        
        self.set_font('Arial', '', 9)
        self.set_text_color(80, 80, 80)
        self.cell(0, 5, sanitize_text('• RevPAR: Revenue per Available Room (Ingreso por Habitación Disponible)'), 0, 1, 'L')
        self.cell(0, 5, sanitize_text(f'• Período analizado: {dias_periodo} días'), 0, 1, 'L')
        self.cell(0, 5, sanitize_text(f'• Total habitaciones: {kpis["total_habitaciones"]}'), 0, 1, 'L')
        
        # Línea final decorativa
        self.ln(5)
        self.set_draw_color(91, 141, 184)
        self.set_line_width(0.5)
        self.line(20, self.get_y(), 190, self.get_y())
    
    def create_guests_report(self, df, fecha_inicio, fecha_fin, top):
        """Genera reporte PDF de Análisis de Huéspedes"""
        self.add_page()
        
        # Encabezado
        self.set_font('Arial', 'B', 22)
        self.set_text_color(91, 141, 184)
        self.cell(0, 15, sanitize_text('Hotel Mirador Andino'), 0, 1, 'C')
        
        self.set_font('Arial', 'I', 12)
        self.set_text_color(80, 80, 80)
        self.cell(0, 8, sanitize_text('Reporte de Análisis de Huéspedes'), 0, 1, 'C')
        self.ln(8)
        
        # Línea decorativa
        self.set_draw_color(91, 141, 184)
        self.set_line_width(1)
        self.line(30, self.get_y(), 180, self.get_y())
        self.ln(10)
        
        # Período
        self.set_fill_color(240, 240, 240)
        self.set_font('Arial', 'B', 10)
        self.set_text_color(44, 74, 127)
        self.cell(40, 8, sanitize_text('Período:'), 0, 0, 'L')
        self.set_font('Arial', '', 10)
        self.set_text_color(0, 0, 0)
        self.cell(0, 8, sanitize_text(f'{fecha_inicio.strftime("%d/%m/%Y")} - {fecha_fin.strftime("%d/%m/%Y")}'), 0, 1, 'L')
        self.ln(5)
        
        # Fecha de generación
        self.set_font('Arial', 'I', 9)
        self.set_text_color(100, 100, 100)
        self.cell(0, 6, sanitize_text(f'Generado: {datetime.now().strftime("%d/%m/%Y %H:%M")}'), 0, 1, 'R')
        self.ln(8)
        
        # Resumen ejecutivo
        self.set_fill_color(91, 141, 184)
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 14)
        self.cell(0, 12, sanitize_text('RESUMEN EJECUTIVO'), 1, 1, 'C', 1)
        self.ln(5)
        
        # Tabla de resumen
        self.set_font('Arial', '', 11)
        self.set_text_color(0, 0, 0)
        
        resumen_data = [
            ('Nuevos Huéspedes:', f'{len(df)}'),
            ('Total Reservas:', f'{int(df["total_reservas"].sum())}'),
            ('Ingresos Totales:', f'S/ {df["total_consumido"].sum():,.2f}')
        ]
        
        for i, (label, valor) in enumerate(resumen_data):
            if i % 2 == 0:
                self.set_fill_color(250, 250, 250)
            else:
                self.set_fill_color(240, 240, 240)
            
            self.cell(50, 10, sanitize_text(label), 1, 0, 'L', 1)
            self.cell(140, 10, sanitize_text(valor), 1, 1, 'R', 1)
        
        self.ln(10)
        
        # Top 10 Huéspedes
        self.set_fill_color(91, 141, 184)
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 14)
        self.cell(0, 12, sanitize_text('TOP 10 HUÉSPEDES POR CONSUMO'), 1, 1, 'C', 1)
        self.ln(5)
        
        # Cabecera de tabla
        self.set_font('Arial', 'B', 9)
        self.set_fill_color(91, 141, 184)
        self.set_text_color(255, 255, 255)
        self.cell(45, 10, sanitize_text('Nombre'), 1, 0, 'C', 1)
        self.cell(45, 10, sanitize_text('Apellido'), 1, 0, 'C', 1)
        self.cell(30, 10, sanitize_text('Reservas'), 1, 0, 'C', 1)
        self.cell(45, 10, sanitize_text('Total Consumido'), 1, 0, 'C', 1)
        self.cell(25, 10, sanitize_text('VIP'), 1, 1, 'C', 1)
        
        # Datos
        self.set_font('Arial', '', 8)
        self.set_text_color(0, 0, 0)
        
        for i, (_, row) in enumerate(top.iterrows()):
            if i % 2 == 0:
                self.set_fill_color(250, 250, 250)
            else:
                self.set_fill_color(240, 240, 240)
            
            self.cell(45, 8, sanitize_text(row['nombre'][:25]), 1, 0, 'L', 1)
            self.cell(45, 8, sanitize_text(row['apellido'][:25]), 1, 0, 'L', 1)
            self.cell(30, 8, sanitize_text(str(int(row['total_reservas']))), 1, 0, 'C', 1)
            self.cell(45, 8, sanitize_text(f"S/ {row['total_consumido']:,.2f}"), 1, 0, 'R', 1)
            self.cell(25, 8, sanitize_text('⭐' if '⭐' in str(row['es_vip']) else ''), 1, 1, 'C', 1)
        
        self.ln(10)
        
        # Nacionalidades (si hay datos)
        if 'nacionalidad' in df.columns and df['nacionalidad'].notna().any():
            self.set_fill_color(91, 141, 184)
            self.set_text_color(255, 255, 255)
            self.set_font('Arial', 'B', 12)
            self.cell(0, 10, sanitize_text('DISTRIBUCIÓN POR NACIONALIDAD'), 1, 1, 'C', 1)
            self.ln(5)
            
            nac_counts = df[df['nacionalidad'].notna()]['nacionalidad'].value_counts().head(5)
            
            self.set_font('Arial', '', 10)
            self.set_text_color(0, 0, 0)
            
            for i, (pais, count) in enumerate(nac_counts.items()):
                if i % 2 == 0:
                    self.set_fill_color(250, 250, 250)
                else:
                    self.set_fill_color(240, 240, 240)
                
                self.cell(100, 8, sanitize_text(f'{pais}:'), 1, 0, 'L', 1)
                self.cell(90, 8, sanitize_text(f'{count} huéspedes'), 1, 1, 'R', 1)
        
        # Línea final
        self.ln(5)
        self.set_draw_color(91, 141, 184)
        self.set_line_width(0.5)
        self.line(20, self.get_y(), 190, self.get_y())