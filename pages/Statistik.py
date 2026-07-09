import streamlit as st
import pandas as pd
import init_path # Pastikan ini ada
from datetime import datetime
from db_utils import jalankan_query
from auth import tampilkan_sidebar
from utils import card_container

# Jika sudah login, tampilkan sidebar
tampilkan_sidebar()

st.title("📈 Statistik Ketersediaan Barang")
st.write("Selamat datang, Anda telah login!")

# 1. Ambil Data
data_riwayat = jalankan_query("SELECT jenis_transaksi, jumlah, tanggal FROM riwayat")

if not data_riwayat:
    st.info("Belum ada data untuk ditampilkan.")
else:
    df = pd.DataFrame(data_riwayat, columns=["Jenis", "Jumlah", "Tanggal"])
    df["Tanggal"] = pd.to_datetime(df["Tanggal"])
    
    # --- TAMBAHKAN INI DI SINI ---
    from pdf_utils import export_to_pdf
    pdf_data = export_to_pdf(df)

    st.download_button(
        label="📥 Unduh Laporan sebagai PDF",
        data=pdf_data,
        file_name = f"Laporan_Gudang_{datetime.now().strftime('%Y%m%d')}.pdf",
        mime="application/pdf",
        key="download_pdf_statistik"  # <--- TAMBAHKAN KEY UNIK DI SINI
    )

    # 2. Ringkasan (Metrics)
    total_masuk = df[df["Jenis"] == "MASUK"]["Jumlah"].sum()
    total_keluar = df[df["Jenis"] == "KELUAR"]["Jumlah"].sum()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Barang Masuk", total_masuk)
    col2.metric("Total Barang Keluar", total_keluar)
    col3.metric("Sisa Stok (Estimasi)", total_masuk - total_keluar)

    # 3. Grafik Tren
    with card_container("Tren Aktivitas Bulanan"):
        df_trend = df.groupby([df["Tanggal"].dt.to_period("M"), "Jenis"])["Jumlah"].sum().reset_index()
        df_trend["Tanggal"] = df_trend["Tanggal"].dt.to_timestamp()
        
        st.line_chart(df_trend, x="Tanggal", y="Jumlah", color="Jenis")

    # 4. Distribusi Barang Keluar (Top 5)
    with card_container("Top Barang Keluar"):
        data_top = jalankan_query("SELECT nama_barang, SUM(jumlah) as total FROM riwayat WHERE jenis_transaksi = 'KELUAR' GROUP BY nama_barang ORDER BY total DESC LIMIT 5")
        if data_top:
            df_top = pd.DataFrame(data_top, columns=["Nama Barang", "Total Keluar"])
            st.bar_chart(df_top.set_index("Nama Barang"))
        else:
            st.write("Belum ada data barang keluar.")
