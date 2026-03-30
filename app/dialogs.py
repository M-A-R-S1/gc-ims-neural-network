from PySide6 import QtWidgets, QtCore
from PySide6.QtGui import QPixmap
from ui.dataset_ui.CreateLabelDialog import Ui_CreateLabelDialog
from ui.dataset_ui.RenameLabelDialog import Ui_RenameLabelDialog
from ui.MessageDialog import Ui_MessageDialog
from ui.YesNoDialog import Ui_YesNoDialog

class CreateLabelDialog(QtWidgets.QDialog, Ui_CreateLabelDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("Create new label")
        self.setWindowFlags(
            QtCore.Qt.WindowType.Dialog |
            QtCore.Qt.WindowType.CustomizeWindowHint |
            QtCore.Qt.WindowType.WindowCloseButtonHint |
            QtCore.Qt.WindowType.WindowTitleHint
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


class RenameLabelDialog(QtWidgets.QDialog, Ui_RenameLabelDialog):
    def __init__(self, current_name, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("Rename label")
        self.setWindowFlags(
            QtCore.Qt.WindowType.Dialog |
            QtCore.Qt.WindowType.CustomizeWindowHint |
            QtCore.Qt.WindowType.WindowCloseButtonHint |
            QtCore.Qt.WindowType.WindowTitleHint
        )

        # Connect the buttons.
        self.button_ok.clicked.connect(self.accept)
        self.button_cancel.clicked.connect(self.reject)
        # Set The OK button as default.
        self.button_ok.setDefault(True)
        # Focus the lineEdit and set the current name.
        self.lineEdit_label_name.setText(current_name)
        self.lineEdit_label_name.selectAll()
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
            QtCore.Qt.WindowType.Dialog |
            QtCore.Qt.WindowType.CustomizeWindowHint |
            QtCore.Qt.WindowType.WindowCloseButtonHint |
            QtCore.Qt.WindowType.WindowTitleHint
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


class CustomYesNoDialog(QtWidgets.QDialog, Ui_YesNoDialog):
    def __init__(self, title, message, type, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.setWindowFlags(
            QtCore.Qt.WindowType.Dialog |
            QtCore.Qt.WindowType.CustomizeWindowHint |
            QtCore.Qt.WindowType.WindowCloseButtonHint |
            QtCore.Qt.WindowType.WindowTitleHint
        )

        # Set default button.
        self.button_no.setFocus()
        # Set the window title
        self.setWindowTitle(title)
        # Set the message.
        self.label_message.setText(message)
        # Set the icon according to the message type.
        if type == "warning":
            self.label_icon.setPixmap(QPixmap("ui/_pics/icons/attention_orange.png"))

        # Connect the buttons.
        self.button_yes.clicked.connect(self.accept)
        self.button_no.clicked.connect(self.reject)
