import sys
from PySide6.QtCore import Qt
from PySide6 import QtWidgets, QtCore
from StartUpWindow import Ui_StartUpWindow


class MainWindow(QtWidgets.QMainWindow, Ui_StartUpWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)


# Create an application instance!
app = QtWidgets.QApplication(sys.argv)

# Create a window and show it.
window = MainWindow()
# turns of the minimize and maximize buttons.
window.setWindowFlags(QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowCloseButtonHint)
window.show()

# Start the App.
app.exec()