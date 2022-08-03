# Copyright: Axel Moreen, 2022
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""
Keyboard module for displaying virtual keyboards alongside the Write the Answer
widget. Designed to match the Windows Japanese hiragana layout, but this
differs on Mac (untested on Linux).   

Currently experimental, see issue tracker.
"""
from __future__ import annotations
from .forms.keyboard import Ui_Keyboard
from aqt.qt import (
    QDialog,
    QWidget,
    QTimer,
    QPushButton,
    QKeyEvent,
    QLineEdit
)
from aqt import mw

import unicodedata

class KeyboardView(QDialog, Ui_Keyboard):
    def __init__(self, translation: List[Tuple]=None):
        """Initialize the keyboard view. 

        Args:
            translation (List[Tuple], optional): Keyboard type to load. See the definitions at the bottom of keyboards.py. Defaults to None.
        """
        super(KeyboardView, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("Virtual Keyboard")
        self.setWindowIcon(mw.windowIcon())
        self.field_entry = None # list of lineedits to modify from this keyboard
        self.buttons = [] # just for character keys for text to get updated on shift / caps 
        self.translation = translation

        self.setup_button_commands()
        self.shift = False
        
        self.caps = False
        
    def link_field(self, field: QLineEdit):
        """Link an input field (LineEdit) to the output
        of this virtual keyboard. 

        Args:
            field (QLineEdit): input field to link.
        """
        self.field_entry = field

    def _link_button(self, button: QPushButton, ind: int=-1):
        """Internal method to link a button to an index in the translation, as
        well as set some other setup.

        Args:
            button (QPushButton): Button to link.
            ind (int, optional): Index in the translation list. Defaults to -1.
        """
        self.buttons.append(
            (button, ind)
        )
        if ind > -1 and self.translation:
            item = self.translation[ind]
            if item:
                button.setText(item[0])
        font = button.font()
        font.setPointSize(20)
        button.setFont(font)
        button.setCheckable(True)
        button.setAutoDefault(False)
        button.clicked.connect(lambda: self._run_command(button, ind))

    def _run_command(self, button: QPushButton, ind: int):
        """Signal callback for qpushbutton. 

        Note: Currently, this method actually looks at
        the button text to determine what to 'type', eventually it would be better
        to look up what the translation should be based on the button that
        has already been linked. 

        This method also has hard-coded support for Japanese dakutens. 

        Args:
            button (QPushButton): Button that was pressed in the clicked signal.
            ind (int): Unused currently.
        """
        if button.text() == "◌゙":
            self._dakuten()
            return
        elif button.text() == "◌゚":
            self._dakuten(han = True)
            return


        if len(button.text()) > 1:
            self.field_entry.insert(button.text()[0])
        else:
            self.field_entry.insert(button.text())
        self.field_entry.setFocus()
        self.shift = False
        self._update_shift_buttons()
        self._update_char_buttons()

    def _shift(self):
        """Signal callback for the Shift buttons.
        """
        self.shift = not self.shift
        self._update_shift_buttons()
        self._update_char_buttons()

    def _update_shift_buttons(self):
        """Helper method to update both of the shift buttons.
        """
        self.pushButton_54.setChecked(self.shift)
        self.pushButton_43.setChecked(self.shift)

    def _update_char_buttons(self):
        """Helper method to update all the keyboard buttons based
        on whether or not shift or caps is pressed.
        """
        if not self.translation: return
        for pair in self.buttons:
            if pair[1]: # has ind
                if len(self.translation[pair[1]]) > 1:
                    pair[0].setText(self.translation[pair[1]][int(self._is_caps())])

    def _caps(self):
        """Signal callback to toggle Caps lock.
        """
        self.caps = not self.caps
        self.pushButton_34.setChecked(self.caps)
        self._update_char_buttons()

    def _is_caps(self) -> bool:
        """Helper method to get if a letter should be outputted as caps,
        so the OR of caps and shift.

        Returns:
            bool: True if next letter should be capitalized, False if not.
        """
        return self.caps or self.shift

    def _backspace(self):
        """Signal callback for backspace.
        """
        self.field_entry.backspace()

    def _space(self):
        """Signal callback for space.
        """
        self.field_entry.insert(" ")
        self.field_entry.setFocus()
        
    # han: false for regular dakuten, true for handakuten
    def _dakuten(self, han: bool=False): # support for japanese dakuten, may be a better way to do this
        """Helper method to insert dakutens. It will act on the character before the cursor
        in the linked field entry, if it is possible.

        Args:
            han (bool, optional): True if it is a handakuten, False if it is a dakuten. Defaults to False.
        """

        pos = self.field_entry.cursorPosition()
        if pos == 0: return
        text = list(self.field_entry.text())
        if not han:
            text[pos-1] = text[pos-1] + "\u3099"
        else:
            text[pos-1] = text[pos-1] + "\u309A"
        # normalize unicode
        _text = unicodedata.normalize("NFC", "".join(text))
        self.field_entry.setText(_text)

    def setup_button_commands(self):
        """Link all the buttons to the translation, and set some options.

        The naming scheme could be improved. :)
        """
        # `1234567890-=
        self._link_button(self.pushButton_3, 0)
        self._link_button(self.pushButton_7, 1)
        self._link_button(self.pushButton_6, 2)
        self._link_button(self.pushButton_5, 3)
        self._link_button(self.pushButton_4, 4)
        self._link_button(self.pushButton_2, 5)
        self._link_button(self.pushButton, 6)
        self._link_button(self.pushButton_11, 7)
        self._link_button(self.pushButton_10, 8)
        self._link_button(self.pushButton_13, 9)
        self._link_button(self.pushButton_12, 10)
        self._link_button(self.pushButton_9, 11)
        self._link_button(self.pushButton_8, 12)
        # backspace

        self.pushButton_29.clicked.connect(self._backspace) 
        self.pushButton_29.setAutoDefault(False)
        # Tab 
        self.pushButton_14.setEnabled(False) # tab shouldn't do anything
        self.pushButton_14.setAutoDefault(False)
 
        # qwertyuiop[]\
        self._link_button(self.pushButton_21, 15)
        self._link_button(self.pushButton_20, 16)
        self._link_button(self.pushButton_23, 17)
        self._link_button(self.pushButton_26, 18)
        self._link_button(self.pushButton_22, 19)
        self._link_button(self.pushButton_25, 20)
        self._link_button(self.pushButton_24, 21)
        self._link_button(self.pushButton_19, 22)
        self._link_button(self.pushButton_18, 23)
        self._link_button(self.pushButton_17, 24)
        self._link_button(self.pushButton_15, 25)
        self._link_button(self.pushButton_28, 26)
        self._link_button(self.pushButton_27, 27)

        # Caps
        self.pushButton_34.clicked.connect(self._caps)
        self.pushButton_34.setCheckable(True)
        self.pushButton_34.setAutoDefault(False)


        # asdfghjkl;' return
        self._link_button(self.pushButton_42, 29)
        self._link_button(self.pushButton_41, 30)
        self._link_button(self.pushButton_40, 31)
        self._link_button(self.pushButton_39, 32)
        self._link_button(self.pushButton_38, 33)
        self._link_button(self.pushButton_37, 34)
        self._link_button(self.pushButton_36, 35)
        self._link_button(self.pushButton_35, 36)
        self._link_button(self.pushButton_33, 37)
        self._link_button(self.pushButton_32, 38)
        self._link_button(self.pushButton_31, 39)
        
        # TODO add return
        # self._link_button(self.pushButton_30, 40)
        self.pushButton_30.setAutoDefault(False)

        # Shift
        self.pushButton_54.clicked.connect(self._shift)
        self.pushButton_54.setCheckable(True)
        self.pushButton_54.setAutoDefault(False)

        # zxcvbnm,./ shift
        self._link_button(self.pushButton_53, 42)
        self._link_button(self.pushButton_52, 43)
        self._link_button(self.pushButton_51, 44)
        self._link_button(self.pushButton_50, 45)
        self._link_button(self.pushButton_49, 46)
        self._link_button(self.pushButton_48, 47)
        self._link_button(self.pushButton_47, 48)
        self._link_button(self.pushButton_46, 49)
        self._link_button(self.pushButton_45, 50)
        self._link_button(self.pushButton_44, 51)
        # Shift
        self.pushButton_43.clicked.connect(self._shift)
        self.pushButton_43.setCheckable(True)
        self.pushButton_43.setAutoDefault(False)

        # bottom row for aesthetics
        self.pushButton_55.setEnabled(False)
        self.pushButton_58.setEnabled(False)
        self.pushButton_61.setEnabled(False)
        self.pushButton_57.setEnabled(False)
        self.pushButton_56.setEnabled(False)
        self.pushButton_59.setEnabled(False)

        #Space
        self.pushButton_60.clicked.connect(self._space)
        self.pushButton_60.setAutoDefault(False)

    def keyPressEvent(self, event: QKeyEvent):
        """Handle the Key Press Event from QT.

        This event won't actually be called too frequently, since other windows / the linked line edit will 
            get focus, but this will handle the events if the keyboard window is what's focused.
        """
        self.on_key(event.text())
    
    def on_key(self, key: str):
        """Handle the input of a character key, displaying that the button is pressed on the virtual keyboard.
        
        A string key instead of QtKey is used currently because the QInputMethodEvent must also be handled
            for foreign languages, and getting the most recent text from that returns a string.

        This is written really poorly right now, as it loops over the entire keyboard (twice!) to check which 
        button should be virtually pressed. This should be updated to make this O(1). However since the number
        of buttons on the keyboard is rather small, perhaps this doesn't have much impact on performance at all.   

        Args:
            key (str): String of the key that was pressed. 
        """
        ind = -1
        for i in range(len(self.translation)):
            if not self.translation[i]: continue
            if key in self.translation[i]:
                ind = i
                break
        if ind < 0: return
        
        for button in self.buttons:
            button[0].setChecked(button[1] == ind)
            if button[1] == ind:
                QTimer.singleShot(200, lambda: button[0].setChecked(False))

# KEYBOARDS (add more in the future..)
KB_AMERICAN_QWERTY = [
# ROW 1
("`", "~"), # 0 
("1", "!"), # 1
("2", "@"), # 2
("3", "#"), # 3
("4", "$"), # 4
("5", "%"), # 5
("6", "^"), # 6
("7", "&"), # 7
("8", "*"), # 8
("9", "("), # 9
("0", ")"), # 10
("-", "_"), # 11
("=", "+"), # 12
(None), # 13 (Backspace)
# ROW 2
(None), # 14 (Tab)
("q", "Q"), # 15
("w", "W"), # 16
("e", "E"), # 17
("r", "R"), # 18
("t", "T"), # 19
("y", "Y"), # 20
("u", "U"), # 21
("i", "I"), # 22
("o", "O"), # 23
("p", "P"), # 24
("[", "{"), # 25
("]","}"), # 26
("\\","|"), # 27
# ROW 3
(None), # 28 (Caps lock)
("a", "A"), # 29
("s", "S"), # 30
("d", "D"), # 31
("f", "F"), # 32
("g", "G"), # 33
("h", "H"), # 34
("j", "J"), # 35
("k", "K"), # 36
("l", "L"), # 37
(";", ":"), # 38
("'", "\""), # 39
(None), # 40 (Return)
# Row 4
(None), # 41 (Shift)
("z", "Z"), # 42
("x", "X"), # 43
("c", "C"), # 44
("v", "V"), # 45
("b", "B"), # 46
("n", "N"), # 47
("m", "M"), # 48
(",", "<"), # 49
(".", ">"), # 50
("/", "?"), # 51
(None), # 52(Shift)
# Row 5  (Doesnt matter)
(None), # 53 (Ctrl)
(None), # 54 (Win)
(None), # 55 (Alt)
(None), # 56 (Space)
(None), # 57  (Fn)
(None), # 58 (Win)
(None) # 59 (Ctrl)
]

KB_JAPANESE_HIRAGANA = [
# ROW 1
("ろ"), # 0 
("ぬ"), # 1
("ふ"), # 2
("あ", "ぁ"), # 3
("う", "ぅ"), # 4
("え", "ぇ"), # 5
("お", "ぉ"), # 6
("や", "ゃ"), # 7
("ゆ", "ゅ"), # 8
("よ", "ょ"), # 9
("わ", "を"), # 10
("ほ", "ー"), # 11
("へ"), # 12
(None), # 13 (Backspace)
# ROW 2
(None), # 14 (Tab)
("た"), # 15
("て"), # 16
("い", "ぃ"), # 17
("す"), # 18
("か"), # 19
("ん"), # 20
("な"), # 21
("に"), # 22
("ら"), # 23
("せ"), # 24
("◌゙", "「"), # 25
("◌゚","」"), # 26
("む"), # 27
# ROW 3
(None), # 28 (Caps lock)
("ち"), # 29
("と"), # 30
("し"), # 31
("は"), # 32
("き"), # 33
("く"), # 34
("ま"), # 35
("の"), # 36
("り"), # 37
("れ"), # 38
("け"), # 39
(None), # 40 (Return)
# Row 4
(None), # 41 (Shift)
("つ", "っ"), # 42
("さ"), # 43
("そ"), # 44
("ひ"), # 45
("こ"), # 46
("み"), # 47
("も"), # 48
("ね", "、"), # 49
("る", "。"), # 50
("め", "・"), # 51
(None), # 52(Shift)
# Row 5  (Doesnt matter)
(None), # 53 (Ctrl)
(None), # 54 (Win)
(None), # 55 (Alt)
(None), # 56 (Space)
(None), # 57  (Fn)
(None), # 58 (Win)
(None) # 59 (Ctrl)
]