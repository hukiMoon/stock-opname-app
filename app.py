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

# FIX: Gunakan session_state agar status login terbaca di semua halaman sidebar
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
        st.write("Isi jumlah fisik hasil pengecekan di kolom **Stok Fisik** bawah ini:")
        df = pd.DataFrame(data_db, columns=["Kode Barang", "Nama Barang", "Stok Sistem", "Satuan"])
        df["Stok Fisik (Hasil Hitung)"] = df["Stok Sistem"]
        
        df_edit = st.data_editor(df, disabled=["Kode Barang", "Nama Barang", "Stok Sistem", "Satuan"], hide_index=True, use_container_width=True, key="ed_opname")
        df_edit["Selisih"] = df_edit["Stok Fisik (Hasil Hitung)"] - df_edit["Stok Sistem"]
        
        def tentukan_status(selisih):
            if selisih == 0: return "🟢 Sesuai"
            elif selisih < 0: return "🔴 Kurang"
            else: return "🟡 Lebih"
            
        df_edit["Status"] = df_edit["Selisih"].apply(tentukan_status)
        st.dataframe(df_edit, hide_index=True, use_container_width=True)
        
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df_edit.to_excel(writer, index=False, sheet_name='Laporan Opname')
            
        col_dl, col_sync = st.columns(2)
        with col_dl:
            st.download_button(label="📥 Download Laporan ke Excel", data=buffer.getvalue(), file_name="Laporan_Opname.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
        with col_sync:
            if st.button("Sinkronisasi Stok Sistem ke Fisik", type="primary", use_container_width=True):
                for index, row in df_edit.iterrows():
                    jalankan_query("UPDATE barang SET stok_sistem = %s WHERE nama_barang = %s", (int(row["Stok Fisik (Hasil Hitung)"]), row["Nama Barang"]), commit=True)
                st.success("Stok cloud berhasil disesuaikan!")
                st.rerun()
