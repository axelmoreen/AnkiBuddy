from aqt.qt import (
    QObject,
    QTimer
)
from aqt import mw
import aqt
from .widgets import *
from os.path import join, dirname
from .models import ListModel, HomeworkModel


class ListController(QObject):
    def __init__(self, model: ListModel):
        """Initialize List Controller for handling logic from the ListView.

        Args:
            model (ListModel): Instance of ListModel to use for data.
        """
        super().__init__()
        self.model = model

    def on_hide_front_changed(self, value: bool):
        """Connected to view's "Hide Front" checkbox. 
        """
        self.model.hide_front = bool(value)

    def on_hide_back_changed(self, value: bool):
        """Connected to view's "Hide Back" checkbox.
        """
        self.model.hide_back = bool(value)

    def cell_double_clicked(self, row: int, column: int):
        """Connected to view's main table. Handles if a cell was double-clicked,
        and then will allow the user to view the corresponding Anki card. 

        Args:
            row (int): row that was clicked
            column (int): column that was clicked
        """
        card = self.model.cards[row]
        self.cardview = SimpleCardView(card)
        self.cardview.setWindowTitle("Card - "+ self.model.note_store.deck_name)
        self.cardview.setWindowIcon(mw.windowIcon())
        self.cardview.show()

class HomeworkController(QObject):
    def __init__(self, model: HomeworkModel):
        """Initialize Homework Controller for handling logic from the HomeworkView.

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
        Asks the model for a new question, instantiates the QuestionWidget here, and sends it
        to the View for rendering.
        """
        self.model.load_new_question()
        
        self.model.corrected = False # for show answer to work properly
        self.model.has_answered = False

        if self.model.curr_question_type == 0:
            newQuestionWidget = MultipleChoiceQuestionWidget(self.model.curr_question, self.model)
        elif self.model.curr_question_type == 1:
            newQuestionWidget = MatchingWidget(self.model.curr_question, self.model)
        elif self.model.curr_question_type == 2:
            newQuestionWidget = WriteTheAnswerWidget(self.model.curr_question, self.model)

        newQuestionWidget.questionAnswered.connect(self.question_answered)
        self.widget = newQuestionWidget
        self.model.answer = newQuestionWidget.get_answer()
        self.model.new_question_update.emit(self.widget)
        
    def question_answered(self, correct: bool, multi_answer: bool):
        """Connected to the current QuestionWidget to handle the user response.
        Handles the overall logic for questions such as history, sounds, revisits.

        Depends on self.model.wait_wrong whether or not to automatically move onto the next
            question, or to pause each time and let the user press Continue or view the Card(s).
            The wait_wrong value is set either by options, if there is an audio
            field in the answers, or if the question was wrong.

        Args:
            correct (bool): True if the answer was correct, False if it was not.
            multi_answer (bool): True if the view should stay on the current question widget
                (e.g. for matching), False if the user should move onto the next question (e.g. multiple choice,
                or the last answer in matching).
        """
        # TODO: move to const
        med_dir = join(dirname(__file__), "resources")
        # handle counting
        if not self.model.has_answered:
            self.model.total_answered += 1
            if correct:
                self.model.total_correct += 1
            
            if not multi_answer: 
                self.model.has_answered = True # 

        # handle sounds
        if self.model.play_sounds and not self.model.corrected:
            if correct:
                aqt.sound.av_player.play_file("{}/correct.mp3".format(med_dir))
            else:
                aqt.sound.av_player.play_file("{}/incorrect.mp3".format(med_dir))

        # handle revisits
        if not correct and self.model.do_revisit and not self.model.has_answered:
            for i in range(self.model.revisit_steps):
                self.model.to_revisit.append(self.model.last_card)

        # allow you to press resubmit (Write the answer) to move to the next question
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

            else: # not correct, should stay on UI no matter what
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

        else: # show answer
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
            view.setWindowTitle("Card - "+ self.model.note_store.deck_name)
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

        self.model.info_update.emit()
            

