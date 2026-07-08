from fpdf import FPDF
from datetime import datetime
import io

# 1. Definisi Kelas HARUS di atas fungsi
class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "Laporan Inventaris Gudang", 0, 1, "C")
        self.set_font("Arial", "", 10)
        self.cell(0, 10, f"Tanggal: {datetime.now().strftime('%d-%m-%Y')}", 0, 1, "C")
        self.ln(5)

# 2. Fungsi baru menggunakan kelas PDF di atas
def export_to_pdf(df):
    pdf = PDF() # Sekarang Python tahu apa itu PDF karena sudah didefinisikan di atas
    pdf.add_page()
    pdf.set_font("Arial", size=10)

    # Header Tabel
    col_width = 190 / len(df.columns)
    for col in df.columns:
        pdf.cell(col_width, 10, str(col), border=1, align="C")
    pdf.ln()

    # Isi Tabel
    for row in df.itertuples(index=False):
        for item in row:
            pdf.cell(col_width, 10, str(item), border=1, align="C")
        pdf.ln()

    # Konversi ke format yang bisa dibaca Streamlit
    return pdf.output(dest='S').encode('latin-1')
