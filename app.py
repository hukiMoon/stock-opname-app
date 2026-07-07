import streamlit as st
import psycopg2
import pandas as pd
from datetime import datetime
import io # Library bawaan untuk memproses file di dalam memori

# ==========================================
# GANTI DENGAN CONNECTION STRING SUPABASE-MU
# ==========================================
DB_URL = "postgresql://postgres.krckbruwpxgiziujgqiy:1P%40ny001%2E%2E%2E@aws-0-ap-northeast-1.pooler.supabase.com:5432/postgres"

# ==========================================
# 1. KONEKSI & INISIALISASI DATABASE ONLINE
# ==========================================
def init_db():
    try:
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()
        
        # Tabel Master Barang
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS barang (
                id SERIAL PRIMARY KEY,
                nama_barang TEXT UNIQUE NOT NULL,
                stok_sistem INTEGER DEFAULT 0
            )
        """)
        
        # Tabel Riwayat Transaksi
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS riwayat (
                id SERIAL PRIMARY KEY,
                nama_barang TEXT,
                jenis_transaksi TEXT,
                jumlah INTEGER,
                tanggal TEXT
            )
        """)
        conn.commit()
        conn.close()
    except Exception as e:
        st.error(f"Gagal terhubung ke Database Supabase: {e}")

init_db()

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

# ==========================================
# 2. TAMPILAN ANTARMUKA (STREAMLIT)
# ==========================================
st.set_page_config(page_title="Aplikasi Stock Opname Online", layout="centered")
st.title("📦 Sistem Stock Opname Persediaan (Online)")

menu = ["Barang Masuk", "Barang Keluar", "Laporan Stock Opname", "Riwayat Transaksi", "Manajemen Barang"]
pilihan = st.sidebar.selectbox("Pilih Menu Navigasi", menu)

# ------------------------------------------
# HALAMAN: BARANG MASUK
# ------------------------------------------
if pilihan == "Barang Masuk":
    st.header("📥 Input Barang Masuk")
    
    opsi_input = st.radio("Pilih Jenis Input:", ["Barang Baru (Belum Terdaftar)", "Tambah Stok Barang Lama"])
    
    with st.form("form_masuk", clear_on_submit=True):
        if opsi_input == "Barang Baru (Belum Terdaftar)":
            nama_barang = st.text_input("Nama Barang Baru:").strip().upper()
        else:
            daftar_barang = [b[0] for b in jalankan_query("SELECT nama_barang FROM barang ORDER BY nama_barang ASC")]
            nama_barang = st.selectbox("Pilih Barang:", daftar_barang) if daftar_barang else "Belum ada barang"
        
        jumlah_masuk = st.number_input("Jumlah Barang Masuk:", min_value=1, step=1)
        tombol_masuk = st.form_submit_button("Simpan Transaksi Masuk")
        
        if tombol_masuk:
            if nama_barang and nama_barang != "Belum ada barang":
                cek_barang = jalankan_query("SELECT stok_sistem FROM barang WHERE nama_barang = ?", (nama_barang,))
                
                if len(cek_barang) == 0:
                    jalankan_query("INSERT INTO barang (nama_barang, stok_sistem) VALUES (%s, %s)", (nama_barang, jumlah_masuk), commit=True)
                else:
                    stok_baru = cek_barang[0][0] + jumlah_masuk
                    jalankan_query("UPDATE barang SET stok_sistem = %s WHERE nama_barang = %s", (stok_baru, nama_barang), commit=True)
                
                tanggal_sekarang = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                jalankan_query("INSERT INTO riwayat (nama_barang, jenis_transaksi, jumlah, tanggal) VALUES (%s, 'MASUK', %s, %s)", 
                               (nama_barang, jumlah_masuk, tanggal_sekarang), commit=True)
                
                st.success(f"Berhasil mencatat: {jumlah_masuk} unit '{nama_barang}' telah masuk (Cloud).")
                st.rerun()
            else:
                st.error("Mohon isi nama barang dengan benar.")

