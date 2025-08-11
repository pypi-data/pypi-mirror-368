# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'displaysettingswidget.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QFormLayout, QFrame,
    QGridLayout, QHBoxLayout, QLabel, QLineEdit,
    QRadioButton, QSizePolicy, QSlider, QSpacerItem,
    QSpinBox, QVBoxLayout, QWidget)

from cmlibs.widgets.fieldchooserwidget import FieldChooserWidget

class Ui_DisplaySettings(object):
    def setupUi(self, DisplaySettings):
        if not DisplaySettings.objectName():
            DisplaySettings.setObjectName(u"DisplaySettings")
        DisplaySettings.resize(999, 729)
        DisplaySettings.setMaximumSize(QSize(16777215, 16777215))
        self.verticalLayout_2 = QVBoxLayout(DisplaySettings)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.displayMisc_frame = QFrame(DisplaySettings)
        self.displayMisc_frame.setObjectName(u"displayMisc_frame")
        self.displayMisc_frame.setFrameShape(QFrame.NoFrame)
        self.displayMisc_frame.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_8 = QHBoxLayout(self.displayMisc_frame)
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.horizontalLayout_8.setContentsMargins(0, 0, 0, 0)
        self.displayAxes_checkBox = QCheckBox(self.displayMisc_frame)
        self.displayAxes_checkBox.setObjectName(u"displayAxes_checkBox")

        self.horizontalLayout_8.addWidget(self.displayAxes_checkBox)

        self.displayModelRadius_checkBox = QCheckBox(self.displayMisc_frame)
        self.displayModelRadius_checkBox.setObjectName(u"displayModelRadius_checkBox")

        self.horizontalLayout_8.addWidget(self.displayModelRadius_checkBox)

        self.displayZeroJacobianContours_checkBox = QCheckBox(self.displayMisc_frame)
        self.displayZeroJacobianContours_checkBox.setObjectName(u"displayZeroJacobianContours_checkBox")

        self.horizontalLayout_8.addWidget(self.displayZeroJacobianContours_checkBox)

        self.displaytMisc_horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_8.addItem(self.displaytMisc_horizontalSpacer)


        self.verticalLayout_2.addWidget(self.displayMisc_frame)

        self.displayData_frame = QFrame(DisplaySettings)
        self.displayData_frame.setObjectName(u"displayData_frame")
        self.displayData_frame.setFrameShape(QFrame.NoFrame)
        self.verticalLayout = QVBoxLayout(self.displayData_frame)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.displayDataPoints_frame = QFrame(self.displayData_frame)
        self.displayDataPoints_frame.setObjectName(u"displayDataPoints_frame")
        self.displayDataPoints_frame.setFrameShape(QFrame.NoFrame)
        self.horizontalLayout = QHBoxLayout(self.displayDataPoints_frame)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.displayDataPoints_checkBox = QCheckBox(self.displayDataPoints_frame)
        self.displayDataPoints_checkBox.setObjectName(u"displayDataPoints_checkBox")

        self.horizontalLayout.addWidget(self.displayDataPoints_checkBox)

        self.displayDataProjections_checkBox = QCheckBox(self.displayDataPoints_frame)
        self.displayDataProjections_checkBox.setObjectName(u"displayDataProjections_checkBox")

        self.horizontalLayout.addWidget(self.displayDataProjections_checkBox)

        self.displayDataProjectionTangents_checkBox = QCheckBox(self.displayDataPoints_frame)
        self.displayDataProjectionTangents_checkBox.setObjectName(u"displayDataProjectionTangents_checkBox")

        self.horizontalLayout.addWidget(self.displayDataProjectionTangents_checkBox)

        self.displayDataLines_checkBox = QCheckBox(self.displayDataPoints_frame)
        self.displayDataLines_checkBox.setObjectName(u"displayDataLines_checkBox")

        self.horizontalLayout.addWidget(self.displayDataLines_checkBox)

        self.displayDataEmbedded_checkBox = QCheckBox(self.displayDataPoints_frame)
        self.displayDataEmbedded_checkBox.setObjectName(u"displayDataEmbedded_checkBox")

        self.horizontalLayout.addWidget(self.displayDataEmbedded_checkBox)

        self.displayDataProjectionPoints_checkBox = QCheckBox(self.displayDataPoints_frame)
        self.displayDataProjectionPoints_checkBox.setObjectName(u"displayDataProjectionPoints_checkBox")

        self.horizontalLayout.addWidget(self.displayDataProjectionPoints_checkBox)

        self.displayDataContours_checkBox = QCheckBox(self.displayDataPoints_frame)
        self.displayDataContours_checkBox.setObjectName(u"displayDataContours_checkBox")

        self.horizontalLayout.addWidget(self.displayDataContours_checkBox)

        self.displayDataRadius_checkBox = QCheckBox(self.displayDataPoints_frame)
        self.displayDataRadius_checkBox.setObjectName(u"displayDataRadius_checkBox")

        self.horizontalLayout.addWidget(self.displayDataRadius_checkBox)

        self.displayDataPoints_horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.displayDataPoints_horizontalSpacer)


        self.verticalLayout.addWidget(self.displayDataPoints_frame)

        self.displayDataField_frame = QFrame(self.displayData_frame)
        self.displayDataField_frame.setObjectName(u"displayDataField_frame")
        self.displayDataField_frame.setFrameShape(QFrame.NoFrame)
        self.displayDataField_frame.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_12 = QHBoxLayout(self.displayDataField_frame)
        self.horizontalLayout_12.setObjectName(u"horizontalLayout_12")
        self.horizontalLayout_12.setContentsMargins(0, 0, 0, 0)
        self.displayDataFieldLabels_label = QLabel(self.displayDataField_frame)
        self.displayDataFieldLabels_label.setObjectName(u"displayDataFieldLabels_label")

        self.horizontalLayout_12.addWidget(self.displayDataFieldLabels_label)

        self.displayDataFieldLabelsNone_radioButton = QRadioButton(self.displayDataField_frame)
        self.displayDataFieldLabelsNone_radioButton.setObjectName(u"displayDataFieldLabelsNone_radioButton")

        self.horizontalLayout_12.addWidget(self.displayDataFieldLabelsNone_radioButton)

        self.displayDataFieldLabelsValue_radioButton = QRadioButton(self.displayDataField_frame)
        self.displayDataFieldLabelsValue_radioButton.setObjectName(u"displayDataFieldLabelsValue_radioButton")

        self.horizontalLayout_12.addWidget(self.displayDataFieldLabelsValue_radioButton)

        self.displayDataFieldLabelsDelta_radioButton = QRadioButton(self.displayDataField_frame)
        self.displayDataFieldLabelsDelta_radioButton.setObjectName(u"displayDataFieldLabelsDelta_radioButton")

        self.horizontalLayout_12.addWidget(self.displayDataFieldLabelsDelta_radioButton)

        self.displayDataFieldLabels_horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_12.addItem(self.displayDataFieldLabels_horizontalSpacer)


        self.verticalLayout.addWidget(self.displayDataField_frame)

        self.displayDataMarkers_frame = QFrame(self.displayData_frame)
        self.displayDataMarkers_frame.setObjectName(u"displayDataMarkers_frame")
        self.displayDataMarkers_frame.setFrameShape(QFrame.NoFrame)
        self.horizontalLayout_7 = QHBoxLayout(self.displayDataMarkers_frame)
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.horizontalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.displayDataMarkerPoints_checkBox = QCheckBox(self.displayDataMarkers_frame)
        self.displayDataMarkerPoints_checkBox.setObjectName(u"displayDataMarkerPoints_checkBox")

        self.horizontalLayout_7.addWidget(self.displayDataMarkerPoints_checkBox)

        self.displayDataMarkerNames_checkBox = QCheckBox(self.displayDataMarkers_frame)
        self.displayDataMarkerNames_checkBox.setObjectName(u"displayDataMarkerNames_checkBox")

        self.horizontalLayout_7.addWidget(self.displayDataMarkerNames_checkBox)

        self.displayDataMarkerProjections_checkBox = QCheckBox(self.displayDataMarkers_frame)
        self.displayDataMarkerProjections_checkBox.setObjectName(u"displayDataMarkerProjections_checkBox")

        self.horizontalLayout_7.addWidget(self.displayDataMarkerProjections_checkBox)

        self.displayDataMarkers_horizontalSpacer = QSpacerItem(520, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_7.addItem(self.displayDataMarkers_horizontalSpacer)


        self.verticalLayout.addWidget(self.displayDataMarkers_frame)

        self.displayMarker_frame = QFrame(self.displayData_frame)
        self.displayMarker_frame.setObjectName(u"displayMarker_frame")
        self.displayMarker_frame.setFrameShape(QFrame.NoFrame)
        self.displayMarker_frame.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.displayMarker_frame)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.displayMarkerPoints_checkBox = QCheckBox(self.displayMarker_frame)
        self.displayMarkerPoints_checkBox.setObjectName(u"displayMarkerPoints_checkBox")

        self.horizontalLayout_2.addWidget(self.displayMarkerPoints_checkBox)

        self.displayMarkerNames_checkBox = QCheckBox(self.displayMarker_frame)
        self.displayMarkerNames_checkBox.setObjectName(u"displayMarkerNames_checkBox")

        self.horizontalLayout_2.addWidget(self.displayMarkerNames_checkBox)

        self.displayMarker_horizontalSpacer = QSpacerItem(750, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.displayMarker_horizontalSpacer)


        self.verticalLayout.addWidget(self.displayMarker_frame)


        self.verticalLayout_2.addWidget(self.displayData_frame)

        self.displayNodes_frame = QFrame(DisplaySettings)
        self.displayNodes_frame.setObjectName(u"displayNodes_frame")
        self.displayNodes_frame.setFrameShape(QFrame.NoFrame)
        self.displayNodes_frame.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_6 = QHBoxLayout(self.displayNodes_frame)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.horizontalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.displayNodePoints_checkBox = QCheckBox(self.displayNodes_frame)
        self.displayNodePoints_checkBox.setObjectName(u"displayNodePoints_checkBox")

        self.horizontalLayout_6.addWidget(self.displayNodePoints_checkBox)

        self.displayNodeNumbers_checkBox = QCheckBox(self.displayNodes_frame)
        self.displayNodeNumbers_checkBox.setObjectName(u"displayNodeNumbers_checkBox")
        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.displayNodeNumbers_checkBox.sizePolicy().hasHeightForWidth())
        self.displayNodeNumbers_checkBox.setSizePolicy(sizePolicy)

        self.horizontalLayout_6.addWidget(self.displayNodeNumbers_checkBox)

        self.displayNodeDerivatives_checkBox = QCheckBox(self.displayNodes_frame)
        self.displayNodeDerivatives_checkBox.setObjectName(u"displayNodeDerivatives_checkBox")
        sizePolicy.setHeightForWidth(self.displayNodeDerivatives_checkBox.sizePolicy().hasHeightForWidth())
        self.displayNodeDerivatives_checkBox.setSizePolicy(sizePolicy)
        self.displayNodeDerivatives_checkBox.setTristate(True)

        self.horizontalLayout_6.addWidget(self.displayNodeDerivatives_checkBox)

        self.displayNodeDerivativesVersion_spinBox = QSpinBox(self.displayNodes_frame)
        self.displayNodeDerivativesVersion_spinBox.setObjectName(u"displayNodeDerivativesVersion_spinBox")

        self.horizontalLayout_6.addWidget(self.displayNodeDerivativesVersion_spinBox)

        self.displayNodes_horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_6.addItem(self.displayNodes_horizontalSpacer)


        self.verticalLayout_2.addWidget(self.displayNodes_frame)

        self.displayNodeDerivativeLabels_frame = QFrame(DisplaySettings)
        self.displayNodeDerivativeLabels_frame.setObjectName(u"displayNodeDerivativeLabels_frame")
        self.displayNodeDerivativeLabels_frame.setFrameShape(QFrame.NoFrame)
        self.gridLayout = QGridLayout(self.displayNodeDerivativeLabels_frame)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.displayNodeDerivativeLabels_horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout.addItem(self.displayNodeDerivativeLabels_horizontalSpacer, 0, 0, 1, 1)

        self.displayNodeDerivativeLabelsD1_checkBox = QCheckBox(self.displayNodeDerivativeLabels_frame)
        self.displayNodeDerivativeLabelsD1_checkBox.setObjectName(u"displayNodeDerivativeLabelsD1_checkBox")
        sizePolicy.setHeightForWidth(self.displayNodeDerivativeLabelsD1_checkBox.sizePolicy().hasHeightForWidth())
        self.displayNodeDerivativeLabelsD1_checkBox.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.displayNodeDerivativeLabelsD1_checkBox, 0, 1, 1, 1)

        self.displayNodeDerivativeLabelsD2_checkBox = QCheckBox(self.displayNodeDerivativeLabels_frame)
        self.displayNodeDerivativeLabelsD2_checkBox.setObjectName(u"displayNodeDerivativeLabelsD2_checkBox")
        sizePolicy.setHeightForWidth(self.displayNodeDerivativeLabelsD2_checkBox.sizePolicy().hasHeightForWidth())
        self.displayNodeDerivativeLabelsD2_checkBox.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.displayNodeDerivativeLabelsD2_checkBox, 0, 2, 1, 1)

        self.displayNodeDerivativeLabelsD3_checkBox = QCheckBox(self.displayNodeDerivativeLabels_frame)
        self.displayNodeDerivativeLabelsD3_checkBox.setObjectName(u"displayNodeDerivativeLabelsD3_checkBox")
        sizePolicy.setHeightForWidth(self.displayNodeDerivativeLabelsD3_checkBox.sizePolicy().hasHeightForWidth())
        self.displayNodeDerivativeLabelsD3_checkBox.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.displayNodeDerivativeLabelsD3_checkBox, 0, 3, 1, 1)

        self.displayNodeDerivativeLabelsD12_checkBox = QCheckBox(self.displayNodeDerivativeLabels_frame)
        self.displayNodeDerivativeLabelsD12_checkBox.setObjectName(u"displayNodeDerivativeLabelsD12_checkBox")
        sizePolicy.setHeightForWidth(self.displayNodeDerivativeLabelsD12_checkBox.sizePolicy().hasHeightForWidth())
        self.displayNodeDerivativeLabelsD12_checkBox.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.displayNodeDerivativeLabelsD12_checkBox, 0, 4, 1, 1)

        self.displayNodeDerivativeLabelsD13_checkBox = QCheckBox(self.displayNodeDerivativeLabels_frame)
        self.displayNodeDerivativeLabelsD13_checkBox.setObjectName(u"displayNodeDerivativeLabelsD13_checkBox")
        sizePolicy.setHeightForWidth(self.displayNodeDerivativeLabelsD13_checkBox.sizePolicy().hasHeightForWidth())
        self.displayNodeDerivativeLabelsD13_checkBox.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.displayNodeDerivativeLabelsD13_checkBox, 0, 5, 1, 1)

        self.displayNodeDerivativeLabelsD23_checkBox = QCheckBox(self.displayNodeDerivativeLabels_frame)
        self.displayNodeDerivativeLabelsD23_checkBox.setObjectName(u"displayNodeDerivativeLabelsD23_checkBox")
        sizePolicy.setHeightForWidth(self.displayNodeDerivativeLabelsD23_checkBox.sizePolicy().hasHeightForWidth())
        self.displayNodeDerivativeLabelsD23_checkBox.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.displayNodeDerivativeLabelsD23_checkBox, 0, 6, 1, 1)

        self.displayNodeDerivativeLabelsD123_checkBox = QCheckBox(self.displayNodeDerivativeLabels_frame)
        self.displayNodeDerivativeLabelsD123_checkBox.setObjectName(u"displayNodeDerivativeLabelsD123_checkBox")
        sizePolicy.setHeightForWidth(self.displayNodeDerivativeLabelsD123_checkBox.sizePolicy().hasHeightForWidth())
        self.displayNodeDerivativeLabelsD123_checkBox.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.displayNodeDerivativeLabelsD123_checkBox, 0, 7, 1, 1)


        self.verticalLayout_2.addWidget(self.displayNodeDerivativeLabels_frame)

        self.displayElements_frame = QFrame(DisplaySettings)
        self.displayElements_frame.setObjectName(u"displayElements_frame")
        self.displayElements_frame.setFrameShape(QFrame.NoFrame)
        self.displayElements_frame.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_4 = QHBoxLayout(self.displayElements_frame)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.displayElementNumbers_checkBox = QCheckBox(self.displayElements_frame)
        self.displayElementNumbers_checkBox.setObjectName(u"displayElementNumbers_checkBox")

        self.horizontalLayout_4.addWidget(self.displayElementNumbers_checkBox)

        self.displayElementFieldPoints_checkBox = QCheckBox(self.displayElements_frame)
        self.displayElementFieldPoints_checkBox.setObjectName(u"displayElementFieldPoints_checkBox")

        self.horizontalLayout_4.addWidget(self.displayElementFieldPoints_checkBox)

        self.displayElementAxes_checkBox = QCheckBox(self.displayElements_frame)
        self.displayElementAxes_checkBox.setObjectName(u"displayElementAxes_checkBox")
        sizePolicy.setHeightForWidth(self.displayElementAxes_checkBox.sizePolicy().hasHeightForWidth())
        self.displayElementAxes_checkBox.setSizePolicy(sizePolicy)

        self.horizontalLayout_4.addWidget(self.displayElementAxes_checkBox)

        self.displayElements_horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_4.addItem(self.displayElements_horizontalSpacer)


        self.verticalLayout_2.addWidget(self.displayElements_frame)

        self.displayLines_frame = QFrame(DisplaySettings)
        self.displayLines_frame.setObjectName(u"displayLines_frame")
        self.displayLines_frame.setFrameShape(QFrame.NoFrame)
        self.displayLines_frame.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_5 = QHBoxLayout(self.displayLines_frame)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.displayLines_checkBox = QCheckBox(self.displayLines_frame)
        self.displayLines_checkBox.setObjectName(u"displayLines_checkBox")

        self.horizontalLayout_5.addWidget(self.displayLines_checkBox)

        self.displayLinesExterior_checkBox = QCheckBox(self.displayLines_frame)
        self.displayLinesExterior_checkBox.setObjectName(u"displayLinesExterior_checkBox")
        sizePolicy.setHeightForWidth(self.displayLinesExterior_checkBox.sizePolicy().hasHeightForWidth())
        self.displayLinesExterior_checkBox.setSizePolicy(sizePolicy)

        self.horizontalLayout_5.addWidget(self.displayLinesExterior_checkBox)

        self.displayLines_horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_5.addItem(self.displayLines_horizontalSpacer)


        self.verticalLayout_2.addWidget(self.displayLines_frame)

        self.displaySurfaces_frame = QFrame(DisplaySettings)
        self.displaySurfaces_frame.setObjectName(u"displaySurfaces_frame")
        self.displaySurfaces_frame.setFrameShape(QFrame.NoFrame)
        self.displaySurfaces_frame.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_3 = QHBoxLayout(self.displaySurfaces_frame)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.displaySurfaces_checkBox = QCheckBox(self.displaySurfaces_frame)
        self.displaySurfaces_checkBox.setObjectName(u"displaySurfaces_checkBox")

        self.horizontalLayout_3.addWidget(self.displaySurfaces_checkBox)

        self.displaySurfacesExterior_checkBox = QCheckBox(self.displaySurfaces_frame)
        self.displaySurfacesExterior_checkBox.setObjectName(u"displaySurfacesExterior_checkBox")
        sizePolicy.setHeightForWidth(self.displaySurfacesExterior_checkBox.sizePolicy().hasHeightForWidth())
        self.displaySurfacesExterior_checkBox.setSizePolicy(sizePolicy)

        self.horizontalLayout_3.addWidget(self.displaySurfacesExterior_checkBox)

        self.displaySurfacesTranslucent_checkBox = QCheckBox(self.displaySurfaces_frame)
        self.displaySurfacesTranslucent_checkBox.setObjectName(u"displaySurfacesTranslucent_checkBox")
        sizePolicy.setHeightForWidth(self.displaySurfacesTranslucent_checkBox.sizePolicy().hasHeightForWidth())
        self.displaySurfacesTranslucent_checkBox.setSizePolicy(sizePolicy)

        self.horizontalLayout_3.addWidget(self.displaySurfacesTranslucent_checkBox)

        self.displaySurfacesWireframe_checkBox = QCheckBox(self.displaySurfaces_frame)
        self.displaySurfacesWireframe_checkBox.setObjectName(u"displaySurfacesWireframe_checkBox")
        sizePolicy.setHeightForWidth(self.displaySurfacesWireframe_checkBox.sizePolicy().hasHeightForWidth())
        self.displaySurfacesWireframe_checkBox.setSizePolicy(sizePolicy)

        self.horizontalLayout_3.addWidget(self.displaySurfacesWireframe_checkBox)

        self.displaySurfaces_horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_3.addItem(self.displaySurfaces_horizontalSpacer)


        self.verticalLayout_2.addWidget(self.displaySurfaces_frame)

        self.displayModelCoordinates_frame = QFrame(DisplaySettings)
        self.displayModelCoordinates_frame.setObjectName(u"displayModelCoordinates_frame")
        self.displayModelCoordinates_frame.setFrameShape(QFrame.NoFrame)
        self.formLayout_3 = QFormLayout(self.displayModelCoordinates_frame)
        self.formLayout_3.setObjectName(u"formLayout_3")
        self.formLayout_3.setFieldGrowthPolicy(QFormLayout.FieldsStayAtSizeHint)
        self.formLayout_3.setContentsMargins(0, 0, 0, 0)
        self.displayModelCoordinates_label = QLabel(self.displayModelCoordinates_frame)
        self.displayModelCoordinates_label.setObjectName(u"displayModelCoordinates_label")

        self.formLayout_3.setWidget(0, QFormLayout.LabelRole, self.displayModelCoordinates_label)

        self.displayModelCoordinates_fieldChooser = FieldChooserWidget(self.displayModelCoordinates_frame)
        self.displayModelCoordinates_fieldChooser.setObjectName(u"displayModelCoordinates_fieldChooser")

        self.formLayout_3.setWidget(0, QFormLayout.FieldRole, self.displayModelCoordinates_fieldChooser)


        self.verticalLayout_2.addWidget(self.displayModelCoordinates_frame)

        self.displayGroup_frame = QFrame(DisplaySettings)
        self.displayGroup_frame.setObjectName(u"displayGroup_frame")
        self.displayGroup_frame.setFrameShape(QFrame.NoFrame)
        self.displayGroup_frame.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_9 = QHBoxLayout(self.displayGroup_frame)
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.horizontalLayout_9.setContentsMargins(0, 0, 0, 0)
        self.displayGroup_label = QLabel(self.displayGroup_frame)
        self.displayGroup_label.setObjectName(u"displayGroup_label")

        self.horizontalLayout_9.addWidget(self.displayGroup_label)

        self.displayGroup_fieldChooser = FieldChooserWidget(self.displayGroup_frame)
        self.displayGroup_fieldChooser.setObjectName(u"displayGroup_fieldChooser")
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.displayGroup_fieldChooser.sizePolicy().hasHeightForWidth())
        self.displayGroup_fieldChooser.setSizePolicy(sizePolicy1)
        self.displayGroup_fieldChooser.setMinimumSize(QSize(0, 0))
        self.displayGroup_fieldChooser.setMaximumSize(QSize(500, 16777215))

        self.horizontalLayout_9.addWidget(self.displayGroup_fieldChooser)


        self.verticalLayout_2.addWidget(self.displayGroup_frame)

        self.displayField_frame = QFrame(DisplaySettings)
        self.displayField_frame.setObjectName(u"displayField_frame")
        self.displayField_frame.setFrameShape(QFrame.NoFrame)
        self.displayField_frame.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_11 = QHBoxLayout(self.displayField_frame)
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.horizontalLayout_11.setContentsMargins(0, 0, 0, 0)
        self.displayFieldColourBar_checkBox = QCheckBox(self.displayField_frame)
        self.displayFieldColourBar_checkBox.setObjectName(u"displayFieldColourBar_checkBox")

        self.horizontalLayout_11.addWidget(self.displayFieldColourBar_checkBox)

        self.displayFieldContours_checkBox = QCheckBox(self.displayField_frame)
        self.displayFieldContours_checkBox.setObjectName(u"displayFieldContours_checkBox")

        self.horizontalLayout_11.addWidget(self.displayFieldContours_checkBox)

        self.displayFieldContoursCount_spinBox = QSpinBox(self.displayField_frame)
        self.displayFieldContoursCount_spinBox.setObjectName(u"displayFieldContoursCount_spinBox")
        self.displayFieldContoursCount_spinBox.setMinimum(1)
        self.displayFieldContoursCount_spinBox.setMaximum(100)

        self.horizontalLayout_11.addWidget(self.displayFieldContoursCount_spinBox)

        self.displayFieldContours_horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_11.addItem(self.displayFieldContours_horizontalSpacer)


        self.verticalLayout_2.addWidget(self.displayField_frame)

        self.displayTime_frame = QFrame(DisplaySettings)
        self.displayTime_frame.setObjectName(u"displayTime_frame")
        self.displayTime_frame.setFrameShape(QFrame.NoFrame)
        self.displayTime_frame.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_13 = QHBoxLayout(self.displayTime_frame)
        self.horizontalLayout_13.setObjectName(u"horizontalLayout_13")
        self.horizontalLayout_13.setContentsMargins(0, 0, 0, 0)
        self.displayTime_label = QLabel(self.displayTime_frame)
        self.displayTime_label.setObjectName(u"displayTime_label")

        self.horizontalLayout_13.addWidget(self.displayTime_label)

        self.displayTime_lineEdit = QLineEdit(self.displayTime_frame)
        self.displayTime_lineEdit.setObjectName(u"displayTime_lineEdit")
        sizePolicy2 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy2.setHorizontalStretch(1)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.displayTime_lineEdit.sizePolicy().hasHeightForWidth())
        self.displayTime_lineEdit.setSizePolicy(sizePolicy2)

        self.horizontalLayout_13.addWidget(self.displayTime_lineEdit)

        self.displayTime_horizontalSlider = QSlider(self.displayTime_frame)
        self.displayTime_horizontalSlider.setObjectName(u"displayTime_horizontalSlider")
        sizePolicy3 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy3.setHorizontalStretch(3)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.displayTime_horizontalSlider.sizePolicy().hasHeightForWidth())
        self.displayTime_horizontalSlider.setSizePolicy(sizePolicy3)
        self.displayTime_horizontalSlider.setOrientation(Qt.Horizontal)
        self.displayTime_horizontalSlider.setTickPosition(QSlider.NoTicks)

        self.horizontalLayout_13.addWidget(self.displayTime_horizontalSlider)


        self.verticalLayout_2.addWidget(self.displayTime_frame)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer)


        self.retranslateUi(DisplaySettings)

        QMetaObject.connectSlotsByName(DisplaySettings)
    # setupUi

    def retranslateUi(self, DisplaySettings):
        DisplaySettings.setWindowTitle(QCoreApplication.translate("DisplaySettings", u"Display Settings", None))
        self.displayAxes_checkBox.setText(QCoreApplication.translate("DisplaySettings", u"Axes", None))
        self.displayModelRadius_checkBox.setText(QCoreApplication.translate("DisplaySettings", u"Model radius", None))
        self.displayZeroJacobianContours_checkBox.setText(QCoreApplication.translate("DisplaySettings", u"Zero Jacobian contours", None))
        self.displayDataPoints_checkBox.setText(QCoreApplication.translate("DisplaySettings", u"Data points", None))
        self.displayDataProjections_checkBox.setText(QCoreApplication.translate("DisplaySettings", u"Data projections", None))
        self.displayDataProjectionTangents_checkBox.setText(QCoreApplication.translate("DisplaySettings", u"Data projection tangents", None))
        self.displayDataLines_checkBox.setText(QCoreApplication.translate("DisplaySettings", u"Data lines", None))
