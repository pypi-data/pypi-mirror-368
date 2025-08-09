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
from PySide6 import QtWidgets

from cmlibs.zinc.material import Material

class MaterialChooserWidget(QtWidgets.QComboBox):

    def __init__(self, parent=None):
        """
        Call the super class init functions
        """
        QtWidgets.QComboBox.__init__(self, parent)
        self._nullObjectName = None
        self._materialmodule = None
        self._materialmodulenotifier = None
        self._material = None

    def _materialmoduleCallback(self, materialmoduleevent):
        """
        Callback for change in materials; may need to rebuild material list
        """
        changeSummary = materialmoduleevent.getSummaryMaterialChangeFlags()
        if 0 != (changeSummary & (Material.CHANGE_FLAG_IDENTIFIER | Material.CHANGE_FLAG_ADD | Material.CHANGE_FLAG_REMOVE)):
            self._buildMaterialList()

    def _buildMaterialList(self):
        """
        Rebuilds the list of items in the ComboBox from the material module
        """
        self.blockSignals(True)
        self.clear()
        if self._materialmodule:
            if self._nullObjectName:
                self.addItem(self._nullObjectName)
            materialiter = self._materialmodule.createMaterialiterator()
            material = materialiter.next()
            while material.isValid():
                name = material.getName()
                self.addItem(name)
                material = materialiter.next()
        self.blockSignals(False)
        self._displayMaterial()

    def _displayMaterial(self):
        """
        Display the currently chosen material in the ComboBox
        """
        self.blockSignals(True)
        if self._material:
            materialName = self._material.getName()
            # following doesn't handle material name matching _nullObjectName
            index = self.findText(materialName)
        else:
            index = 0
        self.setCurrentIndex(index)
        self.blockSignals(False)

    def setNullObjectName(self, nullObjectName):
        """
        Enable a null object option with the supplied name e.g. '-' or '<select>'
        Default is None
        """
        self._nullObjectName = nullObjectName

    def setMaterialmodule(self, materialmodule):
        """
        Sets the region that this widget chooses materials from
        """
        self._materialmodule = materialmodule
        if materialmodule and materialmodule.isValid():
            self._materialmodule = materialmodule
            self._materialmodulenotifier = materialmodule.createMaterialmodulenotifier()
            self._materialmodulenotifier.setCallback(self._materialmoduleCallback)
        else:
            self._materialmodule = None
            self._materialmodulenotifier = None
        self._buildMaterialList()

    def getMaterial(self):
        """
        Must call this from currentIndexChanged() slot to get/update current material
        """
        materialName = self.currentText()
        if self._nullObjectName and (materialName == self._nullObjectName):
            self._material = None
        else:
            self._material = self._materialmodule.findMaterialByName(materialName)
        return self._material

    def setMaterial(self, material):
        """
        Set the currently selected material
        """
        if not material or not material.isValid():
            self._material = None
        else:
            self._material = material
        self._displayMaterial()