# ------------------------------------------
# HALAMAN: BARANG KELUAR
# ------------------------------------------
elif pilihan == "Barang Keluar":
    st.header("📤 Input Barang Keluar")
    
    daftar_barang = [b[0] for b in jalankan_query("SELECT nama_barang FROM barang ORDER BY nama_barang ASC")]
    
    if not daftar_barang:
        st.info("Belum ada data barang di sistem. Silakan input barang masuk terlebih dahulu.")
    else:
        with st.form("form_keluar", clear_on_submit=True):
            nama_barang = st.selectbox("Pilih Barang yang Keluar:", daftar_barang)
            jumlah_keluar = st.number_input("Jumlah Barang Keluar:", min_value=1, step=1)
            tombol_keluar = st.form_submit_button("Simpan Transaksi Keluar")
            
            if tombol_keluar:
                stok_sekarang = jalankan_query("SELECT stok_sistem FROM barang WHERE nama_barang = %s", (nama_barang,))[0][0]
                
                if jumlah_keluar > stok_sekarang:
                    st.error(f"Gagal! Stok tidak mencukupi. Stok saat ini hanya {stok_sekarang} unit.")
                else:
                    stok_baru = stok_sekarang - jumlah_keluar
                    jalankan_query("UPDATE barang SET stok_sistem = %s WHERE nama_barang = %s", (stok_baru, nama_barang), commit=True)
                    
                    tanggal_sekarang = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    jalankan_query("INSERT INTO riwayat (nama_barang, jenis_transaksi, jumlah, tanggal) VALUES (%s, 'KELUAR', %s, %s)", 
                                   (nama_barang, jumlah_keluar, tanggal_sekarang), commit=True)
                    
                    st.success(f"Berhasil mencatat: {jumlah_keluar} unit '{nama_barang}' telah keluar (Cloud).")
                    st.rerun()

