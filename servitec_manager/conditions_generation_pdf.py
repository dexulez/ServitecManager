from reportlab.lib.pagesizes import A5, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Frame, PageTemplate
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER

def crear_pdf_condiciones():
    # Configuración del archivo
    nombre_archivo = "assets/Terminos_Servitec_A5.pdf"
    doc = SimpleDocTemplate(nombre_archivo, pagesize=landscape(A5),
                            rightMargin=30, leftMargin=30,
                            topMargin=30, bottomMargin=30)

    estilos = getSampleStyleSheet()
    
    # Estilos personalizados
    estilo_titulo = ParagraphStyle(
        'TituloPersonalizado',
        parent=estilos['Heading1'],
        fontSize=14,
        alignment=TA_CENTER,
        spaceAfter=15
    )
    
    estilo_cuerpo = ParagraphStyle(
        'CuerpoPersonalizado',
        parent=estilos['BodyText'],
        fontSize=9,
        leading=11,  # Interlineado
        alignment=TA_JUSTIFY,
        spaceAfter=6
    )

    estilo_firma = ParagraphStyle(
        'Firma',
        parent=estilos['BodyText'],
        fontSize=8,
        alignment=TA_CENTER,
        spaceBefore=25
    )

    contenido = []

    # Título
    titulo = "CLÁUSULAS Y CONDICIONES PARA LA RECEPCIÓN DE EQUIPOS<br/>IMPORTADORA Y SERVICIOS SERVITEC SPA"
    contenido.append(Paragraph(titulo, estilo_titulo))

    # Lista de condiciones (Texto formateado)
    textos = [
        "<b>1. PROPIEDAD:</b> El cliente declara que los datos y el equipo entregado son de su propiedad o es totalmente responsable del mismo, eximiendo de responsabilidad legal o de procedencia a la empresa.",
        "<b>2. RIESGO:</b> Todo equipo marcado como <b>RIESGOSO</b> tiene probabilidad de daño permanente. El cliente acepta este riesgo bajo acuerdo mutuo.",
        "<b>3. EQUIPOS MOJADOS:</b> Se consideran reparación RIESGOSA. Todo equipo mojado pierde cualquier garantía después de la entrega.",
        "<b>4. PANTALLA APAGADA:</b> Equipos ingresados con pantalla apagada <b>NO TIENEN GARANTÍA</b>. El cliente autoriza su reparación consciente de esto.",
        "<b>5. GARANTÍA:</b> La empresa no se hace responsable por daños ocasionados por mal uso o imprudencia. <b>Pantallas y Glases NO TIENEN GARANTÍA.</b>",
        "<b>6. RETIRO:</b> La empresa no se hace responsable del equipo si no es retirado pasados <b>sesenta (60) días</b> de la fecha de entrega pautada.",
        "<b>7. ACEPTACIÓN:</b> El cliente declara haber leído y aceptado estas condiciones al momento de firmar."
    ]

    for texto in textos:
        p = Paragraph(texto, estilo_cuerpo)
        contenido.append(p)

    # Nota de validez
    contenido.append(Spacer(1, 10))
    nota_validez = "<b>NOTA: Documento válido SÓLO con firma de funcionario y sello de la empresa.</b>"
    contenido.append(Paragraph(nota_validez, ParagraphStyle('Nota', parent=estilo_cuerpo, alignment=TA_CENTER)))

    # Espacio para firmas (lado a lado simulado con espacios)
    contenido.append(Spacer(1, 10))
    firmas = "_________________________&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_________________________<br/>Firma Cliente&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Sello y Firma Empresa"
    contenido.append(Paragraph(firmas, estilo_firma))

    # Construir PDF
    doc.build(contenido)
    print(f"PDF generado exitosamente: {nombre_archivo}")

if __name__ == "__main__":
    crear_pdf_condiciones()