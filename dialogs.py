from .forms.questions_wizard import *
from .forms.template_wizard import *
from .forms.options import *
from .forms.field_options import *

from aqt.qt import *
from aqt import mw

from .subsets import *

# imports solely for the List preview, TODO: perhaps remove * import
from .models import *
from .controllers import *
from .views import *

# Questions Dialog - setup the questions that are
# asked in Homework and Assessments
# 
# use getResults() to show the dialog and get the configuration to use
# state is managed internally and does not rely on a model
class QuestionsDialog(QDialog, Ui_QuestionsWizard):
    def __init__(self, notecard_store, options_store):
        super(QuestionsDialog, self).__init__()
        self.setupUi(self)

        self.setWindowTitle("Questions Wizard - "+notecard_store.deck_name)
        self.setWindowIcon(mw.windowIcon())
        self.newTemplate.clicked.connect(self.new_template_sig)
        self.editTemplate.clicked.connect(self.edit_template_sig)
        self.deleteTemplate.clicked.connect(self.delete_template_sig)

        self.addSel.clicked.connect(self.add_sel_template_sig)
        self.removeSel.clicked.connect(self.remove_sel_template_sig)

        self.options.clicked.connect(self.show_options_sig)

        self.notecard_store = notecard_store
        self.options_store = options_store

        self.templates = []
        self.sel_templates = []

        self.subsets = []
        self.all_groups = True
        self.curr_subset = 0
        self.sub_group_ind = 0 # group index for the current subset

        lesson_size = options_store.get_globals(self.notecard_store.deck_name)["lesson_size"]
        
        self.addSubset(LinearSubset(notecard_store, lesson_size=lesson_size))
        self.addSubset(LearnedSubset(notecard_store, lesson_size=lesson_size))
        self.addSubset(LapsedSubset(notecard_store, lesson_size=lesson_size))
        self.addSubset(NewSubset(notecard_store, lesson_size=lesson_size))

        # signals / controller
        self.subsetBox.currentIndexChanged.connect(self.subset_index_sig)
        self.allgroups_box.stateChanged.connect(self.allgroups_sig)
        self.group_index_box.valueChanged.connect(self.group_index_sig)
        self.previewSubsetButton.clicked.connect(self.preview_subset_sig)

        self.buttonBox.accepted.connect(self.do_accept)

        # load last templates
        if "templates" in self.options_store.get_homework_config(notecard_store.deck_name):
            for templ in self.options_store.get_homework_config(notecard_store.deck_name)["templates"]:
                self.templates.append(templ)
                self.templatesList.addItem(self.get_template_string(templ))
        if "selected_templates" in self.options_store.get_homework_config(notecard_store.deck_name):
            for sel_templ  in self.options_store.get_homework_config(notecard_store.deck_name)["selected_templates"]:
                self.sel_templates.append(sel_templ)
                self.selectedList.addItem(self.get_template_string(self.templates[sel_templ]))

        # load last subset
        if "last_subset" in self.options_store.get_homework_config(notecard_store.deck_name):
            self.curr_subset = self.options_store.get_homework_config(notecard_store.deck_name)["last_subset"]
            self.subsetBox.setCurrentIndex(self.curr_subset)
    
    def do_accept(self):        
        # to pass: 
        # self.sel_templates = list of templates (dicts)
        ### template schema:
        ###     type_ind: question type. 0= multiple choice, 1=matching, 2=write the answer
        ###     type: question type string. "Multiple Choice", "Matching", or "Write the Answer"
        ###     question: Anki field to populate Question(s) from.
        ###     answer: Anki field to populate Answer(s) from.
        ###     include_reverse: True/False should sometimes reverse the question and answer fields
        # extra fields
        ###### for Multiple choice:
        ######      number_choices: the number of Answers to choose from.
        ###### for Matching:
        ######      groupsize: How many many questions/answers should be on a single page to match from.
        ######      extrabank: (not implemented currently) will be how many extra answers than questions there are.

        # self.subsets[self.curr_subset] -> returns Subset object with information needed
        #           must also include self.sub_group_ind to know which group of the subset to look at. or pass -1 to pass nothing
        if len(self.sel_templates) == 0:
            self._cancelMsg = QMessageBox()
            self._cancelMsg.setText("Please set-up question templates in order to proceed.")
            self._cancelMsg.exec_()
            return
        templs = [self.templates[i] for i in self.sel_templates]
        if self.all_groups:
            model = HomeworkModel(self.notecard_store, templs, self.options_store, subset=self.subsets[self.curr_subset], subset_group = -1)
        else:
            model = HomeworkModel(self.notecard_store, templs, self.options_store, subset=self.subsets[self.curr_subset], subset_group = self.sub_group_ind)
        controller = HomeworkController(model)
        mw._hwView = HomeworkView(model, controller)
        mw._hwView.show()

    def add_template(self, templ):
        self.templates.append(templ)
        # update UI
        self.templatesList.addItem(self.get_template_string(templ))

        # auto-add to selected templates
        row = len(self.templates) - 1
        self.sel_templates.append(row)
        self.selectedList.addItem(self.get_template_string(self.templates[row]))

        # update options store
        self.update_options()

    def edit_template(self, index, templ):
        self.templates[index] = templ
        self.templatesList.item(index).setText(self.get_template_string(templ))
        self.update_options()

    def update_options(self):
        self.options_store.get_homework_config(self.notecard_store.deck_name)["templates"] = self.templates  
        self.options_store.get_homework_config(self.notecard_store.deck_name)["selected_templates"] = self.sel_templates
        self.options_store.save()

    def get_template_string(self, templ):
        return templ["type"] +" - " + templ["question"] +" / " + templ["answer"] + (" (+reverse) "if templ["include_reverse"] else "")


    # Signals
    def new_template_sig(self):
        d = TemplateDialog(self.notecard_store, self.options_store)
        res = d.getResults()
        if res:
            self.add_template(res)
        else:
            pass # nothing happened
    
    def edit_template_sig(self):
        if len(self.templates) < 1: return
        # QListWidget.currentRow() is given -1 if nothing is selected
        # todo : consider selected list as well
        #if self.templatesList.currentRow() < 0 and self.selectedList.currentRow() < 0: return
        if self.templatesList.currentRow() < 0: return
        row = self.templatesList.currentRow()
        d = TemplateDialog(self.notecard_store, self.options_store, self.templates[row])
        res = d.getResults()
        if res:
            self.edit_template(row, res)
        else:
            pass
    
    def delete_template_sig(self):
        if self.templatesList.currentRow() < 0: return # nothing is selected
        row = self.templatesList.currentRow()
        # delete from self.templates
        del self.templates[row]

        # delete from ui
        self.templatesList.takeItem(row)

        # delete any reference in self.sel_templates 
        # so far, there can only be one reference in sel_templates, but will write this as if there could be multiple anyway
        # and,
        # use _below to move all values above row self.sel_templates -1
        to_delete = []
        for i in range(len(self.sel_templates)):
            if self.sel_templates[i] == row: # list index out of range after two deletes
                to_delete.append(i) # roundabout way to avoid concurrent modification?
                
        for ele in to_delete:
            # delete from model
            del self.sel_templates[ele]
            # delete from ui
            self.selectedList.takeItem(ele)

        for i in range(len(self.sel_templates)):
            if self.sel_templates[i] > row:
                self.sel_templates[i] = self.sel_templates[i] - 1
        
        self.update_options()

    def add_sel_template_sig(self):
        if self.templatesList.currentRow() < 0: return
        row = self.templatesList.currentRow()
        if row in self.sel_templates:
            pass
        else:
            self.sel_templates.append(row)
             
            # add to ui
            self.selectedList.addItem(self.get_template_string(self.templates[row]))

    def remove_sel_template_sig(self):
        if self.selectedList.currentRow() < 0: return
        row = self.selectedList.currentRow()

        del self.sel_templates[row]
        self.selectedList.takeItem(row)

    def addSubset(self, subset):
        self.subsets.append(subset)
        self.subsetBox.addItem(subset.get_subset_name())

    def updateSubsetUI(self):
        subset = self.subsets[self.curr_subset]
        if self.all_groups:
            self.group_index_box.setEnabled(False)
        else:
            self.group_index_box.setEnabled(True)

        # set group index combobox
        self.group_index_box.setMaximum(subset.get_max_index())
        self.group_index_box.setMinimum(0)

        
    # fired by changing the subset combo box.
    def subset_index_sig(self, ind):
        self.curr_subset = ind
        self.sub_group_ind = 0
        self.group_index_box.setValue(0)
        self.updateSubsetUI()

        # write this to config
        self.options_store.get_homework_config(self.notecard_store.deck_name)["last_subset"] = self.curr_subset
        self.options_store.save()

    # fired by changing the "All Groups" checkbox.
    def allgroups_sig(self, val):
        self.all_groups = bool(val)
        self.updateSubsetUI()

    # fired by changing the group number spinbox
    def group_index_sig(self, ind):
        self.sub_group_ind = ind

    def preview_subset_sig(self):
        subset_text = self.subsets[self.curr_subset].get_subset_name() +" - " + ("All" if self.all_groups else "Group "+str(self.sub_group_ind))

        if self.all_groups:
            _subset = self.subsets[self.curr_subset].get_all_cards()
        else:
            _subset = self.subsets[self.curr_subset].get_cards(self.sub_group_ind)
        
        model = ListModel(self.notecard_store, self.options_store, subset=_subset, subset_text=subset_text)
        controller = ListController(model) 
        
        self.list = ListView(model, controller)
        self.list.exec_()

    def show_options_sig(self):
        self.options_dialog = OptionsDialog(self.notecard_store, self.options_store)
        self.options_dialog.buttonBox.accepted.connect(self.update_from_options)
        #self.update_from_options()
        self.options_dialog.show()
    def update_from_options(self):
        lesson_size = self.options_store.get_globals(self.notecard_store.deck_name)["lesson_size"]
        for subset in self.subsets:
            subset.lesson_size = lesson_size

        self.updateSubsetUI()

