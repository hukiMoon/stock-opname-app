import sqlite3
import bcrypt

def setup_user_table():
    # Sesuaikan nama file database kamu di sini
    conn = sqlite3.connect('gudang.db') 
    cursor = conn.cursor()

    # Membuat tabel jika belum ada
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT CHECK(role IN ('admin', 'staff')) NOT NULL
        )
    ''')

    # Membuat Admin pertama
    admin_user = "admin"
    admin_pass = "admin123" # Ganti password ini setelah login pertama kali!
    role = "admin"
    
    # Hash password
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(admin_pass.encode('utf-8'), salt)

    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (admin_user, hashed.decode('utf-8'), role)
        )
        conn.commit()
        print("Admin user berhasil dibuat!")
    except sqlite3.IntegrityError:
        print("User admin sudah ada di database.")
    
    conn.close()

if __name__ == "__main__":
    setup_user_table()
