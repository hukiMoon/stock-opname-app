import streamlit as st
import pandas as pd
import io
from datetime import datetime
from db_utils import (
    jalankan_query, 
    get_stok_rendah, 
    export_to_excel_filter, 
    update_stok_opname, 
    jalankan_perintah_db,
    ambil_data_log
)
from utils import check_login, check_role, tampilkan_sidebar

# Konfigurasi Halaman
check_login()
check_role("admin")
tampilkan_sidebar()
            
st.title("📊 Sistem Stock Opname")

# Membuat Tab Navigasi
tab1, tab2 = st.tabs(["📥 Input Opname", "📜 Riwayat Opname"])

# --- TAB 1: INPUT & PREVIEW LAPORAN ---
with tab1:
    st.markdown("### Input Stok Opname")
    
    # Tambahkan ORDER BY kode_barang ASC di akhir kueri SQL
    query_barang = """
    SELECT kode_barang, nama_barang, stok_sistem, satuan 
    FROM barang 
    ORDER BY 
       substring(kode_barang from '^[a-zA-Z]+')::text ASC,  -- Mengurutkan berdasarkan bagian huruf
       (substring(kode_barang from '[0-9]+'))::int ASC      -- Mengurutkan berdasarkan bagian angka secara numerik
    """
    
    data_db = jalankan_query(query_barang)
            
    if data_db:
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
                update_stok_opname(data_to_sync)
                st.success(f"Berhasil sinkronisasi {len(data_to_sync)} item!")
                st.rerun()

    st.divider()

    # --- BAGIAN PREVIEW LAPORAN (YANG DITAMBAHKAN) ---
    st.markdown("### Preview Laporan Transaksi")
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        tgl_awal = st.date_input("Dari Tanggal", datetime.now())
    with col_f2:
        tgl_akhir = st.date_input("Sampai Tanggal", datetime.now())

    # Kueri untuk mengambil data riwayat berdasarkan tanggal
    # Perubahan pada bagian WHERE: menambahkan ::date setelah nama kolom tanggal
    sql_laporan = """
    SELECT id, kode_barang, nama_barang, jenis_transaksi, jumlah, satuan, tanggal, keterangan 
    FROM riwayat 
    WHERE tanggal::date BETWEEN %s::date AND %s::date 
    ORDER BY tanggal DESC
    """
    
    # Menjalankan query dengan parameter tuple
    data_lap = jalankan_query(sql_laporan, (tgl_awal, tgl_akhir))
    
    if data_lap:
        df_laporan = pd.DataFrame(data_lap, columns=["id", "kode_barang", "nama_barang", "jenis_transaksi", "jumlah", "satuan", "tanggal", "keterangan"])
        st.dataframe(df_laporan, use_container_width=True)
        
        # Tombol Download menggunakan fungsi export_to_excel yang sudah ada di db_utils
        st.download_button(
            label="📥 Download Laporan (Excel)",
            data=export_to_excel(sql_laporan, params=(tgl_awal, tgl_akhir)),
            file_name=f"Laporan_{tgl_awal}_sd_{tgl_akhir}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("Tidak ada data transaksi pada rentang tanggal tersebut.")

# --- TAB 2: RIWAYAT DETAIL ---
with tab2:
    st.markdown("### 📜 Riwayat Perubahan Stok (Log)")

    df_log = ambil_data_log() # Memanggil fungsi dari db_utils

    if not df_log.empty:
        st.dataframe(df_log, use_container_width=True)
    else:
        st.info("Belum ada riwayat perubahan stok.")

# (Kode Anda untuk Riwayat Log tetap di sini)
if st.button("🗑️ Hapus Semua Log", type="primary"):
    jalankan_perintah_db("DELETE FROM log_opname")
    st.rerun()
