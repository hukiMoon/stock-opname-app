import streamlit as st
import psycopg2
import pandas as pd
from datetime import datetime
import io
import psycopg2.extras

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

def jalankan_audit_dan_update(data_list):
    """
    data_list: list of tuples (stok_sesudah, stok_sebelum, kode_barang)
    """
    conn = psycopg2.connect(DB_URL)
    cursor = conn.cursor()
    
    # 1. Update stok barang
    sql_update = "UPDATE barang SET stok_sistem = %s WHERE kode_barang = %s"
    psycopg2.extras.execute_batch(cursor, sql_update, [(d[0], d[2]) for d in data_list])
    
    # 2. Masukkan ke log_opname
    sql_log = """
    INSERT INTO log_opname (kode_barang, stok_sebelum, stok_sesudah) 
    VALUES (%s, %s, %s)
    """
    psycopg2.extras.execute_batch(cursor, sql_log, [(d[2], d[1], d[0]) for d in data_list])
    
    conn.commit()
    cursor.close()
    conn.close()

# Halaman Utama (Langsung tampil)
st.title("📊 Laporan Stock Opname & Analisis")
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
        
        # --- PROSES CUSTOM KOLOM EXCEL ---
        # 1. Mengambil data dari Stok Sistem (tanpa dikurangi Stok Fisik)
        # Kita beri nama kolomnya "Stok Akhir" sesuai keinginanmu
        df_download = df_download.rename(columns={"Stok Sistem": "Stok Akhir"})
            
        # 2. Potong & Ambil hanya kolom yang diminta: Nama Barang, Stok Akhir, Satuan
        df_excel_final = df_download[["Nama Barang", "Stok Akhir", "Satuan"]]
            
        # 3. Proses Ekspor ke Excel
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df_excel_final.to_excel(writer, index=False, sheet_name='Laporan Stok Ringkas')
            
        col_dl, col_sync = st.columns(2)
        with col_dl:
            st.download_button(
                label=f"📥 Download Laporan Ringkas ({len(df_excel_final)} Barang) ke Excel", 
                data=buffer.getvalue(), 
                file_name=f"Laporan_Opname_Ringkas_{datetime.now().strftime('%Y%m%d')}.xlsx", 
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", 
                use_container_width=True
            )
        # --- SINKRONISASI DIPERBAIKI ---
with col_sync:
    if st.button("Sinkronisasi & Simpan Log", type="primary", use_container_width=True):
        data_to_sync = []
        for index, row in df_edit.iterrows():
            stok_baru = int(row["Stok Fisik (Hasil Hitung)"])
            stok_lama = int(row["Stok Sistem"])
            kode = row["Kode Barang"]
            
            # Hanya simpan/update jika ada perubahan
            if stok_baru != stok_lama:
                data_to_sync.append((stok_baru, stok_lama, kode))
        
        if data_to_sync:
            try:
                jalankan_audit_dan_update(data_to_sync)
                st.success(f"Berhasil sinkronisasi {len(data_to_sync)} item dan menyimpan log!")
                st.rerun()
            except Exception as e:
                st.error(f"Gagal: {e}")
        else:
            st.info("Tidak ada perubahan stok untuk disinkronisasi.")
