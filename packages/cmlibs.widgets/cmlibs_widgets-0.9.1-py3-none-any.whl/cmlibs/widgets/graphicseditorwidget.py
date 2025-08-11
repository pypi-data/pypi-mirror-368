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

from numbers import Number

from cmlibs.zinc.element import Element
from cmlibs.zinc.glyph import Glyph
from cmlibs.zinc.graphics import Graphics, GraphicsStreamlines, Graphicslineattributes
from cmlibs.zinc.scenecoordinatesystem import SCENECOORDINATESYSTEM_LOCAL, ScenecoordinatesystemEnumFromString, ScenecoordinatesystemEnumToString
from cmlibs.zinc.spectrum import Spectrum
from cmlibs.zinc.status import OK as ZINC_OK

from cmlibs.argon.argonlogger import ArgonLogger
from cmlibs.argon.settings.mainsettings import FLOAT_STRING_FORMAT

from cmlibs.widgets.fieldconditions import *
from cmlibs.widgets.ui.ui_graphicseditorwidget import Ui_GraphicsEditorWidget

DOMAIN_TYPE_ENUM = [Field.DOMAIN_TYPE_POINT, Field.DOMAIN_TYPE_NODES, Field.DOMAIN_TYPE_DATAPOINTS,
                    Field.DOMAIN_TYPE_MESH1D, Field.DOMAIN_TYPE_MESH2D, Field.DOMAIN_TYPE_MESH3D, Field.DOMAIN_TYPE_MESH_HIGHEST_DIMENSION]
POINT_SAMPLING_DOMAIN_TYPE_ENUM = [Field.DOMAIN_TYPE_MESH1D, Field.DOMAIN_TYPE_MESH2D,
                                   Field.DOMAIN_TYPE_MESH3D, Field.DOMAIN_TYPE_MESH_HIGHEST_DIMENSION]


def faceTypeEnumFromString(enumString):
    enumString = enumString.replace('_=_', '_')
    return Element.FaceTypeEnumFromString(enumString)


def faceTypeEnumToString(faceTypeEnum):
    enumString = Element.FaceTypeEnumToString(faceTypeEnum)
    if not enumString:
        return None
    enumString = enumString.replace('_', ' = ')
    return enumString


class GraphicsEditorWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        """
        Call the super class init functions
        """
        QtWidgets.QWidget.__init__(self, parent)
        self._graphics = None
        self._isRangeIsovalues = False
        # Using composition to include the visual element of the GUI.
        self._ui = Ui_GraphicsEditorWidget()
        self._ui.setupUi(self)
        # base graphics attributes
        self._ui.face_enumeration_chooser.setEnumsList(
            faceTypeEnumToString, faceTypeEnumFromString)
        self._ui.scenecoordinatesystem_chooser.setEnumsList(
            ScenecoordinatesystemEnumToString, ScenecoordinatesystemEnumFromString)
        self._ui.boundarymode_chooser.setEnumsList(
            Graphics.BoundaryModeEnumToString, Graphics.BoundaryModeEnumFromString)
        self._ui.streamlines_track_direction_chooser.setEnumsList(
            GraphicsStreamlines.TrackDirectionEnumToString, GraphicsStreamlines.TrackDirectionEnumFromString)
        self._ui.streamlines_colour_data_type_chooser.setEnumsList(
            GraphicsStreamlines.ColourDataTypeEnumToString, GraphicsStreamlines.ColourDataTypeEnumFromString)
        self._ui.line_shape_chooser.setEnumsList(
            Graphicslineattributes.ShapeTypeEnumToString, Graphicslineattributes.ShapeTypeEnumFromString)
        self._ui.domain_chooser.setEnumsList(
            Field.DomainTypeEnumToString, Field.DomainTypeEnumFromString, DOMAIN_TYPE_ENUM)
        self._ui.select_mode_enum_chooser.setEnumsList(
            Graphics.SelectModeEnumToString, Graphics.SelectModeEnumFromString)

        self._ui.subgroup_field_chooser.setNullObjectName('-')
        self._ui.subgroup_field_chooser.setConditional(FieldIsScalar)
        self._ui.coordinate_field_chooser.setNullObjectName('-')
        self._ui.coordinate_field_chooser.setConditional(
            FieldIsCoordinateCapable)
        self._ui.data_field_chooser.setNullObjectName('-')
        self._ui.data_field_chooser.setConditional(FieldIsRealValued)
        self._ui.spectrum_chooser.setNullObjectName('-')
        self._ui.tessellation_field_chooser.setNullObjectName('-')
        self._ui.texture_coordinates_chooser.setNullObjectName('-')
        # contours
        self._ui.isoscalar_field_chooser.setNullObjectName('- choose -')
        self._ui.isoscalar_field_chooser.setConditional(FieldIsScalar)
        self._ui.range_number_spinBox.valueChanged.connect(
            self.numberOfIsovalueRangeChanged)
        # streamlines
        self._ui.stream_vector_field_chooser.setNullObjectName('- choose -')
        self._ui.stream_vector_field_chooser.setConditional(
            FieldIsStreamVectorCapable)
        # line attributes
        self._ui.line_orientation_scale_field_chooser.setNullObjectName('-')
        self._ui.line_orientation_scale_field_chooser.setConditional(
            FieldIsScalar)
        # point attributes
        self._ui.glyph_chooser.setNullObjectName('-')
        self._ui.point_orientation_scale_field_chooser.setNullObjectName('-')
        self._ui.point_orientation_scale_field_chooser.setConditional(
            FieldIsOrientationScaleCapable)
        self._ui.label_field_chooser.setNullObjectName('-')
        self._ui.glyph_repeat_mode_chooser.setEnumsList(
            Glyph.RepeatModeEnumToString, Glyph.RepeatModeEnumFromString)
        self._ui.glyph_signed_scale_field_chooser.setNullObjectName('-')
        self._ui.glyph_signed_scale_field_chooser.setConditional(FieldIsScalar)
        self._ui.glyph_font_comboBox.currentIndexChanged.connect(
            self._fontChanged)
        # mesh point sampling
        self._ui.sampling_mode_chooser.setEnumsList(
            Element.PointSamplingModeEnumToString, Element.PointSamplingModeEnumFromString)
        self._ui.density_field_chooser.setNullObjectName('-')

    def _updateWidgets(self):
        # base graphics attributes
        subgroupField = None
        coordinateField = None
        material = None
        selectedMaterial = None
        tessellationField = None
        textureCoordinatesField = None
        dataField = None
        spectrum = None
        tessellation = None
        isWireframe = False
        pointattributes = None
        lineattributes = None
        samplingattributes = None
        contours = None
        streamlines = None
        if self._graphics:
            subgroupField = self._graphics.getSubgroupField()
            coordinateField = self._graphics.getCoordinateField()
            material = self._graphics.getMaterial()
            selectedMaterial = self._graphics.getSelectedMaterial()
            dataField = self._graphics.getDataField()
            spectrum = self._graphics.getSpectrum()
            tessellationField = self._graphics.getTessellationField()
            tessellation = self._graphics.getTessellation()
            textureCoordinatesField = self._graphics.getTextureCoordinateField()
            isWireframe = self._graphics.getRenderPolygonMode() == Graphics.RENDER_POLYGON_MODE_WIREFRAME
            contours = self._graphics.castContours()
            streamlines = self._graphics.castStreamlines()
            pointattributes = self._graphics.getGraphicspointattributes()
            lineattributes = self._graphics.getGraphicslineattributes()
            samplingattributes = self._graphics.getGraphicssamplingattributes()
            self._ui.general_groupbox.show()
        else:
            self._ui.general_groupbox.hide()
        self._ui.subgroup_field_chooser.setField(subgroupField)
        self._ui.coordinate_field_chooser.setField(coordinateField)
        self._scenecoordinatesystemDisplay()
        self._ui.material_chooser.setMaterial(material)
        self._ui.selected_material_chooser.setMaterial(selectedMaterial)
        self._ui.data_field_chooser.setField(dataField)
        self._ui.spectrum_chooser.setSpectrum(spectrum)
        self._ui.tessellation_field_chooser.setField(tessellationField)
        self._ui.tessellation_chooser.setTessellation(tessellation)
        self._ui.texture_coordinates_chooser.setField(textureCoordinatesField)
        self._renderLineWidthDisplay()
        self._renderPointSizeDisplay()
        self._boundarymodeDisplay()
        self._faceDisplay()
        self._domainTypeDisplay()
        self._selectModeDisplay()
        self._ui.wireframe_checkbox.setCheckState(
            QtCore.Qt.CheckState.Checked if isWireframe else QtCore.Qt.CheckState.Unchecked)
        # contours
        isoscalarField = None
        if contours and contours.isValid():
            isoscalarField = contours.getIsoscalarField()
            self._isRangeIsovalues = contours.getRangeNumberOfIsovalues()
            self._ui.range_number_spinBox.setEnabled(self._isRangeIsovalues)
            self._ui.contours_groupbox.show()
        else:
            self._ui.contours_groupbox.hide()
        self._ui.isoscalar_field_chooser.setField(isoscalarField)
        self._ui.range_isovalues_checkBox.setCheckState(
            QtCore.Qt.CheckState.Checked if self._isRangeIsovalues else QtCore.Qt.CheckState.Unchecked)
        self._isovaluesDisplay()
        # streamlines
        streamVectorField = None
        if streamlines and streamlines.isValid():
            streamVectorField = streamlines.getStreamVectorField()
            self._ui.streamlines_groupbox.show()
        else:
            self._ui.streamlines_groupbox.hide()
        self._ui.stream_vector_field_chooser.setField(streamVectorField)
        self._streamlinesTrackLengthDisplay()
        self._streamlinesTrackDirectionDisplay()
        self._streamlinesColourDataTypeDisplay()
        # line attributes
        lineOrientationScaleField = None
        if lineattributes and lineattributes.isValid():
            lineOrientationScaleField = lineattributes.getOrientationScaleField()
            self._ui.lines_groupbox.show()
        else:
            self._ui.lines_groupbox.hide()
        self._lineShapeDisplay()
        self._lineBaseSizeDisplay()
        self._ui.line_orientation_scale_field_chooser.setField(
            lineOrientationScaleField)
        self._lineScaleFactorsDisplay()
        isStreamline = (streamlines is not None) and streamlines.isValid()
        if not isStreamline:
            isStreamline = False
        model = self._ui.line_shape_chooser.model()
        model.item(1, 0).setEnabled(isStreamline)
        model.item(3, 0).setEnabled(isStreamline)
        self._ui.line_orientation_scale_field_label.setEnabled(
            not isStreamline)
        self._ui.line_orientation_scale_field_chooser.setEnabled(
            not isStreamline)
        self._ui.line_scale_factors_label.setEnabled(not isStreamline)
        self._ui.line_scale_factors_lineedit.setEnabled(not isStreamline)
        # point attributes
        glyph = None
        pointOrientationScaleField = None
        labelField = None
        glyphRepeatMode = None
        glyphSignedScaleField = None
        fontname = None
        if pointattributes and pointattributes.isValid():
            glyph = pointattributes.getGlyph()
            pointOrientationScaleField = pointattributes.getOrientationScaleField()
            labelField = pointattributes.getLabelField()
            glyphRepeatMode = pointattributes.getGlyphRepeatMode()
            glyphSignedScaleField = pointattributes.getSignedScaleField()
            fontname = pointattributes.getFont().getName()
            self._buildFontComboBox()
            self._ui.glyph_font_comboBox.setCurrentIndex(
                self._ui.glyph_font_comboBox.findText(fontname))
            self._ui.points_groupbox.show()
        else:
            self._ui.points_groupbox.hide()
        self._ui.glyph_chooser.setGlyph(glyph)
        self._pointBaseSizeDisplay()
        self._ui.point_orientation_scale_field_chooser.setField(
            pointOrientationScaleField)
        self._pointScaleFactorsDisplay()
        self._ui.label_field_chooser.setField(labelField)
        self._ui.glyph_repeat_mode_chooser.setEnum(glyphRepeatMode)
        self._glyphOffsetDisplay()
        self._ui.glyph_signed_scale_field_chooser.setField(
            glyphSignedScaleField)
        self._labelTextDisplay()
        self._labelTextOffsetDisplay()
        # sampling attributes
        if samplingattributes and samplingattributes.isValid() and self._graphics.getFieldDomainType() in POINT_SAMPLING_DOMAIN_TYPE_ENUM:
            self._ui.sampling_groupbox.show()
        else:
            self._ui.sampling_groupbox.hide()
        self._samplingModeDisplay()
        self._sampleLocationDisplay()
        self._densityFieldDisplay()

    def setScene(self, scene):
        """
        Set when scene changes to initialised widgets dependent on scene

        :param scene: zinc.scene
        """
        self._ui.material_chooser.setMaterialmodule(scene.getMaterialmodule())
        self._ui.selected_material_chooser.setMaterialmodule(scene.getMaterialmodule())
        self._ui.glyph_chooser.setGlyphmodule(scene.getGlyphmodule())
        self._ui.spectrum_chooser.setSpectrummodule(scene.getSpectrummodule())
        self._ui.tessellation_chooser.setTessellationmodule(scene.getTessellationmodule())

        region = scene.getRegion()
        self._ui.subgroup_field_chooser.setRegion(region)
        self._ui.coordinate_field_chooser.setRegion(region)
        self._ui.data_field_chooser.setRegion(region)
        self._ui.tessellation_field_chooser.setRegion(region)
        self._ui.texture_coordinates_chooser.setRegion(region)
        self._ui.isoscalar_field_chooser.setRegion(region)
        self._ui.stream_vector_field_chooser.setRegion(region)
        self._ui.point_orientation_scale_field_chooser.setRegion(region)
        self._ui.label_field_chooser.setRegion(region)
        self._ui.glyph_signed_scale_field_chooser.setRegion(region)
        self._ui.line_orientation_scale_field_chooser.setRegion(region)
        self._ui.density_field_chooser.setRegion(region)

    def getGraphics(self):
        """
        Get the graphics currently in the editor
        """
        return self._graphics

    def setGraphics(self, graphics):
        """
        Set the graphics to be edited

        :param graphics: zinc.graphics.
        """
        if graphics and graphics.isValid():
            self._graphics = graphics
        else:
            self._graphics = None
        self._updateWidgets()

    def _displayReal(self, widget, value):
        """
        Display real value in a widget
        """
        newText = FLOAT_STRING_FORMAT.format(value)
        widget.setText(newText)

    def _displayScale(self, widget, values, numberFormat=FLOAT_STRING_FORMAT):
        """
        Display vector values in a widget, separated by '*'
        """
        newText = "*".join(numberFormat.format(value) for value in values)
        widget.setText(newText)

    def _parseScale(self, widget):
        """
        Return real vector from comma separated text in line edit widget
        """
        text = widget.text()
        values = [float(value) for value in text.split('*')]
        return values

    def _parseScaleInteger(self, widget):
        """
        Return integer vector from comma separated text in line edit widget
        """
        text = widget.text()
        values = [int(value) for value in text.split('*')]
        return values

    def _displayVector(self, widget, values, numberFormat=FLOAT_STRING_FORMAT):
        """
        Display real vector values in a widget. Also handle scalar
        """
        if isinstance(values, Number):
            newText = FLOAT_STRING_FORMAT.format(values)
        else:
            newText = ", ".join(numberFormat.format(value) for value in values)
        widget.setText(newText)

    def _parseVector(self, widget):
        """
        Return real vector from comma separated text in line edit widget
        """
        text = widget.text()
        values = [float(value) for value in text.split(',')]
        return values

    def subgroupFieldChanged(self, index):
        """
        An item was selected at index in subgroup field chooser widget

        :param index: index of new item.
        """
        if self._graphics:
            subgroupField = self._ui.subgroup_field_chooser.getField()
            if subgroupField:
                self._graphics.setSubgroupField(subgroupField)
            else:
                self._graphics.setSubgroupField(Field())
            if self._refreshGraphicListCallback:
                self._refreshGraphicListCallback()

    def coordinateFieldChanged(self, index):
        """
        An item was selected at index in coordinate field chooser widget

        :param index: index of new item.
        """
        if self._graphics:
            coordinateField = self._ui.coordinate_field_chooser.getField()
            if coordinateField:
                self._graphics.setCoordinateField(coordinateField)
            else:
                self._graphics.setCoordinateField(Field())

    def _scenecoordinatesystemDisplay(self):
        """
        Show the current state of the scenecoordinatesystem combo box
        """
        scenecoordinatesystem = SCENECOORDINATESYSTEM_LOCAL
        if self._graphics:
            scenecoordinatesystem = self._graphics.getScenecoordinatesystem()
        self._ui.scenecoordinatesystem_chooser.setEnum(scenecoordinatesystem)

    def scenecoordinatesystemChanged(self, index):
        if self._graphics:
            scenecoordinatesystem = self._ui.scenecoordinatesystem_chooser.getEnum()
            self._graphics.setScenecoordinatesystem(scenecoordinatesystem)

    def dataFieldChanged(self, index):
        """
        An item was selected at index in data field chooser widget

        :param index: index of new item.
        """
        if self._graphics:
            dataField = self._ui.data_field_chooser.getField()
            if dataField:
                scene = self._graphics.getScene()
                scene.beginChange()
                spectrum = self._graphics.getSpectrum()
                if not spectrum.isValid():
                    spectrummodule = scene.getSpectrummodule()
                    spectrum = spectrummodule.getDefaultSpectrum()
                    self._graphics.setSpectrum(spectrum)
                    self._ui.spectrum_chooser.setSpectrum(spectrum)
                self._graphics.setDataField(dataField)
                scene.endChange()
            else:
                self._graphics.setDataField(Field())

    def spectrumChanged(self, index):
        if self._graphics:
            spectrum = self._ui.spectrum_chooser.getSpectrum()
            if spectrum:
                self._graphics.setSpectrum(spectrum)
            else:
                self._graphics.setSpectrum(Spectrum())

    def tessellationChanged(self, index):
        """
        An item was selected at index in tessellation chooser widget

        :param index: index of new item.
        """
        if self._graphics:
            tessellation = self._ui.tessellation_chooser.getTessellation()
            self._graphics.setTessellation(tessellation)

    def tessellationFieldChanged(self, index):
        """
        An item was selected at index in tessellation field chooser widget

        :param index: index of new item.
        """
        if self._graphics:
            tessellationField = self._ui.tessellation_field_chooser.getField()
            if tessellationField:
                self._graphics.setTessellationField(tessellationField)
            else:
                self._graphics.setTessellationField(Field())

    def textureCoordinateFieldChanged(self, index):
        """
        An item was selected at index in texture coordinate field chooser widget

        :param index: index of new item.
        """
        if self._graphics:
            textureCoordinateField = self._ui.texture_coordinates_chooser.getField()
            if textureCoordinateField:
                self._graphics.setTextureCoordinateField(textureCoordinateField)
            else:
                self._graphics.setTextureCoordinateField(Field())

    def _renderLineWidthDisplay(self):
        """
        Display the current render line width
        """
        if self._graphics:
            renderLineWidth = self._graphics.getRenderLineWidth()
            self._displayReal(self._ui.line_width_lineEdit, renderLineWidth)
            return
        self._ui.line_width_lineEdit.setText('')

    def renderLineWidthEntered(self):
        """
        Set render line width from text in widget
        """
        renderLineWidth = self._ui.line_width_lineEdit.text()
        try:
            renderLineWidth = float(renderLineWidth)
            if self._graphics.setRenderLineWidth(renderLineWidth) != ZINC_OK:
                raise
        except:
            print("Invalid render line width", renderLineWidth)
        self._renderLineWidthDisplay()

    def _renderPointSizeDisplay(self):
        """
        Display the current render point size
        """
        if self._graphics:
            renderPointSize = self._graphics.getRenderPointSize()
            self._displayReal(self._ui.point_size_lineEdit, renderPointSize)
            return
        self._ui.point_size_lineEdit.setText('')

    def renderPointSizeEntered(self):
        """
        Set render point size from text in widget
        """
        renderPointSize = self._ui.point_size_lineEdit.text()
        try:
            renderPointSize = float(renderPointSize)
            if self._graphics.setRenderPointSize(renderPointSize) != ZINC_OK:
                raise
        except:
            print("Invalid render point size", renderPointSize)
        self._renderPointSizeDisplay()

    def _boundarymodeDisplay(self):
        """
        Show the current state of the boundarymode enumeration chooser
        """
        boundarymode = Graphics.BOUNDARY_MODE_INVALID
        if self._graphics:
            boundarymode = self._graphics.getBoundaryMode()
        self._ui.boundarymode_chooser.setEnum(boundarymode)

    def boundarymodeChanged(self, index):
        """
        Change the current state of the boundarymode enumeration chooser

        :param index: The index of boundarymode enumeration after change.
        """
        if self._graphics:
            boundarymode = self._ui.boundarymode_chooser.getEnum()
            self._graphics.setBoundaryMode(boundarymode)

    def _faceDisplay(self):
        """
        Show the current state of the face combo box
        """
        faceType = Element.FACE_TYPE_ALL
        if self._graphics:
            faceType = self._graphics.getElementFaceType()
        self._ui.face_enumeration_chooser.setEnum(faceType)

    def faceChanged(self, index):
        """
        Element face combo box changed

        :param index: index of new item.
        """
        if self._graphics:
            faceType = self._ui.face_enumeration_chooser.getEnum()
            self._graphics.setElementFaceType(faceType)

    def _domainTypeDisplay(self):
        """
        Show the current state of the domain combo box
        """
        domainType = Field.DOMAIN_TYPE_INVALID
        if self._graphics:
            domainType = self._graphics.getFieldDomainType()
        self._ui.domain_chooser.setEnum(domainType)

    def domainChanged(self, index):
        """
        Element domain combo box changed

        :param index: index of new item.
        """
        if self._graphics:
            domainType = self._ui.domain_chooser.getEnum()
            self._graphics.setFieldDomainType(domainType)
            self._domainTypeDisplay()
            if self._refreshGraphicListCallback:
                self._refreshGraphicListCallback()

    def setRefreshGraphicListCallback(self, callback):
        self._refreshGraphicListCallback = callback

    def wireframeClicked(self, isChecked):
        """
        The wireframe surface render radiobutton was clicked

        :param isChecked: boolean
        """
        if self._graphics:
            self._graphics.setRenderPolygonMode(
                Graphics.RENDER_POLYGON_MODE_WIREFRAME if isChecked else Graphics.RENDER_POLYGON_MODE_SHADED)

    def glyphChanged(self, index):
        """
        An item was selected at index in glyph chooser widget

        :param index: index of new item.
        """
        if self._graphics:
            pointattributes = self._graphics.getGraphicspointattributes()
            if (pointattributes.isValid()):
                glyph = self._ui.glyph_chooser.getGlyph()
                if glyph:
                    pointattributes.setGlyph(glyph)
                else:
                    pointattributes.setGlyph(Glyph())

    def materialChanged(self, index):
        """
        An item was selected at index in material chooser widget

        :param index: index of new item.
        """
        if self._graphics:
            material = self._ui.material_chooser.getMaterial()
            self._graphics.setMaterial(material)

    def selectedMaterialChanged(self, index):
        """
        An item was selected at index in selected material chooser widget

        :param index: index of new item.
        """
        if self._graphics:
            selectedMaterial = self._ui.selected_material_chooser.getMaterial()
            self._graphics.setSelectedMaterial(selectedMaterial)

    def _selectModeDisplay(self):
        """
        Show the current state of the select mode enum chooser widget
        """
        selectMode = Graphics.SELECT_MODE_INVALID
        if self._graphics:
            selectMode = self._graphics.getSelectMode()
        self._ui.select_mode_enum_chooser.setEnum(selectMode)

    def selectModeChanged(self, index):
        """
        Element select mode enum chooser widget changed

        :param index: index of new item.
        """
        if self._graphics:
            selectMode = self._ui.select_mode_enum_chooser.getEnum()
            self._graphics.setSelectMode(selectMode)
            self._updateWidgets()

    def isoscalarFieldChanged(self, index):
        if self._graphics:
            contours = self._graphics.castContours()
            if contours.isValid():
                isoscalarField = self._ui.isoscalar_field_chooser.getField()
                if not isoscalarField:
                    isoscalarField = Field()
                contours.setIsoscalarField(isoscalarField)

    def rangeIsovaluesClicked(self, isChecked):
        """
        The range isovalues checkbox was clicked

        :param isChecked: boolean
        """
        if self._graphics:
            self._isRangeIsovalues = not self._isRangeIsovalues
            self._ui.range_number_spinBox.setEnabled(self._isRangeIsovalues)
            self._isovaluesDisplay()

    def _isovaluesDisplay(self):
        """
        Display the current iso values list
        """
        if self._graphics:
            contours = self._graphics.castContours()
            if contours.isValid():
                if self._isRangeIsovalues:
                    first = contours.getRangeFirstIsovalue()
                    last = contours.getRangeLastIsovalue()
                    rangeNum = contours.getRangeNumberOfIsovalues()
                    self._displayVector(self._ui.isovalues_lineedit, [first, last])
                    self._ui.range_number_spinBox.setValue(rangeNum)
                    return
                count, isovalues = contours.getListIsovalues(1)
                if count > 1:
                    count, isovalues = contours.getListIsovalues(count)
                if count > 0:
                    self._displayVector(self._ui.isovalues_lineedit, isovalues)
                    return
        self._ui.isovalues_lineedit.setText('')

    def numberOfIsovalueRangeChanged(self, value):
        """
        Set iso values list from text in widget
        """
        try:
            contours = self._graphics.castContours()
            if contours.isValid():
                isovalues = self._parseVector(self._ui.isovalues_lineedit)
                rangeNum = value
                firstIsovalue = isovalues[0]
                lastIsovalue = isovalues[1]
                if contours.setRangeIsovalues(rangeNum, firstIsovalue, lastIsovalue) != ZINC_OK:
                    raise
        except:
            ArgonLogger.getLogger().error("Invalid range number for isovalues")
        self._isovaluesDisplay()

    def isovaluesEntered(self):
        """
        Set iso values list from text in widget
        """
        try:
            isovalues = self._parseVector(self._ui.isovalues_lineedit)
            contours = self._graphics.castContours()
            if contours.isValid():
                if self._isRangeIsovalues:
                    rangeNum = self._ui.range_number_spinBox.value()
                    firstIsovalue = isovalues[0]
                    lastIsovalue = isovalues[1]
                    if contours.setRangeIsovalues(rangeNum, firstIsovalue, lastIsovalue) != ZINC_OK:
                        raise
                elif contours.setListIsovalues(isovalues) != ZINC_OK:
                    raise
        except:
            ArgonLogger.getLogger().error("Invalid isovalues")
        self._isovaluesDisplay()

    def streamVectorFieldChanged(self, index):
        if self._graphics:
            streamlines = self._graphics.castStreamlines()
            if streamlines.isValid():
                streamVectorField = self._ui.stream_vector_field_chooser.getField()
                if not streamVectorField:
                    streamVectorField = Field()
                streamlines.setStreamVectorField(streamVectorField)

    def _streamlinesTrackLengthDisplay(self):
        """
        Display the current streamlines length
        """
        if self._graphics:
            streamlines = self._graphics.castStreamlines()
            if streamlines.isValid():
                trackLength = streamlines.getTrackLength()
                self._displayReal(
                    self._ui.streamlines_track_length_lineedit, trackLength)
                return
        self._ui.streamlines_track_length_lineedit.setText('')

    def streamlinesTrackLengthEntered(self):
        """
        Set iso values list from text in widget
        """
        streamlinesLengthText = self._ui.streamlines_track_length_lineedit.text()
        try:
            trackLength = float(streamlinesLengthText)
            streamlines = self._graphics.castStreamlines()
            if streamlines.isValid():
                if streamlines.setTrackLength(trackLength) != ZINC_OK:
                    raise
        except:
            print("Invalid streamlines track length", streamlinesLengthText)
        self._streamlinesTrackLengthDisplay()

    def _streamlinesTrackDirectionDisplay(self):
        """
        Show the current state of the streamlines track direction combo box
        """
        streamlinesTrackDirection = GraphicsStreamlines.TRACK_DIRECTION_FORWARD
        if self._graphics:
            streamlines = self._graphics.castStreamlines()
            if streamlines.isValid():
                streamlinesTrackDirection = streamlines.getTrackDirection()
        self._ui.streamlines_track_direction_chooser.setEnum(streamlinesTrackDirection)

    def streamlinesTrackDirectionChanged(self, index):
        """
        Element streamlines track direction combo box changed

        :param index: index of new item.
        """
        if self._graphics:
            streamlines = self._graphics.castStreamlines()
            if streamlines.isValid():
                streamlines.setTrackDirection(
                    index + GraphicsStreamlines.TRACK_DIRECTION_FORWARD)

    def _streamlinesColourDataTypeDisplay(self):
        """
        Show the current state of the streamlines colour data type combo box
        """
        streamlinesColourDataType = GraphicsStreamlines.COLOUR_DATA_TYPE_FIELD
        if self._graphics:
            streamlines = self._graphics.castStreamlines()
            if streamlines.isValid():
                streamlinesColourDataType = streamlines.getColourDataType()
        self._ui.streamlines_colour_data_type_chooser.setEnum(
            streamlinesColourDataType)

    def streamlinesColourDataTypeChanged(self, index):
        """
        Element streamlines colour data type combo box changed

        :param index: index of new item.
        """
        if self._graphics:
            streamlines = self._graphics.castStreamlines()
            if streamlines.isValid():
                scene = self._graphics.getScene()
                scene.beginChange()
                spectrum = self._graphics.getSpectrum()
                if not spectrum.isValid():
                    spectrummodule = scene.getSpectrummodule()
                    spectrum = spectrummodule.getDefaultSpectrum()
                    self._graphics.setSpectrum(spectrum)
                streamlines.setColourDataType(
                    index + GraphicsStreamlines.COLOUR_DATA_TYPE_FIELD)
                scene.endChange()

    def _lineShapeDisplay(self):
        """
        Show the current state of the lineShape combo box
        """
        lineShapeType = Graphicslineattributes.SHAPE_TYPE_LINE
        if self._graphics:
            lineattributes = self._graphics.getGraphicslineattributes()
            if lineattributes.isValid():
                lineShapeType = lineattributes.getShapeType()
        self._ui.line_shape_chooser.setEnum(lineShapeType)

    def lineShapeChanged(self, index):
        """
        Element lineShape combo box changed

        :param index: index of new item.
        """
        if self._graphics:
            lineattributes = self._graphics.getGraphicslineattributes()
            if lineattributes.isValid():
                lineattributes.setShapeType(
                    index + Graphicslineattributes.SHAPE_TYPE_LINE)

    def _lineBaseSizeDisplay(self):
        """
        Display the current line base size
        """
        if self._graphics:
            lineattributes = self._graphics.getGraphicslineattributes()
            if lineattributes.isValid():
                _, baseSize = lineattributes.getBaseSize(2)
                self._displayScale(self._ui.line_base_size_lineedit, baseSize)
                return
        self._ui.line_base_size_lineedit.setText('0')

    def lineBaseSizeEntered(self):
        """
        Set line base size from text in widget
        """
        try:
            baseSize = self._parseScale(self._ui.line_base_size_lineedit)
            lineattributes = self._graphics.getGraphicslineattributes()
            if lineattributes.setBaseSize(baseSize) != ZINC_OK:
                raise
        except:
            print("Invalid line base size")
        self._lineBaseSizeDisplay()

    def lineOrientationScaleFieldChanged(self, index):
        if self._graphics:
            lineattributes = self._graphics.getGraphicslineattributes()
            if lineattributes.isValid():
                orientationScaleField = self._ui.line_orientation_scale_field_chooser.getField()
                if not orientationScaleField:
                    orientationScaleField = Field()
                lineattributes.setOrientationScaleField(orientationScaleField)

    def _lineScaleFactorsDisplay(self):
        """
        Display the current line scale factors
        """
        if self._graphics:
            lineattributes = self._graphics.getGraphicslineattributes()
            if lineattributes.isValid():
                _, scaleFactors = lineattributes.getScaleFactors(2)
                self._displayScale(
                    self._ui.line_scale_factors_lineedit, scaleFactors)
                return
        self._ui.line_scale_factors_lineedit.setText('0')

    def lineScaleFactorsEntered(self):
        """
        Set line scale factors from text in widget
        """
        try:
            scaleFactors = self._parseScale(
                self._ui.line_scale_factors_lineedit)
            lineattributes = self._graphics.getGraphicslineattributes()
            if lineattributes.setScaleFactors(scaleFactors) != ZINC_OK:
                raise
        except:
            print("Invalid line scale factors")
        self._lineScaleFactorsDisplay()

    def _pointBaseSizeDisplay(self):
        """
        Display the current point base size
        """
        if self._graphics:
            pointattributes = self._graphics.getGraphicspointattributes()
            if pointattributes.isValid():
                _, baseSize = pointattributes.getBaseSize(3)
                self._displayScale(self._ui.point_base_size_lineedit, baseSize)
                return
        self._ui.point_base_size_lineedit.setText('0')

    def pointBaseSizeEntered(self):
        """
        Set point base size from text in widget
        """
        try:
            baseSize = self._parseScale(self._ui.point_base_size_lineedit)
            pointattributes = self._graphics.getGraphicspointattributes()
            if pointattributes.setBaseSize(baseSize) != ZINC_OK:
                raise
        except:
            print("Invalid point base size")
        self._pointBaseSizeDisplay()

    def pointOrientationScaleFieldChanged(self, index):
        if self._graphics:
            pointattributes = self._graphics.getGraphicspointattributes()
            if pointattributes.isValid():
                orientationScaleField = self._ui.point_orientation_scale_field_chooser.getField()
                if not orientationScaleField:
                    orientationScaleField = Field()
                pointattributes.setOrientationScaleField(orientationScaleField)

    def _pointScaleFactorsDisplay(self):
        """
        Display the current point scale factors
        """
        if self._graphics:
            pointattributes = self._graphics.getGraphicspointattributes()
            if pointattributes.isValid():
                _, scaleFactors = pointattributes.getScaleFactors(3)
                self._displayScale(
                    self._ui.point_scale_factors_lineedit, scaleFactors)
                return
        self._ui.point_scale_factors_lineedit.setText('0')

    def pointScaleFactorsEntered(self):
        """
        Set point scale factors from text in widget
        """
        try:
            scaleFactors = self._parseScale(
                self._ui.point_scale_factors_lineedit)
            pointattributes = self._graphics.getGraphicspointattributes()
            if pointattributes.setScaleFactors(scaleFactors) != ZINC_OK:
                raise
        except:
            print("Invalid point scale factors")
        self._pointScaleFactorsDisplay()

    def labelFieldChanged(self, index):
        if self._graphics:
            pointattributes = self._graphics.getGraphicspointattributes()
            if pointattributes.isValid():
                labelField = self._ui.label_field_chooser.getField()
                if not labelField:
                    labelField = Field()
                pointattributes.setLabelField(labelField)

    def glyphRepeatModeChanged(self, index):
        """
        Glyph repeat mode combo box changed

        :param index: index of new item.
        """
        if self._graphics:
            pointattributes = self._graphics.getGraphicspointattributes()
            if pointattributes.isValid():
                glyphRepeatMode = self._ui.glyph_repeat_mode_chooser.getEnum()
                pointattributes.setGlyphRepeatMode(glyphRepeatMode)

    def glyphSignedScaleFieldChanged(self, index):
        if self._graphics:
            pointattributes = self._graphics.getGraphicspointattributes()
            if pointattributes.isValid():
                glyphSignedScaleField = self._ui.glyph_signed_scale_field_chooser.getField()
                if not glyphSignedScaleField:
                    glyphSignedScaleField = Field()
                pointattributes.setSignedScaleField(glyphSignedScaleField)

    def _glyphOffsetDisplay(self):
        """
        Display the current glyph offset
        """
        if self._graphics:
            pointattributes = self._graphics.getGraphicspointattributes()
            if pointattributes.isValid():
                _, glyphOffset = pointattributes.getGlyphOffset(3)
                self._displayVector(
                    self._ui.glyph_offset_lineedit, glyphOffset)
                return
        self._ui.glyph_offset_lineedit.setText('0')

    def glyphOffsetEntered(self):
        """
        Set glyph offset from text in widget
        """
        try:
            glyphOffset = self._parseVector(self._ui.glyph_offset_lineedit)
            pointattributes = self._graphics.getGraphicspointattributes()
            if pointattributes.setGlyphOffset(glyphOffset) != ZINC_OK:
                raise
        except:
            print("Invalid glyph offset")
        self._glyphOffsetDisplay()

    def _labelTextDisplay(self):
        """
        Display the current label offset
        """
        if self._graphics:
            pointattributes = self._graphics.getGraphicspointattributes()
            if pointattributes.isValid():
                labelTexts = []
                for i in range(3):
                    labelText = pointattributes.getLabelText(i + 1)
                    if labelText:
                        labelTexts.append(labelText)
                self._ui.glyph_label_text_lineedit.setText(
                    ",".join(labelTexts))
                return
        self._ui.glyph_label_text_lineedit.setText('')

    def labelTextEntered(self):
        """
        Set label text from text in widget
        """
        try:
            labelTexts = self._ui.glyph_label_text_lineedit.text().split(',')
            pointattributes = self._graphics.getGraphicspointattributes()
            for i in range(3):
                labelText = labelTexts[i] if i < len(labelTexts) else ''
                if pointattributes.setLabelText(i + 1, labelText) != ZINC_OK:
                    raise
        except:
            print("Invalid label text")
        self._labelTextDisplay()

    def _labelTextOffsetDisplay(self):
        """
        Display the current label text offset
        """
        if self._graphics:
            pointattributes = self._graphics.getGraphicspointattributes()
            if pointattributes.isValid():
                _, labelOffset = pointattributes.getLabelOffset(3)
                self._displayVector(
                    self._ui.glyph_label_text_offset_lineedit, labelOffset)
                return
        self._ui.glyph_label_text_offset_lineedit.setText('0')

    def labelTextOffsetEntered(self):
        """
        Set label text offset from text in widget
        """
        try:
            labelOffset = self._parseVector(
                self._ui.glyph_label_text_offset_lineedit)
            pointattributes = self._graphics.getGraphicspointattributes()
            if pointattributes.setLabelOffset(labelOffset) != ZINC_OK:
                raise
        except:
            print("Invalid label text offset")
        self._labelTextOffsetDisplay()

    def _buildFontComboBox(self):
        self._ui.glyph_font_comboBox.clear()
        self._ui.glyph_font_comboBox.addItems(["default"])

    def _fontChanged(self, index):
        """
        Set label text font to selected font in widget
        """
        try:
            pointattributes = self._graphics.getGraphicspointattributes()
            # Font, fake it till we make it
            # labelFont = findFontbyName(self._ui.glyph_font_comboBox.item(index).text())
            labelFont = pointattributes.getFont()
            if pointattributes.setFont(labelFont) != ZINC_OK:
                raise
        except:
            print("Invalid label text font")

    # Sampling Settings
    def _samplingModeDisplay(self):
        """
        Show the current state of the sampling mode combo box
        """
        samplingMode = Element.POINT_SAMPLING_MODE_CELL_CENTRES
        if self._graphics:
            samplingattributes = self._graphics.getGraphicssamplingattributes()
            if samplingattributes.isValid():
                samplingMode = samplingattributes.getElementPointSamplingMode()
        self._ui.sampling_mode_chooser.setEnum(samplingMode)

    def samplingModeChanged(self, index):
        """
        Sampling mode combo box changed
        """
        if self._graphics:
            samplingattributes = self._graphics.getGraphicssamplingattributes()
            if samplingattributes.isValid():
                samplingMode = self._ui.sampling_mode_chooser.getEnum()
                samplingattributes.setElementPointSamplingMode(samplingMode)
                self._sampleLocationDisplay()

    def _sampleLocationDisplay(self):
        """
        Show current sample location
        """
        self._ui.sample_location_lineedit.setEnabled(False)
        if self._graphics:
            samplingattributes = self._graphics.getGraphicssamplingattributes()
            if samplingattributes.isValid() and samplingattributes.getElementPointSamplingMode() == Element.POINT_SAMPLING_MODE_SET_LOCATION:
                self._ui.sample_location_lineedit.setEnabled(True)
                _, scaleFactors = samplingattributes.getLocation(3)
                self._displayVector(
                    self._ui.sample_location_lineedit, scaleFactors)
                return
        self._ui.sample_location_lineedit.setText('')

    def sampleLocationEntered(self):
        """
        Set sample location from text in widget
        """
        try:
            sampleLocation = self._parseVector(
                self._ui.sample_location_lineedit)
            samplingattributes = self._graphics.getGraphicssamplingattributes()
            if samplingattributes.setLocation(sampleLocation) != ZINC_OK:
                raise
        except:
            print("Invalid sample location")
        self._sampleLocationDisplay()

    def _densityFieldDisplay(self):
        """
        Show the current state of the density field combo box
        """
        if self._graphics:
            samplingattributes = self._graphics.getGraphicssamplingattributes()
            if samplingattributes.isValid():
                densityField = samplingattributes.getDensityField()
                self._ui.density_field_chooser.setField(densityField)
                return

    def densityFieldChanged(self):
        """
        Density field combo box changed
        """
        if self._graphics:
            samplingattributes = self._graphics.getGraphicssamplingattributes()
            if samplingattributes.isValid():
                densityField = self._ui.density_field_chooser.getField()
                samplingattributes.setDensityField(densityField)
                self._densityFieldDisplay()
