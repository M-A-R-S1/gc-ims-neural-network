from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QVBoxLayout, QWidget
import sys


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("GC-IMS Studio")
        #self.setFixedSize(QSize(600, 400))
        self.setMinimumSize(300, 200)
        self.setMaximumSize(600, 400)

        # Define a label.
        self.label = QLabel()
        self.label.setText("Enter some text...")
        # Define a Line Edit field.
        self.input = QLineEdit()
        self.input.textChanged.connect(self.label.setText)

        # Define a layout and add the label and inputline to it.
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.input)

        # Define a container and add the layout to it.
        container = QWidget()
        container.setLayout(layout)

        self.setCentralWidget(container)


# Create an application instance!
app = QApplication(sys.argv)

# Create a window and show it.
window = MainWindow()
window.show()

# Start the App.
app.exec()