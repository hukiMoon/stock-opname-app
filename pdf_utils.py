import io
import pandas as pd
from fpdf import FPDF
from datetime import datetime

class PDF(FPDF):
    def header(self):
        # Judul Laporan
        self.set_font("Arial", "B", 15)
        self.cell(0, 10, "Laporan Inventaris Gudang", 0, 1, "C")
        # Timestamp
        self.set_font("Arial", "I", 10)
        self.cell(0, 10, f"Dicetak pada: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}", 0, 1, "C")
        self.ln(5)

    def footer(self):
        # Nomor Halaman
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Halaman {self.page_no()}", 0, 0, "C")

def export_to_pdf(df):
    # Sesuaikan dengan nama kolom yang baru saja kita buat di Statistik.py
    kolom_diinginkan = ["Nama Barang", "Jumlah", "Satuan", "Jenis Transaksi", "Tanggal"]
    
    # Kita cek dulu apakah kolom ada, untuk mencegah error di masa depan
    kolom_yang_ada = [k for k in kolom_diinginkan if k in df.columns]
    df = df[kolom_yang_ada].copy()
    
    # Pastikan format tanggal hanya menampilkan tanggal (YYYY-MM-DD atau DD-MM-YYYY)
    df["Tanggal"] = pd.to_datetime(df["Tanggal"]).dt.strftime('%d-%m-%Y')
    
    pdf = PDF(orientation='L')
    pdf.add_page()
    pdf.set_font("Arial", size=10)

    col_width = 260 / len(df.columns)

    # Header Tabel
    pdf.set_fill_color(200, 220, 255)
    for col in df.columns:
        pdf.cell(col_width, 10, str(col), border=1, align="C", fill=True)
    pdf.ln()

    # Isi Tabel
    pdf.set_fill_color(255, 255, 255)
    for row in df.itertuples(index=False):
        for item in row:
            pdf.cell(col_width, 10, str(item), border=1, align="C")
        pdf.ln()

    buffer = io.BytesIO()
    pdf.output(buffer)
    return buffer.getvalue()
