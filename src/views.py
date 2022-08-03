# Copyright: Axel Moreen, 2022
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""
Views module, containing the graphical elements of the List and Practice UI's.
The logic for these views are in ./controllers.py and the data
is in ./models.py. The data stores referenced here are in ./stores.py.

Note: Other UI's, such as the main homework wizard, are currently under
the /dialogs/ folder.
"""
from aqt import mw
from aqt.qt import (
    QDialog,
    QWidget,
    QMessageBox,
    QMenu,
    QAction,
    QCloseEvent,
    Qt
)

from .widgets import BTableWidgetItem, QuestionWidget
from .forms.list import Ui_CardList
from .forms.practice import Ui_Practice
from .forms.summary import Ui_Summary
from .models import ListModel, HomeworkModel
from .controllers import ListController, HomeworkController

from .style import incorrect_button_style


class ListView(QDialog):
    def __init__(self, model: ListModel, controller: ListController):
        """Creates a window that simply shows the notecards in a tabular
        format, for manual review. Has a hide front / hide back feature
        for quick and easy practice.

        Note: Currently requires columns be set in the option store, which
            means manually using the options dialog for setup.
        Args:
            model (ListModel): instance of ListModel to load data from
            controller (ListController): instance of ListController to handle
                logic.
        """
        super().__init__()

        self.controller = controller
        self.model = model

        self.ui = Ui_CardList()
        self.ui.setupUi(self)
        self.setWindowTitle("List - " + self.model.note_store.deck_name)
        self.setWindowIcon(mw.windowIcon())

        if self.model.subset_text:
            self.ui.lessonLabel.setText(self.model.subset_text)

        self.ui.tableWidget.setColumnCount(self.model.column_count)
        self.ui.tableWidget.setHorizontalHeaderLabels([None, None])
        self.ui.tableWidget.horizontalHeader().setStretchLastSection(True)

        self.ui.tableWidget.setRowCount(len(self.model.rows))

        for i in range(len(self.model.rows)):
            row = self.model.rows[i]
            for j in range(len(row)):
                item = BTableWidgetItem(row[j])
                self.handle_font(item, 20, self.model.columns[j])
                self.ui.tableWidget.setCellWidget(i, j, item)

        self.ui.tableWidget.resizeColumnsToContents()
        self.ui.tableWidget.resizeRowsToContents()

        self.ui.checkBox_3.setVisible(False)
        # TODO: remove from .ui
        self.ui.pushButton_4.setVisible(False)
        self.ui.pushButton_5.setVisible(False)
        self.ui.pushButton.setVisible(False)

        # signals

        self.ui.checkBox.stateChanged.connect(
            self.controller.on_hide_back_changed)
        self.ui.checkBox_2.stateChanged.connect(
            self.controller.on_hide_front_changed)
        self.ui.pushButton_6.clicked.connect(self.on_close)

        self.ui.tableWidget.cellDoubleClicked.connect(
            self.controller.cell_double_clicked
        )

        self.model.show_cancel_dialog.connect(self._cancel)
        self.model.hide_front_changed.connect(self.handle_hide_front_changed)
        self.model.hide_back_changed.connect(self.handle_hide_back_changed)

        self.ui.exportButton.clicked.connect(self.controller.on_export_button)

        self.show()

    def _cancel(self):
        """Tell the user that the list has not been set up
        in the options dialog yet.
        """
        self._cancelMsg = QMessageBox()
        self._cancelMsg.setText("Please set-up List view in Options first.")
        self._cancelMsg.exec_()  # modal popup

    ######
    # signals
    def on_close(self):
        """Handle signal from the "Close" button."""
        self.close()

    def handle_hide_front_changed(self, value: bool):
        """Handle signal from the model to hide/show the front columns.

        Args:
            value (bool): True if should hide the front columns.
        """
        for i in range(len(self.model.front)):
            for j in range(self.model.length):
                if self.model.front[i]:
                    if value:
                        self.ui.tableWidget.cellWidget(j, i).hide_value()
                    else:
                        self.ui.tableWidget.cellWidget(j, i).show_value()

    def handle_hide_back_changed(self, value: bool):
        """Handle signal form the model to hide/show the back columns.

        Args:
            value (bool): True if should hide the back columns.
        """
        for i in range(len(self.model.front)):
            for j in range(self.model.length):
                if not self.model.front[i]:
                    if value:
                        self.ui.tableWidget.cellWidget(j, i).hide_value()
                    else:
                        self.ui.tableWidget.cellWidget(j, i).show_value()

    def handle_font(self, ele: QWidget, base_size: int, field_name: str):
        """Internal method to set a QWidget's font based on the field-specific
        options set in the Options dialog

        Args:
            ele (QWidget): Element whose font to modify
            base_size (int): Base (recommended) size for this element
            field_name (str): Name of the model's field to get options for
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


