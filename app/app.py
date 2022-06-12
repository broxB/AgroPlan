import sys

from gui.view import MainWindow
from gui.view_py import MainWindowPy
from PyQt6.QtWidgets import QApplication, QDialog, QMainWindow, QPushButton


def main():
    app = QApplication(sys.argv)
    # app.setStyle("Fusion")
    window = MainWindow()
    # window = MainWindowPy()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
