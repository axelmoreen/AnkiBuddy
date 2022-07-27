from aqt.qt import *
from aqt import mw
from PyQt5 import QtWidgets # fix....
import random
import aqt
from .style import button_style, play_anchor_style, confirm_button_style, button_style_custom_border 
import re
from .keyboards import KeyboardView, keyboard_american_qwerty, keyboard_japanese_hiragana


###########################
# WIDGETS
# Qt Widgets to be used in layouts 
##########################
# Table widget (originally used to subclass QWidgetItem, but moved to QLabel for rich text)
# - Can hide and show text without changing the layout of the table. 
class BTableWidgetItem(QLabel):
    def __init__(self, text):
        super().__init__(text)
        self._text = text
        self._isBlank = False
        
    def hide_value(self):
        self._isBlank = True
        self.setText("")

    def show_value(self):
        self._isBlank = False
        self.setText(self._text)

# QLabel that can also accept [sound] tags. 
# default behavior is to auto-play the sound when the widget is loaded.
# shows a button style if it is a sound
# regex pattern: \[sound:[\w.\-]{0,}\]
class QuestionLabel(QLabel):
        
    def __init__(self, parent):
        super().__init__(parent)
        self._isSound = False
        self.sound = None
        self.setOpenExternalLinks(False)
        self.linkActivated.connect(self.click_handler)
        self.setTextInteractionFlags(Qt.LinksAccessibleByMouse)

    def click_handler(self, link):
        aqt.sound.av_player.play_file(self.sound)

    def setText(self, text):
        
        self._text = text

        m = re.search('\[sound:[\w.\-]{0,}\]', text)
        if m:
            super().setText("<a href='#' style='color: #32a3fa; text-decoration: none;'><span style='color: #fff;'>Play </span>▶</a>")
            
            self.sound = m.group(0)[7:-1]
            self._isSound = True
            
            aqt.sound.av_player.play_file(self.sound)
        else:
            super().setText(text)
    # TODO: add sound as an option for some fields here. i.e., optionally listening to the question in multiple choice
    def mousePressEvent(self, event):
        super().mousePressEvent(event)

# Answer Button - can display rich text and handle sound tags
# adapted from https://stackoverflow.com/questions/2990060/qt-qpushbutton-text-formatting
class AnswerButton(QPushButton):
    def __init__(self, parent=None, text=None):
        if parent is not None:
            super().__init__(parent)
        else:
            super().__init__()
        self.__lbl = QLabel(self)
        if text is not None:
            self.__lbl.setText(text)
        self.__lyt = QHBoxLayout()
        self.__lyt.setContentsMargins(0, 0, 0, 0)
        self.__lyt.setSpacing(0)
        self.setLayout(self.__lyt)
        self.__lbl.setAttribute(Qt.WA_TranslucentBackground)
        self.__lbl.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.__lbl.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding,
        )
        self.__lbl.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.__lbl.setTextFormat(Qt.RichText)
        self.__lyt.addWidget(self.__lbl)
        
        self.sound = None
        self._isSound = False
        self.handle_sound(text)

    # TODO: fix duplicate [sound] tag code with QuestionLabel.
    def handle_sound(self, text):
        self.sound = None
        self._isSound = False
        m = re.search('\[sound:[\w.\-]{0,}\]', text)
        if m:
            self.__lbl.setText("Play  <a href='#' style='color: #32a3fa; text-decoration: none;'>▶</a>")
            
            self.sound = m.group(0)[7:-1]
            self._isSound = True
            
            #aqt.sound.av_player.play_file(self.sound) # don't auto-play for buttons
    def setText(self, text):
        self.__lbl.setText(text)
        self.handle_sound(text)
        self.updateGeometry()

    def set_sound(self, sound_field_text):
        m = re.search('\[sound:[\w.\-]{0,}\]', sound_field_text)
        if m:            
            self.sound = m.group(0)[7:-1]
            self._isSound = True

    def is_sound(self):
        return self._isSound
    
    def font(self):
        return self.__lbl.font()
    
    def setFont(self, font):
        self.__lbl.setFont(font)
        self.sizeHint()

    def sizeHint(self):
        s = QPushButton.sizeHint(self)
        w = self.__lbl.sizeHint()
        s.setWidth(w.width())
        s.setHeight(w.height())
        return s
    
    def mousePressEvent(self, event):
        if self._isSound:
            aqt.sound.av_player.play_file(self.sound)
        super().mousePressEvent(event)

# Line edit that passes key press events to its parent
class EventLineEdit(QLineEdit):
    def keyPressEvent(self, event):
        if self.parentWidget():
            self.parentWidget().keyPressEvent(event)
        super().keyPressEvent(event)
    def inputMethodEvent(self, event):
        if self.parentWidget():
            self.parentWidget().inputMethodEvent(event)
        super().inputMethodEvent(event)

