from PySide6 import QtCore


class FieldListModel(QtCore.QAbstractListModel):

    def __init__(self):
        super().__init__()
        self._fields = []

    def rowCount(self, parent=...):
        return len(self._fields)

    def data(self, index, role=...):
        if index.isValid():
            if role == QtCore.Qt.ItemDataRole.DisplayRole:
                return self._fields[index.row()].getName()
            elif role == QtCore.Qt.ItemDataRole.UserRole:
                return self._fields[index.row()]

    def populate(self, fields):
        self.beginResetModel()
        self._fields = fields
        self.endResetModel()
