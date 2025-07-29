# services/transacciones_service.py

from sqlmodel import Session, select
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, date, timedelta
import json

from models.order import Orden, CierreCaja
from schemas.order import OrdenRead, OrdenUpdate, OrdenFiltro

def obtener_transacciones(
    db: Session, 
    filtros: Optional[Dict[str, Any]] = None
) -> List[Orden]:
    """
    Obtiene una lista de transacciones aplicando filtros opcionales.
    
    Args:
        db: Sesión de base de datos
        filtros: Diccionario con filtros a aplicar
        
    Returns:
        Lista de transacciones filtradas
    """
    query = select(Orden)
    
    if filtros:
        if "fecha_desde" in filtros and filtros["fecha_desde"]:
            query = query.where(Orden.fecha >= filtros["fecha_desde"])
        
        if "fecha_hasta" in filtros and filtros["fecha_hasta"]:
            fecha_fin = filtros["fecha_hasta"].replace(hour=23, minute=59, second=59)
            query = query.where(Orden.fecha <= fecha_fin)
        
        if "metodo_pago" in filtros and filtros["metodo_pago"]:
            query = query.where(Orden.metodo_pago == filtros["metodo_pago"])
        
        if "estado" in filtros and filtros["estado"]:
            query = query.where(Orden.estado == filtros["estado"])
        
        if "cierre_caja_id" in filtros and filtros["cierre_caja_id"] is not None:
            if filtros["cierre_caja_id"] == 0:  # 0 significa sin cierre
                query = query.where(Orden.cierre_id == None)
            else:
                query = query.where(Orden.cierre_id == filtros["cierre_caja_id"])
    
    # Ordenar por fecha descendente (más recientes primero)
    query = query.order_by(Orden.fecha.desc())
    
    return db.exec(query).all()

def obtener_transaccion_por_id(db: Session, transaccion_id: int) -> Optional[Orden]:
    """
    Obtiene una transacción por su ID.
    
    Args:
        db: Sesión de base de datos
        transaccion_id: ID de la transacción
    
    Returns:
        Objeto Orden o None si no existe
    """
    return db.get(Orden, transaccion_id)

def actualizar_estado_transaccion(
    db: Session, 
    transaccion_id: int, 
    nuevo_estado: str
) -> Optional[Orden]:
    """
    Actualiza el estado de una transacción.
    
    Args:
        db: Sesión de base de datos
        transaccion_id: ID de la transacción
        nuevo_estado: Nuevo estado (aprobada, anulada, reembolsada)
    
    Returns:
        Transacción actualizada o None si no existe
    """
    transaccion = db.get(Orden, transaccion_id)
    
    if not transaccion:
        return None
    
    if nuevo_estado not in ["aprobada", "anulada", "reembolsada"]:
        raise ValueError(f"Estado no válido: {nuevo_estado}")
    
    transaccion.estado = nuevo_estado
    transaccion.fecha_actualizacion = datetime.now()
    
    db.add(transaccion)
    db.commit()
    db.refresh(transaccion)
    
    return transaccion

def verificar_transferencia_bancaria(
    db: Session, 
    transaccion_id: int, 
    verificada: bool = True
) -> Optional[Orden]:
    """
    Marca una transferencia bancaria como verificada o no verificada.
    
    Args:
        db: Sesión de base de datos
        transaccion_id: ID de la transacción
        verificada: Estado de verificación
    
    Returns:
        Transacción actualizada o None si no existe
    """
    transaccion = db.get(Orden, transaccion_id)
    
    if not transaccion:
        return None
    
    if transaccion.metodo_pago != "transferencia":
        raise ValueError("Esta transacción no es una transferencia bancaria")
    
    # Inicializar datos_adicionales si es None
    if not transaccion.datos_adicionales:
        transaccion.datos_adicionales = {}
    
    # Actualizar estado de verificación
    transaccion.datos_adicionales["transferencia_verificada"] = verificada
    transaccion.datos_adicionales["fecha_verificacion"] = datetime.now().isoformat()
    
    # Asegurar que los datos adicionales se guardan como JSON
    if isinstance(transaccion.datos_adicionales, dict):
        transaccion.datos_adicionales = json.dumps(transaccion.datos_adicionales)
    
    db.add(transaccion)
    db.commit()
    db.refresh(transaccion)
    
    return transaccion

