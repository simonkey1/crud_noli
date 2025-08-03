# services/pdf_service.py

from typing import Tuple, List, Optional, Dict, Any
from datetime import datetime, date
from sqlmodel import Session, select
from io import BytesIO
from models.order import CierreCaja, Orden
import logging

logger = logging.getLogger(__name__)

def generar_pdf_cierre(db: Session, cierre_id: int) -> Tuple[bytes, str]:
    """
    Genera un PDF con los detalles del cierre de caja.
    
    Args:
        db: Sesión de base de datos
        cierre_id: ID del cierre de caja
    
    Returns:
        Tupla con (contenido_pdf, nombre_archivo)
    """
    from io import BytesIO
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import cm
    
    # Obtener el cierre con sus transacciones
    cierre = db.get(CierreCaja, cierre_id)
    
    if not cierre:
        raise ValueError(f"Cierre no encontrado: {cierre_id}")
    
    # Obtener las transacciones asociadas al cierre
    query = select(Orden).where(Orden.cierre_id == cierre_id)
    transacciones = db.exec(query).all()
    
    # Crear un buffer para almacenar el PDF
    buffer = BytesIO()
    
    # Crear el documento PDF
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    # Estilos para el PDF
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    subtitle_style = styles['Heading2']
    normal_style = styles['Normal']
    
    # Título
    elements.append(Paragraph(f"Cierre de Caja #{cierre.id}", title_style))
    elements.append(Spacer(1, 12))
    
    # Información general del cierre
    elements.append(Paragraph("Información General", subtitle_style))
    
    # Formatear fechas
    fecha_formateada = cierre.fecha.strftime('%d/%m/%Y')
    fecha_cierre_formateada = cierre.fecha_cierre.strftime('%d/%m/%Y %H:%M')
    
    # Datos generales en formato de tabla
    data = [
        ["ID:", str(cierre.id)],
        ["Fecha:", fecha_formateada],
        ["Hora de Cierre:", fecha_cierre_formateada],
        ["Total de Ventas:", f"${cierre.total_ventas:,.0f}"],
        ["Total de Transacciones:", str(cierre.cantidad_transacciones)],
        ["Ticket Promedio:", f"${cierre.ticket_promedio:,.0f}"]
    ]
    
    # Si hay usuario, añadir a la tabla
    if cierre.usuario_nombre:
        data.append(["Usuario:", cierre.usuario_nombre])
    
    t = Table(data, colWidths=[100, 300])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (1, 0), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(t)
    elements.append(Spacer(1, 20))
    
    # Desglose por método de pago
    elements.append(Paragraph("Desglose por Método de Pago", subtitle_style))
    
    metodos_data = [
        ["Método", "Monto"],
        ["Efectivo", f"${cierre.total_efectivo:,.0f}"],
        ["Débito", f"${cierre.total_debito:,.0f}"],
        ["Crédito", f"${cierre.total_credito:,.0f}"],
        ["Transferencia", f"${cierre.total_transferencia:,.0f}"],
        ["TOTAL", f"${cierre.total_ventas:,.0f}"]
    ]
    
    metodos_table = Table(metodos_data, colWidths=[150, 150])
    metodos_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),  # Fila total
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 1), (-1, -2), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(metodos_table)
    elements.append(Spacer(1, 20))
    
    # Información de rentabilidad
    elements.append(Paragraph("Información de Rentabilidad", subtitle_style))
    
    rentabilidad_data = [
        ["Concepto", "Valor"],
        ["Costo de Productos", f"${cierre.total_costo:,.0f}"],
        ["Ganancia", f"${cierre.total_ganancia:,.0f}"],
        ["Margen Promedio", f"{cierre.margen_promedio:.2f}%"]
    ]
    
    rentabilidad_table = Table(rentabilidad_data, colWidths=[150, 150])
    rentabilidad_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(rentabilidad_table)
    elements.append(Spacer(1, 20))
    
    # Listado de transacciones
    if transacciones:
        elements.append(Paragraph("Detalle de Transacciones", subtitle_style))
        
        # Cabecera de la tabla de transacciones
        transacciones_data = [["ID", "Hora", "Método", "Estado", "Subtotal", "Descuento", "Total"]]
        
        # Agregar cada transacción
        for t in transacciones:
            hora = t.fecha.strftime('%H:%M')
            subtotal = t.subtotal or t.total
            descuento = t.descuento or 0
            
            transacciones_data.append([
                str(t.id),
                hora,
                t.metodo_pago.capitalize(),
                t.estado.capitalize(),
                f"${subtotal:,.0f}",
                f"${descuento:,.0f}" if descuento > 0 else "-",
                f"${t.total:,.0f}"
            ])
        
        # Crear tabla de transacciones
        trans_table = Table(transacciones_data, colWidths=[40, 40, 70, 70, 70, 70, 70])
        trans_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(trans_table)
    
    # Notas
    if cierre.notas:
        elements.append(Spacer(1, 20))
        elements.append(Paragraph("Notas:", subtitle_style))
        elements.append(Paragraph(cierre.notas, normal_style))
    
    # Construir el PDF
    doc.build(elements)
    
    # Obtener el contenido del buffer
    pdf_contenido = buffer.getvalue()
    buffer.close()
    
    # Nombre del archivo
    fecha_str = cierre.fecha.strftime('%Y%m%d')
    pdf_nombre = f"cierre_caja_{cierre.id}_{fecha_str}.pdf"
    
    return pdf_contenido, pdf_nombre
    
