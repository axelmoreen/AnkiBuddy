# Copyright: Axel Moreen, 2022
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""
Controllers module handles the logic for the List and
Homework UI's.

The related graphical elements are in ./views.py and
the state is held in ./models.py.

Other UI's can be found in ./dialogs/.
"""
from aqt.qt import (
    QObject,
    QTimer,
    QFileDialog,
)
from aqt import mw
import aqt
from .widgets import (
    SimpleCardView,
    MultipleChoiceQuestionWidget,
    MatchingWidget,
    WriteTheAnswerWidget,
)
from os.path import join, dirname
from .models import ListModel, HomeworkModel
from pathlib import Path


class ListController(QObject):
    """List controller handles the logic for the list view.

    This class handles signals from various parts of the List UI.
    """
    def __init__(self, model: ListModel):
        """Initialize List Controller for handling logic from the ListView.

        Args:
            model (ListModel): Instance of ListModel to use for data.
        """
        super().__init__()
        self.model = model

    def on_hide_front_changed(self, value: bool):
        """Connected to view's "Hide Front" checkbox."""
        self.model.hide_front = bool(value)

    def on_hide_back_changed(self, value: bool):
        """Connected to view's "Hide Back" checkbox."""
        self.model.hide_back = bool(value)

    def cell_double_clicked(self, row: int, column: int):
        """Connected to view's main table. Handles if a cell was
        double-clicked, and then will allow the user to view the corresponding
        Anki card.

        Args:
            row (int): row that was clicked
            column (int): column that was clicked
        """
        card = self.model.cards[row]
        self.cardview = SimpleCardView(card)
        self.cardview.setWindowTitle(
            "Card - " + self.model.note_store.deck_name)
        self.cardview.setWindowIcon(mw.windowIcon())
        self.cardview.show()

    def _to_csv(self) -> str:
        """Get a CSV string from the current data in the list model.

        Returns:
            str: CSV string
        """
        return "\n".join([",".join(row) for row in self.model.rows])

    def _to_txt(self) -> str:
        """Get a string from the current data in the list model.

        Note: Maybe it will be possible to make this output prettier in the
            future.

        Returns:
            str: Text representation of list
        """
        out = []
        for row in self.model.rows:
            row_front = []
            row_back = []
            for i in range(len(self.model.columns)):
                if self.model.front[i]:
                    row_front.append(row[i])
                else:
                    row_back.append(row[i])
            row_str = (", ".join(row_front) + " → "
                       + "(" + ", ".join(row_back) + ")")
            out.append(row_str)
        return "\n".join(out)

    def on_export_button(self):
        """Connected to the export button. Will
        prompt the user to save a file with the contents of the
        list view.
        """
        fname, type = QFileDialog.getSaveFileName(
            mw,
            "Save List",
            str(Path.home()),
            "Comma delimited (*.csv);;Text File (*.txt)",
        )
        print(self._to_txt())
        # check string is not empty
        if not fname:
            return

        # valid type
        if type.startswith("Text"):
            out = self._to_txt()
        elif type.startswith("Comma"):
            out = self._to_csv()
        else:
            return

        # write file
        with open(fname, "w", encoding="utf-8") as out_file:
            out_file.write(out)


