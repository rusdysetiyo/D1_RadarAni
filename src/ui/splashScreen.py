from PyQt5.QtWidgets import QSplashScreen, QLabel, QVBoxLayout
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

class SplashScreen(QSplashScreen):
    def __init__(self):
        super().__init__()

        # Set background image for splash screen
        pixmap = QPixmap("assets/covers/splash.png") 
        self.setPixmap(pixmap)
        self.setWindowFlag(Qt.FramelessWindowHint) 
        self.setAutoFillBackground(False)
        
    
    def set_loading_message(self, text):
    # Menggunakan fungsi bawaan QSplashScreen yang lebih aman
        self.showMessage(text, Qt.AlignBottom | Qt.AlignCenter, Qt.blue)

    def mousePressEvent(self, event):
        """Override mousePressEvent to prevent closing on click."""
        pass  

