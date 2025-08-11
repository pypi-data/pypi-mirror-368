# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'regioneditorwidget.ui'
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
from PySide6.QtWidgets import (QApplication, QHeaderView, QSizePolicy, QTreeView,
    QVBoxLayout, QWidget)

class Ui_RegionEditorWidget(object):
    def setupUi(self, RegionEditorWidget):
        if not RegionEditorWidget.objectName():
            RegionEditorWidget.setObjectName(u"RegionEditorWidget")
        RegionEditorWidget.resize(400, 300)
        self.verticalLayout = QVBoxLayout(RegionEditorWidget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.treeViewRegion = QTreeView(RegionEditorWidget)
        self.treeViewRegion.setObjectName(u"treeViewRegion")

        self.verticalLayout.addWidget(self.treeViewRegion)


        self.retranslateUi(RegionEditorWidget)

        QMetaObject.connectSlotsByName(RegionEditorWidget)
    # setupUi

    def retranslateUi(self, RegionEditorWidget):
        RegionEditorWidget.setWindowTitle(QCoreApplication.translate("RegionEditorWidget", u"Region Editor", None))
    # retranslateUi

