import io
from fpdf import FPDF
from datetime import datetime

# Pastikan kelas PDF sudah didefinisikan sebelumnya
class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "Laporan Inventaris Gudang", 0, 1, "C")
        self.ln(5)

def export_to_pdf(df):
    pdf = PDF()
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

    # KONVERSI KE BYTES YANG BENAR:
    # 1. Simpan output ke dalam buffer bytes
    buffer = io.BytesIO()
    # 2. Gunakan output() untuk menulis ke buffer (fpdf2 mendukung ini)
    pdf.output(buffer)
    # 3. Ambil nilai bytes dari buffer
    return buffer.getvalue()
