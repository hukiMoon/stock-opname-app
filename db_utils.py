import pandas as pd
import io
import psycopg2
import psycopg2.extras
import streamlit as st
import bcrypt
import functools
from contextlib import contextmanager

# Mengambil URL dari file .streamlit/secrets.toml
DB_URL = st.secrets["DB_URL"]

def handle_db_errors(func):
    """Decorator untuk menangani error database secara terpusat."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            st.error(f"Terjadi kesalahan sistem: {e}")
            return None
    return wrapper

@contextmanager
def get_db_connection():
    """
    Context manager untuk koneksi database.
    Otomatis membuka koneksi dan menjamin penutupan koneksi.
    """
    conn = psycopg2.connect(DB_URL)
    try:
        yield conn
    finally:
        conn.close()

def jalankan_query(sql, param=(), commit=False):
    """
    Menjalankan query dengan context manager yang aman.
    """
    data = None
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, param)
                if not commit:
                    data = cursor.fetchall()
                else:
                    conn.commit()
    except Exception as e:
        st.error(f"Error Database: {e}")
    
    return data

def jalankan_query_satu(sql, param=()):
    """Mengambil hanya satu baris data, lebih efisien untuk pencarian tunggal."""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, param)
                return cursor.fetchone()
    except Exception as e:
        st.error(f"Error Database: {e}")
        return None

@handle_db_errors
def get_stok_rendah(batas):
    query = "SELECT nama_barang, stok_sistem FROM barang WHERE stok_sistem <= %s"
    return jalankan_query(query, (batas,))

def get_data_barang(role):
    """
    Mengambil data barang berdasarkan peran pengguna.
    """
    # PERBAIKAN: Mengubah nama tabel dari 'inventory' menjadi 'barang'
    if role == "admin":
        # Admin bisa melihat seluruh data barang
        query = "SELECT * FROM barang"
    else:
        # User biasa juga melihat dari tabel barang (sesuaikan kondisi jika ada kolom status)
        query = "SELECT * FROM barang"
        
    return jalankan_query(query)

def cek_barang_ada(nama_barang):
    query = "SELECT COUNT(*) FROM barang WHERE LOWER(nama_barang) = LOWER(%s)"
    hasil = jalankan_query(query, (nama_barang,))
    if hasil:
        return hasil[0][0] > 0
    return False

def jalankan_perintah_db(sql, params=()):
    """Fungsi untuk perintah INSERT, UPDATE, atau DELETE yang butuh commit"""
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            conn.commit()

def update_stok_opname(data_list):
    """Logika untuk update stok dan insert log secara batch"""
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            sql_update = "UPDATE barang SET stok_sistem = %s WHERE kode_barang = %s"
            psycopg2.extras.execute_batch(cursor, sql_update, [(d[0], d[2]) for d in data_list])
            
            sql_log = "INSERT INTO log_opname (kode_barang, stok_sebelum, stok_sesudah) VALUES (%s, %s, %s)"
            psycopg2.extras.execute_batch(cursor, sql_log, [(d[2], d[1], d[0]) for d in data_list])
            conn.commit()

def ambil_data_log():
    query = """
    SELECT l.id, l.kode_barang, b.nama_barang, l.stok_sebelum, l.stok_sesudah, l.waktu_opname, l.petugas 
    FROM log_opname l
    LEFT JOIN barang b ON l.kode_barang = b.kode_barang
    ORDER BY l.id DESC LIMIT 50
    """
    data = jalankan_query(query)
    nama_kolom = ["ID", "Kode Barang", "Nama Barang", "Stok Sebelum", "Stok Sesudah", "Tanggal", "Petugas"]
    
    if not data:
        return pd.DataFrame(columns=nama_kolom)
    
    return pd.DataFrame(data, columns=nama_kolom)

def ambil_riwayat_terfilter(nama_barang, jenis_transaksi, tgl_awal, tgl_akhir, sub_bagian=None):
    query = "SELECT kode_barang, nama_barang, jenis_transaksi, jumlah, satuan, tanggal, keterangan FROM riwayat WHERE 1=1"
    params = []

    if nama_barang:
        query += " AND nama_barang ILIKE %s"
        params.append(f"%{nama_barang}%")
    
    if jenis_transaksi:
        format_strings = ','.join(['%s'] * len(jenis_transaksi))
        query += f" AND jenis_transaksi IN ({format_strings})"
        params.extend(jenis_transaksi)
        
    if sub_bagian:
        query += " AND keterangan ILIKE %s"
        params.append(f"%{sub_bagian}%")
        
    query += " AND tanggal::date BETWEEN %s AND %s"
    params.extend([tgl_awal, tgl_akhir])
    query += " ORDER BY id DESC"
    
    return jalankan_query(query, tuple(params))

def autentikasi_user(username, password):
    hasil = jalankan_query_satu("SELECT password_hash, role FROM users WHERE username = %s", (username,))
    if hasil:
        # Menyesuaikan dengan kolom password_hash di database PostgreSQL
        if bcrypt.checkpw(password.encode('utf-8'), hasil[0].encode('utf-8')):
            return hasil[1]
    return None

def update_password_user(username, password_lama, password_baru):
    """Memverifikasi password lama dan memperbarui dengan password baru yang di-enkripsi."""
    hasil = jalankan_query_satu("SELECT password_hash FROM users WHERE username = %s", (username,))
    
    if not hasil:
        return False, "User tidak ditemukan."
    
    hashed_password_lama_db = hasil[0]
    
    if not bcrypt.checkpw(password_lama.encode('utf-8'), hashed_password_lama_db.encode('utf-8')):
        return False, "Password lama salah!"
        
    salt = bcrypt.gensalt()
    hashed_password_baru = bcrypt.hashpw(password_baru.encode('utf-8'), salt).decode('utf-8')
    
    query_update = "UPDATE users SET password_hash = %s WHERE username = %s"
    jalankan_perintah_db(query_update, (hashed_password_baru, username))
    
    return True, "Password berhasil diubah!"

def export_to_excel(sql, params=()):
    """Mengekspor hasil query laporan langsung ke format Excel."""
    data = jalankan_query(sql, params)
    nama_kolom = ["ID", "Kode Barang", "Nama Barang", "Jenis Transaksi", "Jumlah", "Satuan", "Tanggal", "Keterangan"]
    
    if data:
        df = pd.DataFrame(data, columns=nama_kolom)
    else:
        df = pd.DataFrame(columns=nama_kolom)
        
    if not df.empty:
        df["Tanggal"] = pd.to_datetime(df["Tanggal"]).dt.strftime("%d/%m/%Y")
    
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        judul = pd.DataFrame([["Laporan Transaksi Gudang", "", "", "", "", "", "", ""]])
        judul.to_excel(writer, index=False, header=False, startrow=0)
        df.to_excel(writer, index=False, sheet_name='Laporan', startrow=2)
        
    buffer.seek(0)
    return buffer.getvalue()

def export_to_excel_filter(nama_barang, jenis_transaksi, tgl_awal, tgl_akhir, sub_bagian):
    data = ambil_riwayat_terfilter(nama_barang, jenis_transaksi, tgl_awal, tgl_akhir, sub_bagian)
    nama_kolom = ["Kode Barang", "Nama Barang", "Jenis Transaksi", "Jumlah", "Satuan", "Tanggal", "Keterangan"]
    
    if data:
        df = pd.DataFrame(data, columns=nama_kolom)
    else:
        df = pd.DataFrame(columns=nama_kolom)
        
    if not df.empty:
        df["Tanggal"] = pd.to_datetime(df["Tanggal"]).dt.strftime("%d/%m/%Y")
    
    df = df.rename(columns={
        "Kode Barang": "Kode",
        "Nama Barang": "Nama Produk",
        "Jenis Transaksi": "Kategori",
        "Keterangan": "Tujuan / Sub-Bagian"
    })
    
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        judul = pd.DataFrame([["Laporan Inventaris Gudang", "", "", "", "", "", ""]])
        judul.to_excel(writer, index=False, header=False, startrow=0)
        df.to_excel(writer, index=False, sheet_name='Laporan', startrow=2)
        
    buffer.seek(0)
    return buffer.getvalue()

def get_ringkasan_kpi():
    """Mengambil data total barang, barang masuk, dan barang keluar bulan ini."""
    total_barang = jalankan_query_satu("SELECT COUNT(*) FROM barang")
    
    # PERBAIKAN: Menambahkan ::date pada kolom tanggal agar dibaca sebagai format waktu
    # Serta menggunakan UPPER() agar kata 'Masuk', 'MASUK', atau 'masuk' terbaca semua
    masuk_bulan_ini = jalankan_query_satu("""
        SELECT SUM(jumlah) FROM riwayat 
        WHERE UPPER(jenis_transaksi) = 'MASUK' 
        AND EXTRACT(MONTH FROM tanggal::date) = EXTRACT(MONTH FROM CURRENT_DATE)
        AND EXTRACT(YEAR FROM tanggal::date) = EXTRACT(YEAR FROM CURRENT_DATE)
    """)
    
    keluar_bulan_ini = jalankan_query_satu("""
        SELECT SUM(jumlah) FROM riwayat 
        WHERE UPPER(jenis_transaksi) = 'KELUAR' 
        AND EXTRACT(MONTH FROM tanggal::date) = EXTRACT(MONTH FROM CURRENT_DATE)
        AND EXTRACT(YEAR FROM tanggal::date) = EXTRACT(YEAR FROM CURRENT_DATE)
    """)
    
    return {
        "total_barang": total_barang[0] if total_barang and total_barang[0] else 0,
        "masuk": masuk_bulan_ini[0] if masuk_bulan_ini and masuk_bulan_ini[0] else 0,
        "keluar": keluar_bulan_ini[0] if keluar_bulan_ini and keluar_bulan_ini[0] else 0
    }

def get_data_grafik_riwayat():
    """Mengambil data total barang masuk dan keluar per hari untuk 30 hari terakhir."""
    query = """
        SELECT tanggal::date as tgl, jenis_transaksi, SUM(jumlah) as total
        FROM riwayat
        WHERE tanggal >= CURRENT_DATE - INTERVAL '30 days'
        GROUP BY tanggal::date, jenis_transaksi
        ORDER BY tgl
    """
    return jalankan_query(query)
