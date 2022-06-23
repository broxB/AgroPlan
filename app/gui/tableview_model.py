from database.model import (
    BaseField,
    Crop,
    CropClass,
    Cultivation,
    Field,
    HumusType,
    RemainsType,
    SoilSample,
    SoilType,
)
from database.utils import create_session
from gui.utils import split_meta_name
from loguru import logger
from PyQt6.QtCore import QAbstractTableModel, Qt, QVariant
from PyQt6.QtWidgets import QCheckBox, QTableView


class TableModel(QAbstractTableModel):
    def __init__(self, data, header: list, parent=None):
        super().__init__(parent)
        self._data = data
        self._header = header

    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            return self._data[index.row()][index.column()]

    def rowCount(self, index):
        return len(self._data)

    def columnCount(self, index):
        return len(self._data[0])

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return self._header[section]
            elif orientation == Qt.Orientation.Vertical:
                return QVariant()
        return super().headerData(section, orientation, role)


class MyTableView(QTableView):
    def __init__(self, parent=None):
        super().__init__(parent)
        logger.debug("Init {} from {}", self.__class__.__name__, self.parent().__class__.__name__)

    def cultivation_data(self, field_name: str, year: int):
        session = create_session()
        prefix, suffix, name = split_meta_name(field_name)
        cultivation = (
            session.query(
                Cultivation.crop_class,
                Crop.name,
                Cultivation.crop_yield,
                Cultivation.remains,
                Cultivation.legume_rate,
            )
            .join(Field)
            .join(BaseField)
            .join(Crop)
            .filter(
                BaseField.prefix == prefix,
                BaseField.suffix == suffix,
                BaseField.name == name,
                Field.year == year,
            )
            .all()
        )
        crop = []
        if cultivation:
            for cult in cultivation:
                crop.append(
                    [
                        CropClass(cult.crop_class).value,
                        cult.name,
                        f"{cult.crop_yield:.0f}",
                        RemainsType(cult.remains).value if cult.remains is not None else None,
                        cult.legume_rate,
                    ]
                )
        else:
            crop = [["" for _ in range(5)]]
        header = ["Class", "Crop", "Yield", "Remains", "Legume share"]
        logger.debug(crop)
        self.model = TableModel(crop, header)
        self.setModel(self.model)

        # add checkbox to each row
        # for row, string in enumerate(alaaa, 0):
        #     chkBoxItem = QTableWidgetItem(string)
        #     chkBoxItem.setText(string)
        #     chkBoxItem.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
        #     chkBoxItem.setCheckState(QtCore.Qt.Unchecked)
        #     self.ui.tableWidget.setItem(row, 0, chkBoxItem)

    def soil_sample_data(self, field_name: str):
        session = create_session()
        prefix, suffix, name = split_meta_name(field_name)
        soil_samples = (
            session.query(SoilSample)
            .join(BaseField)
            .filter(
                BaseField.prefix == prefix,
                BaseField.suffix == suffix,
                BaseField.name == name,
            )
            .all()
        )
        samples = []
        if soil_samples:
            for soil_sample in sorted(soil_samples, key=lambda x: x.year, reverse=True):
                samples.append(
                    [
                        soil_sample.year,
                        SoilType(soil_sample.soil_type).value,
                        HumusType(soil_sample.humus).value,
                        f"{soil_sample.ph:.1f}" if soil_sample.ph is not None else None,
                        f"{soil_sample.p2o5:.2f}" if soil_sample.p2o5 is not None else None,
                        f"{soil_sample.k2o:.2f}" if soil_sample.k2o is not None else None,
                        f"{soil_sample.mg:.2f}" if soil_sample.mg is not None else None,
                    ]
                )
        else:
            samples = [["" for _ in range(7)]]
        header = ["Year", "Type", "Humus", "pH", "P2O5", "K2O", "Mg"]
        logger.debug(samples)
        self.model: TableModel = TableModel(samples, header)
        self.setModel(self.model)
