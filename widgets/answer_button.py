from aqt.qt import (
    QPushButton, 
    QSizePolicy, 
    Qt,
    QLabel,
    QHBoxLayout
)
from aqt.sound import av_player

import re

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

    # TODO: fix duplicate [sound] tag code with QuestionLabel.?
    def handle_sound(self, text):
        self.sound = None
        self._isSound = False
        m = re.search('\[sound:[\w.\-]{0,}\]', text)
        if m:
            self.__lbl.setText("Play  <a href='#' style='color: #32a3fa; text-decoration: none;'>▶</a>")
            
            self.sound = m.group(0)[7:-1]
            self._isSound = True
            
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
        self.updateGeometry()
        self.sizeHint()

    def sizeHint(self):
        s = QPushButton.sizeHint(self)
        w = self.__lbl.sizeHint()
        s.setWidth(w.width())
        s.setHeight(w.height())
        return s
    
    def mousePressEvent(self, event):
        if self._isSound:
            av_player.play_file(self.sound)
        super().mousePressEvent(event)
