# This is a sample Python script.
import sys
import json
import os
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, 
                             QPushButton, QVBoxLayout, QMessageBox, QStackedWidget)
from PyQt5.QtCore import Qt, QTimer
from ui.ui_login import LoginRegisterApp
from managers.data_manager import DataManager
from ui.splashScreen import SplashScreen

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


import os

def apply_style(app):
    # Mencari path absolut dari file main.py
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Gabungkan dengan folder 'ui' dan file 'style.qss'
    qss_path = os.path.join(base_dir, "ui", "style.qss")
    
    if os.path.exists(qss_path):
        try:
            with open(qss_path, "r", encoding="utf-8") as f:
                app.setStyleSheet(f.read())
                app.processEvents()
            print(f"✅ Style berhasil dimuat dari: {qss_path}")
        except Exception as e:
            print(f"❌ Gagal membaca file QSS: {e}")
    else:
        print(f"⚠️ Error: File TIDAK ditemukan di {qss_path}")
        # Cetak isi folder untuk debug jika masih gagal
        if os.path.exists(os.path.join(base_dir, "ui")):
            print(f"Isi folder ui: {os.listdir(os.path.join(base_dir, 'ui'))}")

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app = QApplication(sys.argv)

    #splash = SplashScreen()
    #splash.show()
    #splash.set_loading_message("Initializing system...")
    
    
    # Panggil fungsi stylesheet di sini
    try:
        apply_style(app)
    except FileNotFoundError:
        print("Peringatan: style.css tidak ditemukan!")

    #QTimer.singleShot(3000, splash.close)  # Tutup splash screen setelah 3 detik
    window = LoginRegisterApp()
    QTimer.singleShot(3000, window.show)  # Tampilkan jendela utama setelah 3 detik
    sys.exit(app.exec_())
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
