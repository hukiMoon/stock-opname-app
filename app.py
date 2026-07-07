import streamlit as st
import psycopg2
import pandas as pd
from datetime import datetime
import io

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
                kode_barang TEXT UNIQUE NOT NULL,
                nama_barang TEXT UNIQUE NOT NULL,
                stok_sistem INTEGER DEFAULT 0,
                satuan TEXT DEFAULT 'PCS'
            )
        """)
        
        # Tabel Riwayat Transaksi
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS riwayat (
                id SERIAL PRIMARY KEY,
                kode_barang TEXT,
                nama_barang TEXT,
                jenis_transaksi TEXT,
                jumlah INTEGER,
                satuan TEXT,
                tanggal TEXT,
                keterangan TEXT
            )
        """)
        
        # JALANKAN ALTER TABLE JIKA TABEL SUDAH PERNAH ADA
        try:
            cursor.execute("ALTER TABLE barang ADD COLUMN IF NOT EXISTS kode_barang TEXT UNIQUE;")
            cursor.execute("ALTER TABLE barang ADD COLUMN IF NOT EXISTS satuan TEXT DEFAULT 'PCS';")
            cursor.execute("ALTER TABLE riwayat ADD COLUMN IF NOT EXISTS kode_barang TEXT;")
            cursor.execute("ALTER TABLE riwayat ADD COLUMN IF NOT EXISTS satuan TEXT;")
            cursor.execute("ALTER TABLE riwayat ADD COLUMN IF NOT EXISTS keterangan TEXT;")
        except:
            pass
            
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

# Fungsi Generate Kode Barang Otomatis (STM-01, STM-02, dst)
def generate_kode_otomatis():
    data = jalankan_query("SELECT id FROM barang ORDER BY id DESC LIMIT 1")
    if not data:
        return "STM-01"
    else:
        id_terakhir = data[0][0]
        id_baru = id_terakhir + 1
        return f"STM-{id_baru:02d}"

