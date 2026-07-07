import streamlit as st
import psycopg2
import pandas as pd
from datetime import datetime
import io

# ==========================================
# GANTI DENGAN CONNECTION STRING SUPABASE-MU
# ==========================================
DB_URL = "postgresql://postgres.krckbruwpxgiziujgqiy:1P%40ny001%2E%2E%2E@aws-0-ap-northeast-1.pooler.supabase.com:5432/postgres"

st.set_page_config(page_title="Sistem Stock Opname", layout="wide")

def jalankan_query(sql, param=(), commit=False):
    conn = psycopg2.connect(DB_URL)
    cursor = conn.cursor()
    cursor.execute(sql, param)
    data = None
    if not commit:
        data = cursor.fetchall()
    else:
        conn.commit()
    conn.close()
    return data

if "loggedin" not in st.session_state:
    st.session_state["loggedin"] = False

if not st.session_state["loggedin"]:
    st.title("📦 Sistem Stock Opname Persediaan (Online)")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.subheader("🔐 Login Sistem")
        with st.form("form_login"):
            username = st.text_input("Username:")
            password = st.text_input("Password:", type="password")
            if st.form_submit_button("Masuk", use_container_width=True):
                if username == "admin" and password == "gudang123":
                    st.session_state["loggedin"] = True
                    st.success("Login Berhasil!")
                    st.rerun()
                else:
                    st.error("Username atau Password salah!")
else:
    col_title, col_logout = st.columns([5, 1])
    with col_title:
        st.title("📊 Laporan Stock Opname & Analisis")
    with col_logout:
        if st.button("🚪 Keluar", use_container_width=True):
            st.session_state["loggedin"] = False
            st.rerun()
            
    st.write("---")
    
    data_db = jalankan_query("SELECT kode_barang, nama_barang, stok_sistem, satuan FROM barang ORDER BY LENGTH(kode_barang) ASC, kode_barang ASC")
    
    if not data_db:
        st.info("Belum ada data barang. Silakan ke menu sidebar untuk menambah barang masuk.")
    else:
        # --- MEMBUAT DATA FRAME UTAMA ---
        df = pd.DataFrame(data_db, columns=["Kode Barang", "Nama Barang", "Stok Sistem", "Satuan"])
        df["Stok Fisik (Hasil Hitung)"] = df["Stok Sistem"]
        df["Selisih"] = 0
        
        # --- PANEL FILTER KUSTOM ---
        st.markdown("### 🛠️ Panel Filter Laporan")
        col_f1, col_f2, col_f3 = st.columns(3)
        
        with col_f1:
            search_brg = st.text_input("🔍 Cari Nama / Kode Barang:", placeholder="Ketik kata kunci...").strip().upper()
        with col_f2:
            filter_status = st.selectbox("📊 Filter Status Selisih:", ["Tampilkan Semua", "🟢 Sesuai", "🔴 Kurang", "🟡 Lebih"])
        with col_f3:
            filter_stok = st.selectbox("📦 Filter Kondisi Stok:", ["Tampilkan Semua", "Hanya Stok Kritis (0 - 5)", "Hanya Stok Banyak (> 5)"])
            
        st.write("---")
        
        # --- DATA EDITOR UTAMA ---
        st.write("Isi jumlah fisik hasil pengecekan di kolom **Stok Fisik** bawah ini:")
        df_edit = st.data_editor(df, disabled=["Kode Barang", "Nama Barang", "Stok Sistem", "Satuan"], hide_index=True, use_container_width=True, key="ed_opname")
        
        # Kalkulasi Selisih Nyata untuk Tampilan Aplikasi
        df_edit["Selisih"] = df_edit["Stok Fisik (Hasil Hitung)"] - df_edit["Stok Sistem"]
        def tentukan_status(selisih):
            if selisih == 0: return "🟢 Sesuai"
            elif selisih < 0: return "🔴 Kurang"
            else: return "🟡 Lebih"
        df_edit["Status"] = df_edit["Selisih"].apply(tentukan_status)
        
        # --- PROSES PENYARINGAN DATA ---
        df_download = df_edit.copy()
        
        if search_brg:
            df_download = df_download[
                df_download["Nama Barang"].str.contains(search_brg, na=False) | 
                df_download["Kode Barang"].str.contains(search_brg, na=False)
            ]
        if filter_status != "Tampilkan Semua":
            df_download = df_download[df_download["Status"] == filter_status]
            
        if filter_stok == "Hanya Stok Kritis (0 - 5)":
            df_download = df_download[(df_download["Stok Sistem"] >= 0) & (df_download["Stok Sistem"] <= 5)]
        elif filter_stok == "Hanya Stok Banyak (> 5)":
            df_download = df_download[df_download["Stok Sistem"] > 5]
            
        # --- TAMPILKAN PRATINJAU DATA ---
        if df_download.empty:
            st.warning("⚠️ Tidak ada data barang yang cocok dengan kombinasi filter di atas.")
        else:
            if search_brg or filter_status != "Tampilkan Semua" or filter_stok != "Tampilkan Semua":
                st.caption(f"👁️ *Pratinjau: Menampilkan {len(df_download)} barang hasil filter kustom.*")
                st.dataframe(df_download, hide_index=True, use_container_width=True)
            
            # --- FIX: PROSES CUSTOM KOLOM EXCEL (HANYA 3 KOLOM) ---
            # 1. Buat kolom baru hasil kalkulasi: Stok Sistem - Stok Fisik
            df_download["Stok Akhir"] = df_download["Stok Sistem"] - df_download["Stok Fisik (Hasil Hitung)"]
            
            # 2. Potong & Ambil hanya kolom yang diminta
            df_excel_final = df_download[["Nama Barang", "Stok Akhir", "Satuan"]]
            
            # 3. Proses Ekspor ke Excel
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df_excel_final.to_excel(writer, index=False, sheet_name='Laporan Opname Ringkas')
                
            col_dl, col_sync = st.columns(2)
            with col_dl:
                st.download_button(
                    label=f"📥 Download Laporan Ringkas ({len(df_excel_final)} Barang) ke Excel", 
                    data=buffer.getvalue(), 
                    file_name=f"Laporan_Opname_Ringkas_{datetime.now().strftime('%Y%m%d')}.xlsx", 
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", 
                    use_container_width=True
                )
            with col_sync:
                if st.button("Sinkronisasi Stok Sistem ke Fisik (Semua Barang)", type="primary", use_container_width=True):
                    for index, row in df_edit.iterrows():
                        jalankan_query("UPDATE barang SET stok_sistem = %s WHERE nama_barang = %s", (int(row["Stok Fisik (Hasil Hitung)"]), row["Nama Barang"]), commit=True)
                    st.success("Stok cloud berhasil disesuaikan!")
                    st.rerun()
