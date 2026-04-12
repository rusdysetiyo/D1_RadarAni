import sys
from ui.ui_dashboard import MainWindow
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, 
                             QPushButton, QVBoxLayout, QMessageBox, QStackedWidget)
from PyQt5.QtCore import Qt

# Import class DataManager dari file Anda
# Asumsi: file DataManager disimpan dengan nama data_manager.py
from managers.data_manager import DataManager 

class LoginRegisterApp(QWidget):
    def __init__(self):
        super().__init__()
        # 1. Inisialisasi DataManager
        self.setObjectName("main_layout")
        self.dm = DataManager()
        
        
        self.resize(900, 700) 
        self.setMinimumSize(500, 600)
        self.setWindowTitle('Anime List App - Login System')

        self.container = QWidget()
        self.container.setFixedSize(450, 500)
        self.container.setObjectName("main_container")

        self.setAttribute(Qt.WA_StyledBackground, True)

        self.stacked_widget = QStackedWidget(self.container)
        self.setup_login_ui()
        self.setup_register_ui()
        
        self.stacked_widget.addWidget(self.page_login)
        self.stacked_widget.addWidget(self.page_register)
        
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.addWidget(self.stacked_widget)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.container, 0, Qt.AlignCenter)
        self.setLayout(main_layout)


    def setup_login_ui(self):
        self.page_login = QWidget()
        self.page_login.setObjectName("main_container")
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40) # Memberi padding dalam jendela

        # Judul & Subtitle
        lbl_judul = QLabel("RadarAni")
        lbl_judul.setObjectName("judul") # ID untuk QSS
        
        lbl_sub = QLabel("レーダアニ")
        lbl_sub.setObjectName("subtitle")

        # Input Fields
        lbl_user = QLabel("Username")
        lbl_user.setObjectName("field_label")
        self.user_login = QLineEdit(placeholderText="Enter your username")
        
        lbl_pass = QLabel("Password")
        lbl_pass.setObjectName("field_label")
        self.pass_login = QLineEdit(placeholderText="Enter your password", echoMode=QLineEdit.Password)
        
        # Buttons
        btn_login = QPushButton('Login')
        btn_login.setObjectName("btn_login")
        btn_login.clicked.connect(self.proses_login)
        
        btn_ke_regis = QPushButton("Don't have an account? Register")
        btn_ke_regis.setObjectName("btn_link")
        btn_ke_regis.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        
        # Susun ke Layout
        layout.addWidget(lbl_judul, alignment=Qt.AlignCenter)
        layout.addWidget(lbl_sub, alignment=Qt.AlignCenter)
        layout.addWidget(lbl_user)
        layout.addWidget(self.user_login)
        layout.addWidget(lbl_pass)
        layout.addWidget(self.pass_login)
        layout.addWidget(btn_login)
        layout.addWidget(btn_ke_regis)
        
        self.page_login.setLayout(layout)


    def load_stylesheet(app):
        with open("style.css", "r") as f:
            app.setStyleSheet(f.read())

    def setup_register_ui(self):
        self.page_register = QWidget()
        self.page_register.setObjectName("main_container")
    
        layout = QVBoxLayout()   
        layout.setContentsMargins(40, 40, 40, 40) # Memberi padding dalam jendela

        lbl_judul = QLabel("Registasi Akun")
        lbl_judul.setObjectName("judul") # ID untuk QSS
        
        lbl_sub = QLabel("craete your account to start rating anime!")
        lbl_sub.setObjectName("subtitle")

        lbl_newUser = QLabel("Buat Akun Baru")
        lbl_newUser.setObjectName("field_label")  
        self.user_reg = QLineEdit(placeholderText="Username Baru")

        lbl_newPass = QLabel("Password Baru")
        lbl_newPass.setObjectName("field_label")
        self.pass_reg = QLineEdit(placeholderText="Password Baru", echoMode=QLineEdit.Password)

        btn_regis = QPushButton('Buat Akun')
        btn_regis.setObjectName("btn_regist")
        btn_regis.clicked.connect(self.proses_register)
            
        btn_ke_login = QPushButton('Kembali ke Login')
        btn_ke_login.setObjectName("btn_link")
        btn_ke_login.setFlat(True)
        btn_ke_login.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
            
        layout.addWidget(lbl_judul, alignment=Qt.AlignCenter)
        layout.addWidget(lbl_sub, alignment=Qt.AlignCenter)        
        layout.addWidget(lbl_newUser)
        layout.addWidget(self.user_reg)
        layout.addWidget(lbl_newPass)
        layout.addWidget(self.pass_reg)
        layout.addWidget(btn_regis)
        layout.addWidget(btn_ke_login)
        self.page_register.setLayout(layout)

    def proses_login(self):
        username = self.user_login.text()
        password = self.pass_login.text()

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

    def proses_register(self):
        username = self.user_reg.text()
        password = self.pass_reg.text()

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

