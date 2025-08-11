# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'logviewerwidget.ui'
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
from PySide6.QtWidgets import (QApplication, QGridLayout, QHBoxLayout, QPushButton,
    QSizePolicy, QSpacerItem, QTextBrowser, QWidget)

class Ui_LogViewerWidget(object):
    def setupUi(self, LogViewerWidget):
        if not LogViewerWidget.objectName():
            LogViewerWidget.setObjectName(u"LogViewerWidget")
        LogViewerWidget.resize(452, 533)
        self.gridLayout = QGridLayout(LogViewerWidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.logText = QTextBrowser(LogViewerWidget)
        self.logText.setObjectName(u"logText")

        self.gridLayout.addWidget(self.logText, 1, 0, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.clearAllButton = QPushButton(LogViewerWidget)
        self.clearAllButton.setObjectName(u"clearAllButton")

        self.horizontalLayout.addWidget(self.clearAllButton)

        self.copyButton = QPushButton(LogViewerWidget)
        self.copyButton.setObjectName(u"copyButton")

        self.horizontalLayout.addWidget(self.copyButton)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)


        self.retranslateUi(LogViewerWidget)
        self.clearAllButton.clicked.connect(LogViewerWidget.clearAll)
        self.copyButton.clicked.connect(LogViewerWidget.copyToClipboard)

        QMetaObject.connectSlotsByName(LogViewerWidget)
    # setupUi

    def retranslateUi(self, LogViewerWidget):
        LogViewerWidget.setWindowTitle(QCoreApplication.translate("LogViewerWidget", u"Log Viewer", None))
        self.clearAllButton.setText(QCoreApplication.translate("LogViewerWidget", u"Clear All", None))
        self.copyButton.setText(QCoreApplication.translate("LogViewerWidget", u"Copy To Clipboard", None))
    # retranslateUi