class HomeworkController(QObject):
    """Homework controller handles logic for the main practice
    UI i.e. homework view.

    It mainly handles signals from the Question Widget with
    question_answered(), and then gives the user feedback and/or
    moves on to the next question depending on configuration,
    and if they got the question right / wrong. Does not
    make assumptions about how the question is determined
    right vs. wrong, that is determined in the Widget itself.

    Also is responsible for updating the timer.
    """
    def __init__(self, model: HomeworkModel):
        """Initialize Homework Controller for handling logic from the
        HomeworkView.

        Args:
            model (HomeworkModel): Instance of HomeworkModel to use for data.
        """
        super().__init__()
        self.model = model

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.on_timeout)
        self.timer.start(1000)

        self.answer = None

    def next_question(self):
        """Called by self (in question_answered()) to generate a new question.
        Asks the model for a new question, instantiates the QuestionWidget
        here, and sends it to the View for rendering.
        """
        self.model.load_new_question()

        self.model.corrected = False  # for show answer to work properly
        self.model.has_answered = False

        if self.model.curr_question_type == 0:
            newQuestionWidget = MultipleChoiceQuestionWidget(
                self.model.curr_question, self.model
            )
        elif self.model.curr_question_type == 1:
            newQuestionWidget = MatchingWidget(
                self.model.curr_question, self.model)
        elif self.model.curr_question_type == 2:
            newQuestionWidget = WriteTheAnswerWidget(
                self.model.curr_question, self.model
            )

        newQuestionWidget.questionAnswered.connect(self.question_answered)
        self.widget = newQuestionWidget
        self.model.answer = newQuestionWidget.get_answer()
        self.model.new_question_update.emit(self.widget)

    def question_answered(self, correct: bool, multi_answer: bool):
        """Connected to the current QuestionWidget to handle the user response.
        Handles the overall logic for questions such as history, sounds,
        revisits.

        Depends on self.model.wait_wrong whether or not to automatically move
            onto the next question, or to pause each time and let the user
            press Continue or view the Card(s).
            The wait_wrong value is set either by options, if there is an audio
            field in the answers, or if the question was wrong.

        Args:
            correct (bool): True if the answer was correct, False if not.
            multi_answer (bool): True if the view should stay on the current
                question widget (e.g. for matching), False if the user should
                move onto the next question (e.g. multiple choice, or the last
                answer in matching).
        """
        # TODO: move to const
        med_dir = join(dirname(__file__), "resources")
        # handle counting
        if not self.model.has_answered:
            self.model.total_answered += 1
            if correct:
                self.model.total_correct += 1

            if not multi_answer:
                self.model.has_answered = True  #

        # handle sounds
        if self.model.play_sounds and not self.model.corrected:
            if correct:
                aqt.sound.av_player.play_file("{}/correct.mp3".format(med_dir))
            else:
                aqt.sound.av_player.play_file(
                    "{}/incorrect.mp3".format(med_dir))

        # handle revisits
        if not correct and self.model.do_revisit and not\
                self.model.has_answered:
            for i in range(self.model.revisit_steps):
                self.model.to_revisit.append(self.model.last_card)

        # allow you to press resubmit (Write the answer) for next question
        if correct and self.model.corrected:
            self.next_question()
            return

        # handle ui changes
        if not multi_answer:
            if self.model.wait_wrong and correct:
                self.model.answer_pane_update.emit(True, 1)
                self.widget.show_answer()
                self.model.corrected = True

            elif not self.model.wait_wrong and correct:
                self.next_question()

            else:  # not correct, should stay on UI no matter what
                self.model.answer_pane_update.emit(True, 0)
                self.model.corrected = False

        self.model.info_update.emit()

    def accept_wait(self):
        """Connected to the "Continue/Show Answer" button that is shown
        when the question is wrong, or when the question is correct
        and self.model.wait_wrong == True.
        """
        if self.model.corrected:
            self.next_question()

        else:  # show answer
            self.model.answer_pane_update.emit(True, 2)
            self.widget.show_answer()
            self.model.corrected = True

    def do_cards_button(self):
        """Connected to the "Card(s)" button press to review
        the cards that were in the question.
        """
        self.web_views = []
        for card in self.model.curr_cards:
            view = SimpleCardView(card.card)
            view.setWindowTitle("Card - " + self.model.note_store.deck_name)
            view.setWindowIcon(mw.windowIcon())
            self.web_views.append(view)

        for v in self.web_views:
            v.show()

    def on_timeout(self):
        """Connected to the timer every second.
        Will change the display, and also stop the
        practice during timed mode.
        """
        if self.model.timed_mode > 0:
            self.model.time -= 1
        else:
            self.model.time += 1

        if self.model.time < 0:
            # TODO: play sound
            self.timer.stop()
            self.model.time = 0
            self.model.stop = True

        self.model.info_update.emit()