def generar_pdf_transaccion(db: Session, transaccion_id: int) -> Tuple[bytes, str]:
    """
    Genera un PDF con los detalles de una transacción.
    
    Args:
        db: Sesión de base de datos
        transaccion_id: ID de la transacción
    
    Returns:
        Tupla con (contenido_pdf, nombre_archivo)
    """
    from sqlmodel import select
    from io import BytesIO
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    
    # Obtener la transacción con todos sus items
    query = select(Orden).where(Orden.id == transaccion_id)
    transaccion = db.exec(query).first()
    
    if not transaccion:
        raise ValueError(f"Transacción no encontrada: {transaccion_id}")
    
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
    elements.append(Paragraph(f"Factura de Venta #{transaccion.id}", title_style))
    elements.append(Spacer(1, 12))
    
    # Información de la transacción
    elements.append(Paragraph("Información de la Transacción", subtitle_style))
    
    # Datos generales en formato de tabla
    fecha_formateada = transaccion.fecha.strftime('%d/%m/%Y %H:%M')
    data = [
        ["ID:", str(transaccion.id)],
        ["Fecha:", fecha_formateada],
        ["Estado:", transaccion.estado],
        ["Método de Pago:", transaccion.metodo_pago],
        ["Total:", f"${transaccion.total:,.0f}"]
    ]
    
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
    
    # Productos
    elements.append(Paragraph("Productos", subtitle_style))
    
    # Cabecera de la tabla de productos
    productos_data = [["Producto", "Cantidad", "Precio Unitario", "Subtotal"]]
    
    # Agregar cada producto
    for item in transaccion.items:
        subtotal = item.cantidad * item.precio_unitario
        productos_data.append([
            item.producto.nombre if hasattr(item.producto, 'nombre') else "Producto desconocido",
            str(item.cantidad),
            f"${item.precio_unitario:,.0f}",
            f"${subtotal:,.0f}"
        ])
    
    # Crear tabla de productos
    productos_table = Table(productos_data, colWidths=[200, 70, 100, 100])
    productos_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(productos_table)
    
    # Construir el PDF
    doc.build(elements)
    
    # Obtener el contenido del buffer
    pdf_contenido = buffer.getvalue()
    buffer.close()
    
    # Nombre del archivo
    pdf_nombre = f"transaccion_{transaccion_id}_{datetime.now().strftime('%Y%m%d')}.pdf"
    
    return pdf_contenido, pdf_nombre

def enviar_email_transaccion(
    db: Session, 
    transaccion_id: int, 
    email_destinatario: str
) -> bool:
    """
    Envía un email con los detalles de la transacción y un PDF adjunto.
    
    Args:
        db: Sesión de base de datos
        transaccion_id: ID de la transacción
        email_destinatario: Dirección de email del destinatario
    
    Returns:
        True si el email se envió correctamente, False en caso contrario
    """
    import smtplib
    import ssl
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.mime.application import MIMEApplication
    from core.config import settings
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        # Mostrar información de diagnóstico
        logger.info(f"Configuración de correo: HOST={settings.EMAIL_HOST}, PORT={settings.EMAIL_PORT}, "
                   f"USERNAME={settings.EMAIL_USERNAME[:3]}{'*'*(len(settings.EMAIL_USERNAME)-6)}{settings.EMAIL_USERNAME[-3:]}")
        
        # Obtener la transacción
        transaccion = db.get(Orden, transaccion_id)
        if not transaccion:
            raise ValueError(f"Transacción no encontrada: {transaccion_id}")
        
        # Generar el PDF
        pdf_contenido, pdf_nombre = generar_pdf_transaccion(db, transaccion_id)
        
        # Crear el mensaje
        mensaje = MIMEMultipart()
        mensaje["From"] = settings.EMAIL_FROM
        mensaje["To"] = email_destinatario
        mensaje["Subject"] = f"Factura de compra #{transaccion.id}"
        
        # Cuerpo del correo
        texto = f"""
        Estimado cliente,
        
        Adjunto encontrará la factura de su compra #{transaccion.id}.
        
        Detalles de la transacción:
        - Fecha: {transaccion.fecha.strftime('%d/%m/%Y %H:%M')}
        - Total: ${transaccion.total:,.0f}
        - Método de pago: {transaccion.metodo_pago}
        
        Gracias por su compra.
        
        Atentamente,
        El equipo de ventas
        """
        
        mensaje.attach(MIMEText(texto, "plain"))
        
        # Adjuntar el PDF
        attachment = MIMEApplication(pdf_contenido)
        attachment.add_header(
            "Content-Disposition", 
            f"attachment; filename={pdf_nombre}"
        )
        mensaje.attach(attachment)
        
        # Configurar el servidor SMTP
        context = ssl.create_default_context()
        
        # Intentar enviar el correo
        logger.info(f"Conectando a servidor SMTP {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
        with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
            if settings.EMAIL_USE_TLS:
                logger.info("Iniciando TLS")
                server.starttls(context=context)
            
            logger.info(f"Iniciando sesión con usuario {settings.EMAIL_USERNAME}")
            server.login(settings.EMAIL_USERNAME, settings.EMAIL_PASSWORD)
            
            logger.info(f"Enviando mensaje a {email_destinatario}")
            server.send_message(mensaje)
        
        logger.info(f"Email enviado correctamente a {email_destinatario}")
        return True
        
    except Exception as e:
        logger.error(f"Error al enviar email: {str(e)}")
        return False