def generar_pdf_reporte_periodo(db: Session, cierres: List[CierreCaja], resumen: Dict[str, Any], filtros: Dict[str, Any]) -> Tuple[bytes, str]:
    """
    Genera un PDF con el reporte de un período de tiempo.
    
    Args:
        db: Sesión de base de datos
        cierres: Lista de objetos CierreCaja del período
        resumen: Diccionario con los totales y estadísticas del período
        filtros: Filtros aplicados al reporte
    
    Returns:
        Tupla con (contenido_pdf, nombre_archivo)
    """
    from io import BytesIO
    from reportlab.lib.pagesizes import letter, landscape
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import inch
    
    # Crear un buffer para almacenar el PDF
    buffer = BytesIO()
    
    # Crear el documento PDF en orientación horizontal
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))
    elements = []
    
    # Estilos para el PDF
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    subtitle_style = styles['Heading2']
    normal_style = styles['Normal']
    
    # Título
    periodo = resumen.get("periodo", "completo")
    elements.append(Paragraph(f"Reporte de Período: {periodo}", title_style))
    elements.append(Spacer(1, 12))
    
    # Información del resumen en formato de tabla
    elements.append(Paragraph("Resumen del Período", subtitle_style))
    elements.append(Spacer(1, 6))
    
    # Datos generales en formato de tabla
    resumen_data = [
        ["Total Ventas:", f"${resumen['total_ventas']:,.0f}", "Transacciones:", f"{resumen['total_transacciones']}"],
        ["Efectivo:", f"${resumen['total_efectivo']:,.0f}", "Ticket Promedio:", f"${resumen['ticket_promedio']:,.0f}"],
        ["Transferencia:", f"${resumen['total_transferencia']:,.0f}", "Venta Promedio Diaria:", f"${resumen['promedio_diario']:,.0f}"],
        ["Débito:", f"${resumen['total_debito']:,.0f}", "", ""],
        ["Crédito:", f"${resumen['total_credito']:,.0f}", "", ""],
        ["Otros:", f"${resumen['total_otros']:,.0f}", "", ""],
    ]
    
    t = Table(resumen_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('BACKGROUND', (2, 0), (2, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (1, -1), 1, colors.black),
        ('GRID', (2, 0), (3, -1), 1, colors.black),
    ]))
    
    elements.append(t)
    elements.append(Spacer(1, 20))
    
    # Lista de cierres
    if cierres:
        elements.append(Paragraph("Cierres de Caja en el Período", subtitle_style))
        elements.append(Spacer(1, 6))
        
        # Cabecera de la tabla de cierres
        cierres_data = [["ID", "Fecha", "Ventas", "Efectivo", "Transferencia", "Débito", "Crédito", "Transacciones", "Ticket Promedio"]]
        
        # Agregar cada cierre
        for cierre in cierres:
            fecha = cierre.fecha.strftime('%d/%m/%Y') if cierre.fecha else "N/A"
            cierres_data.append([
                str(cierre.id),
                fecha,
                f"${cierre.total_ventas:,.0f}",
                f"${cierre.total_efectivo:,.0f}",
                f"${cierre.total_transferencia:,.0f}",
                f"${cierre.total_debito:,.0f}",
                f"${cierre.total_credito:,.0f}",
                str(cierre.cantidad_transacciones),
                f"${cierre.ticket_promedio:,.0f}"
            ])
        
        # Crear tabla de cierres
        cierres_table = Table(cierres_data, repeatRows=1)
        cierres_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(cierres_table)
    else:
        elements.append(Paragraph("No hay cierres de caja en el período seleccionado.", normal_style))
    
    # Construir el PDF
    doc.build(elements)
    
    # Obtener el contenido del buffer
    pdf_contenido = buffer.getvalue()
    buffer.close()
    
    # Determinar el rango de fechas para el nombre del archivo
    desde = filtros.get("fecha_desde", "").strftime("%Y%m%d") if filtros.get("fecha_desde") else "inicio"
    hasta = filtros.get("fecha_hasta", "").strftime("%Y%m%d") if filtros.get("fecha_hasta") else "actual"
    
    # Nombre del archivo
    pdf_nombre = f"reporte_periodo_{desde}_a_{hasta}.pdf"
    
    return pdf_contenido, pdf_nombre
