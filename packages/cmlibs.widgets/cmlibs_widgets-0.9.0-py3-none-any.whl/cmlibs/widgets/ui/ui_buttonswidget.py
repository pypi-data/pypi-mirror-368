# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'buttonswidget.ui'
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QPushButton, QSizePolicy,
    QSpacerItem, QWidget)

class Ui_Buttons(object):
    def setupUi(self, Buttons):
        if not Buttons.objectName():
            Buttons.setObjectName(u"Buttons")
        Buttons.resize(550, 59)
        self.horizontalLayout = QHBoxLayout(Buttons)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.pushButtonDocumentation = QPushButton(Buttons)
        self.pushButtonDocumentation.setObjectName(u"pushButtonDocumentation")

        self.horizontalLayout.addWidget(self.pushButtonDocumentation)

        self.horizontalSpacer_2 = QSpacerItem(28, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_2)

        self.viewAll_pushButton = QPushButton(Buttons)
        self.viewAll_pushButton.setObjectName(u"viewAll_pushButton")

        self.horizontalLayout.addWidget(self.viewAll_pushButton)

        self.stdViews_pushButton = QPushButton(Buttons)
        self.stdViews_pushButton.setObjectName(u"stdViews_pushButton")

        self.horizontalLayout.addWidget(self.stdViews_pushButton)

        self.horizontalSpacer_9 = QSpacerItem(29, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_9)

        self.done_pushButton = QPushButton(Buttons)
        self.done_pushButton.setObjectName(u"done_pushButton")
        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.done_pushButton.sizePolicy().hasHeightForWidth())
        self.done_pushButton.setSizePolicy(sizePolicy)

        self.horizontalLayout.addWidget(self.done_pushButton)


        self.retranslateUi(Buttons)

        QMetaObject.connectSlotsByName(Buttons)
    # setupUi

    def retranslateUi(self, Buttons):
        Buttons.setWindowTitle(QCoreApplication.translate("Buttons", u"Buttons", None))
        self.pushButtonDocumentation.setText(QCoreApplication.translate("Buttons", u"Online Documentation", None))
        self.viewAll_pushButton.setText(QCoreApplication.translate("Buttons", u"View All", None))
        self.stdViews_pushButton.setText(QCoreApplication.translate("Buttons", u"Std. Views", None))
        self.done_pushButton.setText(QCoreApplication.translate("Buttons", u"Done", None))
    # retranslateUi

