import streamlit as st
import pandas as pd
import plotly.express as px  # <--- Tambahkan import ini
import init_path
from datetime import datetime
from db_utils import jalankan_query
from utils import check_login, tampilkan_sidebar, card_container

check_login()
tampilkan_sidebar()

st.title("📈 Statistik & Dashboard Gudang")
st.write("---")

# 1. Ambil Data
data_riwayat = jalankan_query("SELECT jenis_transaksi, jumlah, tanggal, nama_barang FROM riwayat")

if not data_riwayat:
    st.info("Belum ada data untuk ditampilkan.")
else:
    df = pd.DataFrame(data_riwayat, columns=["Jenis", "Jumlah", "Tanggal", "Nama"])
    df["Tanggal"] = pd.to_datetime(df["Tanggal"])
    
    # Fitur Unduh PDF (yang sudah ada sebelumnya)
    from pdf_utils import export_to_pdf
    pdf_data = export_to_pdf(df)
    st.download_button(label="📥 Unduh Laporan sebagai PDF", data=pdf_data, file_name=f"Laporan_Gudang_{datetime.now().strftime('%Y%m%d')}.pdf", mime="application/pdf")

    # 2. Ringkasan (Metrics)
    total_masuk = df[df["Jenis"] == "MASUK"]["Jumlah"].sum()
    total_keluar = df[df["Jenis"] == "KELUAR"]["Jumlah"].sum()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Barang Masuk", total_masuk)
    col2.metric("Total Barang Keluar", total_keluar)
    col3.metric("Sisa Stok (Estimasi)", total_masuk - total_keluar)

    # 3. Dashboard Visual
    st.write("---")
    st.subheader("📊 Visualisasi Data")
    
    # Grafik Tren
    df_trend = df.groupby([df["Tanggal"].dt.to_period("M"), "Jenis"])["Jumlah"].sum().reset_index()
    df_trend["Tanggal"] = df_trend["Tanggal"].dt.to_timestamp()
    fig1 = px.line(df_trend, x="Tanggal", y="Jumlah", color="Jenis", title="Tren Aktivitas Bulanan", markers=True)
    st.plotly_chart(fig1, use_container_width=True)

    # Grafik Top 5 Barang Keluar
    df_top = df[df["Jenis"] == "KELUAR"].groupby("Nama")["Jumlah"].sum().nlargest(5).reset_index()
    fig2 = px.bar(df_top, x="Jumlah", y="Nama", orientation='h', title="Top 5 Barang Keluar", color="Jumlah")
    st.plotly_chart(fig2, use_container_width=True)
