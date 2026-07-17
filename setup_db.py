from db_utils import jalankan_perintah_db
import bcrypt

def inisialisasi_user_awal():
    """Menambahkan user admin dan staff jika belum ada."""
    users = [
        ("98010786", "1P@ny001", "admin"),
        ("staff", "staff123", "staff")
    ]
    
    for username, password, role in users:
        # Hashing password
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
        
        # SQL dengan ON CONFLICT agar tidak error jika sudah ada
        sql = """
        INSERT INTO users (username, password_hash, role) 
        VALUES (%s, %s, %s) 
        ON CONFLICT (username) DO NOTHING
        """
        try:
            jalankan_perintah_db(sql, (username, hashed, role))
        except Exception as e:
            print(f"Error saat setup user {username}: {e}")
