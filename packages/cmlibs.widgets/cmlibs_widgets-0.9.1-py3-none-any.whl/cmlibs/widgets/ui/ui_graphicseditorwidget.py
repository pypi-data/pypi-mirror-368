# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'graphicseditorwidget.ui'
##
## Created by: Qt User Interface Compiler version 6.4.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QFormLayout,
    QFrame, QGroupBox, QLabel, QLayout,
    QLineEdit, QScrollArea, QSizePolicy, QSpacerItem,
    QSpinBox, QVBoxLayout, QWidget)

from cmlibs.widgets.enumerationchooserwidget import EnumerationChooserWidget
from cmlibs.widgets.fieldchooserwidget import FieldChooserWidget
from cmlibs.widgets.glyphchooserwidget import GlyphChooserWidget
from cmlibs.widgets.materialchooserwidget import MaterialChooserWidget
from cmlibs.widgets.spectrumchooserwidget import SpectrumChooserWidget
from cmlibs.widgets.tessellationchooserwidget import TessellationChooserWidget

class Ui_GraphicsEditorWidget(object):
    def setupUi(self, GraphicsEditorWidget):
        if not GraphicsEditorWidget.objectName():
            GraphicsEditorWidget.setObjectName(u"GraphicsEditorWidget")
        GraphicsEditorWidget.resize(580, 330)
        GraphicsEditorWidget.setMinimumSize(QSize(580, 0))
        self.main_verticalLayout = QVBoxLayout(GraphicsEditorWidget)
        self.main_verticalLayout.setObjectName(u"main_verticalLayout")
        self.main_verticalLayout.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.scrollArea = QScrollArea(GraphicsEditorWidget)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setFrameShape(QFrame.Shape.NoFrame)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaGraphicWidgetContents = QWidget()
        self.scrollAreaGraphicWidgetContents.setObjectName(u"scrollAreaGraphicWidgetContents")
        self.scrollAreaGraphicWidgetContents.setGeometry(QRect(0, 0, 556, 1744))
        self.verticalLayout = QVBoxLayout(self.scrollAreaGraphicWidgetContents)
        self.verticalLayout.setSpacing(6)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.verticalLayout.setContentsMargins(0, 0, 7, 7)
        self.general_groupbox = QGroupBox(self.scrollAreaGraphicWidgetContents)
        self.general_groupbox.setObjectName(u"general_groupbox")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.general_groupbox.sizePolicy().hasHeightForWidth())
        self.general_groupbox.setSizePolicy(sizePolicy)
        self.formLayout_3 = QFormLayout(self.general_groupbox)
        self.formLayout_3.setObjectName(u"formLayout_3")
        self.formLayout_3.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self.formLayout_3.setProperty("Margin", 7)
        self.coordinate_field_label = QLabel(self.general_groupbox)
        self.coordinate_field_label.setObjectName(u"coordinate_field_label")

        self.formLayout_3.setWidget(4, QFormLayout.LabelRole, self.coordinate_field_label)

        self.domain_enum_label = QLabel(self.general_groupbox)
        self.domain_enum_label.setObjectName(u"domain_enum_label")

        self.formLayout_3.setWidget(2, QFormLayout.LabelRole, self.domain_enum_label)

        self.domain_chooser = EnumerationChooserWidget(self.general_groupbox)
        self.domain_chooser.setObjectName(u"domain_chooser")

        self.formLayout_3.setWidget(2, QFormLayout.FieldRole, self.domain_chooser)

        self.coordinate_field_chooser = FieldChooserWidget(self.general_groupbox)
        self.coordinate_field_chooser.setObjectName(u"coordinate_field_chooser")
        self.coordinate_field_chooser.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)

        self.formLayout_3.setWidget(4, QFormLayout.FieldRole, self.coordinate_field_chooser)

        self.scenecoordinatesystem_label = QLabel(self.general_groupbox)
        self.scenecoordinatesystem_label.setObjectName(u"scenecoordinatesystem_label")

        self.formLayout_3.setWidget(5, QFormLayout.LabelRole, self.scenecoordinatesystem_label)

        self.scenecoordinatesystem_chooser = EnumerationChooserWidget(self.general_groupbox)
        self.scenecoordinatesystem_chooser.setObjectName(u"scenecoordinatesystem_chooser")

        self.formLayout_3.setWidget(5, QFormLayout.FieldRole, self.scenecoordinatesystem_chooser)

        self.boundarymode_label = QLabel(self.general_groupbox)
        self.boundarymode_label.setObjectName(u"boundarymode_label")

        self.formLayout_3.setWidget(6, QFormLayout.LabelRole, self.boundarymode_label)

        self.boundarymode_chooser = EnumerationChooserWidget(self.general_groupbox)
        self.boundarymode_chooser.setObjectName(u"boundarymode_chooser")

        self.formLayout_3.setWidget(6, QFormLayout.FieldRole, self.boundarymode_chooser)

        self.face_label = QLabel(self.general_groupbox)
        self.face_label.setObjectName(u"face_label")

        self.formLayout_3.setWidget(7, QFormLayout.LabelRole, self.face_label)

        self.face_enumeration_chooser = EnumerationChooserWidget(self.general_groupbox)
        self.face_enumeration_chooser.setObjectName(u"face_enumeration_chooser")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.face_enumeration_chooser.sizePolicy().hasHeightForWidth())
        self.face_enumeration_chooser.setSizePolicy(sizePolicy1)

        self.formLayout_3.setWidget(7, QFormLayout.FieldRole, self.face_enumeration_chooser)

        self.material_label = QLabel(self.general_groupbox)
        self.material_label.setObjectName(u"material_label")

        self.formLayout_3.setWidget(10, QFormLayout.LabelRole, self.material_label)

        self.material_chooser = MaterialChooserWidget(self.general_groupbox)
        self.material_chooser.setObjectName(u"material_chooser")
        self.material_chooser.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)

        self.formLayout_3.setWidget(10, QFormLayout.FieldRole, self.material_chooser)

        self.selected_material_label = QLabel(self.general_groupbox)
        self.selected_material_label.setObjectName(u"selected_material_label")

        self.formLayout_3.setWidget(11, QFormLayout.LabelRole, self.selected_material_label)

        self.selected_material_chooser = MaterialChooserWidget(self.general_groupbox)
        self.selected_material_chooser.setObjectName(u"selected_material_chooser")

        self.formLayout_3.setWidget(11, QFormLayout.FieldRole, self.selected_material_chooser)

        self.data_field_label = QLabel(self.general_groupbox)
        self.data_field_label.setObjectName(u"data_field_label")

        self.formLayout_3.setWidget(13, QFormLayout.LabelRole, self.data_field_label)

        self.data_field_chooser = FieldChooserWidget(self.general_groupbox)
        self.data_field_chooser.setObjectName(u"data_field_chooser")
        self.data_field_chooser.setEditable(False)
        self.data_field_chooser.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)

        self.formLayout_3.setWidget(13, QFormLayout.FieldRole, self.data_field_chooser)

        self.spectrum_label = QLabel(self.general_groupbox)
        self.spectrum_label.setObjectName(u"spectrum_label")

        self.formLayout_3.setWidget(14, QFormLayout.LabelRole, self.spectrum_label)

        self.spectrum_chooser = SpectrumChooserWidget(self.general_groupbox)
        self.spectrum_chooser.setObjectName(u"spectrum_chooser")

        self.formLayout_3.setWidget(14, QFormLayout.FieldRole, self.spectrum_chooser)

        self.wireframe_checkbox = QCheckBox(self.general_groupbox)
        self.wireframe_checkbox.setObjectName(u"wireframe_checkbox")

        self.formLayout_3.setWidget(9, QFormLayout.LabelRole, self.wireframe_checkbox)

        self.tessellation_chooser = TessellationChooserWidget(self.general_groupbox)
        self.tessellation_chooser.setObjectName(u"tessellation_chooser")

        self.formLayout_3.setWidget(15, QFormLayout.FieldRole, self.tessellation_chooser)

        self.tessellation_label = QLabel(self.general_groupbox)
        self.tessellation_label.setObjectName(u"tessellation_label")

        self.formLayout_3.setWidget(15, QFormLayout.LabelRole, self.tessellation_label)

        self.subgroup_field_label = QLabel(self.general_groupbox)
        self.subgroup_field_label.setObjectName(u"subgroup_field_label")

        self.formLayout_3.setWidget(3, QFormLayout.LabelRole, self.subgroup_field_label)

        self.subgroup_field_chooser = FieldChooserWidget(self.general_groupbox)
        self.subgroup_field_chooser.setObjectName(u"subgroup_field_chooser")

        self.formLayout_3.setWidget(3, QFormLayout.FieldRole, self.subgroup_field_chooser)

        self.tessellation_field_label = QLabel(self.general_groupbox)
        self.tessellation_field_label.setObjectName(u"tessellation_field_label")

        self.formLayout_3.setWidget(16, QFormLayout.LabelRole, self.tessellation_field_label)

        self.tessellation_field_chooser = FieldChooserWidget(self.general_groupbox)
        self.tessellation_field_chooser.setObjectName(u"tessellation_field_chooser")

        self.formLayout_3.setWidget(16, QFormLayout.FieldRole, self.tessellation_field_chooser)

        self.texture_coordinates_label = QLabel(self.general_groupbox)
        self.texture_coordinates_label.setObjectName(u"texture_coordinates_label")

        self.formLayout_3.setWidget(17, QFormLayout.LabelRole, self.texture_coordinates_label)

        self.texture_coordinates_chooser = FieldChooserWidget(self.general_groupbox)
        self.texture_coordinates_chooser.setObjectName(u"texture_coordinates_chooser")

        self.formLayout_3.setWidget(17, QFormLayout.FieldRole, self.texture_coordinates_chooser)

        self.select_mode_label = QLabel(self.general_groupbox)
        self.select_mode_label.setObjectName(u"select_mode_label")

        self.formLayout_3.setWidget(8, QFormLayout.LabelRole, self.select_mode_label)

        self.select_mode_enum_chooser = EnumerationChooserWidget(self.general_groupbox)
        self.select_mode_enum_chooser.setObjectName(u"select_mode_enum_chooser")

        self.formLayout_3.setWidget(8, QFormLayout.FieldRole, self.select_mode_enum_chooser)

        self.line_width_label = QLabel(self.general_groupbox)
        self.line_width_label.setObjectName(u"line_width_label")

        self.formLayout_3.setWidget(18, QFormLayout.LabelRole, self.line_width_label)

        self.line_width_lineEdit = QLineEdit(self.general_groupbox)
        self.line_width_lineEdit.setObjectName(u"line_width_lineEdit")

        self.formLayout_3.setWidget(18, QFormLayout.FieldRole, self.line_width_lineEdit)

        self.point_size_label = QLabel(self.general_groupbox)
        self.point_size_label.setObjectName(u"point_size_label")

        self.formLayout_3.setWidget(19, QFormLayout.LabelRole, self.point_size_label)

        self.point_size_lineEdit = QLineEdit(self.general_groupbox)
        self.point_size_lineEdit.setObjectName(u"point_size_lineEdit")

        self.formLayout_3.setWidget(19, QFormLayout.FieldRole, self.point_size_lineEdit)


        self.verticalLayout.addWidget(self.general_groupbox)

        self.contours_groupbox = QGroupBox(self.scrollAreaGraphicWidgetContents)
        self.contours_groupbox.setObjectName(u"contours_groupbox")
        self.contours_groupbox.setMaximumSize(QSize(16777215, 16777215))
        self.contours_groupbox.setFlat(False)
        self.formLayout_2 = QFormLayout(self.contours_groupbox)
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.formLayout_2.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self.isovalues_lineedit = QLineEdit(self.contours_groupbox)
        self.isovalues_lineedit.setObjectName(u"isovalues_lineedit")

        self.formLayout_2.setWidget(3, QFormLayout.FieldRole, self.isovalues_lineedit)

        self.isoscalar_field_label = QLabel(self.contours_groupbox)
        self.isoscalar_field_label.setObjectName(u"isoscalar_field_label")

        self.formLayout_2.setWidget(0, QFormLayout.LabelRole, self.isoscalar_field_label)

        self.isoscalar_field_chooser = FieldChooserWidget(self.contours_groupbox)
        self.isoscalar_field_chooser.setObjectName(u"isoscalar_field_chooser")
        self.isoscalar_field_chooser.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)

        self.formLayout_2.setWidget(0, QFormLayout.FieldRole, self.isoscalar_field_chooser)

        self.isovalues_label = QLabel(self.contours_groupbox)
        self.isovalues_label.setObjectName(u"isovalues_label")

        self.formLayout_2.setWidget(3, QFormLayout.LabelRole, self.isovalues_label)

        self.range_isovalues_checkBox = QCheckBox(self.contours_groupbox)
        self.range_isovalues_checkBox.setObjectName(u"range_isovalues_checkBox")

        self.formLayout_2.setWidget(1, QFormLayout.LabelRole, self.range_isovalues_checkBox)

        self.range_number_spinBox = QSpinBox(self.contours_groupbox)
        self.range_number_spinBox.setObjectName(u"range_number_spinBox")
        self.range_number_spinBox.setMaximum(2147483646)

        self.formLayout_2.setWidget(1, QFormLayout.FieldRole, self.range_number_spinBox)


        self.verticalLayout.addWidget(self.contours_groupbox)

        self.streamlines_groupbox = QGroupBox(self.scrollAreaGraphicWidgetContents)
        self.streamlines_groupbox.setObjectName(u"streamlines_groupbox")
        self.formLayout_5 = QFormLayout(self.streamlines_groupbox)
        self.formLayout_5.setObjectName(u"formLayout_5")
        self.formLayout_5.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self.stream_vector_field_label = QLabel(self.streamlines_groupbox)
        self.stream_vector_field_label.setObjectName(u"stream_vector_field_label")

        self.formLayout_5.setWidget(0, QFormLayout.LabelRole, self.stream_vector_field_label)

        self.stream_vector_field_chooser = FieldChooserWidget(self.streamlines_groupbox)
        self.stream_vector_field_chooser.setObjectName(u"stream_vector_field_chooser")
        self.stream_vector_field_chooser.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)

        self.formLayout_5.setWidget(0, QFormLayout.FieldRole, self.stream_vector_field_chooser)

        self.streamlines_track_length_label = QLabel(self.streamlines_groupbox)
        self.streamlines_track_length_label.setObjectName(u"streamlines_track_length_label")

        self.formLayout_5.setWidget(1, QFormLayout.LabelRole, self.streamlines_track_length_label)

        self.streamlines_track_length_lineedit = QLineEdit(self.streamlines_groupbox)
        self.streamlines_track_length_lineedit.setObjectName(u"streamlines_track_length_lineedit")

        self.formLayout_5.setWidget(1, QFormLayout.FieldRole, self.streamlines_track_length_lineedit)

        self.streamline_track_direction_label = QLabel(self.streamlines_groupbox)
        self.streamline_track_direction_label.setObjectName(u"streamline_track_direction_label")

        self.formLayout_5.setWidget(2, QFormLayout.LabelRole, self.streamline_track_direction_label)

        self.streamlines_track_direction_chooser = EnumerationChooserWidget(self.streamlines_groupbox)
        self.streamlines_track_direction_chooser.setObjectName(u"streamlines_track_direction_chooser")

        self.formLayout_5.setWidget(2, QFormLayout.FieldRole, self.streamlines_track_direction_chooser)

        self.streamlines_colour_data_type_label = QLabel(self.streamlines_groupbox)
        self.streamlines_colour_data_type_label.setObjectName(u"streamlines_colour_data_type_label")

        self.formLayout_5.setWidget(3, QFormLayout.LabelRole, self.streamlines_colour_data_type_label)

        self.streamlines_colour_data_type_chooser = EnumerationChooserWidget(self.streamlines_groupbox)
        self.streamlines_colour_data_type_chooser.setObjectName(u"streamlines_colour_data_type_chooser")

        self.formLayout_5.setWidget(3, QFormLayout.FieldRole, self.streamlines_colour_data_type_chooser)


        self.verticalLayout.addWidget(self.streamlines_groupbox)

        self.lines_groupbox = QGroupBox(self.scrollAreaGraphicWidgetContents)
        self.lines_groupbox.setObjectName(u"lines_groupbox")
        self.formLayout_4 = QFormLayout(self.lines_groupbox)
        self.formLayout_4.setObjectName(u"formLayout_4")
        self.formLayout_4.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self.line_shape_label = QLabel(self.lines_groupbox)
        self.line_shape_label.setObjectName(u"line_shape_label")

        self.formLayout_4.setWidget(0, QFormLayout.LabelRole, self.line_shape_label)

        self.line_shape_chooser = EnumerationChooserWidget(self.lines_groupbox)
        self.line_shape_chooser.setObjectName(u"line_shape_chooser")

        self.formLayout_4.setWidget(0, QFormLayout.FieldRole, self.line_shape_chooser)

        self.line_base_size_label = QLabel(self.lines_groupbox)
        self.line_base_size_label.setObjectName(u"line_base_size_label")

        self.formLayout_4.setWidget(1, QFormLayout.LabelRole, self.line_base_size_label)

        self.line_base_size_lineedit = QLineEdit(self.lines_groupbox)
        self.line_base_size_lineedit.setObjectName(u"line_base_size_lineedit")

        self.formLayout_4.setWidget(1, QFormLayout.FieldRole, self.line_base_size_lineedit)

        self.line_orientation_scale_field_label = QLabel(self.lines_groupbox)
        self.line_orientation_scale_field_label.setObjectName(u"line_orientation_scale_field_label")

        self.formLayout_4.setWidget(2, QFormLayout.LabelRole, self.line_orientation_scale_field_label)

        self.line_orientation_scale_field_chooser = FieldChooserWidget(self.lines_groupbox)
        self.line_orientation_scale_field_chooser.setObjectName(u"line_orientation_scale_field_chooser")
        sizePolicy1.setHeightForWidth(self.line_orientation_scale_field_chooser.sizePolicy().hasHeightForWidth())
        self.line_orientation_scale_field_chooser.setSizePolicy(sizePolicy1)
        self.line_orientation_scale_field_chooser.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)

        self.formLayout_4.setWidget(2, QFormLayout.FieldRole, self.line_orientation_scale_field_chooser)

        self.line_scale_factors_label = QLabel(self.lines_groupbox)
        self.line_scale_factors_label.setObjectName(u"line_scale_factors_label")

        self.formLayout_4.setWidget(3, QFormLayout.LabelRole, self.line_scale_factors_label)

        self.line_scale_factors_lineedit = QLineEdit(self.lines_groupbox)
        self.line_scale_factors_lineedit.setObjectName(u"line_scale_factors_lineedit")

        self.formLayout_4.setWidget(3, QFormLayout.FieldRole, self.line_scale_factors_lineedit)


        self.verticalLayout.addWidget(self.lines_groupbox)

        self.points_groupbox = QGroupBox(self.scrollAreaGraphicWidgetContents)
        self.points_groupbox.setObjectName(u"points_groupbox")
        self.points_groupbox.setMaximumSize(QSize(16777215, 16777215))
        self.formLayout = QFormLayout(self.points_groupbox)
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self.glyph_label = QLabel(self.points_groupbox)
        self.glyph_label.setObjectName(u"glyph_label")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.glyph_label)

        self.glyph_chooser = GlyphChooserWidget(self.points_groupbox)
        self.glyph_chooser.setObjectName(u"glyph_chooser")
        self.glyph_chooser.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.glyph_chooser)

        self.point_base_size_label = QLabel(self.points_groupbox)
        self.point_base_size_label.setObjectName(u"point_base_size_label")

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.point_base_size_label)

        self.point_base_size_lineedit = QLineEdit(self.points_groupbox)
        self.point_base_size_lineedit.setObjectName(u"point_base_size_lineedit")

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.point_base_size_lineedit)

        self.point_orientation_scale_field_label = QLabel(self.points_groupbox)
        self.point_orientation_scale_field_label.setObjectName(u"point_orientation_scale_field_label")

        self.formLayout.setWidget(3, QFormLayout.LabelRole, self.point_orientation_scale_field_label)

        self.point_orientation_scale_field_chooser = FieldChooserWidget(self.points_groupbox)
        self.point_orientation_scale_field_chooser.setObjectName(u"point_orientation_scale_field_chooser")
        self.point_orientation_scale_field_chooser.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)

        self.formLayout.setWidget(3, QFormLayout.FieldRole, self.point_orientation_scale_field_chooser)

        self.point_scale_factors_label = QLabel(self.points_groupbox)
        self.point_scale_factors_label.setObjectName(u"point_scale_factors_label")

        self.formLayout.setWidget(6, QFormLayout.LabelRole, self.point_scale_factors_label)

        self.label_field_label = QLabel(self.points_groupbox)
        self.label_field_label.setObjectName(u"label_field_label")

        self.formLayout.setWidget(9, QFormLayout.LabelRole, self.label_field_label)

        self.label_field_chooser = FieldChooserWidget(self.points_groupbox)
        self.label_field_chooser.setObjectName(u"label_field_chooser")
        self.label_field_chooser.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)

        self.formLayout.setWidget(9, QFormLayout.FieldRole, self.label_field_chooser)

        self.point_scale_factors_lineedit = QLineEdit(self.points_groupbox)
        self.point_scale_factors_lineedit.setObjectName(u"point_scale_factors_lineedit")

        self.formLayout.setWidget(6, QFormLayout.FieldRole, self.point_scale_factors_lineedit)

        self.glyph_repeat_mode_label = QLabel(self.points_groupbox)
        self.glyph_repeat_mode_label.setObjectName(u"glyph_repeat_mode_label")

        self.formLayout.setWidget(10, QFormLayout.LabelRole, self.glyph_repeat_mode_label)

        self.glyph_repeat_mode_chooser = EnumerationChooserWidget(self.points_groupbox)
        self.glyph_repeat_mode_chooser.setObjectName(u"glyph_repeat_mode_chooser")

        self.formLayout.setWidget(10, QFormLayout.FieldRole, self.glyph_repeat_mode_chooser)

        self.glyph_offset_label = QLabel(self.points_groupbox)
        self.glyph_offset_label.setObjectName(u"glyph_offset_label")

        self.formLayout.setWidget(12, QFormLayout.LabelRole, self.glyph_offset_label)

        self.glyph_offset_lineedit = QLineEdit(self.points_groupbox)
        self.glyph_offset_lineedit.setObjectName(u"glyph_offset_lineedit")

        self.formLayout.setWidget(12, QFormLayout.FieldRole, self.glyph_offset_lineedit)

        self.glyph_label_text_label = QLabel(self.points_groupbox)
        self.glyph_label_text_label.setObjectName(u"glyph_label_text_label")

        self.formLayout.setWidget(13, QFormLayout.LabelRole, self.glyph_label_text_label)

        self.glyph_label_text_lineedit = QLineEdit(self.points_groupbox)
        self.glyph_label_text_lineedit.setObjectName(u"glyph_label_text_lineedit")

        self.formLayout.setWidget(13, QFormLayout.FieldRole, self.glyph_label_text_lineedit)

        self.glyph_label_text_offset_label = QLabel(self.points_groupbox)
        self.glyph_label_text_offset_label.setObjectName(u"glyph_label_text_offset_label")

        self.formLayout.setWidget(14, QFormLayout.LabelRole, self.glyph_label_text_offset_label)

        self.glyph_label_text_offset_lineedit = QLineEdit(self.points_groupbox)
        self.glyph_label_text_offset_lineedit.setObjectName(u"glyph_label_text_offset_lineedit")

        self.formLayout.setWidget(14, QFormLayout.FieldRole, self.glyph_label_text_offset_lineedit)

        self.glyph_font_label = QLabel(self.points_groupbox)
        self.glyph_font_label.setObjectName(u"glyph_font_label")

        self.formLayout.setWidget(15, QFormLayout.LabelRole, self.glyph_font_label)

        self.glyph_font_comboBox = QComboBox(self.points_groupbox)
        self.glyph_font_comboBox.setObjectName(u"glyph_font_comboBox")

        self.formLayout.setWidget(15, QFormLayout.FieldRole, self.glyph_font_comboBox)

        self.glyph_signed_scale_field_chooser = FieldChooserWidget(self.points_groupbox)
        self.glyph_signed_scale_field_chooser.setObjectName(u"glyph_signed_scale_field_chooser")
        self.glyph_signed_scale_field_chooser.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)

        self.formLayout.setWidget(7, QFormLayout.FieldRole, self.glyph_signed_scale_field_chooser)

        self.glyph_signed_scale_field_label = QLabel(self.points_groupbox)
        self.glyph_signed_scale_field_label.setObjectName(u"glyph_signed_scale_field_label")

        self.formLayout.setWidget(7, QFormLayout.LabelRole, self.glyph_signed_scale_field_label)


        self.verticalLayout.addWidget(self.points_groupbox)

        self.sampling_groupbox = QGroupBox(self.scrollAreaGraphicWidgetContents)
        self.sampling_groupbox.setObjectName(u"sampling_groupbox")
        self.formLayout_6 = QFormLayout(self.sampling_groupbox)
        self.formLayout_6.setObjectName(u"formLayout_6")
        self.formLayout_6.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self.formLayout_6.setContentsMargins(9, 9, 9, -1)
        self.sampling_mode_label = QLabel(self.sampling_groupbox)
        self.sampling_mode_label.setObjectName(u"sampling_mode_label")

        self.formLayout_6.setWidget(0, QFormLayout.LabelRole, self.sampling_mode_label)

        self.sampling_mode_chooser = EnumerationChooserWidget(self.sampling_groupbox)
        self.sampling_mode_chooser.setObjectName(u"sampling_mode_chooser")

        self.formLayout_6.setWidget(0, QFormLayout.FieldRole, self.sampling_mode_chooser)

        self.sample_location_label = QLabel(self.sampling_groupbox)
        self.sample_location_label.setObjectName(u"sample_location_label")

        self.formLayout_6.setWidget(1, QFormLayout.LabelRole, self.sample_location_label)

        self.sample_location_lineedit = QLineEdit(self.sampling_groupbox)
        self.sample_location_lineedit.setObjectName(u"sample_location_lineedit")

        self.formLayout_6.setWidget(1, QFormLayout.FieldRole, self.sample_location_lineedit)

        self.density_field_label = QLabel(self.sampling_groupbox)
        self.density_field_label.setObjectName(u"density_field_label")

        self.formLayout_6.setWidget(2, QFormLayout.LabelRole, self.density_field_label)

        self.density_field_chooser = FieldChooserWidget(self.sampling_groupbox)
        self.density_field_chooser.setObjectName(u"density_field_chooser")

        self.formLayout_6.setWidget(2, QFormLayout.FieldRole, self.density_field_chooser)


        self.verticalLayout.addWidget(self.sampling_groupbox)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.scrollArea.setWidget(self.scrollAreaGraphicWidgetContents)

        self.main_verticalLayout.addWidget(self.scrollArea)


        self.retranslateUi(GraphicsEditorWidget)
        self.data_field_chooser.currentIndexChanged.connect(GraphicsEditorWidget.dataFieldChanged)
        self.material_chooser.currentIndexChanged.connect(GraphicsEditorWidget.materialChanged)
        self.selected_material_chooser.currentIndexChanged.connect(GraphicsEditorWidget.selectedMaterialChanged)
        self.glyph_chooser.currentIndexChanged.connect(GraphicsEditorWidget.glyphChanged)
        self.point_base_size_lineedit.editingFinished.connect(GraphicsEditorWidget.pointBaseSizeEntered)
        self.point_scale_factors_lineedit.editingFinished.connect(GraphicsEditorWidget.pointScaleFactorsEntered)
        self.point_orientation_scale_field_chooser.currentIndexChanged.connect(GraphicsEditorWidget.pointOrientationScaleFieldChanged)
        self.label_field_chooser.currentIndexChanged.connect(GraphicsEditorWidget.labelFieldChanged)
        self.isoscalar_field_chooser.currentIndexChanged.connect(GraphicsEditorWidget.isoscalarFieldChanged)
        self.wireframe_checkbox.clicked["bool"].connect(GraphicsEditorWidget.wireframeClicked)
        self.range_isovalues_checkBox.clicked["bool"].connect(GraphicsEditorWidget.rangeIsovaluesClicked)
        self.isovalues_lineedit.editingFinished.connect(GraphicsEditorWidget.isovaluesEntered)
        self.line_base_size_lineedit.editingFinished.connect(GraphicsEditorWidget.lineBaseSizeEntered)
        self.sample_location_lineedit.editingFinished.connect(GraphicsEditorWidget.sampleLocationEntered)
        self.line_orientation_scale_field_chooser.currentIndexChanged.connect(GraphicsEditorWidget.lineOrientationScaleFieldChanged)
        self.line_scale_factors_lineedit.editingFinished.connect(GraphicsEditorWidget.lineScaleFactorsEntered)
        self.line_shape_chooser.currentIndexChanged.connect(GraphicsEditorWidget.lineShapeChanged)
        self.stream_vector_field_chooser.currentIndexChanged.connect(GraphicsEditorWidget.streamVectorFieldChanged)
        self.sampling_mode_chooser.currentIndexChanged.connect(GraphicsEditorWidget.samplingModeChanged)
        self.density_field_chooser.currentIndexChanged.connect(GraphicsEditorWidget.densityFieldChanged)
        self.streamlines_track_length_lineedit.editingFinished.connect(GraphicsEditorWidget.streamlinesTrackLengthEntered)
        self.coordinate_field_chooser.currentIndexChanged.connect(GraphicsEditorWidget.coordinateFieldChanged)
        self.streamlines_track_direction_chooser.currentIndexChanged.connect(GraphicsEditorWidget.streamlinesTrackDirectionChanged)
        self.streamlines_colour_data_type_chooser.currentIndexChanged.connect(GraphicsEditorWidget.streamlinesColourDataTypeChanged)
        self.spectrum_chooser.currentIndexChanged.connect(GraphicsEditorWidget.spectrumChanged)
        self.tessellation_chooser.currentIndexChanged.connect(GraphicsEditorWidget.tessellationChanged)
        self.subgroup_field_chooser.currentIndexChanged.connect(GraphicsEditorWidget.subgroupFieldChanged)
        self.domain_chooser.currentIndexChanged.connect(GraphicsEditorWidget.domainChanged)
        self.select_mode_enum_chooser.currentIndexChanged.connect(GraphicsEditorWidget.selectModeChanged)
        self.face_enumeration_chooser.currentIndexChanged.connect(GraphicsEditorWidget.faceChanged)
        self.scenecoordinatesystem_chooser.currentIndexChanged.connect(GraphicsEditorWidget.scenecoordinatesystemChanged)
        self.boundarymode_chooser.currentIndexChanged.connect(GraphicsEditorWidget.boundarymodeChanged)
        self.subgroup_field_chooser.currentIndexChanged.connect(GraphicsEditorWidget.subgroupFieldChanged)
        self.glyph_repeat_mode_chooser.currentIndexChanged.connect(GraphicsEditorWidget.glyphRepeatModeChanged)
        self.glyph_signed_scale_field_chooser.currentIndexChanged.connect(GraphicsEditorWidget.glyphSignedScaleFieldChanged)
        self.glyph_offset_lineedit.editingFinished.connect(GraphicsEditorWidget.glyphOffsetEntered)
        self.glyph_label_text_lineedit.editingFinished.connect(GraphicsEditorWidget.labelTextEntered)
        self.glyph_label_text_offset_lineedit.editingFinished.connect(GraphicsEditorWidget.labelTextOffsetEntered)
        self.tessellation_field_chooser.currentIndexChanged.connect(GraphicsEditorWidget.tessellationFieldChanged)
        self.texture_coordinates_chooser.currentIndexChanged.connect(GraphicsEditorWidget.textureCoordinateFieldChanged)
        self.line_width_lineEdit.editingFinished.connect(GraphicsEditorWidget.renderLineWidthEntered)
        self.point_size_lineEdit.editingFinished.connect(GraphicsEditorWidget.renderPointSizeEntered)

        QMetaObject.connectSlotsByName(GraphicsEditorWidget)
    # setupUi

    def retranslateUi(self, GraphicsEditorWidget):
        GraphicsEditorWidget.setWindowTitle(QCoreApplication.translate("GraphicsEditorWidget", u"Graphics Editor", None))
        self.coordinate_field_label.setText(QCoreApplication.translate("GraphicsEditorWidget", u"Coordinates:", None))
        self.domain_enum_label.setText(QCoreApplication.translate("GraphicsEditorWidget", u"Domain:", None))
        self.scenecoordinatesystem_label.setText(QCoreApplication.translate("GraphicsEditorWidget", u"Coord system:", None))
        self.boundarymode_label.setText(QCoreApplication.translate("GraphicsEditorWidget", u"Boundary mode:", None))
        self.face_label.setText(QCoreApplication.translate("GraphicsEditorWidget", u"Face:", None))
        self.material_label.setText(QCoreApplication.translate("GraphicsEditorWidget", u"Material:", None))
        self.selected_material_label.setText(QCoreApplication.translate("GraphicsEditorWidget", u"Selected material:", None))
        self.data_field_label.setText(QCoreApplication.translate("GraphicsEditorWidget", u"Data field:", None))
        self.spectrum_label.setText(QCoreApplication.translate("GraphicsEditorWidget", u"Spectrum:", None))
        self.wireframe_checkbox.setText(QCoreApplication.translate("GraphicsEditorWidget", u"Wireframe", None))
        self.tessellation_label.setText(QCoreApplication.translate("GraphicsEditorWidget", u"Tessellation:", None))
        self.subgroup_field_label.setText(QCoreApplication.translate("GraphicsEditorWidget", u"Subgroup:", None))
        self.tessellation_field_label.setText(QCoreApplication.translate("GraphicsEditorWidget", u"Tessellation field:", None))
        self.texture_coordinates_label.setText(QCoreApplication.translate("GraphicsEditorWidget", u"Texture coordinates:", None))
        self.select_mode_label.setText(QCoreApplication.translate("GraphicsEditorWidget", u"Select mode:", None))
        self.line_width_label.setText(QCoreApplication.translate("GraphicsEditorWidget", u"Line width:", None))
        self.point_size_label.setText(QCoreApplication.translate("GraphicsEditorWidget", u"Point size:", None))
        self.contours_groupbox.setTitle(QCoreApplication.translate("GraphicsEditorWidget", u"Contours:", None))
        self.isoscalar_field_label.setText(QCoreApplication.translate("GraphicsEditorWidget", u"Scalar field:", None))
        self.isovalues_label.setText(QCoreApplication.translate("GraphicsEditorWidget", u"Isovalues:", None))
        self.range_isovalues_checkBox.setText(QCoreApplication.translate("GraphicsEditorWidget", u"Range number:", None))
        self.streamlines_groupbox.setTitle(QCoreApplication.translate("GraphicsEditorWidget", u"Streamlines:", None))
        self.stream_vector_field_label.setText(QCoreApplication.translate("GraphicsEditorWidget", u"Vector field:", None))
        self.streamlines_track_length_label.setText(QCoreApplication.translate("GraphicsEditorWidget", u"Time length:", None))
        self.streamline_track_direction_label.setText(QCoreApplication.translate("GraphicsEditorWidget", u"Direction:", None))
        self.streamlines_colour_data_type_label.setText(QCoreApplication.translate("GraphicsEditorWidget", u"Colour data:", None))
        self.lines_groupbox.setTitle(QCoreApplication.translate("GraphicsEditorWidget", u"Lines:", None))
        self.line_shape_label.setText(QCoreApplication.translate("GraphicsEditorWidget", u"Shape:", None))
        self.line_base_size_label.setText(QCoreApplication.translate("GraphicsEditorWidget", u"Base size:", None))
        self.line_orientation_scale_field_label.setText(QCoreApplication.translate("GraphicsEditorWidget", u"Scale field:", None))
        self.line_scale_factors_label.setText(QCoreApplication.translate("GraphicsEditorWidget", u"Scaling:", None))
        self.points_groupbox.setTitle(QCoreApplication.translate("GraphicsEditorWidget", u"Points:", None))
        self.glyph_label.setText(QCoreApplication.translate("GraphicsEditorWidget", u"Glyph:", None))
        self.point_base_size_label.setText(QCoreApplication.translate("GraphicsEditorWidget", u"Base size:", None))
        self.point_orientation_scale_field_label.setText(QCoreApplication.translate("GraphicsEditorWidget", u"Scale field:", None))
        self.point_scale_factors_label.setText(QCoreApplication.translate("GraphicsEditorWidget", u"Scaling:", None))
        self.label_field_label.setText(QCoreApplication.translate("GraphicsEditorWidget", u"Label field:", None))
        self.glyph_repeat_mode_label.setText(QCoreApplication.translate("GraphicsEditorWidget", u"Repeat mode:", None))
        self.glyph_offset_label.setText(QCoreApplication.translate("GraphicsEditorWidget", u"Glyph offset:", None))
        self.glyph_label_text_label.setText(QCoreApplication.translate("GraphicsEditorWidget", u"Label text:", None))
        self.glyph_label_text_offset_label.setText(QCoreApplication.translate("GraphicsEditorWidget", u"Label text offset:", None))
        self.glyph_font_label.setText(QCoreApplication.translate("GraphicsEditorWidget", u"Font:", None))
        self.glyph_signed_scale_field_label.setText(QCoreApplication.translate("GraphicsEditorWidget", u"Signed scale field:", None))
        self.sampling_groupbox.setTitle(QCoreApplication.translate("GraphicsEditorWidget", u"Sampling:", None))
        self.sampling_mode_label.setText(QCoreApplication.translate("GraphicsEditorWidget", u"Mode:", None))
        self.sample_location_label.setText(QCoreApplication.translate("GraphicsEditorWidget", u"Sample location:", None))
        self.density_field_label.setText(QCoreApplication.translate("GraphicsEditorWidget", u"Density field:", None))
    # retranslateUi

