from PySide6 import QtWidgets, QtCore
from DatasetWidget import Ui_DatasetWidget
from app import DatasetLabelEntry
from app.DatasetLabelEntry import Ui_DatasetLabelEntry


class DatasetPage(QtWidgets.QWidget, Ui_DatasetWidget):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # Defining the layout.
        self.scrollArea_labels_Contents.layout().setAlignment(QtCore.Qt.AlignTop)
        self.scrollArea_labels_Contents.layout().setSpacing(5)

        # Connect the "add label" button.
        self.button_add_label.clicked.connect(self.open_add_label_dialog)


    def open_add_label_dialog(self):
        name, status = QtWidgets.QInputDialog.getText(self, "Create a new label", "Label name:")

        if status and name:
            if self.is_label_duplicate(name.strip()):
                QtWidgets.QMessageBox.warning(self, "Error!", "Label already exists, please choose another name")
                return
            else:
                self.add_label_entry(name.strip())


    def is_label_duplicate(self, name: str, exclude_widget=None) -> bool:

        for i in range(self.scrollArea_labels_Contents.layout().count()):
            widget = self.scrollArea_labels_Contents.layout().itemAt(i).widget()

            if isinstance(widget, DatasetLabelEntry) and widget is not exclude_widget:
                if widget.lineEdit_label.text().lower() == name.lower():
                    return True

        return False


    def add_label_entry(self, name: str) -> None:
        label = DatasetLabelEntry(name)
        label.delete_requested.connect(self.confirm_delete)
        label.rename_requested.connect(self.confirm_rename)
        #self.scrollArea_labels_Contents.layout().addWidget(label)
        self.scrollArea_labels_Contents.layout().insertWidget(self.scrollArea_labels_Contents.layout().count() - 1, label)
        self.update_label_count()


    def confirm_delete(self, label: DatasetLabelEntry) -> None:

        label_name = label.lineEdit_label.text()

        message = QtWidgets.QMessageBox(self)
        message.setWindowTitle("Delete label")
        message.setText(f"Are you sure you want to delete the '{label_name}' label?")
        message.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        message.setDefaultButton(QtWidgets.QMessageBox.No)

        if message.exec() == QtWidgets.QMessageBox.Yes:
            label.deleteLater()
            self.scrollArea_labels_Contents.layout().removeWidget(label)
            self.update_label_count()


    def confirm_rename(self, label: DatasetLabelEntry, name: str) -> None:

        if self.is_label_duplicate(name, exclude_widget=label):
            QtWidgets.QMessageBox.warning(self, "Error!", "Label already exists, please choose another name")
            label.use_old_label_name()
            return

        label.use_old_label_name = name


    def update_label_count(self) -> None:
        count = 0

        for i in range(self.scrollArea_labels_Contents.layout().count()):
            widget = self.scrollArea_labels_Contents.layout().itemAt(i).widget()
            if isinstance(widget, DatasetLabelEntry):
                count += 1

        self.label_labelcounter.setText(f"{count} labels")


class DatasetLabelEntry(QtWidgets.QLabel, Ui_DatasetLabelEntry):
    # Delete signal for the label.
    delete_requested = QtCore.Signal(object)
    # Rename signal.
    rename_requested = QtCore.Signal(object, str)

    def __init__(self,
                 label_name: str,
                 count: int = 0) -> None:

        super().__init__()
        self.setupUi(self)

        # Set the label values.
        self.lineEdit_label.setText(label_name.strip())
        self.label_counter.setText(f"{count}x")
        self.old_label_name = label_name.strip()

        # Connect the delete button.
        self.button_labelDelete.clicked.connect(lambda: self.delete_requested.emit(self))
        # Connect the label Edit line.
        self.lineEdit_label.editingFinished.connect(self.handle_label_rename)


    def handle_label_rename(self):
        new_label_name = self.lineEdit_label.text().strip()

        if new_label_name == self.old_label_name:
            return

        self.rename_requested.emit(self, new_label_name)


    def use_old_label_name(self):
        self.lineEdit_label.setText(self.old_label_name)