# Copyright: Axel Moreen, 2022
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""
Contains the Multiple Choice Widget - widget for a multiple choice
question.

Widget manages its own state and passes signals to its parent. The layout is
also generated from code in this class. See ./question_widget.py for more info
about the question widgets.
"""

from .question_widget import QuestionWidget
from .answer_button import AnswerButton
from .question_label import QuestionLabel
from aqt.qt import QVBoxLayout, QGridLayout, Qt, QPushButton
from ..style import button_style, confirm_button_style


# multiple choice widget
# Shows a Question and then a # of answer buttons to press
class MultipleChoiceQuestionWidget(QuestionWidget):
    """Multiple choice widget. Shows a question label at the top,
    then gives the user N answer buttons at the bottom to choose
    the answer from.

    See QuestionWidget for more info.
    """
    def load(self):
        """Load the multiple choice widget."""
        self.conf = self.model.options_store.get_homework_config(
            self.model.note_store.deck_name
        )

        self.vlayout = QVBoxLayout(self)
        self.questionLabel = QuestionLabel(self)
        self.handle_font(
            self.questionLabel,
            self.conf["choice_question_size"],
            self.options["question_field"],
        )
        self.questionLabel.setText(self.options["question"])

        self.vlayout.addWidget(self.questionLabel)
        self.gridLayout = QGridLayout()

        self.model.last_card = self.options["question_card_ind"]
        self.buttons = []

        self.confirm_answer = self.conf["choice_confirm_answer"]
        self.last_clicked = -1
        num_ans = len(self.options["answers"])
        for i in range(num_ans):
            button = AnswerButton(text=self.options["answers"][i], parent=self)
            button.setStyleSheet(button_style)
            # self.set_font_size(button, self.conf["choice_answer_size"])
            self.handle_font(
                button, self.conf["choice_answer_size"],
                self.options["answer_field"]
            )

            button.setAutoDefault(False)
            button.setFocusPolicy(Qt.NoFocus)
            button.clicked.connect(lambda ch, i=i: self.answer_callback(i))
            button.setCheckable(True)

            self.handle_field_sound(
                button, self.options["answer_field"],
                self.options["answer_cards"][i]
            )
            # currently if buttons are allowed to have sound and not confirm
            # answer, sound may not play/might be buggy
            # but this 'if block' could be moved above the line above to create
            # that behavior.
            if button.is_sound():
                # change default behavior
                self.confirm_answer = True

            self.buttons.append(button)
            row = i // 2
            column = i % 2
            self.gridLayout.addWidget(self.buttons[i], row, column, 1, 1)
        if self.confirm_answer:
            self.confirmButton = QPushButton("Confirm Answer")
            self.confirmButton.clicked.connect(self.confirm_callback)
            self.confirmButton.setStyleSheet(confirm_button_style)
            self.set_font_size(self.confirmButton, 14)
            self.gridLayout.addWidget(self.confirmButton, 1 + (num_ans // 2),
                                      0, 1, 2)

        self.vlayout.addLayout(self.gridLayout)

    def answer_callback(self, button_ind: int):
        """Callback when one of the answer buttons was pressed.

        Args:
            button_ind (int): The index of the button that was pressed.
        """
        self.last_clicked = button_ind
        if not self.confirm_answer:
            ansind = int(self.options["correct_answer"])
            self.questionAnswered.emit(button_ind == ansind, False)
            for i in range(len(self.buttons)):
                self.buttons[i].setChecked(False)
        else:
            # show as selected, unselect rest
            for i in range(len(self.buttons)):
                self.buttons[i].setChecked(i == button_ind)

    def confirm_callback(self):
        """Callback when the Confirm answer button is pressed.
        This button is only shown when there's an audio field, or when
        "Always Confirm Answer" is enabled in the options.
        """
        if self.last_clicked == -1:
            return
        ansind = int(self.options["correct_answer"])
        self.questionAnswered.emit(self.last_clicked == ansind, False)

    def get_answer(self) -> str:
        """Get the string for the correct answer.

        Returns:
            str: Correct answer.
        """
        return self.options["answers"][self.options["correct_answer"]]

    def show_answer(self):
        """Visually show which button was the correct one by disabling
        and flattening the others. Called by the parent controller.
        """
        for i in range(len(self.buttons)):
            self.buttons[i].setEnabled(i == self.options["correct_answer"])
            self.buttons[i].setFlat(i != self.options["correct_answer"])
            self.buttons[i].setChecked(i == self.options["correct_answer"])
