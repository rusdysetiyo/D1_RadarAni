#auth_manager.py
import sys
from ui.ui_dashboard import MainWindow
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, 
                             QPushButton, QVBoxLayout, QMessageBox, QStackedWidget)
from PyQt5.QtCore import Qt

# Import class DataManager dari file Anda
# Asumsi: file DataManager disimpan dengan nama data_manager.py
from managers.data_manager import DataManager

class AuthManager:
    def __init__(self):
        self.dm = DataManager()

    def handle_login_click(self):
        # Grab the text here to keep the connection line clean
        u = self.user_login.text()
        p = self.pass_login.text()
        self.proses_login(u, p)

    def proses_login(self, username, password):
        # 2. Menggunakan fungsi DataManager untuk cek kredensial
        if self.dm.cek_kredensial(username, password):
            # Ambil data user untuk mendapatkan ID (untuk simpan sesi)
            users = self.dm._read_json(self.dm.users_file)
            user_data = next(u for u in users if u['username'].lower() == username.lower())
            
            # 3. Simpan sesi login
            self.dm.simpan_sesi(user_data['user_id'])
            
            QMessageBox.information(self, "Berhasil", f"Halo {username}!.")

            self.Dashboard = MainWindow()
            self.Dashboard.show()
            self.close()  # Tutup jendela login setelah berhasil login
            # Di sini Anda bisa membuka Dashboard Utama Anime
        else:
            QMessageBox.warning(self, "Gagal", "Username atau password salah!")

    def proses_register(self, username, password):
        # username = self.user_reg.text()
        # password = self.pass_reg.text()

        if not username or not password:
            return QMessageBox.warning(self, "Error", "Field tidak boleh kosong!")

        # 4. Menggunakan DataManager untuk cek duplikasi username
        if self.dm.cek_username_ada(username):
            return QMessageBox.warning(self, "Error", "Username sudah digunakan!")

        # 5. Generate ID otomatis melalui DataManager
        new_id = self.dm.generate_user_id()

        data_user_baru = {
            "user_id": new_id,
            "username": username,
            "password": password,
            "created_at": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        }

        # 6. Simpan melalui DataManager
        if self.dm.simpan_user_baru(data_user_baru):
            QMessageBox.information(self, "Sukses", f"Akun berhasil dibuat dengan ID: {new_id}")
            self.stacked_widget.setCurrentIndex(0)