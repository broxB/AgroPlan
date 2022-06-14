from gui.tableview_model import MyTableView
from gui.treeview_model import MyTreeView
from gui.views import dialog, mainwindow
from loguru import logger
from modules.utils import get_fields_list, load_data
from PyQt6 import uic
from PyQt6.QtCore import QEvent, Qt
from PyQt6.QtCore import pyqtSlot as Slot
from PyQt6.QtGui import (
    QAction,
    QContextMenuEvent,
    QFocusEvent,
    QMouseEvent,
    QStandardItemModel,
)
from PyQt6.QtWidgets import (
    QComboBox,
    QCompleter,
    QDialog,
    QLabel,
    QLineEdit,
    QListView,
    QListWidget,
    QMainWindow,
    QMenu,
    QPushButton,
    QTableView,
    QTreeView,
    QTreeWidget,
)


class MainWindow(QMainWindow, mainwindow.Ui_MainWindow):
    def __init__(self, parent=None):
        logger.debug("Init {}", self.__class__.__name__)
        super().__init__(parent)
        logger.debug("Init uic.loadUi")
        uic.loadUi("qtdesigner/AgroPlan/mainwindow.ui", self)
        # self.setupUi(self)
        logger.debug("Post uic.loadUi")
        self.pushButton: QPushButton
        self.comboBox: QComboBox
        self.comboBox.addItems(get_fields_list("2022"))
        self.combo_lineEdit = MyLineEdit(self.comboBox)
        self.combo_lineEdit.setClearButtonEnabled(True)
        self.comboBox.setLineEdit(self.combo_lineEdit)
        self.comboBox.setEditable(True)
        self.comboBox.completer().setFilterMode(Qt.MatchFlag.MatchContains)
        self.comboBox.completer().setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.comboBox.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.comboBox.currentIndexChanged.connect(self.change_comboBox_item)
        self.comboBox.setFocus()
        self.treeView: MyTreeView
        self.treeView.insert_data(self.comboBox.currentText())
        self.treeView.doubleClicked.connect(self.getValue)
        self.tableView: MyTableView

    def getValue(self, val):
        logger.info(f"{val.data()=}, {val.row()=}, {val.column()=}")

    @Slot(name="on_comboBox_currentIndexChanged")
    def change_comboBox_item(self) -> None:
        self.treeView.insert_data(self.comboBox.currentText())
        self.combo_lineEdit.first_click = True
        self.tableView.setFocus()
        logger.info(
            f"Selected: {self.comboBox.currentText()}, " f"Index: {self.comboBox.currentIndex()}"
        )

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
        # self.setupUi(self)
        uic.loadUi("qtdesigner/AgroPlan/dialog.ui", self)
        # self.pushButton_3.clicked.connect(self.on_pushButton_clicked)
        self.pushButton_3: QPushButton
        self.pushButton_3.setChecked(True)
        # self.pushButton_3.setText("Checked")
        self.label: QLabel
        self.label.installEventFilter(self)
        self.setMouseTracking(True)

    @Slot(bool)
    def on_pushButton_3_clicked(self, checked: bool) -> None:
        text = "Checked" if checked else "Unchecked"
        self.pushButton_3.setText(text)
        self.setWindowTitle(text)
        logger.debug(text)

    def eventFilter(self, source, event):
        if event.type() == QEvent.Type.MouseButtonPress and source is self.label:
            check_mouse_button(self, event)
        return super(UIDialog, self).eventFilter(source, event)

        # def mouseMoveEvent(self, e):
        #     check_mouse_button(self, e)
        # def mousePressEvent(self, e):
        #     check_mouse_button(self, e)
        # def mouseReleaseEvent(self, e):
        #     check_mouse_button(self, e)
        # def mouseDoubleClickEvent(self, e):
        #     check_mouse_button(self, e)


def check_mouse_button(element, event: QMouseEvent) -> None:

    match event.button():
        case Qt.MouseButton.LeftButton:
            element.label.setText("mousePressEvent LEFT")
        case Qt.MouseButton.MiddleButton:
            element.label.setText("mousePressEvent MIDDLE")
        case Qt.MouseButton.RightButton:
            element.label.setText("mousePressEvent RIGHT")
        case Qt.MouseButton.NoButton:
            element.label.setText("mousePressEvent NONE")


class MyLineEdit(QLineEdit):
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
