import sys
import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
#from managers.data_manager import DataManager

class RadarWidget(FigureCanvas):
    def __init__(self, data, parent=None, width=5, height=5, dpi=100):
        # Gunakan Figure yang lebih modern
        self.fig = Figure(figsize=(width, height), dpi=dpi, facecolor='#f0f0f0')
        self.ax = self.fig.add_subplot(111, polar=True)
        
        super(RadarWidget, self).__init__(self.fig)
        self.setParent(parent)
        
        if data:
            self.draw_radar(data)

    def draw_radar(self, data):
        self.ax.clear()
        
        categories = list(data.keys())
        values = list(data.values())
        N = len(categories)

        angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
        
        # Menutup lingkaran
        values += values[:1]
        angles += angles[:1]

        # Desain Radar
        self.ax.fill(angles, values, color='royalblue', alpha=0.3)
        self.ax.plot(angles, values, color='royalblue', linewidth=2, marker='o', markersize=4)

        # Atur Label
        self.ax.set_xticks(angles[:-1])
        self.ax.set_xticklabels(categories, fontsize=9, fontweight='bold')
        
        # Grid dan Skala
        self.ax.set_ylim(0, 10)
        self.ax.grid(True, linestyle='--', alpha=0.7)
        
        self.fig.tight_layout()
        self.draw() # Render ulang canvas

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Inisialisasi Data Manager di sini sekali saja
        #self.dm = DataManager()
        #self.dm._read_json(self.dm.ratings_file)
        
        self.initUI()

    def initUI(self):
        self.setWindowTitle("User Stats Dashboard")
        self.setGeometry(100, 100, 800, 600)

        self.main_widget = QWidget()
        self.main_widget.setObjectName("main_layout")
        self.setCentralWidget(self.main_widget)
        layout = QVBoxLayout(self.main_widget)

        header = QLabel("Visualisasi Rating User U001 - Item A006")
        header.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        layout.addWidget(header)

        image=QLabel()
        pixmap = QPixmap("assets/covers/CIMG001.jpg").scaled(200, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        image.setPixmap(pixmap)
        layout.addWidget(image, alignment=Qt.AlignLeft)

        # Contoh data yang biasanya datang dari DataManager
        data_item = {
            "plot": 4, "visual": 6, "audio": 7, 
            "characterization": 6, "direction": 6
        }

        # Tambahkan Radar Chart
        self.radar_chart = RadarWidget(data_item)
        layout.addWidget(self.radar_chart, alignment=Qt.AlignRight | Qt.AlignTop)

        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())