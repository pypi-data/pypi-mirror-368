
from PySide6 import QtCore, QtWidgets

from cmlibs.widgets.basesceneviewerwidget import BaseSceneviewerWidget
from cmlibs.widgets.handlers.scenemanipulation import SceneManipulation


class ViewWidget(QtWidgets.QWidget):
    """
    A widget that holds sceneviewers in a specific layout.
    """

    graphicsReady = QtCore.Signal()
    currentChanged = QtCore.Signal()

    def __init__(self, scenes, grid_description=None, parent=None):
        """
        Create a view widget with a list of scenes and associated grid description.

        :param scenes: A list of scenes.
        :param grid_description: A dictionary describing the grid layout of the widgets. (Not currently used.)
        :param parent: Parent widget
        """
        super(ViewWidget, self).__init__(parent)
        layout = QtWidgets.QGridLayout()
        self.setLayout(layout)

        self._sceneviewers = []
        self._ready_state = []
        self._initial_state = []
        self._active_sceneviewer = None
        self._active_sceneviewer_widget = None

        for index, scene in enumerate(scenes):
            s = BaseSceneviewerWidget(self)
            s.register_handler(SceneManipulation())
            s.graphics_initialized.connect(self._graphics_initialised)
            s.became_active.connect(self._active_view_changed)
            self._sceneviewers.append(s)
            self._ready_state.append(False)
            s.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
            row = scene.get("Row", 0)
            col = scene.get("Col", 0)
            self._initial_state.append(scene.get("Sceneviewer", {}))
            layout.addWidget(s, row, col)

    def _active_view_changed(self):
        self._active_sceneviewer = self.sender()
        layout = self.layout()
        rows = layout.rowCount()
        columns = layout.columnCount()
        for r in range(rows):
            for c in range(columns):
                sceneviewer_widget = layout.itemAtPosition(r, c).widget()
                is_active_widget = sceneviewer_widget == self._active_sceneviewer
                sceneviewer_widget.set_active_state(is_active_widget)
                if is_active_widget:
                    self._active_sceneviewer_widget = sceneviewer_widget

        self.currentChanged.emit()

    def _graphics_initialised(self):
        index = self._sceneviewers.index(self.sender())
        self._initial_state[index].applyParameters(self.sender().get_zinc_sceneviewer())
        if self._active_sceneviewer is None:
            self._active_view_changed()
        self._ready_state[index] = True
        if all(self._ready_state):
            self.graphicsReady.emit()

    def getSceneviewer(self, row, col):
        """
        Get the sceneviewer from the view widget layout at position defined by the row and column.

        :param row: The row index of the sceneviewer.
        :param col: The column index of the sceneviewer.
        :return: cmlibs.zinc.sceneviewer.Sceneviewer
        """
        layout = self.layout()
        sceneviewer_widget = layout.itemAtPosition(row, col).widget()
        return sceneviewer_widget.get_zinc_sceneviewer()

    def getActiveSceneviewer(self):
        """
        Get the currently active sceneviewer.  Returns None if there is no currently
        active sceneviewer.

        :return: cmlibs.zinc.sceneviewer.Sceneviewer
        """
        if self._active_sceneviewer is not None:
            return self._active_sceneviewer.get_zinc_sceneviewer()

        return None

    def getActiveSceneviewerWidget(self):
        """
        Get the currently active sceneviewer widget.

        :return: cmlibs.widgets.basesceneviewerwidget.
        """
        return self._active_sceneviewer_widget

    def setContext(self, context):
        """
        Set the context for all sceneviewers in the view widget.

        :param context: cmlibs.zinc.context.Context.
        """
        for sceneviewer in self._sceneviewers:
            sceneviewer.set_context(context)
