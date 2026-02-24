from PySide6.QtWidgets import QApplication, QWidget
import sys

# Create an application instance!
app = QApplication(sys.argv)

# Create a window and show it.
window = QWidget()
window.show()

# Start the App.
app.exec()