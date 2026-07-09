import streamlit as st
import pandas as pd             # Untuk mengolah tabel/dataframe
import io                       # Untuk buffer file
from datetime import datetime   # Untuk tanggal/waktu
import init_path                # Untuk manajemen folder
from db_utils import jalankan_query, get_stok_rendah # Untuk koneksi database
from login import show_login    # Untuk form login
from auth import tampilkan_sidebar # Untuk sidebar dan akses

tampilkan_sidebar()

st.set_page_config(initial_sidebar_state="collapsed") 

# ATAU, jika Anda ingin menyembunyikan menu tersebut sepenuhnya via CSS:
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# Logika login
if not st.session_state.get("logged_in", False):
    from login import show_login
    show_login()
else:
    st.title("📊 Sistem Stock Opname")
    st.write("Selamat datang di sistem manajemen stok.")

def jalankan_audit_dan_update(data_list):
    conn = psycopg2.connect(DB_URL)
    try:
        with conn: # Otomatis commit jika sukses, rollback jika error
            with conn.cursor() as cursor:
                # 1. Update stok
                sql_update = "UPDATE barang SET stok_sistem = %s WHERE kode_barang = %s"
                psycopg2.extras.execute_batch(cursor, sql_update, [(d[0], d[2]) for d in data_list])
                
                # 2. Insert log
                sql_log = "INSERT INTO log_opname (kode_barang, stok_sebelum, stok_sesudah) VALUES (%s, %s, %s)"
                psycopg2.extras.execute_batch(cursor, sql_log, [(d[2], d[1], d[0]) for d in data_list])
    finally:
        conn.close()

# Fungsi ambil log
def ambil_data_log():
    # Ambil data dari database
    data = jalankan_query("SELECT id, kode_barang, nama_barang, jumlah, tanggal, keterangan FROM riwayat ORDER BY id DESC LIMIT 5")
    
    # Jika data kosong, kembalikan DataFrame kosong agar tidak error
    if not data:
        return pd.DataFrame(columns=["ID", "Kode", "Nama Barang", "Jumlah", "Tanggal", "Keterangan"])
    
    # Buat DataFrame
    return pd.DataFrame(data, columns=["ID", "Kode", "Nama Barang", "Jumlah", "Tanggal", "Keterangan"])

# ==========================================
# TAMPILAN APLIKASI
# ==========================================

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
            
            st.divider()
            # Pastikan checkbox dan button di bawah ini memiliki indentasi yang benar
            if st.checkbox("Aktifkan tombol Hapus"):
                if st.button("🗑️ Hapus Semua Log", type="primary"):
                    jalankan_query("DELETE FROM log_opname", commit=True)
                    st.success("Riwayat berhasil dihapus!")
                    st.rerun()
    else:
        st.info("Belum ada riwayat perubahan stok.")


stok_rendah = get_stok_rendah(5)
if stok_rendah:
    with st.expander("⚠️ **Peringatan: Stok Barang Rendah!**", expanded=True):
        st.write("Barang-barang berikut memiliki stok tersisa 5 atau kurang:")
        df_rendah = pd.DataFrame(stok_rendah, columns=["Nama Barang", "Sisa Stok"])
        st.table(df_rendah)