###################################
# Question Frames
# These QWidgets display a full question and answer(s)
# To be used in a parent layout
###################################
# abstract class for question types (multiple choice, matching, write the answer)
#   to set up their UI. 
#   options = {} dict with specific schema for each type of question.
#       assumes that the right dict is passed and that the program knows how to handle it. 
class QuestionWidget(QWidget):
    # arg1 = [True, False] => "Correct", "Incorrect"
    # arg2 = [True, False] True if should continue to next question, False if should stay on the current widget. 
    questionAnswered = pyqtSignal(bool, bool)
    def __init__(self, options, model):
        super().__init__()

        self.options = options
        self.model = model
        self.load()
    
    def load(self):
        pass
        
    # deprecated: use handle_font instead
    def set_font_size(self, ele, size):
        font = ele.font()
        font.setPointSize(size)
        ele.setFont(font)
        
    def handle_font(self, ele, base_size, field_name):
        font = ele.font()
        size = base_size
        field_opts = self.model.options_store.get_globals(self.model.note_store.deck_name)["field_settings"]
        if field_name in field_opts:
            settings = field_opts[field_name]
            size += settings[1] # font size offset
            font.setFamily(settings[0])
        font.setPointSize(size)
        ele.setFont(font)

    def handle_field_sound(self, ele, field_name, card):
        field_opts = self.model.options_store.get_globals(self.model.note_store.deck_name)["field_settings"]
        if field_name in field_opts:
            audio_name = field_opts[field_name][2]
            if audio_name in card.fields:
                ele.set_sound(card.fields[audio_name])
    def on_key(self, event): # event passed from parent
        pass

    def get_answer(self):
        return None

    def show_answer(self):
        pass

