import sys
from PySide6 import QtWidgets
from ui.MainWindow import Ui_MainWindow


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)


# Create an application instance!
app = QtWidgets.QApplication(sys.argv)

# Create a window and show it.
window = MainWindow()
window.show()

# Start the App.
app.exec()