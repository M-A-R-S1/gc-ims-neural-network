from PySide6 import QtWidgets, QtCore
from PySide6.QtGui import QPixmap
from ui.dataset_ui.CreateLabelDialog import Ui_CreateLabelDialog
from ui.dataset_ui.RenameLabelDialog import Ui_RenameLabelDialog
from ui.MessageDialog import Ui_MessageDialog
from ui.YesNoDialog import Ui_YesNoDialog
from ProgressDialog import Ui_ProgressDialog
from ui.TwoChoiceDialog import Ui_TwoChoiceDialog

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


class CustomProgressDialog(QtWidgets.QDialog, Ui_ProgressDialog):
    def __init__(self, title, parent=None):
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
        # Connect the buttons.
        self.button_no.clicked.connect(self.reject)
        # Initialize the progress bar.
        self.progressBar.setValue(0)
        self.progressBar.setMaximum(100)


    def update_progress(self, current, total):
        percentage = int((current / total) * 100)
        self.progressBar.setMaximum(total)
        self.progressBar.setValue(current)
        self.label_percent.setText(f"{percentage} %")


class CustomTwoChoiceDialog(QtWidgets.QDialog, Ui_TwoChoiceDialog):
    def __init__(self, button_a_label, button_b_label, title, message, type, parent=None):
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
        self.button_a.setText(button_a_label)
        self.button_b.setText(button_b_label)

        # Connect the buttons.
        self.button_a.clicked.connect(lambda: self.done(1))
        self.button_b.clicked.connect(lambda: self.done(2))
        self.button_no.clicked.connect(self.reject)