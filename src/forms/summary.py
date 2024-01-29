# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './designer/summary.ui'
#
# Created by: PyQt5 UI code generator 5.15.7
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from aqt.qt import QtCore, QtGui, QtWidgets


class Ui_Summary(object):
    def setupUi(self, Summary):
        Summary.setObjectName("Summary")
        Summary.resize(372, 289)
        self.gridLayout = QGridLayout(Summary)
        self.gridLayout.setObjectName("gridLayout")
        spacerItem = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.gridLayout.addItem(spacerItem, 5, 0, 1, 1)
        self.label_5 = QLabel(Summary)
        font = QFont()
        font.setPointSize(11)
        self.label_5.setFont(font)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 3, 0, 1, 1)
        self.label = QLabel(Summary)
        font = QFont()
        font.setPointSize(11)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)
        self.buttonBox = QDialogButtonBox(Summary)
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 6, 0, 1, 1)
        self.accuracyLabel = QLabel(Summary)
        font = QFont()
        font.setPointSize(11)
        self.accuracyLabel.setFont(font)
        self.accuracyLabel.setObjectName("accuracyLabel")
        self.gridLayout.addWidget(self.accuracyLabel, 2, 1, 1, 1)
        self.correctLabel = QLabel(Summary)
        font = QFont()
        font.setPointSize(11)
        self.correctLabel.setFont(font)
        self.correctLabel.setObjectName("correctLabel")
        self.gridLayout.addWidget(self.correctLabel, 1, 1, 1, 1)
        self.label_3 = QLabel(Summary)
        font = QFont()
        font.setPointSize(11)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        self.cardsLabel = QLabel(Summary)
        font = QFont()
        font.setPointSize(11)
        self.cardsLabel.setFont(font)
        self.cardsLabel.setObjectName("cardsLabel")
        self.gridLayout.addWidget(self.cardsLabel, 3, 1, 1, 1)
        self.label_7 = QLabel(Summary)
        font = QFont()
        font.setPointSize(11)
        self.label_7.setFont(font)
        self.label_7.setObjectName("label_7")
        self.gridLayout.addWidget(self.label_7, 4, 0, 1, 1)
        self.timeLabel = QLabel(Summary)
        font = QFont()
        font.setPointSize(11)
        self.timeLabel.setFont(font)
        self.timeLabel.setObjectName("timeLabel")
        self.gridLayout.addWidget(self.timeLabel, 4, 1, 1, 1)
        spacerItem1 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.gridLayout.addItem(spacerItem1, 0, 0, 1, 1)

        self.retranslateUi(Summary)
        self.buttonBox.accepted.connect(Summary.accept) # type: ignore
        self.buttonBox.rejected.connect(Summary.reject) # type: ignore
        QMetaObject.connectSlotsByName(Summary)

    def retranslateUi(self, Summary):
        _translate = QCoreApplication.translate
        Summary.setWindowTitle(_translate("Summary", "Dialog"))
        self.label_5.setText(_translate("Summary", "Cards Visited"))
        self.label.setText(_translate("Summary", "Questions Correct"))
        self.accuracyLabel.setText(_translate("Summary", "-- %"))
        self.correctLabel.setText(_translate("Summary", "-/-"))
        self.label_3.setText(_translate("Summary", "Accuracy"))
        self.cardsLabel.setText(_translate("Summary", "--"))
        self.label_7.setText(_translate("Summary", "Time Spent"))
        self.timeLabel.setText(_translate("Summary", "--:--:--"))