# ==========================================
# 2. ATUR TAMPILAN & BLOKIR SIDEBAR TOTAL
# ==========================================
st.set_page_config(page_title="Aplikasi Stock Opname Online", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    [data-testid="stSidebar"] {display: none !important;}
    [data-testid="stSidebarCollapseButton"] {display: none !important;}
    [data-testid="stHeader"] {display: none !important;}
    [data-testid="stToolbar"] {display: none !important;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stAppDeployButton {display: none !important;}
    
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        flex-wrap: wrap;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 16px;
        background-color: #f0f2f6;
        border-radius: 6px;
        font-weight: 600;
        font-size: 14px;
        margin-bottom: 4px;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: #ff4b4b;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. MANAJEMEN LOGIN MENGGUNAKAN URL PARAMETER
# ==========================================
is_authenticated = st.query_params.get("session") == "loggedin"

def halaman_login():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.subheader("🔐 Login Sistem Stock Opname")
        st.write("Silakan masukkan akun admin gudang untuk mengakses sistem.")
        
        with st.form("form_login"):
            username = st.text_input("Username:")
            password = st.text_input("Password:", type="password")
            tombol_login = st.form_submit_button("Masuk", use_container_width=True)
            
            if tombol_login:
                if username == "admin" and password == "gudang123":
                    st.query_params["session"] = "loggedin"
                    st.success("Login Berhasil!")
                    st.rerun()
                else:
                    st.error("Username atau Password salah! Silakan coba lagi.")

if not is_authenticated:
    st.title("📦 Sistem Stock Opname Persediaan (Online)")
    halaman_login()

else:
    # Header Dashboard Utama
    col_title, col_logout = st.columns([5, 1])
    with col_title:
        st.title("📦 Sistem Stock Opname Persediaan")
    with col_logout:
        if st.button("🚪 Keluar", use_container_width=True):
            st.query_params.clear()
            st.rerun()
            
    st.write("---")

    # Menu Navigasi Menetap di Atas
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📥 Barang Masuk", 
        "📤 Barang Keluar", 
        "📊 Laporan Opname", 
        "📜 Riwayat Log", 
        "⚙️ Master Barang"
    ])

    # ------------------------------------------
    # TAB 1: BARANG MASUK
    # ------------------------------------------
    with tab1:
        st.subheader("📥 Input Barang Masuk")
        col_form, col_info = st.columns([3, 2])
        
        with col_form:
            opsi_input = st.radio("Pilih Jenis Input:", ["Barang Baru (Belum Terdaftar)", "Tambah Stok Barang Lama"], key="r_masuk")
            
            if opsi_input == "Barang Baru (Belum Terdaftar)":
                with st.form("form_masuk_baru", clear_on_submit=True):
                    kode_otomatis = generate_kode_otomatis()
                    st.info(f"📋 **Kode Barang Baru Otomatis:** {kode_otomatis}")
                    nama_barang = st.text_input("Nama Barang Baru:").strip().upper()
                    satuan_barang = st.selectbox("Pilih Satuan:", ["PCS", "SET", "RIM", "LEMBAR", "ROLL", "BOX", "PACK", "UNIT", "KILOGRAM", "LITER"])
                    jumlah_masuk = st.number_input("Jumlah Barang Masuk:", min_value=1, step=1, key="n_masuk_baru")
                    tanggal_pilihan = st.date_input("Tanggal Barang Masuk:", value=datetime.now().date())
                    input_keterangan = st.text_input("Keterangan (Opsional):", placeholder="Contoh: Dari Supplier A").strip()
                    
                    if st.form_submit_button("Simpan Transaksi Masuk", use_container_width=True):
                        if nama_barang:
                            tanggal_str = tanggal_pilihan.strftime("%Y-%m-%d")
                            txt_ket = input_keterangan if input_keterangan else "-"
                            jalankan_query("INSERT INTO barang (kode_barang, nama_barang, stok_sistem, satuan) VALUES (%s, %s, %s, %s)", (kode_otomatis, nama_barang, jumlah_masuk, satuan_barang), commit=True)
                            jalankan_query("INSERT INTO riwayat (kode_barang, nama_barang, jenis_transaksi, jumlah, satuan, tanggal, keterangan) VALUES (%s, %s, 'MASUK', %s, %s, %s, %s)", (kode_otomatis, nama_barang, jumlah_masuk, satuan_barang, tanggal_str, txt_ket), commit=True)
                            st.success("Berhasil mendaftarkan barang baru!")
                            st.rerun()
            else:
                daftar_db = jalankan_query("SELECT kode_barang, nama_barang FROM barang ORDER BY nama_barang ASC")
                daftar_barang = [f"{b[0]} - {b[1]}" for b in daftar_db] if daftar_db else []
                
                if not daftar_barang:
                    st.info("Belum ada data barang lama di database.")
                else:
                    pilihan_barang = st.selectbox("Pilih Barang:", daftar_barang, key="s_masuk_lama_select")
                    nama_barang = pilihan_barang.split(" - ")[1]
                    
                    data_stok = jalankan_query("SELECT kode_barang, stok_sistem, satuan FROM barang WHERE nama_barang = %s", (nama_barang,))[0]
                    kd_brg, stok_sekarang_tampil, satuan_tampil = data_stok
                    
                    # Form dinamis dikunci menggunakan KEY berbasis nama barang agar tidak menumpuk di memori browser
                    with st.form(f"form_masuk_lama_{nama_barang.replace(' ', '_')}", clear_on_submit=True):
                        col_stok_kiri, col_input_kanan = st.columns(2)
                        with col_stok_kiri:
                            st.text_input("Stok Tersedia Saat Ini:", value=f"{stok_sekarang_tampil} {satuan_tampil}", disabled=True)
                        with col_input_kanan:
                            jumlah_masuk = st.number_input("Jumlah Barang Masuk:", min_value=1, step=1, key="n_masuk_lama_val")
                            
                        tanggal_pilihan = st.date_input("Tanggal Barang Masuk:", value=datetime.now().date())
                        input_keterangan = st.text_input("Keterangan (Opsional):", placeholder="Contoh: Tambah Stok").strip()
                        
                        if st.form_submit_button("Simpan Tambah Stok", use_container_width=True):
                            stok_baru = stok_sekarang_tampil + jumlah_masuk
                            tanggal_str = tanggal_pilihan.strftime("%Y-%m-%d")
                            txt_ket = input_keterangan if input_keterangan else "-"
                            jalankan_query("UPDATE barang SET stok_sistem = %s WHERE nama_barang = %s", (stok_baru, nama_barang), commit=True)
                            jalankan_query("INSERT INTO riwayat (kode_barang, nama_barang, jenis_transaksi, jumlah, satuan, tanggal, keterangan) VALUES (%s, %s, 'MASUK', %s, %s, %s, %s)", (kd_brg, nama_barang, jumlah_masuk, satuan_tampil, tanggal_str, txt_ket), commit=True)
                            st.success("Stok berhasil ditambahkan!")
                            st.rerun()
        with col_info:
            st.info("💡 **Informasi Tambahan:**\n\nSistem mencatat data barang masuk ke database awan (Supabase) secara aman.")

    # ------------------------------------------
    # TAB 2: BARANG KELUAR (SISTEM FORM FORCED-RELOAD)
    # ------------------------------------------
    with tab2:
        st.subheader("📤 Input Barang Keluar")
        col_form_k, col_info_k = st.columns([3, 2])
        
        with col_form_k:
            daftar_db = jalankan_query("SELECT kode_barang, nama_barang FROM barang ORDER BY nama_barang ASC")
            daftar_barang = [f"{b[0]} - {b[1]}" for b in daftar_db] if daftar_db else []
            
            if not daftar_barang:
                st.info("Belum ada data barang di sistem.")
            else:
                pilihan_barang_luar = st.selectbox("Pilih Barang Keluar:", daftar_barang, key="s_keluar_select")
                nama_barang_keluar = pilihan_barang_luar.split(" - ")[1]
                
                # Menarik data paling segar dari Database cloud
                cek_stok_db = jalankan_query("SELECT kode_barang, stok_sistem, satuan FROM barang WHERE nama_barang = %s", (nama_barang_keluar,))[0]
                kd_brg, stok_sekarang_k, sat_brg_k = cek_stok_db
                
                # KRITIKAL: Nama Form dibuat unik mengikuti nama barang agar cache reload otomatis
                with st.form(f"form_keluar_dinamis_{nama_barang_keluar.replace(' ', '_')}", clear_on_submit=True):
                    col_stok_k_kiri, col_input_k_kanan = st.columns(2)
                    with col_stok_k_kiri:
                        st.text_input("Stok Tersedia Saat Ini:", value=f"{stok_sekarang_k} {sat_brg_k}", disabled=True)
                    with col_input_k_kanan:
                        jumlah_keluar = st.number_input("Jumlah Barang Keluar:", min_value=1, step=1, key="n_keluar_val")
                    
                    if jumlah_keluar > stok_sekarang_k:
                        st.warning(f"⚠️ **Peringatan:** Jumlah yang diinput ({jumlah_keluar} {sat_brg_k}) melebihi stok tersedia ({stok_sekarang_k} {sat_brg_k})!")
                        
                    tanggal_keluar_pilihan = st.date_input("Tanggal Barang Keluar:", value=datetime.now().date())
                    input_keterangan_keluar = st.text_input("Keterangan Keluar (Opsional):", placeholder="Contoh: Pembeli B").strip()
                    
                    if st.form_submit_button("Simpan Transaksi Keluar", use_container_width=True):
                        if jumlah_keluar > stok_sekarang_k:
                            st.error(f"Gagal menyimpan! Stok tidak mencukupi.")
                        else:
                            stok_baru = stok_sekarang_k - jumlah_keluar
                            tanggal_k_str = tanggal_keluar_pilihan.strftime("%Y-%m-%d")
                            txt_ket_k = input_keterangan_keluar if input_keterangan_keluar else "-"
                            
                            jalankan_query("UPDATE barang SET stok_sistem = %s WHERE nama_barang = %s", (stok_baru, nama_barang_keluar), commit=True)
                            jalankan_query("INSERT INTO riwayat (kode_barang, nama_barang, jenis_transaksi, jumlah, satuan, tanggal, keterangan) VALUES (%s, %s, 'KELUAR', %s, %s, %s, %s)", (kd_brg, nama_barang_keluar, jumlah_keluar, sat_brg_k, tanggal_k_str, txt_ket_k), commit=True)
                            st.success(f"Berhasil mencatat transaksi keluar!")
                            st.rerun()
        with col_info_k:
            st.info("💡 **Sistem Validasi:**\n\nSistem memantau sisa barang secara dinamis berdasarkan barang yang Anda pilih di menu dropdown.")

    # ------------------------------------------
    # TAB 3: LAPORAN STOCK OPNAME
    # ------------------------------------------
    with tab3:
        st.subheader("📊 Laporan & Analisis Selisih")
        data_db = jalankan_query("SELECT kode_barang, nama_barang, stok_sistem, satuan FROM barang ORDER BY kode_barang ASC")
        
        if not data_db:
            st.info("Belum ada data barang untuk dilaporkan.")
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
            
            st.write("---")
            st.subheader("📋 Hasil Analisis Selisih")
            st.dataframe(df_edit, hide_index=True, use_container_width=True)
            
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df_edit.to_excel(writer, index=False, sheet_name='Laporan Opname')
            
            col_dl, col_sync = st.columns(2)
            with col_dl:
                st.download_button(
                    label="📥 Download Laporan ke Excel",
                    data=buffer.getvalue(),
                    file_name=f"Laporan_Opname_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                    key="b_dl"
                )
            with col_sync:
                if st.button("Sinkronisasi Stok Sistem ke Fisik", type="primary", use_container_width=True, key="b_sync"):
                    for index, row in df_edit.iterrows():
                        jalankan_query("UPDATE barang SET stok_sistem = %s WHERE nama_barang = %s", (int(row["Stok Fisik (Hasil Hitung)"]), row["Nama Barang"]), commit=True)
                    st.success("Stok cloud berhasil disesuaikan!")
                    st.rerun()

    # ------------------------------------------
    # TAB 4: RIWAYAT TRANSAKSI
    # ------------------------------------------
    with tab4:
        st.subheader("📜 Log Aktivitas Gudang Real-time")
        data_riwayat = jalankan_query("SELECT kode_barang, nama_barang, jenis_transaksi, jumlah, satuan, tanggal, keterangan FROM riwayat ORDER BY id DESC")
        
        if not data_riwayat:
            st.info("Belum ada riwayat transaksi.")
        else:
            df_riwayat = pd.DataFrame(data_riwayat, columns=["Kode Barang", "Nama Barang", "Jenis Transaksi", "Jumlah", "Satuan", "Tanggal Transaksi", "Keterangan"])
            st.dataframe(df_riwayat, hide_index=True, use_container_width=True)

    # ------------------------------------------
    # TAB 5: MANAJEMEN MASTER BARANG
    # ------------------------------------------
    with tab5:
        st.subheader("⚙️ Manajemen Master Data")
        daftar_db = jalankan_query("SELECT kode_barang, nama_barang FROM barang ORDER BY nama_barang ASC")
        daftar_barang = [f"{b[0]} - {b[1]}" for b in daftar_db] if daftar_db else []
        
        if not daftar_barang:
            st.info("Belum ada data barang di database.")
        else:
            aksi = st.radio("Pilih Tindakan:", ["Edit Nama Barang", "Hapus Barang Dari Sistem"], horizontal=True, key="r_mgmt")
            st.write("---")
            
            if aksi == "Edit Nama Barang":
                col_e1, col_e2 = st.columns(2)
                with col_e1:
                    pilihan_barang = st.selectbox("Pilih Barang:", daftar_barang, key="e_sel")
                    nama_barang_terpilih = pilihan_barang.split(" - ")[1]
                    
                    nama_baru = st.text_input("Masukkan Nama Baru:", value=nama_barang_terpilih, key="i_new").strip().upper()
                    if st.button("Simpan Perubahan Nama", use_container_width=True, key="b_edit"):
                        if nama_baru and nama_baru != nama_barang_terpilih:
                            jalankan_query("UPDATE barang SET nama_barang = %s WHERE nama_barang = %s", (nama_baru, nama_barang_terpilih), commit=True)
                            jalankan_query("UPDATE riwayat SET nama_barang = %s WHERE nama_barang = %s", (nama_baru, nama_barang_terpilih), commit=True)
                            st.success("Nama barang berhasil diubah!")
                            st.rerun()
                            
            elif aksi == "Hapus Barang Dari Sistem":
                col_h1, col_h2 = st.columns(2)
                with col_h1:
                    pilihan_barang = st.selectbox("Pilih Barang Dihapus:", daftar_barang, key="h_sel")
                    nama_barang_hapus = pilihan_barang.split(" - ")[1]
                    
                    st.warning(f"Anda akan menghapus secara permanen barang: **{pilihan_barang}**")
                    konfirmasi = st.checkbox("Saya menyetujui penghapusan data ini.", key="c_del")
                    
                    if st.button("Hapus Permanen", type="primary", use_container_width=True, key="b_del"):
                        if konfirmasi:
                            jalankan_query("DELETE FROM barang WHERE nama_barang = %s", (nama_barang_hapus,), commit=True)
                            st.success("Barang berhasil dihapus.")
                            st.rerun()
