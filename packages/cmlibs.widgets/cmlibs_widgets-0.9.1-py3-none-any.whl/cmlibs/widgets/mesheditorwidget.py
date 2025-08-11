"""
   Copyright 2015 University of Auckland

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""
from PySide6 import QtWidgets, QtCore

from cmlibs.widgets.handlers.nodeeditor import NodeEditor
from cmlibs.widgets.ui.ui_mesheditorwidget import Ui_MeshEditorWidget

"""
Zinc Scene Editor Widget

Allows a Zinc Scene object to be edited in Qt / Python.

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""


class MeshEditorWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        """
        Call the super class init functions
        """
        QtWidgets.QWidget.__init__(self, parent)
        self._scene = None
        # Using composition to include the visual element of the GUI.
        self._ui = Ui_MeshEditorWidget()
        self._ui.setupUi(self)
        self._sceneviewer_widget = None
        self._current_handler = None
        self._edit_button_group = QtWidgets.QButtonGroup()
        self._edit_button_group.addButton(self._ui.toolButtonNone, 1)
        self._edit_button_group.addButton(self._ui.toolButtonNodes, 2)

        self._make_connections()
        self._update_ui()

    def _make_connections(self):
        self._edit_button_group.buttonClicked.connect(self._edit_button_clicked)

    def _update_ui(self):
        self._ui.toolButtonNone.setEnabled(self._sceneviewer_widget is not None)
        self._ui.toolButtonNodes.setEnabled(self._sceneviewer_widget is not None)

    def _update_handler(self):
        if self._sceneviewer_widget is not None:
            self._sceneviewer_widget.register_handler(self._current_handler)

    def _edit_button_clicked(self, button):
        self._sceneviewer_widget.unregister_handler(self._current_handler)
        if button.objectName() == "toolButtonNodes":
            self._current_handler = NodeEditor(QtCore.Qt.Key.Key_E)
        else:
            self._current_handler = None
        self._update_handler()

    def setSceneviewerWidget(self, sceneviewer_widget):
        if self._sceneviewer_widget is not None:
            self._sceneviewer_widget.unregister_handler(self._current_handler)
        self._sceneviewer_widget = sceneviewer_widget
        self._update_handler()
        self._update_ui()
