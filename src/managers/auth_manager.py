class AuthManager:
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self._user_aktif = None

    def get_user_aktif(self) -> str:
        return self._user_aktif

    def login(self, username, password) -> bool:
        users = self.data_manager._read_json(self.data_manager.users_file) or []

        for u in users:
            if u.get("username") == username and u.get("password") == password:
                self._user_aktif = u.get("user_id")
                return True

        return False

    def register(self, username, password) -> bool:
        users = self.data_manager._read_json(self.data_manager.users_file) or []

        for u in users:
            if u.get("username") == username:
                return False

        new_id = f"U{len(users) + 1:03d}"

        new_user = {
            "user_id": new_id,
            "username": username,
            "password": password
        }

        users.append(new_user)
        self.data_manager._write_json(self.data_manager.users_file, users)

        return True

    def logout(self):
        self._user_aktif = None

    def hapus_akun_aktif(self):
        if self._user_aktif:
            self._user_aktif = None