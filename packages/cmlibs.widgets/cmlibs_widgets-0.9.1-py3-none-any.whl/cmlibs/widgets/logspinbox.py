import math

from PySide6 import QtWidgets


class LogSpinBox(QtWidgets.QDoubleSpinBox):
    def __init__(self, parent=None):
        super().__init__(parent)

    def stepBy(self, steps):
        current = self.value()
        self.setValue(current * math.pow(10, steps))
