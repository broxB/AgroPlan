from gui.tableview_model import MyTableView
from gui.treeview_model import MyTreeView
from gui.views import dialog, mainwindow
from loguru import logger
from PyQt6 import uic
from PyQt6.QtCore import QModelIndex, Qt
from PyQt6.QtCore import pyqtSlot as Slot
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QGroupBox,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QStyle,
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
        uic.loadUi("qtdesigner/AgroPlan/new_mainwindow.ui", self) if USE_UI else self.setupUi(self)
        logger.debug("Post setup UI")
        self.setFocus()
        self.pushButton_soil_samples: QPushButton
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
        self.comboBox.currentIndexChanged.connect(self.changed_comboBox)
        self.spinBox.valueChanged.connect(self.changed_spinBox)
        self.spinBox.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.treeView.clicked.connect(self.click_treeview_item)
        self.treeView: MyTreeView
        self.tableView: MyTableView
        self.spinBox: QSpinBox
        self.treeView.insert_data(self.comboBox.currentText())
        self.tableView.cultivation_data(self.comboBox.currentText(), self.spinBox.value())
        self.groupBox_zhf: QGroupBox
        self.groupBox_zhf.setVisible(True)

    # @Slot()
    # def select_popup(self):
    #     """Remove focus from combo_lineEdit if the completer was clicked"""
    #     self.combo_lineEdit.setFocus()
    #     self.setFocus()

    def generate_list(self):
        self.comboBox.addItems()

    def changed_comboBox(self):
        logger.info(f"Selected: {self.comboBox.currentText()} - {self.spinBox.value()}")
        self.treeView.insert_data(self.comboBox.currentText())
        self.tableView.cultivation_data(self.comboBox.currentText(), self.spinBox.value())

    def changed_spinBox(self):
        logger.info(f"Selected: {self.comboBox.currentText()} - {self.spinBox.value()}")
        self.tableView.cultivation_data(self.comboBox.currentText(), self.spinBox.value())
        if self.spinBox.hasFocus():
            self.setFocus()

    def click_treeview_item(self, value: QModelIndex):
        if value.parent().data() is None:
            # year = int(value.data())
            return
        else:
            year = int(value.parent().data())
        self.spinBox.setValue(year)

    @Slot(name="on_pushButton_prev_clicked")
    def lower_combobox_index(self) -> None:
        index = self.comboBox.currentIndex()
        if index == 0:
            return
        self.comboBox.setCurrentIndex(index - 1)

    @Slot(name="on_pushButton_next_clicked")
    def raise_combobox_index(self) -> None:
        index = self.comboBox.currentIndex()
        if index == self.comboBox.count() - 1:
            return
        self.comboBox.setCurrentIndex(index + 1)

    @Slot(name="on_pushButton_soil_samples_clicked")
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
        self.select_button: QPushButton
        self.close_button: QPushButton
        self.tableView: MyTableView
        self.label: QLabel
        self.tableView.soil_sample_data(self.parent().comboBox.currentText())
        self.tableView.resizeColumnsToContents()
        self.set_window_size()

    def set_window_size(self):
        margins = self.layout().contentsMargins()
        self.resize(
            (
                margins.left()
                + margins.right()
                + self.tableView.frameWidth() * 2
                + self.tableView.verticalHeader().width()
                + self.tableView.horizontalHeader().length()
                + self.tableView.style().pixelMetric(QStyle.PixelMetric.PM_ScrollBarExtent)
            ),
            self.height(),
        )

    @Slot(name="on_select_button_clicked")
    def select_sample(self):
        if not self.tableView.hasFocus():
            QMessageBox.critical(
                self,
                "Error dialog",
                "Please select a soil sample.",
                buttons=QMessageBox.StandardButton.Ok,
            )
        else:
            self.reject()


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
