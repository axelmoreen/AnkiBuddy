from sys import maxunicode
from aqt import mw
from aqt.qt import *
import aqt
from PyQt5.QtWidgets import QTableWidgetItem
import random

from .forms.list import *
from .forms.practice import *
from .forms.summary import *
from .widgets import *
from .style import *

from os.path import join, dirname

# TODO: move datastore access to the ListModel
class ListView(QDialog):
    # TODO: fix terrible naming scheme.. and document
    def __init__(self, note_store, options_store, model, controller, do_subsets = True, subset = None, subset_text = None):
        super().__init__()
        self.note_store = note_store
        self.options_store = options_store
        self.controller = controller
        self.model = model
        self.do_subsets = do_subsets

        #self.widget = widget = QWidget()
        self.ui = Ui_CardList()
        self.ui.setupUi(self)
        self.setWindowTitle("List - "+note_store.deck_name)
        self.setWindowIcon(mw.windowIcon())
        dConf = options_store.get_list_config(note_store.deck_name)

        # check to see if there are no columns set in options yet
        if "columns" not in dConf:
            self._cancel()
        if len(dConf["columns"]) == 0:
            self._cancel()

        self.ui.tableWidget.setColumnCount(len(dConf["columns"]))
        self.ui.tableWidget.setHorizontalHeaderLabels([None, None])
        self.ui.tableWidget.horizontalHeader().setStretchLastSection(True)

        # load fonts
        self.fonts = {}
        #
        #for item in dConf["fonts"]:
        #    self.fonts[item[0]] = QFont(dConf["fonts"][item[0]])

        self.front = []
        for item in dConf["front"]:
            self.front.append(item)

        self.length = note_store.length()

        if not subset:
            i = 0
            self.ui.tableWidget.setRowCount(note_store.length())
            for notecard in note_store.notecards:
                for j in range(0, len(dConf["columns"])):
                    item = BTableWidgetItem(str(notecard.fields[
                        dConf["columns"][j]
                    ]))

                    self.handle_font(item, 20, dConf["columns"][j])
                    
                    self.ui.tableWidget.setCellWidget(i, j, item)
                i += 1
        # manually set subset
        else: # TODO really need to clean this up ....
            i = 0
            self.ui.tableWidget.setRowCount(len(subset))
            self.length = len(subset)
            if subset_text:
                self.ui.lessonLabel.setText(subset_text)
        
            for ele in subset:
                notecard = note_store.notecards[ele]

                for j in range(0, len(dConf["columns"])):
                    item = BTableWidgetItem(str(notecard.fields[
                        dConf["columns"][j]
                    ]))

                    self.handle_font(item, 20, dConf["columns"][j])
                    
                    self.ui.tableWidget.setCellWidget(i, j, item)
                i += 1
            # will disable the subset widgets here. 
            #self.ui.checkBox.setVisible(False)
            #self.ui.checkBox_2.setVisible(False)
            self.ui.checkBox_3.setVisible(False)
            # TODO: will soon be defunct.... 
            self.ui.pushButton_4.setVisible(False)
            self.ui.pushButton_5.setVisible(False)
            self.ui.pushButton.setVisible(False)
            #self.ui.lessonLabel.setVisible(False)
            
        self.ui.tableWidget.resizeColumnsToContents()
        self.ui.tableWidget.resizeRowsToContents()

        # setup signals to model
        self.ui.checkBox.stateChanged.connect(self.controller.on_hide_back_changed)
        self.ui.checkBox_2.stateChanged.connect(self.controller.on_hide_front_changed)
        self.ui.checkBox_3.stateChanged.connect(self.controller.on_all_lessons_changed)

        self.ui.pushButton_4.clicked.connect(self.controller.on_forward)
        self.ui.pushButton_5.clicked.connect(self.controller.on_backward)

        self.ui.pushButton.clicked.connect(self.controller.on_options)
        self.ui.pushButton_6.clicked.connect(self.on_close)

        # setup signals from model
        self.model.hide_front_changed.connect(self.on_hide_front_changed)
        self.model.hide_back_changed.connect(self.on_hide_back_changed)
        self.model.show_all_changed.connect(self.on_show_all_changed)
        self.model.lesson_changed.connect(self.on_lesson_changed)

        self.show()

    def _cancel(self):
        self._cancelMsg = QMessageBox()
        self._cancelMsg.setText("Please set-up List view in Options first.")
        self._cancelMsg.exec_() # modal popup
        
    ######
    # signals
    def on_close(self, value):
        self.close()

    def on_hide_front_changed(self, value):
        for i in range(len(self.front)):
            for j in range(self.length):
                if self.front[i]:
                    if value:
                        self.ui.tableWidget.cellWidget(j, i).hide_value()
                    else:
                        self.ui.tableWidget.cellWidget(j, i).show_value()

    def on_hide_back_changed(self, value):
        for i in range(len(self.front)):
            for j in range(self.length):
                if not self.front[i]:
                    if value:
                        self.ui.tableWidget.cellWidget(j, i).hide_value()
                    else:
                        self.ui.tableWidget.cellWidget(j, i).show_value()

    # No longer supported
    def on_show_all_changed(self, value):
        pass
    # No longer supported
    def on_lesson_changed(self, value):
        pass

    # end signals

    # TODO: copy pasted from widgets.py...
    def handle_font(self, ele, base_size, field_name):
        font = ele.font()
        size = base_size
        field_opts = self.options_store.get_globals(self.note_store.deck_name)["field_settings"]
        if field_name in field_opts:
            settings = field_opts[field_name]
            size += settings[1] # font size offset
            font.setFamily(settings[0])
        font.setPointSize(size)
        ele.setFont(font)

