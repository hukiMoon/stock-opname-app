import streamlit as st
import pandas as pd
import plotly.express as px  # <--- Tambahkan import ini
import init_path
from datetime import datetime
from db_utils import jalankan_query
from utils import check_login, tampilkan_sidebar, card_container
from pdf_utils import export_to_pdf

check_login()
tampilkan_sidebar()

st.title("📈 Statistik & Dashboard Gudang")
st.write("---")

# 1. Ambil Data
data_riwayat = jalankan_query("SELECT jenis_transaksi, jumlah, tanggal, nama_barang FROM riwayat")

if not data_riwayat:
    st.info("Belum ada data untuk ditampilkan.")
else:
    # Pastikan nama kolom di sini SAMA PERSIS dengan apa yang ada di database atau hasil query
    df = pd.DataFrame(data_riwayat, columns=["Jenis Transaksi", "Jumlah", "Tanggal", "Nama Barang"])
    df["Tanggal"] = pd.to_datetime(df["Tanggal"])

    # --- PERBAIKAN DI SINI ---
    # Ganti 'Jenis' menjadi 'Jenis Transaksi' sesuai nama kolom yang baru
    total_masuk = df[df["Jenis Transaksi"] == "MASUK"]["Jumlah"].sum()
    total_keluar = df[df["Jenis Transaksi"] == "KELUAR"]["Jumlah"].sum()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Barang Masuk", total_masuk)
    col2.metric("Total Barang Keluar", total_keluar)
    col3.metric("Sisa Stok (Estimasi)", total_masuk - total_keluar)

    st.download_button(
    label="📥 Download Statistik (PDF)",
    data=export_to_pdf(df), # Menggunakan fungsi dari pdf_utils[span_4](start_span)[span_4](end_span)
    file_name="Laporan_Statistik.pdf",
    mime="application/pdf"
    )

    # 3. Dashboard Visual
    st.write("---")
    st.subheader("📊 Visualisasi Data")
    
    # Grafik Tren
    df_trend = df.groupby([df["Tanggal"].dt.to_period("M"), "Jenis Transaksi"])["Jumlah"].sum().reset_index()
    df_trend["Tanggal_Str"] = df_trend["Tanggal"].astype(str)
    
    fig1 = px.line(
        df_trend, # Gunakan dataframe-nya di sini
        x="Tanggal_Str", # Gunakan kolom yang sudah diubah
        y="Jumlah", 
        color="Jenis Transaksi", 
        title="Tren Aktivitas Bulanan", 
        markers=True
    )
    st.plotly_chart(fig1, use_container_width=True)

    # Grafik Top 5 Barang Keluar
    df_top = df[df["Jenis Transaksi"] == "KELUAR"].groupby("Nama Barang")["Jumlah"].sum().nlargest(5).reset_index()
    fig2 = px.bar(
        df_top, 
        x="Jumlah", 
        y="Nama Barang", 
        orientation='h', 
        title="Top 5 Barang Keluar", 
        color="Jumlah"
    )
    st.plotly_chart(fig2, use_container_width=True)