# Template Dialog - create and edit templates to be used in the Questions dialog. 
# saves templates to configuration for convenience
#
# should just be called by QuestionsDialog
class TemplateDialog(QDialog, Ui_TemplateDialog):
    # set templ for edit card dialog, otherwise leave as None to create new card
    def __init__(self, notecard_store, options_store, templ=None):
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
    def getResults(self):
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

    # signal for changing Question Type combobox
    # changes the StackedWidget below. 
    def change_type(self, val):
        self.stackedWidget.setCurrentIndex(val)

class OptionsDialog(Ui_OptionsDialog, QDialog):
    def __init__(self, notecard_store, options_store):
        super(OptionsDialog, self).__init__()
        self.setupUi(self)

        self.setWindowTitle("AnkiBuddy Options - "+notecard_store.deck_name)
        self.setWindowIcon(mw.windowIcon())

        self.options_store = options_store
        self.notecard_store = notecard_store
        ### initialize "field" comboboxes

        self.load_values()
        ### signals
        # "OK" exiting options
        self.buttonBox.accepted.connect(self.do_accept)

        # timer checkbox to enable spinbox
        self.gen_cbTimed.stateChanged.connect(lambda state, widget=self.gen_timedAmount: self._bind_enabled_widget(state, widget))
        # revisit checkbox to enable spinbox
        self.gen_cbDoRevisit.stateChanged.connect(lambda state, widget=self.gen_revisitSteps: self._bind_enabled_widget(state, widget))
        # sound checkbox to enable volume slider
        self.gen_cbDoSounds.stateChanged.connect(lambda state, widget=self.gen_soundVolume: self._bind_enabled_widget(state, widget))
        # edit field button
        self.gen_editFieldButton.clicked.connect(self._edit_field_btn)
        # MC play audio on button press to enable combo box (moved to edit field...)
        # self.mc_cbAudio.stateChanged.connect(lambda state, widget=self.mc_audioField: self._bind_enabled_widget(state, widget))
        # Matching play audio on button press to enable combo box (moved to edit field..)
        # self.ma_cbAudio.stateChanged.connect(lambda state, widget=self.ma_audioField: self._bind_enabled_widget(state, widget))
        # Show virtual keyboard enable type combobox
        self.wr_cbKeyboard.stateChanged.connect(lambda state, widget=self.wr_coKeyboardType: self._bind_enabled_widget(state, widget))

        # list dialog
        self.list_addButton.clicked.connect(self._list_add_btn)
        self.list_removeButton.clicked.connect(self._list_remove_btn)
        self.list_moveUpButton.clicked.connect(self._list_move_up_btn)
        self.list_moveDownButton.clicked.connect(self._list_move_down_btn)
        self.list_setFrontButton.clicked.connect(self._list_front_back_btn)

        ### hidden widgets (unsupported currently) 
        self.gen_soundVolume.setVisible(False)
        self.gen_SoundVolumeLabel.setVisible(False)
    def do_accept(self):
        self.save_values()

    def load_values(self):
        g = self.options_store.get_globals(self.notecard_store.deck_name)
        l = self.options_store.get_list_config(self.notecard_store.deck_name)
        h = self.options_store.get_homework_config(self.notecard_store.deck_name)
        ### General
        # Show answer before moving on
        self.gen_showAnswer.setChecked(g["show_answer_before_next"])
        # Enable/disable timer
        self.gen_cbTimed.setChecked(g["do_timer"])
        self.gen_timedAmount.setEnabled(g["do_timer"])
        # Set timer length
        self.gen_timedAmount.setValue(g["timer_seconds"])
        # Group size
        self.gen_groupSize.setValue(g["lesson_size"])
        # True random
        self.gen_doTrueRandom.setChecked(g["true_random"])
        # Enable/disable revisit wrong answers
        self.gen_cbDoRevisit.setChecked(g["revisit_mistakes"])
        self.gen_revisitSteps.setEnabled(g["revisit_mistakes"])
        # revisit steps
        self.gen_revisitSteps.setValue(g["revisit_steps"])
        # play correct/incorrect sounds
        self.gen_cbDoSounds.setChecked(g["play_sounds"])
        # sort by field 
        self._load_notecard_fields(self.gen_sortByCb)
        if "sort" in g:
            self.gen_sortByCb.setCurrentText(g["sort"])
        # fields options 
        self._load_notecard_fields(self.gen_fieldsCb)
        
        ### List
        # load types of fields to use as list columns
        self._load_notecard_fields(self.list_fieldSelCo)
        # load columns / frontback
        for i in range(len(l["columns"])):
            item = QListWidgetItem(l["columns"][i])
            font = item.font()
            font.setBold(bool(l["front"][i]))
            font.setItalic(bool(l["front"][i]))
            item.setFont(font)
            self.list_list.addItem(item)
        
        ### Multiple Choice 
        # confirm answer
        self.mc_cbConfirm.setChecked(h["choice_confirm_answer"])
        # mc question font size
        self.mc_questionFontSize.setValue(h["choice_question_size"])
        # mc answer button font size
        self.mc_answerFontSize.setValue(h["choice_answer_size"])

        ### Matching
        # matching answer button font size
        self.ma_answerFontSize.setValue(h["matching_answer_size"])

        ### Write the answer
        # show virtual keyboard 
        self.wr_cbKeyboard.setChecked(h["write_show_keyboard"])
        self.wr_coKeyboardType.setEnabled(h["write_show_keyboard"])
        # virtual keyboard type
        self.wr_coKeyboardType.setCurrentIndex(h["write_keyboard_type"])
        # written question font size
        self.wr_questionFontSize.setValue(h["write_question_size"])
        
    def save_values(self):
        g = self.options_store.get_globals(self.notecard_store.deck_name)
        l = self.options_store.get_list_config(self.notecard_store.deck_name)
        h = self.options_store.get_homework_config(self.notecard_store.deck_name)
        ### General options
        # show answer before moving on
        g["show_answer_before_next"] = bool(self.gen_showAnswer.isChecked())
        # enable/disable timer
        g["do_timer"] = bool(self.gen_cbTimed.isChecked())
        # timer length
        g["timer_seconds"] = int(self.gen_timedAmount.value())
        # group size
        g["lesson_size"] = int(self.gen_groupSize.value())
        # true random
        g["true_random"] = bool(self.gen_doTrueRandom.isChecked())
        # enable/disable revisit wrong answers
        g["revisit_mistakes"] = bool(self.gen_cbDoRevisit.isChecked())
        # revisit steps
        g["revisit_steps"] = int(self.gen_revisitSteps.value())
        # play correct/incorrect sounds
        g["play_sounds"] = bool(self.gen_cbDoSounds.isChecked())
        # sort by field
        g["sort"] = str(self.gen_sortByCb.currentText())

        # TODO: more field options here??

        ### List
        cols = []
        front = []
        for i in range(self.list_list.count()):
            item = self.list_list.item(i)
            cols.append(item.text())
            front.append(bool(item.font().bold()))

        l["columns"] = cols
        l["front"] = front

        ### Multiple Choice
        h["choice_confirm_answer"] = bool(self.mc_cbConfirm.isChecked())
        h["choice_question_size"] = int(self.mc_questionFontSize.value())
        h["choice_answer_size"] = int(self.mc_answerFontSize.value())
        ### Matching
        h["matching_answer_size"] = int(self.ma_answerFontSize.value())
        ### Write the answer
        h["write_show_keyboard"] = bool(self.wr_cbKeyboard.isChecked())
        h["write_keyboard_type"] = int(self.wr_coKeyboardType.currentIndex())
        h["write_question_size"] = int(self.wr_questionFontSize.value())

        self.options_store.config["decks"][self.notecard_store.deck_name] = g
        self.options_store.config["list"][self.notecard_store.deck_name] = l
        self.options_store.config["homework"][self.notecard_store.deck_name] = h

        self.options_store.save()

    # general method for checkbox signals to enable/disable widgets
    def _bind_enabled_widget(self, val, widget):
        widget.setEnabled(bool(val))

    def _load_notecard_fields(self, combobox):
        for field in self.notecard_store.model["flds"]:
            combobox.addItem(field["name"])

    # list_list : list widget 
    # list_fieldSelCo : combobox with fields
    def _list_add_btn(self):
        self.list_list.addItem(self.list_fieldSelCo.currentText())

    def _list_remove_btn(self):
        if not self.list_list.currentItem():
            return 
        self.list_list.takeItem(self.list_list.currentRow())

    def _list_move_up_btn(self):
        row = self.list_list.currentRow()
        if row <= 0: return
        item = self.list_list.takeItem(row)
        self.list_list.insertItem(row - 1, item)

    def _list_move_down_btn(self):
        row = self.list_list.currentRow()
        if row >= self.list_list.count() -1: return
        item = self.list_list.takeItem(row)
        self.list_list.insertItem(row + 1, item)

    def _list_front_back_btn(self):
        item = self.list_list.currentItem()
        if not item: return
        font = item.font()
        if font.bold():
            font.setBold(False)
            font.setItalic(False)
        else:
            font.setBold(True)
            font.setItalic(True)
        item.setFont(font)
        self.list_list.setCurrentItem(item)

    def _edit_field_btn(self):
        self._fieldopts = FieldOptionsDialog(self.options_store, 
            self.notecard_store, 
            self.gen_fieldsCb.currentText())
        self._fieldopts.show()

