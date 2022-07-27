# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'field_options.ui'
#
# Created by: PyQt5 UI code generator 5.15.7
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_FieldOptions(object):
    def setupUi(self, FieldOptions):
        FieldOptions.setObjectName("FieldOptions")
        FieldOptions.resize(388, 305)
        self.gridLayout = QtWidgets.QGridLayout(FieldOptions)
        self.gridLayout.setObjectName("gridLayout")
        self.fieldName = QtWidgets.QLabel(FieldOptions)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.fieldName.setFont(font)
        self.fieldName.setObjectName("fieldName")
        self.gridLayout.addWidget(self.fieldName, 0, 0, 1, 1)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(FieldOptions)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.fontTypeBox = QtWidgets.QFontComboBox(FieldOptions)
        self.fontTypeBox.setObjectName("fontTypeBox")
        self.verticalLayout.addWidget(self.fontTypeBox)
        self.label_3 = QtWidgets.QLabel(FieldOptions)
        self.label_3.setObjectName("label_3")
        self.verticalLayout.addWidget(self.label_3)
        self.fontSizeOffsetBox = QtWidgets.QSpinBox(FieldOptions)
        self.fontSizeOffsetBox.setMinimum(-15)
        self.fontSizeOffsetBox.setMaximum(15)
        self.fontSizeOffsetBox.setObjectName("fontSizeOffsetBox")
        self.verticalLayout.addWidget(self.fontSizeOffsetBox)
        self.label_4 = QtWidgets.QLabel(FieldOptions)
        self.label_4.setObjectName("label_4")
        self.verticalLayout.addWidget(self.label_4)
        self.fieldAudioBox = QtWidgets.QComboBox(FieldOptions)
        self.fieldAudioBox.setObjectName("fieldAudioBox")
        self.fieldAudioBox.addItem("")
        self.verticalLayout.addWidget(self.fieldAudioBox)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.gridLayout.addLayout(self.verticalLayout, 1, 0, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(FieldOptions)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 2, 0, 1, 1)

        self.retranslateUi(FieldOptions)
        self.buttonBox.accepted.connect(FieldOptions.accept) # type: ignore
        self.buttonBox.rejected.connect(FieldOptions.reject) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(FieldOptions)

    def retranslateUi(self, FieldOptions):
        _translate = QtCore.QCoreApplication.translate
        FieldOptions.setWindowTitle(_translate("FieldOptions", "Dialog"))
        self.fieldName.setText(_translate("FieldOptions", "Field"))
        self.label.setText(_translate("FieldOptions", "Font"))
        self.label_3.setText(_translate("FieldOptions", "Font Size Offset"))
        self.label_4.setText(_translate("FieldOptions", "Field Audio"))
        self.fieldAudioBox.setItemText(0, _translate("FieldOptions", "(None)"))