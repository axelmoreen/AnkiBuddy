# Copyright: Axel Moreen, 2022
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""
Contains the Question Label widget. This is used in Multiple
Choice and in Write the Answer to display the question.

It was originally a subclass of QLabel, but it has been made
a subclass of AnkiWebView because QLabel rich tags don't support
ruby tags (for furigana). Could use clean-up / refactoring.
"""
from aqt.qt import (
    QWidget,
    QFont,
)
from aqt.webview import AnkiWebView
from aqt.sound import av_player
import re


# QLabel that can also accept [sound] tags.
# default behavior is to auto-play the sound when the widget is loaded.
# shows a button style if it is a sound
# regex pattern: \[sound:[\w.\-]{0,}\]
# recently was changed from QLabel to webview to support ruby tags, needs
# cleanup / further testing
class QuestionLabel(AnkiWebView):
    def __init__(self, parent: QWidget):
        """Load question label."""
        super().__init__(parent)
        self._isSound = False
        self.sound = None
        # self.setOpenExternalLinks(False)
        # self.linkActivated.connect(self.click_handler)
        # self.setTextInteractionFlags(Qt.LinksAccessibleByMouse)
        self.set_bridge_command(self.sound_req, None)

    # def click_handler(self, link: str):
    def sound_req(self, inp):
        """Handle button clicks."""
        if inp == "playsound" and self.sound:
            av_player.play_file(self.sound)

    def setText(self, text):
        """Override QLabel setText() to handle sound tags.

        The sound gets auto-played here, since it will be run when the
            question is loaded anyway.

        If it is a sound, then the text will be replaced with a link so that
            the user can re-play the sound if needed.

        If it is not a sound, the text just gets set as normal.

        Args:
            text (str): Text (or sound tag) for the label to handle.
        """
        self._text = text

        m = re.search("\[sound:[\w.\-]{0,}\]", text)
        style_string = (
            "style='position: absolute; top: 50%; width: 95%;"
            + "transform:translateY(-50%); margin: 0 auto; text-align: center;"
            + "font-size: "
            + str(4 * self.font().pointSize())
            + "px; font-family: "
            + self.font().family()
            + "'"
        )
        html_out = """
        <div>
        <p $(stylestring)>
        $(content)
        </p>
        </div>

        """
        content = "<span></span>"
        if m:
            self.sound = m.group(0)[7:-1]
            self._isSound = True
            content = (
                "<a href='#' onclick='pycmd(\"playsound\")'; "
                + "style='color: #32a3fa; text-decoration: none;"
                + "font-size: 35px;'><span style='color: #fff;'>"
                + "Play </span>▶</a>"
            )
            av_player.play_file(self.sound)
        else:
            # super().setText(text)
            text = self.handle_cloze(text)
            text = self.handle_furigana(text)
            # html_out = "<p "+style_string+">"+text+"</p>"
            content = text
        self.stdHtml(
            html_out.replace("$(stylestring)", style_string).replace(
                "$(content)", content
            )
        )

    def setFont(self, font: QFont):
        """Override QWidget's setFont() to apply the CSS to the web view.

        Args:
            font (QFont): font to set.
        """
        pass

    def handle_furigana(self, text):
        """Replace bracket notation in the parent label with html ruby tags."""

        if "[" not in text:
            return text
        to_replace = []
        # is_kanji = lambda char: u'\u3400'<= char <= u'\u4DB5' or \
        #    u'\u4E00' <= char <= u'\u9FCB' or u'\uF900' <= char <= u'\uFA6A'
        is_kanji = True
        line = (
            "<ruby style='display: inline-flex; flex-direction:"
            + "column-reverse;'><rb style='line-height: 1;"
            + "display: inline;'>{}</rb><rt style="
            + "'line-height: 1; display: inline;'>{}</rt></ruby>"
        )

        for word in text.split(" "):
            is_furi = False
            furi_start = -1
            furi_end = -1
            for i in range(len(word)):
                is_br = word[i] == "["
                if is_br:
                    for j in range(i + 1, len(word)):
                        if word[j] == "]":
                            is_furi = True
                            furi_start = i + 1
                            furi_end = j
                            break
                    # if it didn't find the end bracket,
                    # it doesn't exist in this word,
                    # so just move onto the next.
                    break

            if not is_furi or furi_start < 0 or furi_end < 0:
                continue

            # check backwards for the start of the kanji
            rkanj_str = ""
            t = i - 1

            while is_kanji(word[t]) and t > -1:
                print(word[t])
                rkanj_str += word[t]
                t -= 1

            if len(rkanj_str) < 1:
                continue
            print("replacing with furigana")
            to_replace.append(
                (
                    word[t + 1:furi_end + 1],
                    line.format(rkanj_str[::-1], word[furi_start:furi_end]),
                )
            )

        for group in to_replace:
            text = text.replace(group[0], group[1])

        return text

    def handle_cloze(self, text):
        """Handles Core2k's cloze format."""
        return text.replace("（　）", "____")
