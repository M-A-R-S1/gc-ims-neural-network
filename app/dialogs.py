from PySide6 import QtWidgets, QtCore
from CreateLabelDialog import Ui_CreateLabelDialog


class CreateLabelDialog(QtWidgets.QDialog, Ui_CreateLabelDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("Create new label")
        self.setWindowFlags(
            QtCore.Qt.Dialog |
            QtCore.Qt.CustomizeWindowHint |
            QtCore.Qt.WindowCloseButtonHint |
            QtCore.Qt.WindowTitleHint
        )

        # Connect the buttons.
        self.button_ok.clicked.connect(self.accept)
        self.button_cancel.clicked.connect(self.reject)
        # Set The OK button as default.
        self.button_ok.setDefault(True)
        # Focus the lineEdit.
        self.lineEdit_label_name.setFocus()

    def get_data(self):
        return {
            "name": self.lineEdit_label_name.text().strip()
        }