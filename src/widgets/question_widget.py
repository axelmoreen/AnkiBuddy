# Copyright: Axel Moreen, 2022
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""
Contains QuestionWidget, which is a superclass for practice question widgets.

The children are:
./question_widget_multiplechoice.py
./question_widget_matching.py
./question_widget_writeanswer.py

These widgets manage their own state and emit a signal to the parent layout
whenever an answser is given by the user. See QuestionWidget class for more
documentation.
"""

from __future__ import annotations
from typing import Any

from aqt.qt import QWidget, pyqtSignal, QKeyEvent
from ..stores import Notecard
from ..models import HomeworkModel


class QuestionWidget(QWidget):
    """Abstract class for question widgets, with some helper functions.

    Question widgets should override .load() to setup their UI.
    Sub-classes may also override .get_answer() to display a text answer when
    the Show Answer button is pressed, and .show_answer() to modify UI elements
    when the button is pressed.

    Emits questionAnswered, which is a signal connected to the Homework
    Controller to let it know when the user has answered. The widget must
    specify in questionAnswered whether the user was right or wrong,
    and if it should continue to the next question or stay on the current
    widget (i.e. it's multi-answer, in the case of matching.)

    questionAnswered args:
        correct (bool): True if the user answered correct, False if wrong
        multi_answer: True if the parent should stay on the current widget,
            False if it should continue.
    """
    questionAnswered = pyqtSignal(bool, bool)

    def __init__(self, options: dict[str, Any], model: HomeworkModel):
        """Instantiate the question widget. Options is a question model to
        build the widget from, created by the HomeworkModel.

        Args:
            options (dict[str,Any]): Dictionary of values to render the
                question from.
            model (HomeworkModel): Instance of HomeworkModel to use.
        """
        super().__init__()

        self.options = options
        self.model = model
        self.load()

    def load(self):
        """Used by sub-classes to render the widget."""
        pass

    # deprecated: use handle_font
    def set_font_size(self, ele: QWidget, size: int):
        """Helper method to set the font-size of a QWidget in one line.

        Args:
            ele (QWidget): QWidget to set the font size for.
            size (int): integer point size to set the font to.
        """
        font = ele.font()
        font.setPointSize(size)
        ele.setFont(font)

    def handle_font(self, ele: QWidget, base_size: int, field_name: str):
        """Helper method to set the font based on the field settings.
        This way, a suggested font family and size for the field can be set,
            but it can be changed based on the individual field settings set
            in the options dialog. For example, for a Japanese-English deck,
            the Japanese fields can be given a separate font and made larger
            than the English fields.

        Args:
            ele (QWidget): QWidget to set the font for.
            base_size (int): Size default for this widget.
            field_name (str): Field to get font options for. If field_name is
                not set in options, the defaults will be used.
        """
        font = ele.font()
        size = base_size
        field_opts = self.model.options_store.get_globals(
            self.model.note_store.deck_name
        )["field_settings"]
        if field_name in field_opts:
            settings = field_opts[field_name]
            size += settings[1]  # font size offset
            font.setFamily(settings[0])
        font.setPointSize(size)
        ele.setFont(font)

    def handle_field_sound(self, ele: QWidget, field_name: str,
                           card: Notecard):
        """Helper method to handle fields that should have an audio that is
        played. For labels, the audio should be auto-played when the question
        is loaded, and for buttons, the audio should be played when the button
        is pressed. Note, this is not the same as a question widget with an
        audio as the question/answer itself, as those are handled separately.
        This is for non-audio fields to have an extra audio that accompanies
        them.

        Note: Assumes QWidget has been extended to include a set_sound()
        method. This is certainly bad practice, # TODO: create a superclass to
        use for widgets that support this.

        Args:
            ele (QWidget): Element to modify.
            field_name (str): Field name for the element to check options for.
            card (Notecard): Instance of Notecard dataclass to get sound value.
        """
        field_opts = self.model.options_store.get_globals(
            self.model.note_store.deck_name
        )["field_settings"]
        if field_name in field_opts:
            audio_name = field_opts[field_name][2]
            if audio_name in card.fields:
                ele.set_sound(card.fields[audio_name])

    def on_key(self, event: QKeyEvent):
        """Handle key events that get passed from this widget's parent.

        Args:
            event (QKeyEvent): instance of QKeyEvent
        """
        pass

    def get_answer(self) -> str:
        """Returns a STRING answer for this question, which
        is placed in the answer label in the parent layout, after corrected.
        This should typically be one of the fields on the card.

        Returns:
            str: Answer to the question.
        """
        return None

    def show_answer(self):
        """Sub-classes can override this method to run code when the Show
        Answer button is pressed, as to alter UI elements to show the answer
        visually.
        """
        pass
