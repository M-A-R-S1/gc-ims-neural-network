from PySide6 import QtWidgets
from DatasetWidget import Ui_DatasetWidget

class DatasetPage(QtWidgets.QWidget, Ui_DatasetWidget):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