#if QT_CONFIG(tooltip)
        self.displayDataEmbedded_checkBox.setToolTip(QCoreApplication.translate("DisplaySettings", u"<html><head/><body><p>Show data embedded in model coordinates.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.displayDataEmbedded_checkBox.setText(QCoreApplication.translate("DisplaySettings", u"Data embedded", None))
        self.displayDataProjectionPoints_checkBox.setText(QCoreApplication.translate("DisplaySettings", u"Data projection points", None))
        self.displayDataContours_checkBox.setText(QCoreApplication.translate("DisplaySettings", u"Data contours", None))
        self.displayDataRadius_checkBox.setText(QCoreApplication.translate("DisplaySettings", u"Data radius", None))
        self.displayDataFieldLabels_label.setText(QCoreApplication.translate("DisplaySettings", u"Data field label:", None))
        self.displayDataFieldLabelsNone_radioButton.setText(QCoreApplication.translate("DisplaySettings", u"None", None))
        self.displayDataFieldLabelsValue_radioButton.setText(QCoreApplication.translate("DisplaySettings", u"Value", None))
        self.displayDataFieldLabelsDelta_radioButton.setText(QCoreApplication.translate("DisplaySettings", u"Delta", None))
        self.displayDataMarkerPoints_checkBox.setText(QCoreApplication.translate("DisplaySettings", u"Marker data points", None))
        self.displayDataMarkerNames_checkBox.setText(QCoreApplication.translate("DisplaySettings", u"Marker data names", None))
        self.displayDataMarkerProjections_checkBox.setText(QCoreApplication.translate("DisplaySettings", u"Marker data projections", None))
        self.displayMarkerPoints_checkBox.setText(QCoreApplication.translate("DisplaySettings", u"Marker points", None))
        self.displayMarkerNames_checkBox.setText(QCoreApplication.translate("DisplaySettings", u"Marker names", None))
        self.displayNodePoints_checkBox.setText(QCoreApplication.translate("DisplaySettings", u"Node points", None))
        self.displayNodeNumbers_checkBox.setText(QCoreApplication.translate("DisplaySettings", u"Node numbers", None))
#if QT_CONFIG(tooltip)
        self.displayNodeDerivatives_checkBox.setToolTip(QCoreApplication.translate("DisplaySettings", u"<html><head/><body><p>Show node derivatives on:<br/>[ ] None<br/>[-] Selected nodes<br/>[/] All nodes</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.displayNodeDerivatives_checkBox.setText(QCoreApplication.translate("DisplaySettings", u"Node derivatives", None))
#if QT_CONFIG(tooltip)
        self.displayNodeDerivativesVersion_spinBox.setToolTip(QCoreApplication.translate("DisplaySettings", u"<html><head/><body><p>Show specified node derivative version, or 0 to show all versions.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.displayNodeDerivativeLabelsD1_checkBox.setText(QCoreApplication.translate("DisplaySettings", u"D1", None))
        self.displayNodeDerivativeLabelsD2_checkBox.setText(QCoreApplication.translate("DisplaySettings", u"D2", None))
        self.displayNodeDerivativeLabelsD3_checkBox.setText(QCoreApplication.translate("DisplaySettings", u"D3", None))
        self.displayNodeDerivativeLabelsD12_checkBox.setText(QCoreApplication.translate("DisplaySettings", u"D12", None))
        self.displayNodeDerivativeLabelsD13_checkBox.setText(QCoreApplication.translate("DisplaySettings", u"D13", None))
        self.displayNodeDerivativeLabelsD23_checkBox.setText(QCoreApplication.translate("DisplaySettings", u"D23", None))
        self.displayNodeDerivativeLabelsD123_checkBox.setText(QCoreApplication.translate("DisplaySettings", u"D123", None))
        self.displayElementNumbers_checkBox.setText(QCoreApplication.translate("DisplaySettings", u"Element numbers", None))
        self.displayElementFieldPoints_checkBox.setText(QCoreApplication.translate("DisplaySettings", u"Element field points", None))
        self.displayElementAxes_checkBox.setText(QCoreApplication.translate("DisplaySettings", u"Element axes", None))
        self.displayLines_checkBox.setText(QCoreApplication.translate("DisplaySettings", u"Lines", None))
        self.displayLinesExterior_checkBox.setText(QCoreApplication.translate("DisplaySettings", u"Exterior", None))
        self.displaySurfaces_checkBox.setText(QCoreApplication.translate("DisplaySettings", u"Surfaces", None))
        self.displaySurfacesExterior_checkBox.setText(QCoreApplication.translate("DisplaySettings", u"Exterior", None))
        self.displaySurfacesTranslucent_checkBox.setText(QCoreApplication.translate("DisplaySettings", u"Transluc.", None))
        self.displaySurfacesWireframe_checkBox.setText(QCoreApplication.translate("DisplaySettings", u"Wireframe", None))
        self.displayModelCoordinates_label.setText(QCoreApplication.translate("DisplaySettings", u"Model coordinates:", None))
        self.displayGroup_label.setText(QCoreApplication.translate("DisplaySettings", u"Group:", None))
#if QT_CONFIG(tooltip)
        self.displayGroup_fieldChooser.setToolTip(QCoreApplication.translate("DisplaySettings", u"<html><head/><body><p>Optional group to limit display of model and data to.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.displayFieldColourBar_checkBox.setText(QCoreApplication.translate("DisplaySettings", u"Field colour bar", None))
        self.displayFieldContours_checkBox.setText(QCoreApplication.translate("DisplaySettings", u"Field contours:", None))
        self.displayTime_label.setText(QCoreApplication.translate("DisplaySettings", u"Time:", None))
    # retranslateUi

