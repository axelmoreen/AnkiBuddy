from aqt.qt import *
import aqt
from .widgets import *
from os.path import join, dirname


class ListController(QObject):
    def __init__(self, model):
        super().__init__()
        self.model = model

    def on_hide_front_changed(self, value):
        self.model.hide_front = bool(value)

    def on_hide_back_changed(self, value):
        self.model.hide_back = bool(value)

    def cell_double_clicked(self, row, column):
        card = self.model.cards[row]
        self.cardview = SimpleCardView(card)
        self.cardview.setWindowTitle("Card - "+ self.model.note_store.deck_name)
        self.cardview.setWindowIcon(mw.windowIcon())
        self.cardview.show()

class HomeworkController(QObject):
    def __init__(self, model):
        super().__init__()
        self.model = model

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.on_timeout)
        self.timer.start(1000)

        self.answer = None

    def next_question(self):
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
        
    def question_answered(self, correct, multi_answer):
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
        if self.model.corrected:
            self.next_question()

        else: # show answer
            self.model.answer_pane_update.emit(True, 2)
            self.widget.show_answer()
            self.model.corrected = True
            

    def do_cards_button(self):
        self.web_views = []
        for card in self.model.curr_cards:
            view = SimpleCardView(card.card)
            view.setWindowTitle("Card - "+ self.model.note_store.deck_name)
            view.setWindowIcon(mw.windowIcon())
            self.web_views.append(view)
            
        for v in self.web_views:
            v.show()
            
            
    def on_timeout(self):
        if self.model.timed_mode > 0:
            self.model.time -= 1
        else:
            self.model.time += 1
        
        if self.model.time < 0:
            # TODO: play sound
            self.timer.stop()
            self.model.time = 0

        self.model.info_update.emit()
            

