from gui.tableview_model import MyTableView
from gui.treeview_model import MyTreeView
from gui.views import dialog, mainwindow
from loguru import logger
from PyQt6 import uic
from PyQt6.QtCore import QEvent, QModelIndex, Qt
from PyQt6.QtCore import pyqtSlot as Slot
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSpinBox,
)
from utils.utils import get_fields_list

USE_UI = True


class MainWindow(QMainWindow, mainwindow.Ui_MainWindow):
    def __init__(self, parent=None, use_ui=True):
        logger.debug("Init {}", self.__class__.__name__)
        super().__init__(parent)
        global USE_UI
        USE_UI = use_ui
        logger.debug("Init setup UI")
        uic.loadUi("qtdesigner/AgroPlan/mainwindow.ui", self) if USE_UI else self.setupUi(self)
        logger.debug("Post setup UI")
        self.setFocus()
        self.pushButton: QPushButton
        self.comboBox: QComboBox
        self.comboBox.addItems(get_fields_list("2022"))
        # self.combo_lineEdit = MyLineEdit(self.comboBox)
        # self.combo_lineEdit.setClearButtonEnabled(True)
        # self.comboBox.setLineEdit(self.combo_lineEdit)
        # self.comboBox.setEditable(True)
        # self.comboBox.completer().setFilterMode(Qt.MatchFlag.MatchContains)
        # self.comboBox.completer().setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        # self.comboBox.completer().popup().clicked.connect(self.select_popup)
        # self.comboBox.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.comboBox.currentIndexChanged.connect(self.change_comboBox)
        self.spinBox.valueChanged.connect(self.change_spinBox)
        self.spin_edit = QLineEdit()
        self.spinBox.setLineEdit(self.spin_edit)
        self.spin_edit.setReadOnly(True)
        self.treeView.clicked.connect(self.click_treeview_item)
        self.treeView: MyTreeView
        self.tableView: MyTableView
        self.spinBox: QSpinBox
        self.treeView.insert_data(self.comboBox.currentText())
        self.tableView.insert_data(self.comboBox.currentText(), self.spinBox.value())

    @Slot()
    def select_popup(self):
        """Remove focus from combo_lineEdit if the completer was clicked"""
        # self.combo_lineEdit.setFocus()
        # self.setFocus()

    def change_comboBox(self) -> None:
        logger.info(f"Selected: {self.comboBox.currentText()} - {self.spinBox.value()}")
        self.treeView.insert_data(self.comboBox.currentText())
        self.tableView.insert_data(self.comboBox.currentText(), self.spinBox.value())

    def change_spinBox(self):
        logger.info(f"Selected: {self.comboBox.currentText()} - {self.spinBox.value()}")
        self.tableView.insert_data(self.comboBox.currentText(), self.spinBox.value())
        if self.spinBox.hasFocus():
            self.setFocus()

    def click_treeview_item(self, value: QModelIndex):
        if value.parent().data() is None:
            year = int(value.data())
        else:
            year = int(value.parent().data())
        self.spinBox.setValue(year)

    @Slot(name="on_pushButton_3_clicked")
    def lower_combobox_index(self) -> None:
        index = self.comboBox.currentIndex()
        if index == 0:
            return
        self.comboBox.setCurrentIndex(index - 1)

    @Slot(name="on_pushButton_2_clicked")
    def raise_combobox_index(self) -> None:
        index = self.comboBox.currentIndex()
        if index == self.comboBox.count() - 1:
            return
        self.comboBox.setCurrentIndex(index + 1)

    @Slot(name="on_pushButton_clicked")
    @Slot(name="on_actionDialog_triggered")
    def open_dialog(self) -> None:
        dialog = UIDialog(self)
        dialog.exec()

    @Slot(name="on_actionDemo_triggered")
    def demo_treeview(self):
        self.treeView.setup_demo()


class UIDialog(QDialog, dialog.Ui_Dialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi("qtdesigner/AgroPlan/dialog.ui", self) if USE_UI else self.setupUi(self)
        self.pushButton_3: QPushButton
        self.pushButton_3.setChecked(True)
        self.label: QLabel
        self.label.installEventFilter(self)
        self.label.setMouseTracking(True)

    @Slot(name="on_pushButton_clicked")
    def clear_button(self):
        if self.textEdit.document().isEmpty() and self.pushButton_3.isChecked():
            QMessageBox.critical(
                self,
                "Error dialog",
                "Can't clear text if there is none!",
                buttons=QMessageBox.StandardButton.Discard
                | QMessageBox.StandardButton.NoToAll
                | QMessageBox.StandardButton.Ignore,
                defaultButton=QMessageBox.StandardButton.Discard,
            )
        else:
            self.textEdit.clear()

    @Slot(bool)
    def on_pushButton_3_clicked(self, checked: bool) -> None:
        text = "Checked" if checked else "Unchecked"
        self.pushButton_3.setText(text)
        self.setWindowTitle(text)
        logger.debug(text)

    def eventFilter(self, source, event):
        if event.type() == QEvent.Type.MouseButtonPress and source is self.label:
            self.label.setText(self.check_mouse_button(self, event))
        return super(UIDialog, self).eventFilter(source, event)

    def check_mouse_button(self, element, event: QMouseEvent) -> None:
        match event.button():
            case Qt.MouseButton.LeftButton:
                txt = "mousePressEvent LEFT"
            case Qt.MouseButton.MiddleButton:
                txt = "mousePressEvent MIDDLE"
            case Qt.MouseButton.RightButton:
                txt = "mousePressEvent RIGHT"
            case Qt.MouseButton.NoButton:
                txt = "mousePressEvent NONE"
        return txt


class ComboLineEdit(QLineEdit):
    """Custom QLineEdit to force special behavior on the entering left-click"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.first_click = True  # trigger mousePress only on entering for the first time

    def mousePressEvent(self, e):
        super().mousePressEvent(e)
        if e.button() == Qt.MouseButton.LeftButton and self.first_click:
            # self.selectAll()
            self.parent().showPopup()
            self.first_click = False

    def focusOutEvent(self, e):
        super().focusOutEvent(e)
        if e.reason() == Qt.FocusReason.MouseFocusReason:
            self.parent().setCurrentText(self.parent().itemText(self.parent().currentIndex()))
            self.first_click = True
