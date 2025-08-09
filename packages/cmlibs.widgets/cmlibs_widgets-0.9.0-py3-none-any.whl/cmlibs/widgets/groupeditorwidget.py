"""
   Copyright 2023 University of Auckland

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
from enum import IntEnum
from PySide6 import QtCore, QtWidgets

from cmlibs.zinc.field import Field
from cmlibs.zinc.element import Element
from cmlibs.widgets.ui.ui_groupeditorwidget import Ui_GroupEditorWidget
from cmlibs.utils.zinc.group import group_add_group_elements, group_remove_group_elements, \
    group_add_not_group_elements, group_remove_not_group_elements, group_get_highest_dimension


NULL_PLACEHOLDER = "---"

OPERATION_MAP = {
    "Add": {"operation": group_add_group_elements, "NOT-operation": group_add_not_group_elements,
            "tooltip": "Add all nodes/elements in this group to the selected group"},
    "Remove": {"operation": group_remove_group_elements, "NOT-operation": group_remove_not_group_elements,
               "tooltip": "Remove all nodes/elements in this group from the selected group"},
}

DEFAULT_FACE_FIELDS = {
    NULL_PLACEHOLDER: lambda field_module: field_module.createFieldIsOnFace(Element.FACE_TYPE_ALL),
}

GENERAL_FACE_FIELDS = {
    "Exterior": lambda field_module: field_module.createFieldIsExterior()
}

XI_FIELDS = [
    {"xi1=0": lambda field_module: field_module.createFieldIsOnFace(Element.FACE_TYPE_XI1_0),
     "xi1=1": lambda field_module: field_module.createFieldIsOnFace(Element.FACE_TYPE_XI1_1)},
    {"xi2=0": lambda field_module: field_module.createFieldIsOnFace(Element.FACE_TYPE_XI2_0),
     "xi2=1": lambda field_module: field_module.createFieldIsOnFace(Element.FACE_TYPE_XI2_1)},
    {"xi3=0": lambda field_module: field_module.createFieldIsOnFace(Element.FACE_TYPE_XI3_0),
     "xi3=1": lambda field_module: field_module.createFieldIsOnFace(Element.FACE_TYPE_XI3_1)}
]


def region_get_highest_dimension(field_module):
    for dimension in range(3, 0, -1):
        mesh = field_module.findMeshByDimension(dimension)
        if mesh.getSize() > 0:
            return dimension
    node_set = field_module.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_NODES)
    if node_set.getSize() > 0:
        return 0
    return -1


class Column(IntEnum):
    GROUP = 0
    FACE_TYPE = 1
    OPERATION = 2
    COMPLEMENT = 3


class GroupEditorWidget(QtWidgets.QWidget):
    """
    This widget takes a list of Zinc groups as an input and provides a GUI allowing the user to redefine a specific group based on the
    nodes/elements contained in each of the other groups in the list. Calls to the GroupEditorWidget constructor must ensure that the
    group arguments are valid and non-empty.

    This widget emits a group_updated signal when the group operations are applied.

    :param current_group: The FieldGroup to add elements to.
    :param group_list: A list of FieldGroups to use for redefining the current group.
    """
    group_updated = QtCore.Signal()
    close_requested = QtCore.Signal()

    def __init__(self, parent=None, current_group=None, group_list=None):
        QtWidgets.QWidget.__init__(self, parent)
        self._ui = Ui_GroupEditorWidget()
        self._ui.setupUi(self)

        self._current_group = current_group
        self._group_map = {group.getName(): group for group in group_list}
        self._dimension_of_operation = self._define_dimension_of_operation()
        self._face_type_fields = self._define_face_type_fields()

        self._setup_widget()
        self._make_connections()

    def _define_dimension_of_operation(self):
        highest_dimension = group_get_highest_dimension(self._current_group)
        if highest_dimension == -1:
            field_module = self._current_group.getFieldmodule()
            highest_dimension = region_get_highest_dimension(field_module)
        return highest_dimension

    def _define_face_type_fields(self):
        field_module = self._current_group.getFieldmodule()
        highest_dimension = region_get_highest_dimension(field_module)
        if self._dimension_of_operation < highest_dimension:
            xi_fields = {k: v for d in XI_FIELDS[:highest_dimension + 1] for k, v in d.items()}
            return {**DEFAULT_FACE_FIELDS, **GENERAL_FACE_FIELDS, **xi_fields}
        else:
            return {**DEFAULT_FACE_FIELDS}

    def _setup_widget(self):
        current_group_name = self._current_group.getName()
        if current_group_name in self._group_map:
            del self._group_map[current_group_name]

        # Set the current group label text.
        self._ui.currentGroupLabel.setText(current_group_name)

        # Define the dimensions of operation.
        highest_dimension = region_get_highest_dimension(self._current_group.getFieldmodule())
        dimensions = ["0D (Nodes)", "1D (Lines)", "2D (Faces)", "3D (Elements)"][:highest_dimension + 1]
        self._ui.dimensionComboBox.addItems(dimensions)
        self._ui.dimensionComboBox.setCurrentIndex(self._dimension_of_operation)

        self._setup_table()
        self._setup_whats_this()

    def _setup_table(self):
        horizontal_header = self._ui.groupTableWidget.horizontalHeader()
        horizontal_header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.Stretch)
        self._create_row(0)

    def _create_row(self, i):
        self._ui.groupTableWidget.insertRow(i)

        group_combo_box = QtWidgets.QComboBox()
        group_combo_box.addItems([NULL_PLACEHOLDER] + list(self._group_map.keys()))
        group_combo_box.currentTextChanged.connect(self._group_selection_changed)

        face_type_combo_box = QtWidgets.QComboBox()
        face_type_combo_box.addItems(list(self._face_type_fields.keys()))

        operation_combo_box = QtWidgets.QComboBox()
        operation_combo_box.addItem(NULL_PLACEHOLDER)
        for j in range(len(OPERATION_MAP)):
            key, value = list(OPERATION_MAP.items())[j]
            operation_combo_box.addItem(key)
            operation_combo_box.setItemData(j + 1, value["tooltip"], QtCore.Qt.ItemDataRole.ToolTipRole)

        not_combo_box = QtWidgets.QComboBox()
        not_combo_box.addItems([NULL_PLACEHOLDER, "Not"])

        self._ui.groupTableWidget.setCellWidget(i, Column.GROUP, group_combo_box)
        self._ui.groupTableWidget.setCellWidget(i, Column.FACE_TYPE, face_type_combo_box)
        self._ui.groupTableWidget.setCellWidget(i, Column.OPERATION, operation_combo_box)
        self._ui.groupTableWidget.setCellWidget(i, Column.COMPLEMENT, not_combo_box)

    def _setup_whats_this(self):
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowType.WindowContextHelpButtonHint)
        self.setWhatsThis(
            f"""
            <html>
            The Group Editor Widget provides the ability to redefine the selected group (<i>{self._current_group.getName()}</i>) based on
            elements of other groups defined over the same model. For each line in the widget:
            
            <ul>
            <li>The <b>Group</b> combo-box defines the group of elements to be used for the operation.</li>
            <li>The <b>Operation</b> combo-box defines whether to <i>Add</i> or <i>Remove</i> elements to/from
            <i>{self._current_group.getName()}</i>.</li>
            <li>The <b>Complement</b> combo-box defines whether we should use all elements in the group or all elements <i>Not</i> in the
            group for the operation.</li>
            </ul>
            
            Group operations will be performed in the order that they are listed in the widget.
            </html>
            """
        )

    def _make_connections(self):
        self._ui.clearPushButton.clicked.connect(self._reset_table)
        self._ui.applyPushButton.clicked.connect(self._apply_group_operations)
        self._ui.closePushButton.clicked.connect(self.close_requested)
        self._ui.dimensionComboBox.currentIndexChanged.connect(self._update_dimension_of_operation)

    def get_current_group(self):
        return self._current_group

    def set_current_group(self, current_group):
        self._current_group = current_group
        self.reset()

    def get_group_list(self):
        return list(self._group_map.values())

    def set_group_list(self, group_list):
        self._group_map = {group.getName(): group for group in group_list}
        self.reset()

    def _update_dimension_of_operation(self, dimension):
        self._dimension_of_operation = dimension
        self._face_type_fields = self._define_face_type_fields()

        self._clear_table()
        self._setup_table()

    def _clear_table(self):
        for _ in range(self._ui.groupTableWidget.rowCount()):
            self._ui.groupTableWidget.removeRow(0)

    def _reset_table(self):
        self._clear_table()
        self._create_row(0)

    def _clear_widget(self):
        self._ui.currentGroupLabel.clear()
        self._ui.dimensionComboBox.clear()
        self._clear_table()

    def reset(self):
        self._clear_widget()
        self._setup_widget()

    def _group_selection_row(self, sender):
        row = 0
        while self._ui.groupTableWidget.cellWidget(row, 0) != sender:
            row += 1

        return row

    def _group_selection_changed(self, current_text):
        count = self._ui.groupTableWidget.rowCount()
        current_row = self._group_selection_row(self.sender())
        if current_text in self._group_map.keys():
            if current_row == count - 1:
                self._create_row(count)
        elif count > 1:
            self._ui.groupTableWidget.removeRow(current_row)

    def _apply_group_operations(self):
        field_module = self._current_group.getFieldmodule()
        for i in range(self._ui.groupTableWidget.rowCount()):
            text = self._ui.groupTableWidget.cellWidget(i, Column.OPERATION).currentText()
            if text in OPERATION_MAP.keys():
                group = self._group_map[self._ui.groupTableWidget.cellWidget(i, Column.GROUP).currentText()]
                face_type_name = self._ui.groupTableWidget.cellWidget(i, Column.FACE_TYPE).currentText()
                face_type = self._face_type_fields[face_type_name](field_module)

                if self._ui.groupTableWidget.cellWidget(i, Column.COMPLEMENT).currentText() == NULL_PLACEHOLDER:
                    operation = OPERATION_MAP[text]["operation"]
                else:
                    operation = OPERATION_MAP[text]["NOT-operation"]
                operation(self._current_group, group, highest_dimension=self._dimension_of_operation, conditional_field=face_type)

        self.group_updated.emit()
