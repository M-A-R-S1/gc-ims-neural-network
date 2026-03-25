from PySide6 import QtWidgets
from ui.ClassifierWidget import Ui_ClassifierWidget

class ClassifierPage(QtWidgets.QWidget, Ui_ClassifierWidget):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

