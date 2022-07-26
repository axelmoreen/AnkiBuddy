# Copyright: Axel Moreen, 2022
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
"""
Contains the options dialog, which appears when the user
clicks on "Options" within the questions dialog.

This dialog controls the config for the add-on and links them
to its UI.
"""
from ..stores import NotecardStore, OptionStore
from ..forms.options import Ui_OptionsDialog
from ..forms.field_options import Ui_FieldOptions
from aqt.qt import (
    QDialog,
    QListWidgetItem,
    QWidget,
    QComboBox,
    QFont,
)
from aqt import mw


class OptionsDialog(Ui_OptionsDialog, QDialog):
    """Options dialog used to control the config.
    Loads the UI, and then links all of the widgets so their values
    are the same as the config. Then it saves the values
    when do_accept() is called (the OK button is pressed).
    """
    def __init__(self, notecard_store: NotecardStore,
                 options_store: OptionStore):
        """Setup the options dialog.

        Args:
            notecard_store (NotecardStore): Instance of notecard store to load
                the model from.
            options_store (OptionStore): Option store to modify and save
                config with.
        """
        super(OptionsDialog, self).__init__()
        self.setupUi(self)

        self.setWindowTitle("AnkiBuddy Options - " + notecard_store.deck_name)
        self.setWindowIcon(mw.windowIcon())

        self.options_store = options_store
        self.notecard_store = notecard_store
        # initialize "field" comboboxes

        self.load_values()
        # signals
        # "OK" exiting options
        self.buttonBox.accepted.connect(self.do_accept)

        # timer checkbox to enable spinbox
        self.gen_cbTimed.stateChanged.connect(
            lambda state, widget=self.gen_timedAmount:
            self._bind_enabled_widget(
                state, widget
            )
        )
        # revisit checkbox to enable spinbox
        self.gen_cbDoRevisit.stateChanged.connect(
            lambda state, widget=self.gen_revisitSteps:
            self._bind_enabled_widget(
                state, widget
            )
        )
        # sound checkbox to enable volume slider
        self.gen_cbDoSounds.stateChanged.connect(
            lambda state, widget=self.gen_soundVolume:
            self._bind_enabled_widget(
                state, widget
            )
        )
        # edit field button
        self.gen_editFieldButton.clicked.connect(self._edit_field_btn)
        self.wr_cbKeyboard.stateChanged.connect(
            lambda state, widget=self.wr_coKeyboardType:
            self._bind_enabled_widget(
                state, widget
            )
        )

        # list dialog
        self.list_addButton.clicked.connect(self._list_add_btn)
        self.list_removeButton.clicked.connect(self._list_remove_btn)
        self.list_moveUpButton.clicked.connect(self._list_move_up_btn)
        self.list_moveDownButton.clicked.connect(self._list_move_down_btn)
        self.list_setFrontButton.clicked.connect(self._list_front_back_btn)

        # hidden widgets (unsupported currently)
        self.gen_soundVolume.setVisible(False)
        self.gen_SoundVolumeLabel.setVisible(False)

    def do_accept(self):
        """Connected to the accepted button box."""
        self.save_values()

    def load_values(self):
        """Load all the values from the option store, that can be modified,
        into their respective widgets in the options dialog.
        """
        g = self.options_store.get_globals(self.notecard_store.deck_name)
        lc = self.options_store.get_list_config(self.notecard_store.deck_name)
        h = self.options_store.get_homework_config(
            self.notecard_store.deck_name)
        # General
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

        # List
        # load types of fields to use as list columns
        self._load_notecard_fields(self.list_fieldSelCo)
        # load columns / frontback
        for i in range(len(lc["columns"])):
            item = QListWidgetItem(lc["columns"][i])
            font = item.font()
            font.setBold(bool(lc["front"][i]))
            font.setItalic(bool(lc["front"][i]))
            item.setFont(font)
            self.list_list.addItem(item)

        # Multiple Choice
        # confirm answer
        self.mc_cbConfirm.setChecked(h["choice_confirm_answer"])
        # mc question font size
        self.mc_questionFontSize.setValue(h["choice_question_size"])
        # mc answer button font size
        self.mc_answerFontSize.setValue(h["choice_answer_size"])

        # Matching
        # matching answer button font size
        self.ma_answerFontSize.setValue(h["matching_answer_size"])

        # Write the answer
        # show virtual keyboard
        self.wr_cbKeyboard.setChecked(h["write_show_keyboard"])
        self.wr_coKeyboardType.setEnabled(h["write_show_keyboard"])
        # virtual keyboard type
        self.wr_coKeyboardType.setCurrentIndex(h["write_keyboard_type"])
        # written question font size
        self.wr_questionFontSize.setValue(h["write_question_size"])

    def save_values(self):
        """Save all the values from the option dialog's widgets, into the
        option store dicts, and then save that to a file.
        """
        g = self.options_store.get_globals(self.notecard_store.deck_name)
        lc = self.options_store.get_list_config(self.notecard_store.deck_name)
        h = self.options_store.get_homework_config(
            self.notecard_store.deck_name)
        # General options
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

        # List
        cols = []
        front = []
        for i in range(self.list_list.count()):
            item = self.list_list.item(i)
            cols.append(item.text())
            front.append(bool(item.font().bold()))

        lc["columns"] = cols
        lc["front"] = front

        # Multiple Choice
        h["choice_confirm_answer"] = bool(self.mc_cbConfirm.isChecked())
        h["choice_question_size"] = int(self.mc_questionFontSize.value())
        h["choice_answer_size"] = int(self.mc_answerFontSize.value())
        # Matching
        h["matching_answer_size"] = int(self.ma_answerFontSize.value())
        # Write the answer
        h["write_show_keyboard"] = bool(self.wr_cbKeyboard.isChecked())
        h["write_keyboard_type"] = int(self.wr_coKeyboardType.currentIndex())
        h["write_question_size"] = int(self.wr_questionFontSize.value())

        self.options_store.config["decks"][self.notecard_store.deck_name] = g
        self.options_store.config["list"][self.notecard_store.deck_name] = lc
        self.options_store.config["homework"][
            self.notecard_store.deck_name] = h

        self.options_store.save()

    def _bind_enabled_widget(self, val: int, widget: QWidget):
        """Handle checkbox signal to enable or disable another widget.

        Args:
            val (int): Checkbox value (passed from checkbox signal)
            widget (QWidget): Widget to modify.
        """
        widget.setEnabled(bool(val))

    def _load_notecard_fields(self, combobox: QComboBox):
        """Load all the field names from the notecard store's model,
        into the combobox. Ignores combobox items that are already present.

        Args:
            combobox (QComboBox): Combobox to load into
        """
        for field in self.notecard_store.model["flds"]:
            combobox.addItem(field["name"])

    # list_list : list widget
    # list_fieldSelCo : combobox with fields
    def _list_add_btn(self):
        """Handler for the Add button, under the List tab."""
        self.list_list.addItem(self.list_fieldSelCo.currentText())

    def _list_remove_btn(self):
        """Handler for the Remove button, under the List tab."""
        if not self.list_list.currentItem():
            return
        self.list_list.takeItem(self.list_list.currentRow())

    def _list_move_up_btn(self):
        """Handler for the Move Up button, under the List tab."""
        row = self.list_list.currentRow()
        if row <= 0:
            return
        item = self.list_list.takeItem(row)
        self.list_list.insertItem(row - 1, item)

    def _list_move_down_btn(self):
        """Handler for the Move Down button, under the List tab."""
        row = self.list_list.currentRow()
        if row >= self.list_list.count() - 1:
            return
        item = self.list_list.takeItem(row)
        self.list_list.insertItem(row + 1, item)

    def _list_front_back_btn(self):
        """Handler for the Set Front/Back button, under the List tab."""
        item = self.list_list.currentItem()
        if not item:
            return
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
        """Handler for the Edit... button in the General tab.
        Opens up a secondary dialog to edit the field options, using
        the field that is selected in the gen_fieldsCb combobox.
        """
        self._fieldopts = FieldOptionsDialog(
            self.options_store, self.notecard_store,
            self.gen_fieldsCb.currentText()
        )
        self._fieldopts.show()


