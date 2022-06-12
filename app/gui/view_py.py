from gui.views.dialog import Ui_Dialog
from gui.views.mainwindow import Ui_MainWindow
from PyQt6.QtWidgets import QDialog, QMainWindow


class MainWindowPy(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self.on_pushBotton_clicked)

    def on_pushBotton_clicked(self):
        dialog = UIDialogPy(self)
        dialog.exec()


class UIDialogPy(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
