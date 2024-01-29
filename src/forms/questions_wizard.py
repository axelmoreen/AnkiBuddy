# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './designer/questions_wizard.ui'
#
# Created by: PyQt5 UI code generator 5.15.7
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from aqt.qt import *

class Ui_QuestionsWizard(object):
    def setupUi(self, QuestionsWizard):
        QuestionsWizard.setObjectName("QuestionsWizard")
        QuestionsWizard.resize(1033, 390)
        self.gridLayout = QGridLayout(QuestionsWizard)
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label = QLabel(QuestionsWizard)
        self.label.setObjectName("label")
        self.verticalLayout_3.addWidget(self.label)
        self.templatesList = QListWidget(QuestionsWizard)
        self.templatesList.setObjectName("templatesList")
        self.verticalLayout_3.addWidget(self.templatesList)
        self.horizontalLayout_2.addLayout(self.verticalLayout_3)
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        spacerItem = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        self.addSel = QPushButton(QuestionsWizard)
        self.addSel.setObjectName("addSel")
        self.verticalLayout_2.addWidget(self.addSel)
        self.removeSel = QPushButton(QuestionsWizard)
        self.removeSel.setObjectName("removeSel")
        self.verticalLayout_2.addWidget(self.removeSel)
        spacerItem1 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.verticalLayout_2.addItem(spacerItem1)
        self.horizontalLayout_2.addLayout(self.verticalLayout_2)
        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.label_2 = QLabel(QuestionsWizard)
        self.label_2.setObjectName("label_2")
        self.verticalLayout_4.addWidget(self.label_2)
        self.selectedList = QListWidget(QuestionsWizard)
        self.selectedList.setObjectName("selectedList")
        self.verticalLayout_4.addWidget(self.selectedList)
        self.horizontalLayout_2.addLayout(self.verticalLayout_4)
        self.gridLayout.addLayout(self.horizontalLayout_2, 0, 0, 1, 1)
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.newTemplate = QPushButton(QuestionsWizard)
        self.newTemplate.setObjectName("newTemplate")
        self.verticalLayout.addWidget(self.newTemplate)
        self.editTemplate = QPushButton(QuestionsWizard)
        self.editTemplate.setObjectName("editTemplate")
        self.verticalLayout.addWidget(self.editTemplate)
        self.deleteTemplate = QPushButton(QuestionsWizard)
        self.deleteTemplate.setObjectName("deleteTemplate")
        self.verticalLayout.addWidget(self.deleteTemplate)
        self.options = QPushButton(QuestionsWizard)
        self.options.setObjectName("options")
        self.verticalLayout.addWidget(self.options)
        spacerItem2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.verticalLayout.addItem(spacerItem2)
        self.label_3 = QLabel(QuestionsWizard)
        self.label_3.setObjectName("label_3")
        self.verticalLayout.addWidget(self.label_3)
        self.subsetBox = QComboBox(QuestionsWizard)
        self.subsetBox.setObjectName("subsetBox")
        self.verticalLayout.addWidget(self.subsetBox)
        self.allgroups_box = QCheckBox(QuestionsWizard)
        self.allgroups_box.setChecked(True)
        self.allgroups_box.setObjectName("allgroups_box")
        self.verticalLayout.addWidget(self.allgroups_box)
        self.group_index_box = QSpinBox(QuestionsWizard)
        self.group_index_box.setEnabled(False)
        self.group_index_box.setMinimum(0)
        self.group_index_box.setMaximum(0)
        self.group_index_box.setObjectName("group_index_box")
        self.verticalLayout.addWidget(self.group_index_box)
        self.previewSubsetButton = QPushButton(QuestionsWizard)
        self.previewSubsetButton.setObjectName("previewSubsetButton")
        self.verticalLayout.addWidget(self.previewSubsetButton)
        spacerItem3 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.verticalLayout.addItem(spacerItem3)
        self.gridLayout.addLayout(self.verticalLayout, 0, 1, 1, 1)
        self.buttonBox = QDialogButtonBox(QuestionsWizard)
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 2)

        self.retranslateUi(QuestionsWizard)
        self.buttonBox.accepted.connect(QuestionsWizard.accept) # type: ignore
        self.buttonBox.rejected.connect(QuestionsWizard.reject) # type: ignore
        QMetaObject.connectSlotsByName(QuestionsWizard)

    def retranslateUi(self, QuestionsWizard):
        _translate = QCoreApplication.translate
        QuestionsWizard.setWindowTitle(_translate("QuestionsWizard", "Dialog"))
        self.label.setText(_translate("QuestionsWizard", "All Question Templates"))
        self.addSel.setText(_translate("QuestionsWizard", "→"))
        self.removeSel.setText(_translate("QuestionsWizard", "←"))
        self.label_2.setText(_translate("QuestionsWizard", "Selected Templates"))
        self.newTemplate.setText(_translate("QuestionsWizard", "New..."))
        self.editTemplate.setText(_translate("QuestionsWizard", "Edit..."))
        self.deleteTemplate.setText(_translate("QuestionsWizard", "Delete"))
        self.options.setText(_translate("QuestionsWizard", "Options"))
        self.label_3.setText(_translate("QuestionsWizard", "Subset"))
        self.allgroups_box.setText(_translate("QuestionsWizard", "All Groups"))
        self.previewSubsetButton.setText(_translate("QuestionsWizard", "List"))
