# Copyright: Axel Moreen, 2022
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""
Convenience class for importing these widgets.
"""

# Elements
from .answer_button import AnswerButton
from .event_line_edit import EventLineEdit
from .question_label import QuestionLabel
from .simple_card import SimpleCardView
from .table_widget import BTableWidgetItem

# Question Frames
# These QWidgets display a full question and answer(s)
# To be used in a parent layout
from .question_widget import QuestionWidget
from .question_widget_multiplechoice import MultipleChoiceQuestionWidget
from .question_widget_matching import MatchingWidget
from .question_widget_writeanswer import WriteTheAnswerWidget
