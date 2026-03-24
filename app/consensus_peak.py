from PySide6 import QtWidgets
from ConsensusPeakWidget import Ui_ConsensusPeakWidget

class ConsensusPeakPage(QtWidgets.QWidget, Ui_ConsensusPeakWidget):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

