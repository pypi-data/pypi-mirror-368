# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'groupeditorwidget.ui'
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QComboBox, QGridLayout,
    QHBoxLayout, QHeaderView, QLabel, QPushButton,
    QSizePolicy, QSpacerItem, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget)

class Ui_GroupEditorWidget(object):
    def setupUi(self, GroupEditorWidget):
        if not GroupEditorWidget.objectName():
            GroupEditorWidget.setObjectName(u"GroupEditorWidget")
        GroupEditorWidget.resize(600, 400)
        self.verticalLayout = QVBoxLayout(GroupEditorWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.groupTableWidget = QTableWidget(GroupEditorWidget)
        if (self.groupTableWidget.columnCount() < 4):
            self.groupTableWidget.setColumnCount(4)
        __qtablewidgetitem = QTableWidgetItem()
        self.groupTableWidget.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.groupTableWidget.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.groupTableWidget.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.groupTableWidget.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        self.groupTableWidget.setObjectName(u"groupTableWidget")
        self.groupTableWidget.setFocusPolicy(Qt.NoFocus)
        self.groupTableWidget.setAlternatingRowColors(True)
        self.groupTableWidget.setSelectionMode(QAbstractItemView.NoSelection)
        self.groupTableWidget.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.groupTableWidget.setShowGrid(False)
        self.groupTableWidget.setRowCount(0)
        self.groupTableWidget.setColumnCount(4)
        self.groupTableWidget.horizontalHeader().setVisible(True)
        self.groupTableWidget.horizontalHeader().setCascadingSectionResizes(False)
        self.groupTableWidget.horizontalHeader().setHighlightSections(True)
        self.groupTableWidget.verticalHeader().setVisible(False)

        self.gridLayout.addWidget(self.groupTableWidget, 4, 0, 1, 1)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label = QLabel(GroupEditorWidget)
        self.label.setObjectName(u"label")

        self.horizontalLayout_2.addWidget(self.label)

        self.dimensionComboBox = QComboBox(GroupEditorWidget)
        self.dimensionComboBox.setObjectName(u"dimensionComboBox")

        self.horizontalLayout_2.addWidget(self.dimensionComboBox)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)


        self.gridLayout.addLayout(self.horizontalLayout_2, 2, 0, 1, 1)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_2 = QLabel(GroupEditorWidget)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout_3.addWidget(self.label_2)

        self.currentGroupLabel = QLabel(GroupEditorWidget)
        self.currentGroupLabel.setObjectName(u"currentGroupLabel")

        self.horizontalLayout_3.addWidget(self.currentGroupLabel)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_3)


        self.gridLayout.addLayout(self.horizontalLayout_3, 1, 0, 1, 1)


        self.verticalLayout.addLayout(self.gridLayout)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.clearPushButton = QPushButton(GroupEditorWidget)
        self.clearPushButton.setObjectName(u"clearPushButton")

        self.horizontalLayout.addWidget(self.clearPushButton)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.applyPushButton = QPushButton(GroupEditorWidget)
        self.applyPushButton.setObjectName(u"applyPushButton")

        self.horizontalLayout.addWidget(self.applyPushButton)

        self.closePushButton = QPushButton(GroupEditorWidget)
        self.closePushButton.setObjectName(u"closePushButton")

        self.horizontalLayout.addWidget(self.closePushButton)


        self.verticalLayout.addLayout(self.horizontalLayout)


        self.retranslateUi(GroupEditorWidget)

        QMetaObject.connectSlotsByName(GroupEditorWidget)
    # setupUi

    def retranslateUi(self, GroupEditorWidget):
        GroupEditorWidget.setWindowTitle(QCoreApplication.translate("GroupEditorWidget", u"Group Editor Widget", None))
#if QT_CONFIG(whatsthis)
        GroupEditorWidget.setWhatsThis("")
#endif // QT_CONFIG(whatsthis)
        ___qtablewidgetitem = self.groupTableWidget.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("GroupEditorWidget", u"Group", None));
        ___qtablewidgetitem1 = self.groupTableWidget.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("GroupEditorWidget", u"Face-Type", None));
        ___qtablewidgetitem2 = self.groupTableWidget.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("GroupEditorWidget", u"Operation", None));
        ___qtablewidgetitem3 = self.groupTableWidget.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("GroupEditorWidget", u"Complement", None));
        self.label.setText(QCoreApplication.translate("GroupEditorWidget", u"Dimension of Operations:", None))
        self.label_2.setText(QCoreApplication.translate("GroupEditorWidget", u"Managing Group: ", None))
        self.currentGroupLabel.setText("")
        self.clearPushButton.setText(QCoreApplication.translate("GroupEditorWidget", u"Clear", None))
        self.applyPushButton.setText(QCoreApplication.translate("GroupEditorWidget", u"Apply", None))
        self.closePushButton.setText(QCoreApplication.translate("GroupEditorWidget", u"Close", None))
    # retranslateUi

