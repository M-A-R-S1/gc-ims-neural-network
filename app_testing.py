from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton
import sys


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("GC-IMS Studio")
        button = QPushButton("Click me")
        self.setCentralWidget(button)

        #self.setFixedSize(QSize(600, 400))
        self.setMinimumSize(300, 200)
        self.setMaximumSize(600, 400)

# Create an application instance!
app = QApplication(sys.argv)

# Create a window and show it.
window = MainWindow()
window.show()

# Start the App.
app.exec()