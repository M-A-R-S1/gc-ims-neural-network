from PySide6 import QtWidgets, QtCore
from DatasetWidget import Ui_DatasetWidget
from app import DatasetLabelEntry
from app.DatasetLabelEntry import Ui_DatasetLabelEntry
from dialogs import CreateLabelDialog, CustomMessageDialog, CustomYesNoDialog


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
        dialog = CreateLabelDialog(self)

        if dialog.exec() == QtWidgets.QDialog.Accepted:
            data = dialog.get_data()
            name = data['name']

            if name:
                if not self.is_label_duplicate(name):
                    self.add_label_entry(name)
                else:
                    CustomMessageDialog.show_error("Error - Duplication", "Label already exists, please choose another name")
            else:
                CustomMessageDialog.show_error("Error - Empty", "Empty label name! Please choose a name for your label.")


    def is_label_duplicate(self, name: str, exclude_widget=None) -> bool:

        for i in range(self.scrollArea_labels_Contents.layout().count()):
            widget = self.scrollArea_labels_Contents.layout().itemAt(i).widget()

            if isinstance(widget, DatasetLabelEntry) and widget is not exclude_widget:
                if widget.label_name.text().lower() == name.lower():
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

        label_name = label.label_name.text()
        dialog = CustomYesNoDialog(title="Delete label",
                                   message=f"Are you sure you want to delete the '{label_name}' label?",
                                   type="warning",
                                   parent=self)


        if dialog.exec() == QtWidgets.QDialog.Accepted:
            label.deleteLater()
            self.scrollArea_labels_Contents.layout().removeWidget(label)
            self.update_label_count()


    def confirm_rename(self, label: DatasetLabelEntry, name: str) -> None:

        if self.is_label_duplicate(name, exclude_widget=label):
            CustomMessageDialog.show_error("Error - Duplication", "Label already exists, please choose another name")
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
        self.label_name.setText(label_name.strip())
        self.label_counter.setText(f"{count}x")
        self.old_label_name = label_name.strip()

        # Connect the delete button.
        self.button_labelDelete.clicked.connect(lambda: self.delete_requested.emit(self))
        # Connect the label Edit line.
        self.button_labelRename.clicked.connect(self.handle_label_rename)
        # TODO ...


    def handle_label_rename(self):
        new_label_name = self.label_name.text().strip()

        if new_label_name == self.old_label_name:
            return

        self.rename_requested.emit(self, new_label_name)


    def use_old_label_name(self):
        self.label_name.setText(self.old_label_name)