# ------------------------------------------
# HALAMAN: LAPORAN STOCK OPNAME (DENGAN DOWNLOAD EXCEL)
# ------------------------------------------
elif pilihan == "Laporan Stock Opname":
    st.header("📊 Laporan & Hasil Stock Opname")
    
    data_db = jalankan_query("SELECT nama_barang, stok_sistem FROM barang ORDER BY nama_barang ASC")
    
    if not data_db:
        st.info("Belum ada data barang untuk dilaporkan.")
    else:
        st.write("Silakan isi jumlah fisik hasil pengecekan gudang di bawah ini:")
        
        df = pd.DataFrame(data_db, columns=["Nama Barang", "Stok Sistem"])
        df["Stok Fisik (Hasil Hitung)"] = df["Stok Sistem"]
        
        df_edit = st.data_editor(df, disabled=["Nama Barang", "Stok Sistem"], hide_index=True)
        
        df_edit["Selisih"] = df_edit["Stok Fisik (Hasil Hitung)"] - df_edit["Stok Sistem"]
        
        def tentukan_status(selisih):
            if selisih == 0: return "🟢 Sesuai"
            elif selisih < 0: return "🔴 Kurang (Minus)"
            else: return "🟡 Lebih"
            
        df_edit["Status"] = df_edit["Selisih"].apply(tentukan_status)
        
        st.subheader("📋 Hasil Analisis Selisih")
        st.dataframe(df_edit, hide_index=True)
        
        # --- FITUR DOWNLOAD EXCEL BARU ---
        # Membuat buffer memori untuk menampung file Excel tanpa menyimpannya ke hardisk server
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            # Mengonversi DataFrame hasil analisis ke sheet Excel bernama 'Laporan Opname'
            df_edit.to_excel(writer, index=False, sheet_name='Laporan Opname')
        
        # Menyiapkan tombol download di antarmuka web
        st.download_button(
            label="📥 Download Laporan ke Excel",
            data=buffer.getvalue(),
            file_name=f"Laporan_Stock_Opname_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        # ----------------------------------
        
        st.write("---")
        if st.button("Update Stok Sistem Berdasarkan Stok Fisik"):
            for index, row in df_edit.iterrows():
                jalankan_query("UPDATE barang SET stok_sistem = %s WHERE nama_barang = %s", 
                               (int(row["Stok Fisik (Hasil Hitung)"]), row["Nama Barang"]), commit=True)
            st.success("Stok sistem di cloud berhasil disesuaikan!")
            st.rerun()

# ------------------------------------------
# HALAMAN: RIWAYAT TRANSAKSI (LOG)
# ------------------------------------------
elif pilihan == "Riwayat Transaksi":
    st.header("📜 Log Riwayat Transaksi")
    st.write("Berikut adalah daftar kronologi semua aktivitas barang masuk dan keluar:")
    
    data_riwayat = jalankan_query("SELECT nama_barang, jenis_transaksi, jumlah, tanggal FROM riwayat ORDER BY id DESC")
    
    if not data_riwayat:
        st.info("Belum ada riwayat transaksi barang masuk atau keluar.")
    else:
        df_riwayat = pd.DataFrame(data_riwayat, columns=["Nama Barang", "Jenis Transaksi", "Jumlah", "Waktu Transaksi"])
        
        def beri_warna_status(jenis):
            if jenis == "MASUK": return "📥 MASUK"
            else: return "📤 KELUAR"
            
        df_riwayat["Jenis Transaksi"] = df_riwayat["Jenis Transaksi"].apply(beri_warna_status)
        st.dataframe(df_riwayat, hide_index=True, use_container_width=True)

# ------------------------------------------
# HALAMAN: MANAJEMEN BARANG (EDIT/HAPUS)
# ------------------------------------------
elif pilihan == "Manajemen Barang":
    st.header("⚙️ Manajemen Master Barang")
    st.write("Gunakan halaman ini untuk mengubah nama barang atau menghapus barang dari sistem.")
    
    daftar_barang = [b[0] for b in jalankan_query("SELECT nama_barang FROM barang ORDER BY nama_barang ASC")]
    
    if not daftar_barang:
        st.info("Belum ada data barang di database.")
    else:
        aksi = st.radio("Pilih Tindakan:", ["Edit Nama Barang", "Hapus Barang Dari Sistem"], horizontal=True)
        
        if aksi == "Edit Nama Barang":
            st.subheader("✏️ Edit Nama Barang")
            barang_dipilih = st.selectbox("Pilih Barang yang Ingin Diubah:", daftar_barang, key="edit_sel")
            nama_baru = st.text_input("Masukkan Nama Baru:", value=barang_dipilih).strip().upper()
            
            if st.button("Simpan Perubahan Nama"):
                if nama_baru and nama_baru != barang_dipilih:
                    cek_duplikat = jalankan_query("SELECT id FROM barang WHERE nama_barang = %s", (nama_baru,))
                    if cek_duplikat:
                        st.error(f"Gagal! Nama barang '{nama_baru}' sudah terdaftar di sistem.")
                    else:
                        jalankan_query("UPDATE barang SET nama_barang = %s WHERE nama_barang = %s", (nama_baru, barang_dipilih), commit=True)
                        jalankan_query("UPDATE riwayat SET nama_barang = %s WHERE nama_barang = %s", (nama_baru, barang_dipilih), commit=True)
                        st.success(f"Berhasil mengubah nama '{barang_dipilih}' menjadi '{nama_baru}'!")
                        st.rerun()
                else:
                    st.warning("Nama baru tidak boleh kosong atau sama dengan nama lama.")
                    
        elif aksi == "Hapus Barang Dari Sistem":
            st.subheader("❌ Hapus Barang")
            barang_dipilih = st.selectbox("Pilih Barang yang Ingin Dihapus:", daftar_barang, key="hapus_sel")
            stok_saat_ini = jalankan_query("SELECT stok_sistem FROM barang WHERE nama_barang = %s", (barang_dipilih,))[0][0]
            st.warning(f"Tindakan ini akan menghapus barang **'{barang_dipilih}'** (Stok Saat Ini: {stok_saat_ini}) dari database.")
            
            konfirmasi = st.checkbox("Saya benar-benar ingin menghapus barang ini secara permanen.")
            
            if st.button("Hapus Permanen", type="primary"):
                if konfirmasi:
                    jalankan_query("DELETE FROM barang WHERE nama_barang = %s", (barang_dipilih,), commit=True)
                    st.success(f"Barang '{barang_dipilih}' telah berhasil dihapus dari sistem!")
                    st.rerun()
                else:
                    st.error("Gagal! Anda harus mencentang kotak konfirmasi terlebih dahulu.")
