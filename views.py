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
    def __init__(self, note_store, option_store, model, controller, do_subsets = True, subset = None):
        super().__init__()
        self.note_store = note_store
        self.option_store = option_store
        self.controller = controller
        self.model = model
        self.do_subsets = do_subsets

        #self.widget = widget = QWidget()
        self.ui = Ui_CardList()
        self.ui.setupUi(self)
        self.setWindowTitle("List - "+note_store.deck_name)
        self.setWindowIcon(mw.windowIcon())
        dConf = option_store.get_list_config(note_store.deck_name)

        self.ui.tableWidget.setColumnCount(len(dConf["columns"]))
        self.ui.tableWidget.setHorizontalHeaderLabels([None, None])
        self.ui.tableWidget.horizontalHeader().setStretchLastSection(True)

        # load fonts
        self.fonts = {}

        for item in dConf["fonts"]:
            self.fonts[item[0]] = QFont(dConf["fonts"][item[0]])

        self.front = []
        for item in dConf["front"]:
            self.front.append(item)
        # TODO: save preference to either start with all lessons or start with groups 
        # load all lessons into table
        
        if not subset:
            i = 0
            self.ui.tableWidget.setRowCount(note_store.length())
            for notecard in note_store.notecards:
                for j in range(0, len(dConf["columns"])):
                    item = BTableWidgetItem(str(notecard.fields[
                        dConf["columns"][j]
                    ]))
                    if str(j) in self.fonts:
                        item.setFont(self.fonts[str(j)])
                    
                    if str(j) in dConf["font-sizes"]:
                        f = item.font()
                        f.setPointSize(dConf["font-sizes"][str(j)])
                        item.setFont(f)
                    
                    #self.ui.tableWidget.setItem(i, j, item)
                    self.ui.tableWidget.setCellWidget(i, j, item)
                i += 1
        else: # TODO really need to clean this up ....
            i = 0
            self.ui.tableWidget.setRowCount(len(subset))
            for ele in subset:
                notecard = note_store.notecards[ele]

                for j in range(0, len(dConf["columns"])):
                    item = QTableWidgetItem(str(notecard.fields[
                        dConf["columns"][j]
                    ]))
                    if str(j) in self.fonts:
                        item.setFont(self.fonts[str(j)])
                    # TODO: use global font format
                    if str(j) in dConf["font-sizes"]:
                        f = item.font()
                        f.setPointSize(dConf["font-sizes"][str(j)])
                        item.setFont(f)
                    
                    self.ui.tableWidget.setItem(i, j, item)
                i += 1
            # will disable the subset widgets here. 
            self.ui.checkBox.setVisible(False)
            self.ui.checkBox_2.setVisible(False)
            self.ui.checkBox_3.setVisible(False)
            # TODO: will soon be defunct.... 
            self.ui.pushButton_4.setVisible(False)
            self.ui.pushButton_5.setVisible(False)
            self.ui.pushButton.setVisible(False)
            self.ui.lessonLabel.setVisible(False)
            
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
    
    ######
    # signals
    def on_close(self, value):
        self.close()

    # todo: validate length of front [] so it does not throw error on too many columns input 
    def on_hide_front_changed(self, value):
        for i in range(len(self.front)):
            for j in range(self.note_store.length()):
                if self.front[i] == 1:
                    if value:
                        #self.ui.tableWidget.item(j, i).hide_value()
                        self.ui.tableWidget.cellWidget(j, i).hide_value()
                    else:
                        #self.ui.tableWidget.item(j, i).show_value()
                        self.ui.tableWidget.cellWidget(j, i).show_value()

    def on_hide_back_changed(self, value):
        for i in range(len(self.front)):
            for j in range(self.note_store.length()):
                if self.front[i] == 0:
                    if value:
                        #self.ui.tableWidget.item(j, i).hide_value()
                        self.ui.tableWidget.cellWidget(j, i).hide_value()
                    else:
                        #self.ui.tableWidget.item(j, i).show_value()
                        self.ui.tableWidget.cellWidget(j, i).show_value()

    def on_show_all_changed(self, value):
        print("show all")

    def on_lesson_changed(self, value):
        print("lesson changed to: "+str(value))

    # end signals


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
        # TODO: get rid of this as it currently causes console spam since it doesnt work
        #self.keypress = lambda x: print("AnkiBuddy Warning: keypress event not loaded?")
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
        #self.ui.labelLeft.setText(self.model.curr_question["type"])
        if self.model.curr_question_type == 0:
            newQuestionWidget = MultipleChoiceQuestionWidget(self.model.curr_question)
        elif self.model.curr_question_type == 1:
            newQuestionWidget = MatchingWidget(self.model.curr_question)
        elif self.model.curr_question_type == 2:
            newQuestionWidget = WriteTheAnswerWidget(self.model.curr_question)

        oldQuestionWidget = self.ui.verticalLayout.itemAt(0)
        oldQuestionWidget.widget().deleteLater()
        newQuestionWidget.questionAnswered.connect(self.question_answered)
        #self.keypress = newQuestionWidget.on_key
        self.model.answer = newQuestionWidget.show_answer()
        self.ui.verticalLayout.replaceWidget(oldQuestionWidget.widget(), newQuestionWidget)
        # refocus window
        #self.setFocus(Qt.ActiveWindowFocusReason)
    def question_answered(self, correct, next):
        med_dir = join(dirname(__file__), "resources")
        if not self.model.corrected:
            self.model.total_answered += 1
        if correct:
            if not self.model.corrected:
                aqt.sound.av_player.play_file("{}/correct.mp3".format(med_dir))
                self.model.total_correct += 1
                if next:
                    self.model.corrected = True
            elif self.model.wait_wrong and next:
                if self.model.corrected:
                    self.next_question()     
                # wait for pushbutton
                self.ui.pushButton.setText("Continue")
                self.ui.label.setText("Correct")
                self.ui.horizontalWidget.show()
                self.ui.pushButton.show()
            if next:
                self.next_question()
            
        else:
            aqt.sound.av_player.play_file("{}/incorrect.mp3".format(med_dir))
            self.model.wait_wrong = True
            self.ui.horizontalWidget.show()
            self.ui.label.setText("Incorrect!")
            if self.model.answer: # None or set by widget, will tell you answer if you're wrong
                self.ui.pushButton.setText("Show Answer")
                self.ui.pushButton.show()
                self.model.corrected = False

    def accept_wait(self):
        if self.model.corrected:
            self.next_question()

        else: # show answer
            self.ui.label.setText(self.model.answer)
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
            print("Times up!!!!")
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
        print("Exited homework view")
        print(event)

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