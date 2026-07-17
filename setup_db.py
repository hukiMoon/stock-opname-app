import bcrypt
from db_utils import jalankan_perintah_db

def tambahkan_user_awal():
    """
    Menambahkan user admin dan staff ke tabel yang sudah ada.
    """
    # Fungsi pembantu untuk insert user dengan penanganan duplikat
    def tambah_user_ke_db(username, password, role):
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
        
        # Menggunakan ON CONFLICT agar tidak error jika user sudah ada
        sql = """
        INSERT INTO users (username, password_hash, role) 
        VALUES (%s, %s, %s) 
        ON CONFLICT (username) DO NOTHING
        """
        try:
            jalankan_perintah_db(sql, (username, hashed, role))
            print(f"✅ User '{username}' dengan role '{role}' berhasil diproses.")
        except Exception as e:
            print(f"❌ Gagal memproses user '{username}': {e}")

    # Menambahkan data
    tambah_user_ke_db("admin", "admin123", "admin")
    tambah_user_ke_db("staff", "staff123", "staff")

if __name__ == "__main__":
    tambahkan_user_awal()
