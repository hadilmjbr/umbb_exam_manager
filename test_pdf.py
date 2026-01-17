from backend.pdf_gen import generate_schedule_pdf
import pandas as pd
from datetime import datetime

print("Testing PDF Generation...")
data = {
    'module': ['Maths', 'Physique'],
    'date_heure': [datetime(2026, 6, 1, 9, 0), datetime(2026, 6, 2, 14, 0)],
    'salle': ['A101', 'B202'],
    'fake_col': ['Ignore', 'Me']
}
df = pd.DataFrame(data)

try:
    pdf = generate_schedule_pdf(
        "Test Title", "Test Subtitle", df, 
        {'module': 'Module', 'date_heure': 'Date', 'salle': 'Salle'}
    )
    print(f"PDF Generated successfully. Size: {len(pdf.getvalue())} bytes")
except Exception as e:
    print(f"PDF Generation Failed: {e}")
