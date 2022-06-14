import sys

from gui.view import MainWindow
from loguru import logger
from PyQt6.QtWidgets import QApplication, QDialog, QMainWindow, QPushButton


def main():
    app = QApplication(sys.argv)
    logger.debug("Post creating app")
    # app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
