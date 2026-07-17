import pandas as pd
import io
import psycopg2
import psycopg2.extras
import streamlit as st
import bcrypt

# Mengambil URL dari file .streamlit/secrets.toml
DB_URL = st.secrets["DB_URL"]

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

@st.cache_data(ttl=600)
def jalankan_query(sql, param=(), commit=False):
    """
    Menjalankan query dengan context manager yang aman.
    """
    data = None
    try:
        # Menggunakan 'with' agar koneksi otomatis tertutup
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

def get_stok_rendah(batas):
    # Gunakan string biasa tanpa spasi aneh
    query = "SELECT nama_barang, stok_sistem FROM barang WHERE stok_sistem <= %s"
    return jalankan_query(query, (batas,))

def get_data_barang(role):
    """
    Mengambil data barang berdasarkan peran pengguna.
    """
    # Contoh koneksi database (sesuaikan dengan kode Anda saat ini)
    # conn = connect_db() 
    
    if role == "admin":
        # Admin bisa melihat seluruh data
        query = "SELECT * FROM inventory"
    else:
        # User biasa hanya melihat barang yang statusnya 'tersedia'
        query = "SELECT * FROM inventory WHERE status = 'tersedia'"

def cek_barang_ada(nama_barang):
    # Mengecek apakah nama barang sudah ada (case-insensitive)
    query = "SELECT COUNT(*) FROM barang WHERE LOWER(nama_barang) = LOWER(%s)"
    hasil = jalankan_query(query, (nama_barang,))
    # hasil akan berupa list berisi tuple, misal: [(1,)]
    return hasil[0][0] > 0

def export_to_excel(query, params=(), kolom_pilihan=None):
    data = jalankan_query(query, params)
    nama_kolom = ["id", "kode_barang", "nama_barang", "jenis_transaksi", "jumlah", "satuan", "tanggal", "keterangan"]
    df = pd.DataFrame(data, columns=nama_kolom)
    
    # Filter hanya kolom yang dipilih di multiselect
    if kolom_pilihan:
        df = df[kolom_pilihan]
        
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Data')
    buffer.seek(0)
    return buffer.getvalue()

def jalankan_perintah_db(sql, params=()):
    """Fungsi untuk perintah INSERT, UPDATE, atau DELETE yang butuh commit"""
    conn = psycopg2.connect(DB_URL) # Sesuaikan dengan variabel koneksi Anda
    try:
        with conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
    finally:
        conn.close()

def update_stok_opname(data_list):
    """Logika untuk update stok dan insert log secara batch"""
    conn = psycopg2.connect(DB_URL)
    try:
        with conn:
            with conn.cursor() as cursor:
                # Update stok
                sql_update = "UPDATE barang SET stok_sistem = %s WHERE kode_barang = %s"
                psycopg2.extras.execute_batch(cursor, sql_update, [(d[0], d[2]) for d in data_list])
                
                # Insert log
                sql_log = "INSERT INTO log_opname (kode_barang, stok_sebelum, stok_sesudah) VALUES (%s, %s, %s)"
                psycopg2.extras.execute_batch(cursor, sql_log, [(d[2], d[1], d[0]) for d in data_list])
    finally:
        conn.close()

def ambil_data_log():
    """
    Mengambil data log dari tabel log_opname.
    Fungsi ini diletakkan di db_utils agar bisa digunakan di banyak halaman.
    """
    # Menggunakan fungsi jalankan_query yang sudah ada di file ini
    query = "SELECT id, kode_barang, stok_sebelum, stok_sesudah, waktu_opname, petugas FROM log_opname ORDER BY id DESC LIMIT 50"
    
    data = jalankan_query(query)
    
    # Memproses data menjadi DataFrame
    if not data:
        return pd.DataFrame(columns=["ID", "Kode Barang", "Stok Sebelum", "Stok Sesudah", "Tanggal"])
    
    df = pd.DataFrame(data, columns=["ID", "Kode Barang", "Stok Sebelum", "Stok Sesudah", "Tanggal"])
    return df
