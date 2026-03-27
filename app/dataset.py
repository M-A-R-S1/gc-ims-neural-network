from PySide6 import QtWidgets, QtCore, QtGui
from DatasetWidget import Ui_DatasetWidget
import DatasetLabelEntry
from DatasetLabelEntry import Ui_DatasetLabelEntry
from DatasetSpectrumEntry import Ui_DatasetSpectrumEntry
from dialogs import CreateLabelDialog, CustomMessageDialog, CustomYesNoDialog, RenameLabelDialog
from pathlib import Path


class DatasetPage(QtWidgets.QWidget, Ui_DatasetWidget):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # Defining the layout.
        self.scrollArea_labels_Contents.layout().setAlignment(QtCore.Qt.AlignTop)
        self.scrollArea_labels_Contents.layout().setSpacing(5)
        self.scrollArea_spectra_Contents.layout().setAlignment(QtCore.Qt.AlignTop)
        self.scrollArea_spectra_Contents.layout().setSpacing(5)
        # Connect the "add label" button.
        self.button_add_label.clicked.connect(self.open_label_file_dialog)
        # The selected label.
        self.current_selected_label = None
        # Connect the "add spectra" button.
        self.button_add_spectra.clicked.connect(self.open_spectra_file_dialog)


    def open_label_file_dialog(self):
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
                if widget.label_name.text() == name:
                    return True

        return False


    def add_label_entry(self, name: str) -> None:
        label = DatasetLabelEntry(name)
        label.delete_requested.connect(self.confirm_delete)
        label.rename_requested.connect(self.confirm_rename)
        label.clicked.connect(self.handle_label_selection)
        self.scrollArea_labels_Contents.layout().insertWidget(self.scrollArea_labels_Contents.layout().count() - 1, label)
        self.update_label_count()


    def handle_label_selection(self, selected_widget) -> None:
        self.clear_spectra_list()
        if self.current_selected_label:
            self.current_selected_label.set_active(False)

        self.current_selected_label = selected_widget
        self.current_selected_label.set_active(True)

        label_text = selected_widget.label_name.text()
        self.spectra_container_header.setText(label_text)


    def confirm_delete(self, label: DatasetLabelEntry) -> None:

        label_name = label.label_name.text()
        dialog = CustomYesNoDialog(title="Delete label",
                                   message=f"Are you sure you want to delete the '{label_name}' label?",
                                   type="warning",
                                   parent=self)


        if dialog.exec() == QtWidgets.QDialog.Accepted:
            if label == self.current_selected_label:
                self.spectra_container_header.setText("No label selected")
                self.current_selected_label = None

            label.deleteLater()
            self.scrollArea_labels_Contents.layout().removeWidget(label)
            self.update_label_count()


    def confirm_rename(self, label: DatasetLabelEntry, name: str) -> None:

        if self.is_label_duplicate(name, exclude_widget=label):
            CustomMessageDialog.show_error("Error - Duplication", "Label already exists, please choose another name")
            label.use_old_label_name()
            return

        label.label_name.setText(name)
        label.old_label_name = name

        if label == self.current_selected_label:
            self.spectra_container_header.setText(name)


    def update_label_count(self) -> None:
        count = 0

        for i in range(self.scrollArea_labels_Contents.layout().count()):
            widget = self.scrollArea_labels_Contents.layout().itemAt(i).widget()
            if isinstance(widget, DatasetLabelEntry):
                count += 1

        self.label_labelcounter.setText(f"{count} labels")


    def open_spectra_file_dialog(self):
        if not self.current_selected_label:
            CustomMessageDialog.show_error("Error - no label selected!", "You can't add a spectrum unless you select a label first!" , self)
            return

        file_paths, _ = QtWidgets.QFileDialog.getOpenFileNames(self,
                                                               "Select GC-IMS spectra",
                                                               "",
                                                               "GC-IMS File (*.mea)")

        if file_paths:
            self.add_spectra_to_list(file_paths)


    def add_spectra_to_list(self, file_paths):
        file_paths.sort(key=lambda x: str(x).lower())
        layout = self.scrollArea_spectra_Contents.layout()

        for path in file_paths:
            new_spectrum = DatasetSpectrumEntry(path, layout.count()+1)
            new_spectrum.delete_requested.connect(self.remove_spectrum)
            layout.insertWidget(layout.count(), new_spectrum)


    def clear_spectra_list(self):
        layout = self.scrollArea_spectra_Contents.layout()
        while layout.count() > 0:
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()


    def remove_spectrum(self, spectrum_widget):
        full_text = spectrum_widget.spectrum_name.text()
        display_name = full_text.split(" - ", 1)[1] if " - " in full_text else full_text

        dialog = CustomYesNoDialog(title="Delete spectrum",
                                   message=f"Do you really want to remove this spectrum?\n\n {display_name}",
                                   type="warning",
                                   parent=self)

        if dialog.exec() == QtWidgets.QDialog.Accepted:
            spectrum_widget.deleteLater()
            self.scrollArea_spectra_Contents.layout().removeWidget(spectrum_widget)
            QtCore.QTimer.singleShot(10, self.renumber_spectra)


    def renumber_spectra(self):
        layout = self.scrollArea_spectra_Contents.layout()
        counter = 1

        for i in range(layout.count()):
            item = layout.itemAt(i)
            widget = item.widget()

            if isinstance(widget, DatasetSpectrumEntry):
                current_text = widget.spectrum_name.text()
                if " - " in current_text:
                    pure_name = current_text.split(" - ", 1)[1]
                    widget.spectrum_name.setText(f"{counter} - {pure_name}")
                    counter += 1


