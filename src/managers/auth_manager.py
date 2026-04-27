
class AuthManager:
    def __init__(self, data_manager):
        self.data_manager = data_manager
        # Set ke "U001" agar sistem menganggap ada user yang sedang login
        self._user_aktif = "U001"

    def get_user_aktif(self) -> str:
        return self._user_aktif

    def login(self, username, password) -> bool:
        self._user_aktif = "U001"
        return True

    def register(self, username, password) -> bool:
        pass

    def logout(self):
        self._user_aktif = None
        print("Logout berhasil")

    def hapus_akun_aktif(self):
        if self._user_aktif:
            print(f"Akun {self._user_aktif} dihapus")
            self._user_aktif = None