class HomeworkView(QWidget):
    def __init__(self, model: HomeworkModel, controller: HomeworkController):
        """Initialize homework (practice) view.

        Args:
            model (HomeworkModel): Homework model class for data
            controller (HomeworkController): Homework controller class
        """
        super().__init__()

        self.ui = Ui_Practice()
        self.ui.setupUi(self)
        self.setWindowTitle("Practice - " + model.note_store.deck_name)
        self.setWindowIcon(mw.windowIcon())
        self.model = model
        self.controller = controller

        self.ui.horizontalWidget.hide()
        self.ui.pushButton.hide()
        self.ui.pushButton.clicked.connect(self.controller.accept_wait)
        self.ui.pushButton.setStyleSheet(incorrect_button_style)
        self.ui.cardsButton.setStyleSheet(incorrect_button_style)
        self.ui.cardsButton.clicked.connect(self.controller.do_cards_button)

        font = self.ui.labelLeft.font()
        font.setPointSize(14)
        self.ui.labelLeft.setFont(font)
        self.ui.labelRight.setFont(font)
        font.setPointSize(16)  # Note: answer gets made this size currently
        self.ui.label.setFont(font)

        self.ui.labelRight.setText("--:--:--")
        self.ui.labelLeft.setText(
            self.model.subset.get_subset_name()
            + " - "
            + (
                "All"
                if self.model.subset_group == -1
                else "Group " + str(self.model.subset_group)
            )
        )

        self.info_menu = QMenu(self)
        self.correctAction = QAction("Score: ")
        self.accuracyAction = QAction("Accuracy: ")
        self.cardsAction = QAction("Unique cards")

        # one way to disable hover... looks bad, though
        # self.correctAction.setEnabled(False)
        # self.accuracyAction.setEnabled(False)
        # self.cardsAction.setEnabled(False)

        self.info_menu.addAction(self.correctAction)
        self.info_menu.addAction(self.accuracyAction)
        self.info_menu.addAction(self.cardsAction)

        self.ui.toolButton.setMenu(self.info_menu)

        self.model.info_update.connect(self.info_update_handler)
        self.model.answer_pane_update.connect(self.answer_pane_handler)
        self.model.new_question_update.connect(self.new_question_handler)

        self.controller.next_question()

    def closeEvent(self, event: QCloseEvent):
        """Override QT's default window close behavior.

        Args:
            event (QCloseEvent): Qt's close event
        """
        dial = SummaryDialog()
        dial.load(self.model)
        dial.show()

    def info_update_handler(self):
        """Update progress summary with information from the model
        such as time and score.
        This is connected to a signal from the model.
        """
        self.correctAction.setText(
            "Score: "
            + "{}/{}".format(
                self.model.total_correct, self.model.total_answered)
        )
        self.accuracyAction.setText(
            "Accuracy: "
            + "{:d}%".format(
                int(100 * self.model.total_correct / max(
                    1, self.model.total_answered))
            )
        )
        self.cardsAction.setText(
            "{} cards visited".format(len(self.model.card_history))
        )

        self.ui.labelRight.setText(
            ("-" if self.model.timed_mode > 0 else "")
            + _sec2Time(self.model.time)
        )

        if self.model.stop:
            self.ui.labelRight.setText("Time's Up!")
            # TODO: instead of self.close(), pause the screen
            self.close()

    # CORRECT: 0 = wrong, 1 = right, 2 = show answer
    def answer_pane_handler(self, show_pane: bool, correct: int):
        """Handle the bottom bar answer pane with feedback for the user
        if they answered correctly / incorrectly.

        The three main states of the answer pane, and what they should display:
        0. Incorrect - Show Answer [they tried to answer and got it wrong,
            so show a "Show Answer" button or let them try again]
        1. Correct - Continue [they answered correctly and program should
            pause, so show a "Continue" button to move on]
        2. Shown Answer - Continue [they pressed Show Answer and program will
            pause, show a "Continue" button to move on]

        By default, the add-on should move on to the next question (i.e. not
        show the Continue button) unless:
        1. Pausing before the next question is enabled in the options
        2. There is an audio field present in the Answers
        3. The user got the question wrong

        Args:
            show_pane (bool): True to display message below question,
                False to hide.
            correct (int): Integer from 0-2 containing state of the answer
                pane. See the example in this docstring.
        """
        if show_pane:
            self.ui.horizontalWidget.show()
            if correct == 0:
                self.ui.pushButton.setText("Show Answer")
                self.ui.label.setText("Incorrect!")
                self.ui.cardsButton.hide()
                self.ui.pushButton.show()
            elif correct == 1:
                self.ui.pushButton.setText("Continue")
                self.ui.label.setText("Correct")
                self.ui.pushButton.show()
                self.ui.cardsButton.show()
            else:  # correct == 2
                self.ui.label.setText(self.model.answer)
                self.ui.cardsButton.show()
                self.ui.pushButton.setText("Continue")
        else:
            self.ui.horizontalWidget.hide()

    def new_question_handler(self, widget: QuestionWidget):
        """Replace the old question widget with a new one in the layout.
        Called from the model when a new question has started.

        Args:
            widget (QuestionWidget): A QuestionWidget to place in the layout.
        """
        self.ui.pushButton.hide()
        self.ui.pushButton.setFocusPolicy(Qt.NoFocus)
        self.ui.horizontalWidget.hide()

        oldQuestionWidget = self.ui.verticalLayout.itemAt(0)
        oldQuestionWidget.widget().deleteLater()

        self.ui.verticalLayout.replaceWidget(
            oldQuestionWidget.widget(), widget)


