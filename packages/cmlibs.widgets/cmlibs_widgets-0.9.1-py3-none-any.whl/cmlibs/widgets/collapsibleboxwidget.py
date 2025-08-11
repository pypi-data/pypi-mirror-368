from PySide6 import QtCore, QtWidgets


FIXED_VPOL = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
EXPAND_VPOL = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)


class CollapsibleBox(QtWidgets.QWidget):
    def __init__(self, title: str = "", parent=None, checked: bool = False):
        super().__init__(parent)

        self.setSizePolicy(EXPAND_VPOL if checked else FIXED_VPOL)

        self._toggle_button = QtWidgets.QToolButton(text=title, checkable=True, checked=checked)
        self._toggle_button.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self._toggle_button.setArrowType(QtCore.Qt.ArrowType.DownArrow if checked else QtCore.Qt.ArrowType.RightArrow)

        self._toggle_button.setSizePolicy(FIXED_VPOL)

        self._content_area = QtWidgets.QScrollArea(maximumHeight=16777215 if checked else 0, minimumHeight=0)
        self._content_area.setSizePolicy(EXPAND_VPOL if checked else FIXED_VPOL)
        self._content_area.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)

        lay = QtWidgets.QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self._toggle_button)
        lay.addWidget(self._content_area)

        self._animation = QtCore.QPropertyAnimation(self._content_area, b"maximumHeight")
        self._animation.setDuration(200)
        self._animation.setEasingCurve(QtCore.QEasingCurve.Type.InOutQuad)

        self._inner = QtWidgets.QWidget()
        self._inner.setLayout(QtWidgets.QVBoxLayout())
        self._content_area.setWidget(self._inner)
        self._content_area.setWidgetResizable(True)

        self._make_connections()

    def set_state(self, state: bool):
        self._toggle_button.setChecked(state)
        self._start_animation(state)

    def _make_connections(self):
        self._toggle_button.toggled.connect(self._start_animation)
        self._animation.finished.connect(self._on_animation_finished)

    def _start_animation(self, checked: bool):
        self._toggle_button.setArrowType(QtCore.Qt.ArrowType.DownArrow if checked else QtCore.Qt.ArrowType.RightArrow)

        content_height = self._inner.sizeHint().height()
        start = 0 if checked else content_height
        end = content_height if checked else 0

        self._content_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self._animation.stop()
        self._animation.setStartValue(start)
        self._animation.setEndValue(end)
        self._animation.start()

        self.setSizePolicy(FIXED_VPOL)
        self._content_area.setSizePolicy(FIXED_VPOL)

        self.updateGeometry()

    @QtCore.Slot()
    def _on_animation_finished(self):
        checked = self._toggle_button.isChecked()
        self.setSizePolicy(EXPAND_VPOL if checked else FIXED_VPOL)
        self._content_area.setSizePolicy(EXPAND_VPOL if checked else FIXED_VPOL)
        self._content_area.setMaximumHeight(16777215 if checked else 0)
        self._content_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)

    def add_widget(self, widget: QtWidgets.QWidget):
        self._inner.layout().addWidget(widget)