# TODO: move logic to the controller...
class HomeworkView(QWidget):
    def __init__(self, model):
        super().__init__()

        self.ui = Ui_Practice()
        self.ui.setupUi(self)
        self.setWindowTitle("Practice - "+model.note_store.deck_name)
        self.setWindowIcon(mw.windowIcon())
        self.model = model
        self.ui.horizontalWidget.hide()
        self.ui.pushButton.hide()
        self.ui.pushButton.clicked.connect(self.accept_wait)
        self.ui.pushButton.setStyleSheet(incorrect_button_style)
        self.next_question()

        font = self.ui.labelLeft.font()
        font.setPointSize(14)
        self.ui.labelLeft.setFont(font)
        self.ui.labelRight.setFont(font)
        font.setPointSize(20)
        self.ui.label.setFont(font)

        self.ui.labelRight.setText("--:--:--")
        self.ui.labelLeft.setText(self.model.subset.get_subset_name() +" - "+
            ("All" if self.model.subset_group == -1 else "Group "+str(self.model.subset_group))
        )
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.on_timeout)
        self.timer.start(1000)

        self.info_menu = QMenu(self)
        self.correctAction = QAction("Score: ")
        self.accuracyAction = QAction("Accuracy: ")
        self.cardsAction = QAction("Unique cards")

        # one way to disable hover... looks bad, though
        #self.correctAction.setEnabled(False) 
        #self.accuracyAction.setEnabled(False)
        #self.cardsAction.setEnabled(False)

        self.info_menu.addAction(self.correctAction)
        self.info_menu.addAction(self.accuracyAction)
        self.info_menu.addAction(self.cardsAction)
        self.answer = None
        self.ui.toolButton.setMenu(self.info_menu)

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
    
    def mousePressEvent(self, event):
        super().mousePressEvent(event)

    def next_question(self):
        # hide virtual keyboard to next question
        #if hasattr(mw, "_bKeyboard"):
            #mw._bKeyboard.showMinimized()
        self.model.load_new_question()
        self.ui.pushButton.hide()
        self.ui.pushButton.setFocusPolicy(Qt.NoFocus)
        self.ui.horizontalWidget.hide()
        self.model.corrected = False # for show answer to work properly
        self.model.has_answered = False
        #self.ui.labelLeft.setText(self.model.curr_question["type"])
        if self.model.curr_question_type == 0:
            newQuestionWidget = MultipleChoiceQuestionWidget(self.model.curr_question, self.model)
        elif self.model.curr_question_type == 1:
            newQuestionWidget = MatchingWidget(self.model.curr_question, self.model)
        elif self.model.curr_question_type == 2:
            newQuestionWidget = WriteTheAnswerWidget(self.model.curr_question, self.model)

        oldQuestionWidget = self.ui.verticalLayout.itemAt(0)
        oldQuestionWidget.widget().deleteLater()
        newQuestionWidget.questionAnswered.connect(self.question_answered)
        self.widget = newQuestionWidget
        #self.keypress = newQuestionWidget.on_key
        self.model.answer = newQuestionWidget.get_answer()
        self.ui.verticalLayout.replaceWidget(oldQuestionWidget.widget(), newQuestionWidget)
        # refocus window
        #self.setFocus(Qt.ActiveWindowFocusReason)

    
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
                self.ui.pushButton.setText("Continue")
                self.ui.label.setText("Correct")
                self.ui.horizontalWidget.show()
                self.ui.pushButton.show()
                self.widget.show_answer()
                self.model.corrected = True

            elif not self.model.wait_wrong and correct: 
                self.next_question()

            else: # not correct, should stay on UI no matter what
                self.ui.pushButton.setText("Show Answer")
                self.ui.label.setText("Incorrect!")
                self.model.corrected = False
                self.ui.horizontalWidget.show()
                self.ui.pushButton.show()
        
    def accept_wait(self):
        if self.model.corrected:
            self.next_question()

        else: # show answer
            self.ui.label.setText(self.model.answer)
            self.widget.show_answer()
            self.model.corrected = True
            self.ui.pushButton.setText("Continue")

    def on_timeout(self):
        if self.model.timed_mode > 0:
            self.model.time -= 1
        else:
            self.model.time += 1
        self.ui.labelRight.setText( (
            "-" if self.model.timed_mode > 0 else ""
        ) + 
            _sec2Time(self.model.time))

        # update tooltip
        # TODO: fix duplicate code with Summary Dialog.
        self.correctAction.setText("Score: "+
        "{}/{}".format(self.model.total_correct, self.model.total_answered))
        self.accuracyAction.setText("Accuracy: "+ "{:d}%".format(int(100 * self.model.total_correct/max(1,self.model.total_answered))))  
        self.cardsAction.setText("{} cards visited".format(len(self.model.card_history)))

        if self.model.time < 0:
            # TODO: play sound
            self.timer.stop()
            self.model.time = 0
            self.ui.labelRight.setText("Time's Up!")
            #TODO: instead of self.close(), simply just pause the screen and open dialog.
            self.close()
    
    def closeEvent(self, event):
        # TODO: display practice summary 
        dial = SummaryDialog()
        dial.load(self.model)
        dial.show()

class SummaryDialog(QDialog, Ui_Summary):
    def __init__(self):
        super(SummaryDialog, self).__init__()
        self.setupUi(self)
        #self.tableWidget.setColumnCount(2)
        #self.tableWidget.setRowCount(3)
    def load(self, hwmodel):
        self.correctLabel.setText("{}/{}".format(hwmodel.total_correct, hwmodel.total_answered))
        self.accuracyLabel.setText( "{:d}%".format(int(100 * hwmodel.total_correct/max(1,hwmodel.total_answered))))
        self.cardsLabel.setText("{} cards".format(len(hwmodel.card_history)))
        if hwmodel.timed_mode > 0: 
            self.timeLabel.setText(_sec2Time(hwmodel.timed_mode * 60 - hwmodel.time))
        else:
            self.timeLabel.setText(_sec2Time(hwmodel.time))
    def show(self):
        return self.exec_()

def _sec2Time(sec):
        hrs = sec // 3600
        sec2 = sec - 3600 * hrs
        mins = sec2 // 60
        sec3 = sec - 60 * mins  - 3600 * hrs
        return "{:02d}:{:02d}:{:02d}".format(hrs, mins, sec3)