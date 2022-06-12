from PyQt6 import uic
from PyQt6.QtCore import QEvent, QPoint, Qt
from PyQt6.QtCore import pyqtSlot as Slot
from PyQt6.QtGui import QAction, QContextMenuEvent, QCursor, QFocusEvent, QMouseEvent
from PyQt6.QtWidgets import (
    QComboBox,
    QCompleter,
    QDialog,
    QLabel,
    QLineEdit,
    QListView,
    QMainWindow,
    QMenu,
    QPushButton,
    QTextEdit,
)


class MyLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super(MyLineEdit, self).__init__(parent)

    def mousePressEvent(self, e):
        self.selectAll()

    def focusOutEvent(self, e):
        self.parent().setCurrentText(
            self.parent().itemText(self.parent().currentIndex())
        )
        QLineEdit.focusOutEvent(self, e)


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi("qtdesigner/mainwindow_2.ui", self)
        # self.pushButton.clicked.connect(self.on_pushButton_clicked)
        self.pushButton: QPushButton
        self.comboBox: QComboBox
        fields = [
            [
                "1-0 Am Hof 1 (3,32 ha)",
                "33-0 Hinter den Häusern (32,23 ha)",
                "72-0 Hänschen (0,89 ha)",
            ]
            * 10
        ]
        self.comboBox.addItems(*fields)
        # self.comboBox.addItems([f"{i}-0 Feld {i}" for i in range(15)])
        self.comboBox.setEditable(True)
        # self.combo_lineEdit = MyLineEdit(self.comboBox)
        self.combo_lineEdit = QLineEdit()
        self.comboBox.setLineEdit(self.combo_lineEdit)
        self.comboBox.completer().setFilterMode(Qt.MatchFlag.MatchContains)
        self.comboBox.completer().setCompletionMode(
            QCompleter.CompletionMode.PopupCompletion
        )
        self.comboBox.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.comboBox.currentIndexChanged.connect(self.change_comboBox_item)
        self.combo_lineEdit.setClearButtonEnabled(True)
        self.combo_lineEdit.mousePressEvent = self.click_comboBox_editText
        self.combo_lineEdit.focusOutEvent = self.leave_comboBox_editText
        self.listView: QListView
        self.listView.contextMenuEvent = self.listView_contextMenuEvent

    def click_comboBox_editText(self, e: QMouseEvent) -> None:
        QLineEdit.mousePressEvent(self.combo_lineEdit, e)
        if e.button() == Qt.MouseButton.LeftButton:
            if self.combo_lineEdit.selectedText() == self.combo_lineEdit.text():
                # self.combo_lineEdit.deselect()
                ...
            else:
                # self.combo_lineEdit.selectAll()
                print("Edited:", self.combo_lineEdit.text())

    def leave_comboBox_editText(self, e) -> None:
        if e.reason() == Qt.FocusReason.MouseFocusReason:
            QLineEdit.focusOutEvent(self.combo_lineEdit, e)
            self.comboBox.setCurrentText(
                self.comboBox.itemText(self.comboBox.currentIndex())
            )

    @Slot(name="on_comboBox_currentIndexChanged")
    def change_comboBox_item(self) -> None:
        print(
            "Selected:",
            self.comboBox.currentText(),
            "Index:",
            self.comboBox.currentIndex(),
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

    def listView_contextMenuEvent(self, event: QContextMenuEvent) -> None:
        context = QMenu(self)
        context.addAction(QAction("test 1", self))
        context.exec(event.globalPos())


class UIDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi("qtdesigner/dialog.ui", self)
        # self.pushButton_3.clicked.connect(self.on_pushButton_clicked)
        self.pushButton_3: QPushButton
        self.pushButton_3.setChecked(True)
        self.pushButton_3.setText("Checked")
        self.label: QLabel
        self.label.installEventFilter(self)
        self.setMouseTracking(True)

    @Slot(bool)
    def on_pushButton_3_clicked(self, checked: bool) -> None:
        text = "Checked" if checked else "Unchecked"
        self.pushButton_3.setText(text)
        self.setWindowTitle(text)
        print(text)

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
