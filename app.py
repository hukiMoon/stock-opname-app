import streamlit as st
import psycopg2
import psycopg2.extras
import pandas as pd
from datetime import datetime
import io

# ==========================================
# KONFIGURASI DATABASE
# ==========================================
DB_URL = "postgresql://postgres.krckbruwpxgiziujgqiy:1P%40ny001%2E%2E%2E@aws-0-ap-northeast-1.pooler.supabase.com:5432/postgres"

st.set_page_config(page_title="Sistem Stock Opname", layout="wide")

# Fungsi untuk query biasa
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

# Fungsi untuk Batch Update & Audit (Poin 1 & 2)
def jalankan_audit_dan_update(data_list):
    conn = psycopg2.connect(DB_URL)
    cursor = conn.cursor()
    
    # 1. Update stok
    sql_update = "UPDATE barang SET stok_sistem = %s WHERE kode_barang = %s"
    psycopg2.extras.execute_batch(cursor, sql_update, [(d[0], d[2]) for d in data_list])
    
    # 2. Insert log
    sql_log = "INSERT INTO log_opname (kode_barang, stok_sebelum, stok_sesudah) VALUES (%s, %s, %s)"
    psycopg2.extras.execute_batch(cursor, sql_log, [(d[2], d[1], d[0]) for d in data_list])
    
    conn.commit()
    cursor.close()
    conn.close()

# Fungsi ambil log
def ambil_data_log():
    # Menggunakan LEFT JOIN agar jika barang dihapus dari tabel barang, log tetap muncul
    sql = """
    SELECT 
        l.id, 
        l.kode_barang, 
        b.nama_barang, 
        l.stok_sebelum, 
        l.stok_sesudah, 
        l.waktu_opname, 
        l.petugas 
    FROM log_opname l
    LEFT JOIN barang b ON l.kode_barang = b.kode_barang
    ORDER BY l.waktu_opname DESC
    """
    conn = psycopg2.connect(DB_URL)
    cursor = conn.cursor()
    cursor.execute(sql)
    data = cursor.fetchall()
    conn.close()
    
    # Update nama kolom agar lebih jelas
    return pd.DataFrame(data, columns=["ID", "Kode", "Nama Barang", "Stok Sebelum", "Stok Sesudah", "Waktu", "Petugas"])

# ==========================================
# TAMPILAN APLIKASI
# ==========================================
st.title("📊 Sistem Stock Opname")

# Membuat Tab Navigasi
tab1, tab2 = st.tabs(["📥 Input Opname", "📜 Riwayat Opname"])

with tab1:
    st.markdown("### Laporan Stock Opname & Analisis")
    data_db = jalankan_query("SELECT kode_barang, nama_barang, stok_sistem, satuan FROM barang ORDER BY kode_barang ASC")

    if not data_db:
        st.info("Belum ada data barang.")
    else:
        df = pd.DataFrame(data_db, columns=["Kode Barang", "Nama Barang", "Stok Sistem", "Satuan"])
        df["Stok Fisik (Hasil Hitung)"] = df["Stok Sistem"]
        
        df_edit = st.data_editor(df, disabled=["Kode Barang", "Nama Barang", "Stok Sistem", "Satuan"], hide_index=True, use_container_width=True)
        
        if st.button("Sinkronisasi & Simpan Log", type="primary"):
            data_to_sync = []
            for index, row in df_edit.iterrows():
                stok_baru = int(row["Stok Fisik (Hasil Hitung)"])
                stok_lama = int(row["Stok Sistem"])
                if stok_baru != stok_lama:
                    data_to_sync.append((stok_baru, stok_lama, row["Kode Barang"]))
            
            if data_to_sync:
                jalankan_audit_dan_update(data_to_sync)
                st.success(f"Berhasil sinkronisasi {len(data_to_sync)} item!")
                st.rerun()
            else:
                st.warning("Tidak ada perubahan stok.")

with tab2:
    st.markdown("### 📜 Riwayat Perubahan Stok")
    
    # Ambil data
    df_log = ambil_data_log()
    
    if not df_log.empty:
        # 1. Tombol Ekspor ke Excel
        buffer_log = io.BytesIO()
        with pd.ExcelWriter(buffer_log, engine='openpyxl') as writer:
            df_log.to_excel(writer, index=False, sheet_name='Riwayat Opname')
        
        col_t1, col_t2 = st.columns([0.8, 0.2])
        with col_t1:
            st.dataframe(
                df_log, 
                use_container_width=True, 
                hide_index=True,
                column_config={"Waktu": st.column_config.DatetimeColumn(format="DD/MM/YYYY HH:mm")}
            )
        with col_t2:
            st.download_button(
                label="📥 Download Excel",
                data=buffer_log.getvalue(),
                file_name=f"Riwayat_Opname_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

            if st.checkbox("Saya yakin ingin menghapus semua riwayat"):
            if st.button("Konfirmasi Hapus Permanen", type="primary"):
                jalankan_query("DELETE FROM log_opname", commit=True)
                st.rerun()
        
            # 2. Tombol Hapus Semua Riwayat
            if st.button("🗑️ Hapus Semua Log", type="primary"):
                # Konfirmasi sederhana bisa ditambah dengan session_state jika ingin lebih aman
                jalankan_query("DELETE FROM log_opname", commit=True)
                st.success("Riwayat berhasil dihapus!")
                st.rerun()
    else:
        st.info("Belum ada riwayat perubahan stok.")
