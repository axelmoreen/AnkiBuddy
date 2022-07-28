from aqt.qt import *
from .widgets import *
from os.path import join, dirname
from aqt.webview import AnkiWebView
from anki.sound import SoundOrVideoTag
from aqt.sound import av_refs_to_play_icons, av_player

class ListController(QObject):
    def __init__(self, model):
        super().__init__()
        self.model = model

    @pyqtSlot(int)
    def on_hide_front_changed(self, value):
        self.model.hide_front = bool(value)

    @pyqtSlot(int)
    def on_hide_back_changed(self, value):
        self.model.hide_back = bool(value)

    @pyqtSlot(int)
    def on_all_lessons_changed(self, value):
        self.model.show_all = bool(value)

    # deprecated
    @pyqtSlot(bool)
    def on_options(self, value):
        pass

    # deprecated
    @pyqtSlot(bool)
    def on_forward(self, value):
        if not self.model.show_all:
            self.model.lesson = self.model.lesson + 1
    
    # deprecated
    @pyqtSlot(bool)
    def on_backward(self, value):
        if not self.model.show_all:
            self.model.lesson = self.model.lesson - 1

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
            view = AnkiWebView()
            view.card = card.card

            html = card.card.answer()
            html = av_refs_to_play_icons(html)

            # a weird way to fix a bug
            # for some reason, to use the default pycmd (e.g. play:a:0) 
            #   and setting separate bridge commands
            # results in them all playing the same audio
            # ONLY if the webviews are created in the same method scope 
            # (i.e. after a Matching question)   
            html= html.replace("play:a:0", "play:"+view.card.answer_av_tags()[0].filename)
            html = html.replace("play:a:1", "play:"+view.card.answer_av_tags()[1].filename)

            view.stdHtml(html,
                css=["css/reviewer.css"],
                js=[
                    "js/mathjax.js",
                    "js/vendor/mathjax/tex-chtml.js",
                    "js/reviewer.js",
                ]
            )
            def play_tag(inp):
                play, tag = inp.split(":")
                av_player.play_tags([SoundOrVideoTag(tag)])
            
            view.set_bridge_command(play_tag, view)

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
            

