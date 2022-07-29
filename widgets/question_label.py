from aqt.qt import Qt, QLabel
from aqt.sound import av_player
import re

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
        av_player.play_file(self.sound)

    def setText(self, text):
        
        self._text = text

        m = re.search('\[sound:[\w.\-]{0,}\]', text)
        if m:
            super().setText("<a href='#' style='color: #32a3fa; text-decoration: none;'><span style='color: #fff;'>Play </span>▶</a>")
            
            self.sound = m.group(0)[7:-1]
            self._isSound = True
            
            av_player.play_file(self.sound)
        else:
            super().setText(text)
    # TODO: add sound as an option for some fields here. i.e., optionally listening to the question in multiple choice
    def mousePressEvent(self, event):
        super().mousePressEvent(event)