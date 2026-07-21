import streamlit as st
import pandas as pd
import plotly.express as px
from utils import check_login, tampilkan_sidebar
from db_utils import jalankan_query
from pdf_utils import export_to_pdf

# 1. Konfigurasi halaman
st.set_page_config(page_title="Beranda - Dashboard Stock Opname", page_icon="Setum_Polri.png", layout="wide")

# 2. Proteksi Halaman & Tampilkan Sidebar
# check_login() akan memaksa user kembali/berhenti jika belum login
check_login()
tampilkan_sidebar()

# 3. Logika Utama Beranda
role = st.session_state.get("role", "User").capitalize()

st.title(f"Hallo, Selamat datang {role}! 👋")
st.markdown("---")

# --- Mengambil Data Riwayat (Gabungan dari Statistik) ---
data_riwayat = jalankan_query("SELECT jenis_transaksi, jumlah, tanggal, nama_barang FROM riwayat")

if not data_riwayat:
    st.info("Belum ada data transaksi untuk ditampilkan di dashboard.")
else:
    df = pd.DataFrame(data_riwayat, columns=["Jenis Transaksi", "Jumlah", "Tanggal", "Nama Barang"])
    df["Tanggal"] = pd.to_datetime(df["Tanggal"])

    total_masuk = df[df["Jenis Transaksi"] == "MASUK"]["Jumlah"].sum()
    total_keluar = df[df["Jenis Transaksi"] == "KELUAR"]["Jumlah"].sum()
    
    # --- Ringkasan Operasional ---
    st.subheader("📦 Ringkasan Operasional")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Barang Masuk", total_masuk)
    col2.metric("Total Barang Keluar", total_keluar)
    col3.metric("Sisa Stok (Estimasi)", total_masuk - total_keluar)

    # Tombol Download PDF
    st.download_button(
        label="📥 Download Laporan Statistik (PDF)",
        data=export_to_pdf(df),
        file_name="Laporan_Statistik_Dashboard.pdf",
        mime="application/pdf"
    )
    st.markdown("---")
    
    # --- Visualisasi Data Gudang ---
    st.subheader("📈 Visualisasi Data Gudang")
    
    # Grafik Tren Aktivitas Bulanan
    df_trend = df.groupby([df["Tanggal"].dt.to_period("M"), "Jenis Transaksi"])["Jumlah"].sum().reset_index()
    df_trend["Tanggal_Str"] = df_trend["Tanggal"].astype(str)
    
    fig1 = px.line(
        df_trend, 
        x="Tanggal_Str", 
        y="Jumlah", 
        color="Jenis Transaksi", 
        title="Tren Aktivitas Bulanan", 
        markers=True
    )
    st.plotly_chart(fig1, use_container_width=True)

    # Grafik Top 5 Barang Keluar
    st.markdown("<br>", unsafe_allow_html=True)
    df_top = df[df["Jenis Transaksi"] == "KELUAR"].groupby("Nama Barang")["Jumlah"].sum().nlargest(5).reset_index()
    fig2 = px.bar(
        df_top, 
        x="Jumlah", 
        y="Nama Barang", 
        orientation='h', 
        title="Top 5 Barang Paling Sering Keluar", 
        color="Jumlah"
    )
    st.plotly_chart(fig2, use_container_width=True)

# --- Akses Cepat ---
st.markdown("---")
left_col, right_col = st.columns([2, 1])
with left_col:
    st.subheader("Informasi Terkini")
    st.write("Aplikasi ini digunakan untuk memantau arus barang keluar-masuk gudang secara real-time.")
with right_col:
    st.subheader("Akses Cepat")
    st.page_link("pages/1_Barang Masuk.py", label="Input Barang Masuk", icon="📥")
    st.page_link("pages/5_Laporan.py", label="Lihat Laporan Stok", icon="📊")