class DatasetLabelEntry(QtWidgets.QLabel, Ui_DatasetLabelEntry):
    # Delete signal for the label.
    delete_requested = QtCore.Signal(object)
    # Rename signal.
    rename_requested = QtCore.Signal(object, str)
    # Label was clicked signal.
    clicked = QtCore.Signal(object)

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
        self.button_labelRename.clicked.connect(self.rename_dialog)
        # Hover effects for the rename button.
        self.button_labelRename.enterEvent = lambda e: self.button_hover_effect(self.button_labelRename, 'edit_orange', True)
        self.button_labelRename.leaveEvent = lambda e: self.button_hover_effect(self.button_labelRename, 'edit_grey', False)
        # Hover effects for the delete button.
        self.button_labelDelete.enterEvent = lambda e: self.button_hover_effect(self.button_labelDelete, 'delete_magenta',True)
        self.button_labelDelete.leaveEvent = lambda e: self.button_hover_effect(self.button_labelDelete, 'delete_grey',False)


    def button_hover_effect(self,
                            button: QtWidgets.QPushButton,
                            icon_name: str,
                            hover: bool):

        if hover:
            button.setIcon(QtGui.QIcon(f'ui/_pics/icons/{icon_name}.png'))
        else:
            button.setIcon(QtGui.QIcon(f'ui/_pics/icons/{icon_name}.png'))

    def rename_dialog(self):
        dialog = RenameLabelDialog(self.label_name.text(), self)

        if dialog.exec() == QtWidgets.QDialog.Accepted:
            new_label_name = dialog.get_data()['name']

            if new_label_name == self.label_name.text():
                return

            self.rename_requested.emit(self, new_label_name)


    def use_old_label_name(self):
        self.label_name.setText(self.old_label_name)


    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.button() == QtCore.Qt.LeftButton:
            self.clicked.emit(self)


    def set_active(self, active: bool) -> None:
        if active:
            self.label_name.setStyleSheet("border: None; color: #ff9000; background-color: transparent; font-weight: bold;")
            self.label_counter.setStyleSheet("border: None; color: #ff9000; background-color: transparent; font-weight: bold;")
        else:
            self.label_name.setStyleSheet("border: None; color: #ebebeb; background-color: transparent; font-weight: light;")
            self.label_counter.setStyleSheet("border: None; color: #ebebeb; background-color: transparent; font-weight: light;")


class DatasetSpectrumEntry(QtWidgets.QWidget, Ui_DatasetSpectrumEntry):
    # Delete signal
    delete_requested = QtCore.Signal(object)

    def __init__(self, path:str, number: int):
        super().__init__()
        self.setupUi(self)

        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)

        self.spectrum_path = Path(path)
        self.spectrum_name.setText(f"{number} - {self.spectrum_path.parent.name}/{self.spectrum_path.stem}")
        self.button_spectrumDelete.enterEvent = lambda e: self.button_spectrumDelete.setIcon(QtGui.QIcon(r'ui/_pics/icons/delete_magenta.png'))
        self.button_spectrumDelete.leaveEvent = lambda e: self.button_spectrumDelete.setIcon(QtGui.QIcon(r'ui/_pics/icons/delete_grey.png'))

        # Connect the delete button
        self.button_spectrumDelete.clicked.connect(lambda: self.delete_requested.emit(self))