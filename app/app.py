import sys

from gui.view import MainWindow
from loguru import logger
from PyQt6.QtWidgets import QApplication


def main():
    app = QApplication(sys.argv)
    logger.debug("Creating app")
    # app.setStyle("windows")
    window = MainWindow(use_ui=True)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
