import bcrypt
from db_utils import jalankan_query, jalankan_perintah_db

def inisialisasi_user_awal():
    """Menambahkan user admin dan staff hanya jika belum ada di database."""
    users = [
        ("98010786", "1P@ny001", "admin"),
        ("staff", "staff123", "staff")
    ]
    
    for username, raw_password, role in users:
        # 1. Cek dulu apakah user sudah ada di database
        # Asumsi: jalankan_query mengembalikan list of tuples
        cek_user = jalankan_query("SELECT username FROM users WHERE username = %s", (username,))
        
        if not cek_user:
            # 2. Hanya lakukan hashing jika user memang belum ada
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(raw_password.encode('utf-8'), salt).decode('utf-8')
            
            sql = """
            INSERT INTO users (username, password_hash, role) 
            VALUES (%s, %s, %s)
            """
            try:
                jalankan_perintah_db(sql, (username, hashed, role))
                print(f"User {username} berhasil ditambahkan.")
            except Exception as e:
                print(f"Error saat setup user {username}: {e}")
        else:
            print(f"User {username} sudah ada, melewati proses setup.")
