from PySide6 import QtWidgets
from ui.settings_ui.SettingsWidget import Ui_SettingsWidget

class SettingsPage(QtWidgets.QWidget, Ui_SettingsWidget):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

