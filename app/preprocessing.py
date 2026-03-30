from PySide6 import QtWidgets
from PreprocessingWidget import Ui_PreprocessingWidget

class PreprocessingPage(QtWidgets.QWidget, Ui_PreprocessingWidget):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

