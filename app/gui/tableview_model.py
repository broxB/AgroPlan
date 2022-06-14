from loguru import logger
from PyQt6.QtCore import QAbstractTableModel, Qt
from PyQt6.QtGui import QColor, QFont, QStandardItem, QStandardItemModel
from PyQt6.QtWidgets import QAbstractItemView, QTableView


class ItemModel(QStandardItem):
    def __init__(self, parent=None):
        super().__init__(parent)
        logger.debug("Init {}", self.__class__.__name__)


class TableModel(QAbstractTableModel):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self._data = data
        logger.debug("Init {}", self.__class__.__name__)

    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            # See below for the nested-list data structure.
            # .row() indexes into the outer list,
            # .column() indexes into the sub-list
            return self._data[index.row()][index.column()]

    def rowCount(self, index):
        # The length of the outer list.
        return len(self._data)

    def columnCount(self, index):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        return len(self._data[0])


class MyTableView(QTableView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_demo()
        logger.debug("Init {}", self.__class__.__name__)

    def insert_data(self, field_name: str):
        # table_model = QStandardItemModel()
        # root_node
        # table_data = get_data(field_name)
        # for
        # self.model = TableModel(table_data)
        # self.setModel(self.model)
        pass
        # add checkbox to each row
        # for row, string in enumerate(alaaa, 0):
        #     chkBoxItem = QTableWidgetItem(string)
        #     chkBoxItem.setText(string)
        #     chkBoxItem.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
        #     chkBoxItem.setCheckState(QtCore.Qt.Unchecked)
        #     self.ui.tableWidget.setItem(row, 0, chkBoxItem)

    def setup_demo(self):
        table_data = [
            [4, 9, 2],
            [1, 0, 0],
            [3, 5, 0],
            [3, 3, 2],
            [7, 8, 9],
        ]
        self.model = TableModel(table_data)
        self.setModel(self.model)