# multiple choice widget 
# Shows a Question and then a # of answer buttons to press 
class MultipleChoiceQuestionWidget(QuestionWidget):
    def load(self):
        self.conf = self.model.options_store.get_homework_config(self.model.note_store.deck_name)

        self.vlayout = QtWidgets.QVBoxLayout(self)
        self.questionLabel = QuestionLabel(self)
        self.questionLabel.setText(self.options["question"])
        #self.set_font_size(self.questionLabel, self.conf["choice_question_size"])
        self.handle_font(self.questionLabel, 
            self.conf["choice_question_size"], self.options["question_field"])
        self.questionLabel.setAlignment(Qt.AlignCenter)
        
        self.questionLabel.setTextFormat(Qt.RichText)
        self.vlayout.addWidget(self.questionLabel)
        self.gridLayout = QtWidgets.QGridLayout()
        
        self.model.last_card = self.options["question_card_ind"]
        self.buttons = []
        
        self.confirm_answer = self.conf["choice_confirm_answer"]
        self.last_clicked = -1
        num_ans = len(self.options["answers"])
        for i in range(num_ans):
            button =  AnswerButton(text=self.options["answers"][i], parent=self)
            button.setStyleSheet(button_style)
            #self.set_font_size(button, self.conf["choice_answer_size"])
            self.handle_font(button, 
                self.conf["choice_answer_size"], self.options["answer_field"])
            
            button.setAutoDefault(False)
            button.setFocusPolicy(Qt.NoFocus)
            button.clicked.connect(lambda ch, i=i:self.answer_callback(i))
            button.setCheckable(True)
            
            self.handle_field_sound(button, self.options["answer_field"], self.options["answer_cards"][i])
            # currently if buttons are allowed to have sound and not confirm answer, sound may not play/might be buggy
            # but this if block could be moved above the line above to create that behavior. 
            if button.is_sound():
                # change default behavior
                self.confirm_answer = True
            
            self.buttons.append(button)
            row = i // 2
            column = i % 2
            self.gridLayout.addWidget(self.buttons[i], row, column, 1, 1)
        if self.confirm_answer:
            self.confirmButton = QtWidgets.QPushButton("Confirm Answer")
            self.confirmButton.clicked.connect(self.confirm_callback)
            self.confirmButton.setStyleSheet(confirm_button_style)
            self.set_font_size(self.confirmButton, 14)
            self.gridLayout.addWidget(self.confirmButton, 1 + (num_ans // 2), 0, 1, 2)
            
        self.vlayout.addLayout(self.gridLayout)

    def answer_callback(self, button_ind):
        self.last_clicked = button_ind
        if not self.confirm_answer:
            ansind = int(self.options["correct_answer"])
            self.questionAnswered.emit(button_ind == ansind, False)
        else:
            # show as selected, unselect rest
            for i in range(len(self.buttons)):
                self.buttons[i].setChecked(i == button_ind)
    def confirm_callback(self):
        if self.last_clicked == -1:
            return
        ansind = int(self.options["correct_answer"])
        self.questionAnswered.emit(self.last_clicked == ansind, False)

    def get_answer(self):
        return self.options["answers"][self.options["correct_answer"]]
    
    def show_answer(self):
        # highlight the button that is correct
        for i in range(len(self.buttons)):
            self.buttons[i].setEnabled(i == self.options["correct_answer"])
            self.buttons[i].setFlat(i != self.options["correct_answer"])
            self.buttons[i].setChecked(i == self.options["correct_answer"])
# Matching widget
# Shows two columns of buttons to match
class MatchingWidget(QuestionWidget):
    def load(self):
        self.conf = self.model.options_store.get_homework_config(self.model.note_store.deck_name)
        self.left_layout = QtWidgets.QVBoxLayout()
        self.right_layout = QtWidgets.QVBoxLayout()

        self.gridLayout = QtWidgets.QGridLayout(self)
        self.gridLayout.addLayout(self.left_layout, 0, 0, 10, 1)
        self.gridLayout.addLayout(self.right_layout, 0, 1, 10, 1)
        # build randomized mapping 
        self.size = len(self.options["questions"])

        self.order = [i for i in range(self.size)]
        random.shuffle(self.order)

        # assume len(questions) = len(answers)
        self.l_buttons = []
        self.r_buttons = []
        for i in range(self.size):
            buttonL = AnswerButton(text=self.options["questions"][i], parent=self)
            buttonL.clicked.connect(lambda ch, i=i:self.left_callback(i))
            buttonL.setStyleSheet(button_style)
            buttonL.setAutoDefault(False)
            buttonL.setFocusPolicy(Qt.NoFocus)

            self.handle_font(buttonL, self.conf["matching_answer_size"],
                self.options["question_field"])
            self.handle_field_sound(buttonL, self.options["question_field"], self.options["cards"][i])
            self.l_buttons.append(buttonL)
            self.left_layout.addWidget(self.l_buttons[i])

            buttonR = AnswerButton(text=self.options["answers"][self.order[i]], parent=self)
            buttonR.clicked.connect(lambda ch, i=i:self.right_callback(i))
            buttonR.setStyleSheet(button_style)
            buttonR.setAutoDefault(False)
            buttonR.setFocusPolicy(Qt.NoFocus)

            self.handle_font(buttonR, self.conf["matching_answer_size"],
                self.options["answer_field"])
            self.handle_field_sound(buttonR, self.options["answer_field"], self.options["cards"][self.order[i]])
            self.r_buttons.append(buttonR)
            self.right_layout.addWidget(self.r_buttons[i])

        self.sel_left = -1
        self.sel_right = -1
        self.answered = []

    def unsel_buttons(self):
        if self.sel_left > -1:
            buttonL = self.l_buttons[self.sel_left]      
            buttonL.setEnabled(True)
            self.sel_left = -1
        if self.sel_right > -1:
            buttonR = self.r_buttons[self.sel_right]
            buttonR.setEnabled(True)
            self.sel_right = -1  

    def left_callback(self, i):
        button = self.l_buttons[i]
        button.setEnabled(False)
        # try match first
        if self.sel_right > -1:
            self.sel_left = i
            self.model.last_card = self.options["cards_inds"][i]
            if self.order[self.sel_right] == i: # correct
                self.answered.append(i)
                self.questionAnswered.emit(True, len(self.answered) < self.size)

                button2 = self.r_buttons[self.sel_right]
                button.setFlat(True)
                button2.setFlat(True)
                button.setEnabled(False)
                button2.setEnabled(False)
                self.sel_left = -1
                self.sel_right = -1
                
            else:
                self.questionAnswered.emit(False, True)
                self.unsel_buttons()
            
        # right is not selected
        else:
            if self.sel_left > -1:
                self.l_buttons[self.sel_left].setEnabled(True)
            self.sel_left = i
            
    def right_callback(self, i):
        button = self.r_buttons[i]
        button.setEnabled(False)
        # try match
        if self.sel_left > -1:
            self.sel_right = i
            self.model.last_card = self.options["cards_inds"][self.order[i]]
            if self.order[i] == self.sel_left: # correct
                self.answered.append(self.sel_left)
                self.questionAnswered.emit(True, len(self.answered) < self.size)
                button2 = self.l_buttons[self.sel_left]
                button.setFlat(True)
                button2.setFlat(True)
                button.setEnabled(False)
                button2.setEnabled(False)
                self.sel_left = -1
                self.sel_right = -1
            else:
                self.questionAnswered.emit(False, True)
                self.unsel_buttons()

        # left is not selected
        else:
            if self.sel_right > -1:
                self.r_buttons[self.sel_right].setEnabled(True)
            self.sel_right = i
    # use mouse-clicks that are unhandled by a child widget to clear current selection
    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.unsel_buttons()

    def show_answer(self):
        used_cols = []
        for i in range(len(self.l_buttons)):
            buttonL = self.l_buttons[i]
            buttonR = self.r_buttons[self.order[i]]

            # pick a color
            r = lambda: random.randint(0,255)
            # try to avoid similar colors...
            d = lambda col1, col2, i: (col1[i]- col2[i]) ** 2  
            su_sq = lambda col1, col2: d(col1,col2, 0) + d(col1,col2, 1) + d(col1, col2, 2)
            min_sq_dist = 350
            def valid_col(col, col_array):
                for other in col_array:
                    if su_sq(col, other) < min_sq_dist:
                        return False
                return True
            col_pick = (r(),r(),r())
            i = 0
            while not valid_col(col_pick, used_cols):
                col_pick = (r(), r(), r())
                i += 1
                if i > 50: break # don't know how else to prevent infinite recursion here..
                    
            used_cols.append(col_pick)
            col = '#%02X%02X%02X' % col_pick
            buttonL.setStyleSheet(button_style_custom_border % col)
            buttonR.setStyleSheet(button_style_custom_border % col)
            buttonL.setFlat(False)
            buttonR.setFlat(False)
            buttonL.setEnabled(True)
            buttonR.setEnabled(True)
            buttonL.clicked.disconnect()
            buttonR.clicked.disconnect()
            buttonL.setCheckable(False)
            buttonR.setCheckable(False)
            buttonL.setChecked(False)
            buttonR.setChecked(False)


# Write the answer widget
# Shows a question at the top and you must write the answer in the line edit
# Support for japanese learners to use a "virtual keyboard" to help learn how to type with IME, or to entirely replace the keyboard with virtual buttons 
# - planned pinyin support
class WriteTheAnswerWidget(QuestionWidget):
    def load(self):
        self.conf = self.model.options_store.get_homework_config(self.model.note_store.deck_name)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.questionLabel = QuestionLabel(self)
        self.questionLabel.setText(self.options["question"])
        self.questionLabel.setAlignment(Qt.AlignCenter)
        self.questionLabel.setTextFormat(Qt.RichText)

        #self.set_font_size(self.questionLabel, 30)
        self.handle_font(self.questionLabel, self.conf["write_question_size"],
            self.options["question_field"])
        self.ansLayout = QtWidgets.QHBoxLayout()
        self.ansBox = EventLineEdit()
        self.ansBox.setFixedHeight(60)
        self.model.last_card = self.options["card_ind"]
        self.ansBox.returnPressed.connect(self.submit_callback)
        self.set_font_size(self.ansBox, 20)
        #self.set_font_size(self.ansBox, self.conf["write_question_size"])
        #self.handle_font(self.ansBox, self.conf["write_question_size"], 
        #    self.options["question_field"])

        self.ansSubmit = QtWidgets.QPushButton()
        self.ansSubmit.setFixedHeight(60)
        self.ansSubmit.setText("Submit")
        self.ansSubmit.setFocusPolicy(Qt.NoFocus)
        # self.ansSubmit.setAutoDefault(True)
        self.set_font_size(self.ansSubmit, 15)
        self.ansSubmit.setStyleSheet(confirm_button_style)
        self.ansSubmit.clicked.connect(self.submit_callback)
        self.ansLayout.addWidget(self.ansBox)
        self.ansLayout.addWidget(self.ansSubmit)
        self.layout.addWidget(self.questionLabel)
        self.layout.addLayout(self.ansLayout)
        self.ansBox.setFocusPolicy(Qt.StrongFocus)
        self.show_keyboard = self.conf["write_show_keyboard"]
        if self.show_keyboard:
            if not hasattr(mw, "_bKeyboard"):
                if self.conf["write_keyboard_type"] == 0:
                    mw._bKeyboard = KeyboardView(translation=keyboard_japanese_hiragana)
                
            if not mw._bKeyboard.isVisible():
                mw._bKeyboard.showNormal()
            mw._bKeyboard.link_field(self.ansBox)

        QTimer.singleShot(0, lambda: self.ansBox.setFocus(True))

    def submit_callback(self):
        text = self.ansBox.text()
        self.questionAnswered.emit(text.casefold() == self.options["answer"].casefold(), False)
    
    # sending key events to virtual keyboard to display key strokes
    def on_key(self, event):
        if self.show_keyboard:
            # TODO: support caps shift etc
            if len(event.text()) > 0:
                mw._bKeyboard.on_key(event.text())

    # sending ime events to virtual keyboard to display key strokes
    def inputMethodEvent(self, event):
        if self.show_keyboard:
            mw._bKeyboard.on_key(event.preeditString()[-1:])

    def keyPressEvent(self, event):
        self.on_key(event)

    def get_answer(self):
        return self.options["answer"]

