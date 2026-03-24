from PySide6 import QtWidgets
from PeakExplorerWidget import Ui_PeakExplorerWidget

class PeakExplorerPage(QtWidgets.QWidget, Ui_PeakExplorerWidget):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

