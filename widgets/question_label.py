from aqt.qt import (
    Qt, 
    QLabel, 
    QWidget,
    QMouseEvent,
)
from aqt.sound import av_player
import re

# QLabel that can also accept [sound] tags. 
# default behavior is to auto-play the sound when the widget is loaded.
# shows a button style if it is a sound
# regex pattern: \[sound:[\w.\-]{0,}\]
class QuestionLabel(QLabel):
        
    def __init__(self, parent: QWidget):
        """Load question label.
        """
        super().__init__(parent)
        self._isSound = False
        self.sound = None
        self.setOpenExternalLinks(False)
        self.linkActivated.connect(self.click_handler)
        self.setTextInteractionFlags(Qt.LinksAccessibleByMouse)

    def click_handler(self, link: str):
        """Handle button clicks. It is connected to the self.linkActivated signal. 
        The link itself does not matter, because the link will always be meant to play the sound. 
        """
        if self.sound:
            av_player.play_file(self.sound)

    def setText(self, text):
        """Override QLabel setText() to handle sound tags.  

        The sound gets auto-played here, since it will be run when the question is loaded anyway. 

        If it is a sound, then the text will be replaced with a link so that the user can re-play the sound if needed.

        If it is not a sound, the text just gets set as normal. 

        Args:
            text (_type_): Text (or sound tag) for the label to handle.  
        """
        self._text = text

        m = re.search('\[sound:[\w.\-]{0,}\]', text)
        if m:
            super().setText("<a href='#' style='color: #32a3fa; text-decoration: none;'><span style='color: #fff;'>Play </span>▶</a>")
            
            self.sound = m.group(0)[7:-1]
            self._isSound = True
            
            av_player.play_file(self.sound)
        else:
            super().setText(text)