class SummaryDialog(QDialog, Ui_Summary):
    def __init__(self):
        """Initialize the summary dialog."""
        super(SummaryDialog, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("Practice Summary")
        self.setWindowIcon(mw.windowIcon())

    def load(self, hwmodel: HomeworkModel):
        """Loads the practice session's information into the summary dialog.

        Args:
            hwmodel (HomeworkModel): Homework (practice) model instance
        """
        self.correctLabel.setText(
            "{}/{}".format(hwmodel.total_correct, hwmodel.total_answered)
        )
        self.accuracyLabel.setText(
            "{:d}%".format(
                int(100 * hwmodel.total_correct /
                    max(1, hwmodel.total_answered))
            )
        )
        self.cardsLabel.setText("{} cards".format(len(hwmodel.card_history)))
        if hwmodel.timed_mode > 0:
            self.timeLabel.setText(
                _sec2Time(hwmodel.timed_mode * 60 - hwmodel.time))
        else:
            self.timeLabel.setText(_sec2Time(hwmodel.time))

    def show(self):
        """Override show() dialog behavior in favor of a modal dialog."""
        return self.exec_()


def _sec2Time(sec: int) -> str:
    """Simple utility function for displaying time in a HH:MM:SS format.

    Note: this may be moved in the future.

    Args:
        sec (int): Time in seconds

    Returns:
        str: Time formatted string
    """
    hrs = sec // 3600
    sec2 = sec - 3600 * hrs
    mins = sec2 // 60
    sec3 = sec - 60 * mins - 3600 * hrs
    return "{:02d}:{:02d}:{:02d}".format(hrs, mins, sec3)