class FieldOptionsDialog(QDialog, Ui_FieldOptions):
    # set templ for edit card dialog, otherwise leave as None to create new card
    def __init__(self, options_store, note_store, field):
        super(FieldOptionsDialog, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("Field Options - "+note_store.deck_name)
        self.setWindowIcon(mw.windowIcon())

        self.options_store = options_store
        self.note_store = note_store
        self.field = field

        g = self.options_store.config["decks"][self.note_store.deck_name]
        self.all_settings = g["field_settings"] # field dict

        self.field_settings = [mw.font().family(), 0, "(None)"]
        if field in self.all_settings: # load from settings present
            self.field_settings = self.all_settings[field]

        # TODO: fix duplicate code
        for f in self.note_store.model["flds"]:
            self.fieldAudioBox.addItem(f["name"])

        # update ui to current settings
        self.fieldName.setText(field)

        self.fontTypeBox.setCurrentFont(QFont(self.field_settings[0]))
        self.fontSizeOffsetBox.setValue(self.field_settings[1])
        self.fieldAudioBox.setCurrentText(self.field_settings[2])

        # sig accepted
        self.buttonBox.accepted.connect(self.do_accept)
    
    def do_accept(self):
        self.field_settings[0] = self.fontTypeBox.currentFont().family()
        self.field_settings[1] = self.fontSizeOffsetBox.value()
        self.field_settings[2] = self.fieldAudioBox.currentText()

        self.options_store.config["decks"][self.note_store.deck_name]["field_settings"][self.field] = self.field_settings
        self.options_store.save()
