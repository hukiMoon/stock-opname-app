import bcrypt
from db_utils import jalankan_perintah_db

def buat_user_awal():
    # Contoh password awal
    admin_user = "admin"
    admin_pass = "admin123" 
    
    # Hash password menggunakan bcrypt
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(admin_pass.encode('utf-8'), salt).decode('utf-8')
    
    # Masukkan ke database
    sql = "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, 'admin')"
    jalankan_perintah_db(sql, (admin_user, hashed))
    print("User Admin berhasil dibuat!")

if __name__ == "__main__":
    buat_user_awal()
