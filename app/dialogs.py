from PySide6 import QtWidgets, QtCore
from CreateLabelDialog import Ui_CreateLabelDialog
from MessageDialog import Ui_MessageDialog

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


class CustomMessageDialog(QtWidgets.QDialog, Ui_MessageDialog):
    def __init__(self, title, message, type, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.setWindowFlags(
            QtCore.Qt.Dialog |
            QtCore.Qt.CustomizeWindowHint |
            QtCore.Qt.WindowCloseButtonHint |
            QtCore.Qt.WindowTitleHint
        )

        # Set the window title
        self.setWindowTitle(title)
        # Set the message.
        self.label_message.setText(message)
        # Set the icon according to the message type.
        # TODO ....

        # Connect the button with the close function of the dialog.
        self.button_ok.clicked.connect(self.accept)


    @staticmethod
    def show_error(title, message, parent=None):
        dlg = CustomMessageDialog(title, message, "error", parent)
        dlg.exec()