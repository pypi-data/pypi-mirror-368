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
from PySide6 import QtCore, QtWidgets


class CheckBoxDelegate(QtWidgets.QStyledItemDelegate):

    def __init__(self, parent=None):
        super(CheckBoxDelegate, self).__init__(parent)

    def createEditor(self, parent, option, index):
        return None
        # return QtWidgets.QCheckBox(parent)

    def paint(self, painter, option, index):
        checked = bool(index.model().data(index, QtCore.Qt.ItemDataRole.DisplayRole))
        check_box_style_option = QtWidgets.QStyleOptionButton()

        editable = (index.flags() & QtCore.Qt.ItemFlag.ItemIsEditable) == QtCore.Qt.ItemFlag.ItemIsEditable
        if editable:
            check_box_style_option.state |= QtWidgets.QStyle.StateFlag.State_Enabled
        else:
            check_box_style_option.state |= QtWidgets.QStyle.StateFlag.State_ReadOnly

        if checked:
            check_box_style_option.state |= QtWidgets.QStyle.StateFlag.State_On
        else:
            check_box_style_option.state |= QtWidgets.QStyle.StateFlag.State_Off

        check_box_style_option.rect = option.rect

        QtWidgets.QApplication.style().drawControl(QtWidgets.QStyle.ControlElement.CE_CheckBox, check_box_style_option, painter)

    def editorEvent(self, event, model, option, index):
        '''
        Change the data in the model and the state of the checkbox
        if the user presses the left mousebutton or presses
        Key_Space or Key_Select and this cell is editable. Otherwise do nothing.
        '''
        editable = (index.flags() & QtCore.Qt.ItemFlag.ItemIsEditable) == QtCore.Qt.ItemFlag.ItemIsEditable
        if not editable:
            return False

        # Do not change the checkbox-state
        event_type = event.type()
        if event_type == QtCore.QEvent.MouseButtonRelease or event_type == QtCore.QEvent.MouseButtonDblClick:
            if event.button() != QtCore.Qt.MouseButton.LeftButton or not option.rect.contains(event.pos()):
                return False
            if event_type == QtCore.QEvent.MouseButtonDblClick:
                return True
        elif event_type == QtCore.QEvent.KeyPress:
            if event_type != QtCore.Qt.Key.Key_Space and event_type != QtCore.Qt.Key.Key_Select:
                return False
        else:
            return False

        # Change the checkbox-state
        self.setModelData(None, model, index)
        return True

    def setEditorData(self, editor, index):
        data = index.model().data(index, QtCore.Qt.ItemDataRole.DisplayRole)
        if data is not None:
            editor.setChecked(data)

    def setModelData(self, editor, model, index):
        value = index.model().data(index, QtCore.Qt.ItemDataRole.DisplayRole)
        model.setData(index, value, QtCore.Qt.ItemDataRole.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)
