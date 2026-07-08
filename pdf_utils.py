import io

def export_to_pdf(df):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)

    # Header Tabel
    col_width = 190 / len(df.columns)
    for col in df.columns:
        pdf.cell(col_width, 10, col, border=1, align="C")
    pdf.ln()

    # Isi Tabel
    for row in df.itertuples(index=False):
        for item in row:
            pdf.cell(col_width, 10, str(item), border=1, align="C")
        pdf.ln()

    return io.BytesIO(pdf.output(dest='S').encode('latin-1')).getvalue()