class FieldOptionsDialog(QDialog, Ui_FieldOptions):
    """Field options dialog. Used to change the font size, font family,
    and the linked audio field (experimental) for a field.
    Instantiate with the options store, notecard store, and the field name
    to load the options for.
    """
    def __init__(
        self, options_store: OptionStore, note_store: NotecardStore, field: str
    ):
        """Load the field options dialog.

        Args:
            options_store (OptionStore): instance of option store to write
                config.
            note_store (NotecardStore): instance of notecard store to get card
                model.
            field (str): model field to edit options for.
        """
        super(FieldOptionsDialog, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("Field Options - " + note_store.deck_name)
        self.setWindowIcon(mw.windowIcon())

        self.options_store = options_store
        self.note_store = note_store
        self.field = field

        g = self.options_store.config["decks"][self.note_store.deck_name]
        self.all_settings = g["field_settings"]  # field dict

        self.field_settings = [mw.font().family(), 0, "(None)"]
        if field in self.all_settings:  # load from settings present
            self.field_settings = self.all_settings[field]

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
        """Connected to buttonBox. Set field options, and save to config file.
        """
        self.field_settings[0] = self.fontTypeBox.currentFont().family()
        self.field_settings[1] = self.fontSizeOffsetBox.value()
        self.field_settings[2] = self.fieldAudioBox.currentText()

        self.options_store.config["decks"][self.note_store.deck_name][
            "field_settings"][
            self.field
        ] = self.field_settings
        self.options_store.save()
