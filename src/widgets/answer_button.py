# Copyright: Axel Moreen, 2022
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
"""
Contains the Answer Button widget. This is used in
Matching and Multiple Choice layouts.
"""
from aqt.qt import (
    QPushButton,
    QSizePolicy,
    Qt,
    QLabel,
    QHBoxLayout,
    QWidget,
    QFont,
    QKeyEvent,
    QSize,
)
from aqt.sound import av_player

import re

# Answer Button - can display rich text and handle sound tags
# adapted from https://stackoverflow.com/questions/2990060/qt-qpushbutton-text-formatting
class AnswerButton(QPushButton):
    def __init__(self, parent: QWidget = None, text: str = None):
        """Create answer button.

        Args:
            parent (QWidget, optional): Parent widget if applicable. Defaults to None.
            text (str, optional): Text to set. Defaults to None.
        """
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
    def handle_sound(self, text: str):
        """Handle if the text is a sound tag.
        If the text is a sound tag, then replace the text with the Play button,
        and set the button to play its sound when it is clicked.

        Args:
            text (str): field text
        """
        self.sound = None
        self._isSound = False
        m = re.search("\[sound:[\w.\-]{0,}\]", text)
        if m:
            self.__lbl.setText(
                "Play  <a href='#' style='color: #32a3fa; text-decoration: none;'>▶</a>"
            )

            self.sound = m.group(0)[7:-1]
            self._isSound = True

    def setText(self, text: str):
        """Set the text string on the button,
        and handle resizing / sound if necessary.

        Args:
            text (str): Text to set.
        """
        self.__lbl.setText(text)
        self.handle_sound(text)
        self.updateGeometry()

    def set_sound(self, sound_field_text: str):
        """Set the button's sound, based on the text.

        Args:
            sound_field_text (str): Sound button
        """
        m = re.search("\[sound:[\w.\-]{0,}\]", sound_field_text)
        if m:
            self.sound = m.group(0)[7:-1]
            self._isSound = True

    def is_sound(self) -> bool:
        """True if the button contains a sound, else False."""
        return self._isSound

    def font(self) -> QFont:
        """Return the button's font."""
        return self.__lbl.font()

    def setFont(self, font: QFont):
        """Set the button's font."""
        self.__lbl.setFont(font)
        self.updateGeometry()
        self.sizeHint()

    def sizeHint(self) -> QSize:
        """Change the size of the button
        to the size of its child label.

        Returns:
            QSize: new size of the button.
        """
        s = QPushButton.sizeHint(self)
        w = self.__lbl.sizeHint()
        s.setWidth(w.width())
        s.setHeight(w.height())
        return s

    def mousePressEvent(self, event: QKeyEvent):
        """Override button presses to also include
        playing sounds.
        """
        if self._isSound:
            av_player.play_file(self.sound)
        super().mousePressEvent(event)
