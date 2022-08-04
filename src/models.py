# Copyright: Axel Moreen, 2022
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""
Models module for managing state in the List and Homework UI's.

The related UI code is managed in ./views.py, and logic in ./controllers.py.
State for other UI's, like the homework wizard dialog, is in /dialogs/.
"""
from __future__ import annotations
from typing import Any

from aqt.qt import (
    pyqtSignal,
    QObject,
    QWidget,
)
import random
from .stores import Notecard, NotecardStore, OptionStore
from .subsets import Subset


class Model(QObject):
    """Parent class for Models.
    """
    pass


class ListModel(Model):
    """Model class for the ListView / ListController.

    Emits:
        hide_front_changed: Should hide table columns that are Front
        hide_back_changed: Should hide table columns that are Back
        show_cancel_dialog: Inform the user that they should set-up
            the columns in the options. 
    """
    hide_front_changed = pyqtSignal(bool)
    hide_back_changed = pyqtSignal(bool)
    show_cancel_dialog = pyqtSignal()

    def __init__(
        self,
        note_store: NotecardStore,
        options_store: OptionStore,
        subset: Subset = None,
        subset_text: str = None,
    ):
        """Initialize a list model for use with the ListView.

        Args:
            note_store (NotecardStore): instance of notecard store to pull
                cards from.
            options_store (OptionStore): instance of options store to use
                config.
            subset (Subset, optional): An instance of Subset with cards loaded
                to use instead of full deck. Defaults to None.
            subset_text (str, optional): Text to display with this subset.
                Defaults to None.
        """
        super().__init__()
        self._hide_front = False
        self._hide_back = False

        self.note_store = note_store
        self.options_store = options_store
        self.subset = subset
        self.subset_text = subset_text

        self.cards = []
        conf = options_store.get_list_config(note_store.deck_name)
        # check to see if there are no columns set in options yet
        if "columns" not in conf:
            self.show_cancel_dialog.emit()
        elif len(conf["columns"]) == 0:
            self.show_cancel_dialog.emit()

        self.columns = conf["columns"]
        self.column_count = len(self.columns)

        self.front = []
        for item in conf["front"]:
            self.front.append(item)

        self.rows = []

        def build_row(notecard):
            row = []
            for j in range(0, len(self.columns)):
                row.append(str(notecard.fields[self.columns[j]]))
            return tuple(row)

        if not subset:  # subset should always be passed, so not executed
            self.length = note_store.length()
            for notecard in note_store.notecards:
                self.rows.append(build_row(notecard))
                self.cards.append(notecard.card)
        else:
            self.length = len(subset)
            for ele in subset:
                self.rows.append(build_row(note_store.notecards[ele]))
                self.cards.append(note_store.notecards[ele].card)

    @property
    def hide_front(self) -> bool:
        """Getter.

        Returns:
            bool: True if the View should hide the "front" column(s).
        """
        return self._hide_front

    @property
    def hide_back(self) -> bool:
        """Getter.

        Returns:
            bool: True if the View should hide the "back" column(s).
        """
        return self._hide_back

    @hide_front.setter
    def hide_front(self, value: bool):
        """Setter.

        Args:
            value (bool): Set True if the View should hide the "front"
                column(s), else False to show them.
        """
        self._hide_front = value
        self.hide_front_changed.emit(value)

    @hide_back.setter
    def hide_back(self, value: bool):
        """Setter.

        Args:
            value (bool): Set True if the View should hide the "back"
                column(s), else False to show them.
        """
        self._hide_back = value
        self.hide_back_changed.emit(value)


class HomeworkModel(Model):
    """Homework model for the homework controller / view.

    Represents the main Practice window where the user is asked one question
        at a time.
    The config for the quizzer are set in the Question Wizard before hand.

    Emits:
        info_update: Tell the view to update practice summary such as timer,
            correct/ incorrect.
        answer_pane_update: Update the bottom bar based on user input, i.e.
            if they got the question right / wrong or to show answer.
        new_question_update: Clear the view to start a new question.
    """
    info_update = pyqtSignal()
    answer_pane_update = pyqtSignal(bool, int)
    new_question_update = pyqtSignal(QWidget)

    def __init__(
        self,
        note_store: NotecardStore,
        templates: list[dict[str, Any]],
        options_store: OptionStore,
        subset: Subset = None,
        subset_group: int = -1,
    ):
        """Initialize the homework model, for use with HomeworkView.

        Args:
            note_store (NotecardStore): notecard store instance to pull cards
                from.
            templates (List[Dict[str, Any]]): question templates to build
                questions from.
            options_store (OptionStore): option store instance for config.`
            subset (Subset, optional): instance of Subset with cards list. If
                none, will use entire deck. Defaults to None.
            subset_group (int, optional): group for the subset to use (between
                [-1, subset.get_max_index()).). -1 will use the entire subset.
                Defaults to -1.
        """
        super().__init__()

        self.note_store = note_store
        self.options_store = options_store

        self.templates = []
        for templ in templates:  # double templates for reverses here.
            self.templates.append(templ)
            if templ["include_reverse"]:
                rev = templ.copy()
                rev["question"] = templ["answer"]
                rev["answer"] = templ["question"]
                self.templates.append(rev)

        self.subset = subset
        self.subset_group = subset_group
        if not subset:
            self.cards = [i for i in range(note_store.length())]
        else:
            if subset_group == -1:
                self.cards = subset.get_all_cards()
            else:
                self.cards = subset.get_cards(subset_group)
        self.curr_question = {}
        self.curr_question_type = -1  # use index instead of name.
        self.globals = self.options_store.get_globals(
            self.note_store.deck_name)
        if "do_timer" in self.globals and "timer_seconds" in self.globals:
            if self.globals["do_timer"]:
                self.timed_mode = self.globals["timer_seconds"]
            else:
                self.timed_mode = 0
        else:
            self.timed_mode = 0
        # history
        self.total_correct = 0
        self.total_answered = 0

        self.time = self.timed_mode

        self.card_history = set()  # previous cards

        self.wait_wrong = self.globals["show_answer_before_next"]

        self.true_random = self.globals["true_random"]
        self.cards_shuffle = [i for i in range(len(self.cards))]
        random.shuffle(self.cards_shuffle)
        self.card_i = 0

        self.play_sounds = self.globals["play_sounds"]

        # revisit mistakes
        self.do_revisit = self.globals["revisit_mistakes"]
        self.revisit_steps = self.globals["revisit_steps"]

        self.to_revisit = []

        self.curr_cards = []
        self.stop = False

    def next_template(self) -> dict[str, Any]:
        """Get a random template to use (for the next question).

        Returns:
            dict[str, Any]: Template dict representing a question type.
        """
        return self.templates[random.randrange(len(self.templates))]

    def next_card(self, move_ind: bool = True,
                  revisit: bool = True) -> Notecard:
        """Get random card to use (for the next question.)
        This method either gets a card as the next one in a balanced/shuffled
            deck (default setting) or it gets a card randomly from the deck
            (if True Random is set in the options dialog.)

        Also, this method implements "card revisiting." If the user gets a
            question wrong (i.e. misses a card), then if Card Revisits are
            enabled in options the card will return for N revisit steps
            (set in Options). This method will randomly try to insert cards
            that need revisiting. However, since next_card() may be rejected
            by load_new_question() (see below),card revisits are only satisfied
            and removed from the array self.to_revisit[] in that method.

        Note:
            Currently, load_new_question() always uses move_ind true to move
            the shuffled deck index on every call. This is sub-optimal because
            since load_new_question() sometimes rejects next_card(), some
            cards will be skipped over the pass of the subset/deck as a result,
            and will not re-appear until looping over the cards.
            This may be avoided by re-ordering the deck when a card is
            rejected, i.e. moving rejected cards after the index where they
            can be visited.

            Of course, using True Random is unaffected by this, but that
            method comes with its own shortcomings.

        Args:
            move_ind (bool, optional): Used for shuffled deck (balanced)
                random to move onto the next card.
                If true, increase shuffled index. Defaults to True.
            revisit (bool, optional): If True, do card revisits.
                Defaults to True.

        Returns:
            Notecard: instance of the Notecard data-class to use for the next
                question.
        """
        if (
            revisit and len(self.to_revisit) > 0 and random.random() < 0.4
        ):  # roll the dice...
            card_ind = self.to_revisit[random.randrange(len(self.to_revisit))]
            return self.note_store.notecards[self.cards[card_ind]], card_ind

        if self.true_random:
            ind = random.randrange(len(self.cards))
            return self.note_store.notecards[self.cards[ind]], ind
        else:
            if self.card_i >= len(self.cards_shuffle):
                random.shuffle(self.cards_shuffle)  # reshuffle deck
                self.card_i = self.card_i % len(self.cards_shuffle)
            ind = self.cards_shuffle[self.card_i]
            if move_ind:
                self.card_i += 1
            return self.note_store.notecards[self.cards[ind]], ind

    # TODO: shorten this function:)
    def load_new_question(self):
        """Load the next question. Called when the user is going to move on
        to the next question, before the view is going to be displayed.

        Currently, this method should be improved. It
            may be best to have a simple API for loading question-models and
            corresponding question-widgets so that it is easy
            to add new custom question types (even from another add-on).
            As it stands, having three question models hard-coded in this
            method is not versatile at all, but it exists for now.

        This method does everything in preparation of the next question. It
            gets a new question template, then based on the type (multiple
            choice, matching, write the answer) it will populate a dict
            in the model called self.curr_question with information for the
            View to use. So, it creates a question model within a dict for the
            question widget.
        This method also adds cards to the list self.curr_cards for viewing
            the Card(s) with SimpleCardView later.
        """
        templ = self.next_template()
        self.answer_card = None
        self.curr_question_type = q_type = templ["type_ind"]
        self.curr_question.clear()
        self.curr_cards.clear()
        self.curr_question["type"] = templ["type"]
        # Multiple Choice
        if q_type == 0:
            quest, ind = self.next_card()
            while (
                quest.fields[templ["answer"]].casefold()
                == quest.fields[templ["question"]]
            ):
                quest, ind = self.next_card()
            self.answer_card = quest
            self.card_history.add(ind)

            if ind in self.to_revisit:
                self.to_revisit.remove(ind)

            ans = []
            ans_cards = []
            ans_cards_inds = []
            while len(ans) < templ["number_choices"]:
                card, _ind = self.next_card(revisit=False)
                while (
                    card.fields[templ["answer"]].casefold()
                    == card.fields[templ["question"]]
                ):
                    card, _ind = self.next_card(
                        revisit=False
                    )  # happens sometimes with the core2k set
                while (
                    card.fields[templ["question"]].casefold()
                    == quest.fields[templ["question"]]
                ):
                    card, _ind = self.next_card(
                        revisit=False
                    )  # avoiding duplicating question
                while self._has_card(ans, card, templ["answer"]):
                    card, _ind = self.next_card(revisit=False)
                ans.append(card.fields[templ["answer"]])
                ans_cards.append(card)
                ans_cards_inds.append(_ind)

            ans_ind = random.randrange(templ["number_choices"])
            ans[ans_ind] = quest.fields[templ["answer"]]
            ans_cards[ans_ind] = quest

            self.curr_question["question"] = quest.fields[templ["question"]]
            self.curr_question["answers"] = ans
            self.curr_question["correct_answer"] = ans_ind

            # extended behavior
            self.curr_question["question_field"] = templ["question"]
            self.curr_question["answer_field"] = templ["answer"]

            self.curr_question["question_card"] = quest
            self.curr_question["answer_cards"] = ans_cards

            self.curr_question["question_card_ind"] = ind
            self.curr_question["answer_cards_ind"] = ans_cards_inds

            self.curr_cards.append(quest)
        # Matching
        elif q_type == 1:
            quest = []
            ans = []

            cards = []
            cards_inds = []
            while len(quest) < templ["groupsize"]:
                card, _ind = self.next_card()
                while (
                    card.fields[templ["answer"]].casefold()
                    == card.fields[templ["question"]]
                ):
                    (
                        card,
                        _ind,
                    ) = self.next_card()  # happens sometimes with core2k
                while self._has_card(quest, card, templ["question"]):
                    card, _ind = self.next_card()
                self.card_history.add(_ind)
                if _ind in self.to_revisit:
                    self.to_revisit.remove(_ind)
                quest.append(card.fields[templ["question"]])

                ans.append(card.fields[templ["answer"]])
                cards.append(card)
                cards_inds.append(_ind)
            self.curr_question["questions"] = quest
            self.curr_question["answers"] = ans

            self.curr_question["question_field"] = templ["question"]
            self.curr_question["answer_field"] = templ["answer"]

            self.curr_question["cards"] = cards
            self.curr_question["cards_inds"] = cards_inds

            self.curr_cards.extend(cards)
        # Write the Answer
        elif q_type == 2:
            card, _ind = self.next_card()
            while (
                card.fields[templ["answer"]].casefold()
                == card.fields[templ["question"]]
            ):
                card, ind = self.next_card()

            self.answer_card = card
            self.card_history.add(_ind)
            if _ind in self.to_revisit:
                self.to_revisit.remove(_ind)
            quest = card.fields[templ["question"]]
            ans = card.fields[templ["answer"]]
            self.curr_question["question"] = quest
            self.curr_question["answer"] = ans

            self.curr_question["question_field"] = templ["question"]
            self.curr_question["answer_field"] = templ["answer"]

            self.curr_question["card"] = card
            self.curr_question["card_ind"] = _ind

            self.curr_cards.append(card)

    def _has_card(
        self, card_arr: list[str], new_card: Notecard, check_field: str
    ) -> bool:
        """Helper method to check if an array contains a card, by comparison
        of a field.
        Since this is used to validate/reject cards based on what the question
        template needs, a list of strings here is passed in card_arr.
        Returns true if new_cards.field[check_field] is in this array.

        Args:
            card_arr (list[Notecard]): String list to check.
            new_card (Notecard): Notecard to check.
            check_field (str): Check if this field in the notecard is in
                card_arr.

        Returns:
            bool: True if the array has the card, False if not.
        """
        for stri in card_arr:
            if new_card.fields[check_field] == stri:
                return True
        return False
