# Copyright: Axel Moreen, 2022
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
"""
Contains Template Dialog. 
This is created from the Homework wizard in ./questions_dialog.py. 
It is used to create new question templates or edit an existing one
by letting the user choose which fields to use for the question
and giving some extra options based on the type (multiple choice, matching, written).  
"""
from __future__ import annotations
from typing import Any

from ..stores import NotecardStore, OptionStore

from ..forms.template_wizard import *

from aqt.qt import (
    QDialog
)
from aqt import mw
# Template Dialog - create and edit templates to be used in the Questions dialog. 
# saves templates to configuration for convenience
#
# should just be called by QuestionsDialog
class TemplateDialog(QDialog, Ui_TemplateDialog):
    # set templ for edit card dialog, otherwise leave as None to create new card
    def __init__(self, notecard_store: NotecardStore, options_store: OptionStore, templ: dict[str,Any]=None):
        """Create template dialog. 

        Args:
            notecard_store (NotecardStore): Instance of notecard store to pull cards from.
            options_store (OptionStore): Option store to use for config.
            templ (dict[str,Any], optional): Template to edit. Pass none, if creating new template. Defaults to None.
        """
        super(TemplateDialog, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("Template - "+notecard_store.deck_name)
        self.setWindowIcon(mw.windowIcon())
        self.questiontype.currentIndexChanged.connect(self.change_type)
        
        self.stackedWidget.setCurrentIndex(0)

        # data
        self.notecard_store = notecard_store
        self.options_store = options_store

        # load fields
        for field in notecard_store.model["flds"]:
            self.question.addItem(field["name"])
            self.question_2.addItem(field["name"])
            self.question_3.addItem(field["name"])

            self.answer.addItem(field["name"])
            self.answer_2.addItem(field["name"])
            self.answer_3.addItem(field["name"])

        # set to template settings
        if templ:
            self.questiontype.setCurrentIndex(templ["type_ind"])
            self.stackedWidget.setCurrentIndex(templ["type_ind"])

            self.question.setCurrentText(templ["question"])
            self.question_2.setCurrentText(templ["question"])
            self.question_3.setCurrentText(templ["question"])

            self.answer.setCurrentText(templ["answer"])
            self.answer_2.setCurrentText(templ["answer"])
            self.answer_3.setCurrentText(templ["answer"])

            if templ["type_ind"] == 0:
                self.choices.setValue(templ["number_choices"])
            elif templ["type_ind"] == 1:
                self.groupsize.setValue(templ["groupsize"])
                self.extrabank.setValue(templ["extrabank"])
            
            self.reverse.setChecked(templ["include_reverse"])
            self.reverse_2.setChecked(templ["include_reverse"])
            self.reverse_3.setChecked(templ["include_reverse"])
        
        # extra bank unsupported yet
        self.extrabank.setVisible(False)
        self.label_7.setVisible(False)

    def getResults(self) -> dict[str, Any]:
        """Get the results of the template dialog.

        Returns:
            dict[str, Any]: Returns dict representing the template.
        """
        if self.exec_() == QDialog.Accepted:
            res = {}
            res["type_ind"] = self.stackedWidget.currentIndex()

            if self.stackedWidget.currentIndex() == 0:
                # multiple choice
                res["type"] = "Multiple Choice"
                res["question"] = self.question.currentText()
                res["answer"] = self.answer.currentText()
                res["number_choices"] = self.choices.value()
                res["include_reverse"] = bool(self.reverse.isChecked())

            elif self.stackedWidget.currentIndex() == 1:
                #matching
                res["type"] = "Matching"
                res["question"] = self.question_2.currentText()
                res["answer"] = self.answer_2.currentText()
                res["groupsize"] = self.groupsize.value()
                res["extrabank"] = self.extrabank.value()
                res["include_reverse"] = bool(self.reverse_2.isChecked())
            
            elif self.stackedWidget.currentIndex() == 2:
                # write the answer
                res["type"] = "Write the Answer"
                res["question"] = self.question_3.currentText()
                res["answer"] = self.answer_3.currentText()
                res["include_reverse"] = bool(self.reverse_3.isChecked())
            return res
        return None

    def change_type(self, val):
        """Connected to the "Question Type" combobox signal,
        this changes which frame to show in the StackedWidget.
        """
        self.stackedWidget.setCurrentIndex(val)