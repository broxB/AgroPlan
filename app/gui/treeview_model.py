from loguru import logger
from PyQt6.QtGui import QColor, QFont, QStandardItem, QStandardItemModel
from PyQt6.QtWidgets import QTreeView
from utils.utils import get_field_cultivation


class StandardItem(QStandardItem):
    def __init__(self, text="", checkable=False, selectable=True):
        super().__init__()
        self.setEditable(False)
        self.setCheckable(checkable)
        self.setSelectable(selectable)
        self.setText(text)


class MyTreeView(QTreeView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHeaderHidden(True)
        logger.debug("Init {}", self.__class__.__name__)

    def insert_data(self, field: str):
        tree_model = QStandardItemModel()
        root_node = tree_model.invisibleRootItem()

        field_data = get_field_cultivation(field)
        for year in field_data:
            year_item = StandardItem(year, selectable=False)
            for crop in field_data[year]:
                crop_item = StandardItem(crop, checkable=False)
                year_item.appendRow(crop_item)
            root_node.appendRow(year_item)

        self.setModel(tree_model)
        self.expandAll()

    def setup_demo(self):
        treeModel = QStandardItemModel()
        rootNode = treeModel.invisibleRootItem()

        # America
        america = StandardItem("America")

        california = StandardItem("California")
        america.appendRow(california)

        oakland = StandardItem("Oakland")
        sanfrancisco = StandardItem("San Francisco")
        sanjose = StandardItem("San Jose")

        california.appendRow(oakland)
        california.appendRow(sanfrancisco)
        california.appendRow(sanjose)

        texas = StandardItem("Texas")
        america.appendRow(texas)

        austin = StandardItem("Austin")
        houston = StandardItem("Houston")
        dallas = StandardItem("dallas")

        texas.appendRow(austin)
        texas.appendRow(houston)
        texas.appendRow(dallas)

        # Canada
        canada = StandardItem("Canada")

        alberta = StandardItem("Alberta")
        bc = StandardItem("British Columbia")
        ontario = StandardItem("Ontario")
        canada.appendRows([alberta, bc, ontario])

        rootNode.appendRow(america)
        rootNode.appendRow(canada)

        self.setModel(treeModel)
        self.expandAll()
