from ..forms.options import *
from ..forms.field_options import *
from aqt.qt import QDialog, QListWidgetItem
from aqt import mw

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
