import sys

from gui.view import MainWindow
from PyQt6.QtWidgets import QApplication


def main():
    app = QApplication(sys.argv)
    # app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
