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
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS barang (
                id SERIAL PRIMARY KEY,
                nama_barang TEXT UNIQUE NOT NULL,
                stok_sistem INTEGER DEFAULT 0
            )
        """)
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
# 2. ATUR TAMPILAN & BLOKIR SIDEBAR TOTAL
# ==========================================
st.set_page_config(page_title="Aplikasi Stock Opname Online", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    /* 1. Hapus total komponen sidebar kiri dan tombol panahnya dari sistem */
    [data-testid="stSidebar"] {display: none !important;}
    [data-testid="stSidebarCollapseButton"] {display: none !important;}
    
    /* 2. Lenyapkan toolbar bawaan Streamlit (Share, Manage app, GitHub, dll.) */
    [data-testid="stHeader"] {display: none !important;}
    [data-testid="stToolbar"] {display: none !important;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stAppDeployButton {display: none !important;}
    
    /* 3. Atur jarak atas halaman agar lebih rapi */
    .stAppViewContainer {padding-top: 2rem;}
    
    /* 4. Percantik tampilan Tab Navigasi Atas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 8px 14px;
        background-color: #f0f2f6;
        border-radius: 4px;
        font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. MANAJEMEN LOGIN MENGGUNAKAN URL PARAMETER
# ==========================================
is_authenticated = st.query_params.get("session") == "loggedin"

# Fungsi Form Login
def halaman_login():
    st.subheader("🔐 Login Sistem Stock Opname")
    st.write("Silakan masukkan akun admin gudang untuk mengakses sistem.")
    
    with st.form("form_login"):
        username = st.text_input("Username:")
        password = st.text_input("Password:", type="password")
        tombol_login = st.form_submit_button("Masuk")
        
        if tombol_login:
            if username == "admin" and password == "gudang123":
                st.query_params["session"] = "loggedin"
                st.success("Login Berhasil!")
                st.rerun()
            else:
                st.error("Username atau Password salah! Silakan coba lagi.")

# JIKA BELUM LOGIN, TAMPILKAN FORM LOGIN
if not is_authenticated:
    st.title("📦 Sistem Stock Opname Persediaan (Online)")
    halaman_login()

# JIKA SUDAH LOGIN, TAMPILKAN MENU ATAS PERMANEN
else:
    # Baris Judul & Tombol Keluar / Logout
    st.title("📦 Sistem Stock Opname Persediaan")
    
    col_kosong, col_logout = st.columns([4, 1])
    with col_logout:
        if st.button("🚪 Keluar", use_container_width=True):
            st.query_params.clear()
            st.rerun()
            
    st.write("---")

    # Pembuatan Menu Navigasi Menetap di Atas (Menggunakan st.tabs)
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
        opsi_input = st.radio("Pilih Jenis Input:", ["Barang Baru (Belum Terdaftar)", "Tambah Stok Barang Lama"], key="r_masuk")
        
        with st.form("form_masuk", clear_on_submit=True):
            if opsi_input == "Barang Baru (Belum Terdaftar)":
                nama_barang = st.text_input("Nama Barang Baru:").strip().upper()
            else:
                daftar_barang = [b[0] for b in jalankan_query("SELECT nama_barang FROM barang ORDER BY nama_barang ASC")]
                nama_barang = st.selectbox("Pilih Barang:", daftar_barang) if daftar_barang else "Belum ada barang"
            
            jumlah_masuk = st.number_input("Jumlah Barang Masuk:", min_value=1, step=1, key="n_masuk")
            tombol_masuk = st.form_submit_button("Simpan Transaksi Masuk")
            
            if tombol_masuk:
                if nama_barang and nama_barang != "Belum ada barang":
                    cek_barang = jalankan_query("SELECT stok_sistem FROM barang WHERE nama_barang = %s", (nama_barang,))
                    if len(cek_barang) == 0:
                        jalankan_query("INSERT INTO barang (nama_barang, stok_sistem) VALUES (%s, %s)", (nama_barang, jumlah_masuk), commit=True)
                    else:
                        stok_baru = cek_barang[0][0] + jumlah_masuk
                        jalankan_query("UPDATE barang SET stok_sistem = %s WHERE nama_barang = %s", (stok_baru, nama_barang), commit=True)
                    
                    tanggal_sekarang = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    jalankan_query("INSERT INTO riwayat (nama_barang, jenis_transaksi, jumlah, tanggal) VALUES (%s, 'MASUK', %s, %s)", 
                                   (nama_barang, jumlah_masuk, tanggal_sekarang), commit=True)
                    st.success(f"Berhasil mencatat transaksi masuk!")
                    st.rerun()

    # ------------------------------------------
    # TAB 2: BARANG KELUAR
    # ------------------------------------------
    with tab2:
        st.subheader("📤 Input Barang Keluar")
        daftar_barang = [b[0] for b in jalankan_query("SELECT nama_barang FROM barang ORDER BY nama_barang ASC")]
        
        if not daftar_barang:
            st.info("Belum ada data barang di sistem.")
        else:
            with st.form("form_keluar", clear_on_submit=True):
                nama_barang = st.selectbox("Pilih Barang Keluar:", daftar_barang, key="s_keluar")
                jumlah_keluar = st.number_input("Jumlah Barang Keluar:", min_value=1, step=1, key="n_keluar")
                tombol_keluar = st.form_submit_button("Simpan Transaksi Keluar")
                
                if tombol_keluar:
                    stok_sekarang = jalankan_query("SELECT stok_sistem FROM barang WHERE nama_barang = %s", (nama_barang,))[0][0]
                    if jumlah_keluar > stok_sekarang:
                        st.error(f"Gagal! Stok tidak mencukupi (Sisa: {stok_sekarang}).")
                    else:
                        stok_baru = stok_sekarang - jumlah_keluar
                        jalankan_query("UPDATE barang SET stok_sistem = %s WHERE nama_barang = %s", (stok_baru, nama_barang), commit=True)
                        
                        tanggal_sekarang = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        jalankan_query("INSERT INTO riwayat (nama_barang, jenis_transaksi, jumlah, tanggal) VALUES (%s, 'KELUAR', %s, %s)", 
                                       (nama_barang, jumlah_keluar, tanggal_sekarang), commit=True)
                        st.success(f"Berhasil mencatat transaksi keluar!")
                        st.rerun()

    # ------------------------------------------
    # TAB 3: LAPORAN STOCK OPNAME
    # ------------------------------------------
    with tab3:
        st.subheader("📊 Laporan & Analisis Selisih")
        data_db = jalankan_query("SELECT nama_barang, stok_sistem FROM barang ORDER BY nama_barang ASC")
        
        if not data_db:
            st.info("Belum ada data barang untuk dilaporkan.")
        else:
            df = pd.DataFrame(data_db, columns=["Nama Barang", "Stok Sistem"])
            df["Stok Fisik (Hasil Hitung)"] = df["Stok Sistem"]
            
            df_edit = st.data_editor(df, disabled=["Nama Barang", "Stok Sistem"], hide_index=True, key="ed_opname")
            df_edit["Selisih"] = df_edit["Stok Fisik (Hasil Hitung)"] - df_edit["Stok Sistem"]
            
            def tentukan_status(selisih):
                if selisih == 0: return "🟢 Sesuai"
                elif selisih < 0: return "🔴 Kurang"
                else: return "🟡 Lebih"
                
            df_edit["Status"] = df_edit["Selisih"].apply(tentukan_status)
            st.dataframe(df_edit, hide_index=True)
            
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df_edit.to_excel(writer, index=False, sheet_name='Laporan Opname')
            
            st.download_button(
                label="📥 Download Excel",
                data=buffer.getvalue(),
                file_name=f"Laporan_Opname_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="b_dl"
            )
            
            if st.button("Sinkronisasi Stok Sistem ke Fisik", key="b_sync"):
                for index, row in df_edit.iterrows():
                    jalankan_query("UPDATE barang SET stok_sistem = %s WHERE nama_barang = %s", 
                                   (int(row["Stok Fisik (Hasil Hitung)"]), row["Nama Barang"]), commit=True)
                st.success("Stok cloud berhasil disesuaikan!")
                st.rerun()

    # ------------------------------------------
    # TAB 4: RIWAYAT TRANSAKSI (LOG)
    # ------------------------------------------
    with tab4:
        st.subheader("📜 Log Aktivitas Gudang")
        data_riwayat = jalankan_query("SELECT nama_barang, jenis_transaksi, jumlah, tanggal FROM riwayat ORDER BY id DESC")
        
        if not data_riwayat:
            st.info("Belum ada riwayat transaksi.")
        else:
            df_riwayat = pd.DataFrame(data_riwayat, columns=["Nama Barang", "Jenis Transaksi", "Jumlah", "Waktu Transaksi"])
            st.dataframe(df_riwayat, hide_index=True, use_container_width=True)

    # ------------------------------------------
    # TAB 5: MANAJEMEN MASTER BARANG
    # ------------------------------------------
    with tab5:
        st.subheader("⚙️ Manajemen Master Data")
        daftar_barang = [b[0] for b in jalankan_query("SELECT nama_barang FROM barang ORDER BY nama_barang ASC")]
        
        if not daftar_barang:
            st.info("Belum ada data barang di database.")
        else:
            aksi = st.radio("Pilih Tindakan:", ["Edit Nama Barang", "Hapus Barang Dari Sistem"], horizontal=True, key="r_mgmt")
            
            if aksi == "Edit Nama Barang":
                barang_dipilih = st.selectbox("Pilih Barang:", daftar_barang, key="e_sel")
                nama_baru = st.text_input("Masukkan Nama Baru:", value=barang_dipilih, key="i_new").strip().upper()
                
                if st.button("Simpan Perubahan Nama", key="b_edit"):
                    if nama_baru and nama_baru != barang_dipilih:
                        jalankan_query("UPDATE barang SET nama_barang = %s WHERE nama_barang = %s", (nama_baru, barang_dipilih), commit=True)
                        jalankan_query("UPDATE riwayat SET nama_barang = %s WHERE nama_barang = %s", (nama_baru, barang_dipilih), commit=True)
                        st.success("Nama barang berhasil diubah!")
                        st.rerun()
                        
            elif aksi == "Hapus Barang Dari Sistem":
                barang_dipilih = st.selectbox("Pilih Barang Dihapus:", daftar_barang, key="h_sel")
                st.warning(f"Anda akan menghapus secara permanen barang: **{barang_dipilih}**")
                konfirmasi = st.checkbox("Saya menyetujui penghapusan data ini.", key="c_del")
                
                if st.button("Hapus Permanen", type="primary", key="b_del"):
                    if konfirmasi:
                        jalankan_query("DELETE FROM barang WHERE nama_barang = %s", (barang_dipilih,), commit=True)
                        st.success("Barang berhasil dihapus.")
                        st.rerun()
