from datetime import datetime

class AuthManager:
    # Constructor
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.current_user = None 

    # Manajemen State ----------------------------------------------
    
    def set_user_aktif(self, user_id):
        """Menyimpan ID user ke memori saat berhasil login."""
        self.current_user = user_id
        self.data_manager.simpan_sesi(user_id)
        
    def get_user_aktif(self):
        """Mengembalikan ID user yang sedang login saat ini."""
        return self.current_user
        
    def logout(self):
        """Menghapus sesi dari memori."""
        self.current_user = None
        self.data_manager.hapus_sesi()

    # Login, Register, Hapus Akun -----------------------------------

    def login(self, username, password):
        """Memvalidasi kredensial. Mengembalikan True jika sukses, False jika gagal."""
        # Mengecek kecocokan data
        user_id = self.data_manager.cek_kredensial(username, password)
        
        if user_id is not None:
            # Jika cocok, simpan ID ke memori dan update waktu login
            self.set_user_aktif(user_id)
            self.data_manager.update_last_login(user_id)
            return True
        else:
            return False

    def register(self, username, password):
        """Mendaftarkan user baru. Mengembalikan pesan sukses atau error."""
        # Cek username sudah ada atau belum
        if self.data_manager.cek_username_ada(username):
            return "Username sudah terpakai!"
            
        # Jika belum, buat ID unik dan simpan datanya
        user_id_baru = self.data_manager.generate_user_id()
        waktu_sekarang = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        data_user_baru = {
            "user_id": user_id_baru,
            "username": username,
            "password": password,
            "created_at": waktu_sekarang,
            "last_login": "",
        }
        
        # Simpan ke JSON lewat DataManager
        self.data_manager.simpan_user_baru(data_user_baru)
        return "Registrasi berhasil! Silakan login."

    def hapus_akun_aktif(self):
        """Menghapus akun yang sedang login beserta semua ratingnya."""
        if self.current_user is not None:
            # Suruh DataManager hapus data di JSON
            self.data_manager.hapus_user_dan_rating(self.current_user)
            # Bersihkan sesi di memori
            self.logout()
