from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
import pandas as pd

def generate_schedule_pdf(title, subtitle, df_schedule, columns_map):
    """
    Generates a PDF for the schedule.
    df_schedule: DataFrame containing the data
    columns_map: Dict mapping DataFrame columns to PDF table headers {col_name: header_name}
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []

    styles = getSampleStyleSheet()
    title_style = styles['Title']
    subtitle_style = styles['Normal'] # or Heading2

    # Title
    elements.append(Paragraph(title, title_style))
    elements.append(Spacer(1, 12))
    
    # Subtitle (Info line)
    elements.append(Paragraph(subtitle, subtitle_style))
    elements.append(Spacer(1, 24))

    # Prepare data for Table
    # Filter and reorder columns
    cols_to_use = [c for c in columns_map.keys() if c in df_schedule.columns]
    
    if not cols_to_use:
        elements.append(Paragraph("Aucune donnée à afficher", styles['Normal']))
    else:
        # Headers
        headers = [columns_map[c] for c in cols_to_use]
        data = [headers]
        
        # Rows
        for _, row in df_schedule.iterrows():
            row_data = []
            for col in cols_to_use:
                val = row[col]
                if pd.api.types.is_datetime64_any_dtype(val):
                    val = val.strftime("%Y-%m-%d %H:%M")
                row_data.append(str(val))
            data.append(row_data)

        # Table Style
        t = Table(data)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(t)

    doc.build(elements)
    buffer.seek(0)
    return buffer
