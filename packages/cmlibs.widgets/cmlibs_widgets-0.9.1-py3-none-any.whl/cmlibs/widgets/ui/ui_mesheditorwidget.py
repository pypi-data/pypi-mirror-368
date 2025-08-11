# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mesheditorwidget.ui'
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
from PySide6.QtWidgets import (QApplication, QFormLayout, QGroupBox, QSizePolicy,
    QSpacerItem, QToolButton, QVBoxLayout, QWidget)

class Ui_MeshEditorWidget(object):
    def setupUi(self, MeshEditorWidget):
        if not MeshEditorWidget.objectName():
            MeshEditorWidget.setObjectName(u"MeshEditorWidget")
        MeshEditorWidget.resize(300, 725)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MeshEditorWidget.sizePolicy().hasHeightForWidth())
        MeshEditorWidget.setSizePolicy(sizePolicy)
        self.verticalLayout = QVBoxLayout(MeshEditorWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBoxEditMode = QGroupBox(MeshEditorWidget)
        self.groupBoxEditMode.setObjectName(u"groupBoxEditMode")
        self.formLayout = QFormLayout(self.groupBoxEditMode)
        self.formLayout.setObjectName(u"formLayout")
        self.toolButtonNone = QToolButton(self.groupBoxEditMode)
        self.toolButtonNone.setObjectName(u"toolButtonNone")
        self.toolButtonNone.setCheckable(True)
        self.toolButtonNone.setChecked(True)

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.toolButtonNone)

        self.toolButtonNodes = QToolButton(self.groupBoxEditMode)
        self.toolButtonNodes.setObjectName(u"toolButtonNodes")
        self.toolButtonNodes.setCheckable(True)

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.toolButtonNodes)


        self.verticalLayout.addWidget(self.groupBoxEditMode)

        self.verticalSpacer = QSpacerItem(20, 624, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)


        self.retranslateUi(MeshEditorWidget)

        QMetaObject.connectSlotsByName(MeshEditorWidget)
    # setupUi

    def retranslateUi(self, MeshEditorWidget):
        MeshEditorWidget.setWindowTitle(QCoreApplication.translate("MeshEditorWidget", u"Mesh Editor", None))
        self.groupBoxEditMode.setTitle(QCoreApplication.translate("MeshEditorWidget", u"EditMode", None))
        self.toolButtonNone.setText(QCoreApplication.translate("MeshEditorWidget", u"...", None))
        self.toolButtonNodes.setText(QCoreApplication.translate("MeshEditorWidget", u"...", None))
    # retranslateUi

