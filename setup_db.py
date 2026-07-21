import streamlit as st
from db_utils import jalankan_query, jalankan_perintah_db
import bcrypt

def inisialisasi_tabel():
    """Membuat tabel-tabel database jika belum ada."""
    # Contoh query pembuatan tabel users (sesuaikan dengan skema PostgreSQL Anda)
    query_users = """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            role VARCHAR(20) NOT NULL
        )
    """
    jalankan_perintah_db(query_users)

def inisialisasi_user_awal():
    """Membuat akun admin default jika tabel masih kosong."""
    cek_user = "SELECT COUNT(*) FROM users"
    
    # PERBAIKAN: Menghapus argumen 'fetch=True' karena jalankan_query otomatis mengambil data
    hasil = jalankan_query(cek_user)
    
    if hasil and hasil[0][0] == 0:
        # Enkripsi password default admin menggunakan bcrypt
        password_polos = "admin123"
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password_polos.encode('utf-8'), salt).decode('utf-8')
        
        query_insert = "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)"
        jalankan_perintah_db(query_insert, ("admin", hashed_password, "admin"))
