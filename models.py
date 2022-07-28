from email.policy import strict
from aqt.qt import *
import random

class ListModel(QObject):
    hide_front_changed = pyqtSignal(bool)
    hide_back_changed = pyqtSignal(bool)
    
    show_cancel_dialog = pyqtSignal()       

    def __init__(self, note_store, options_store, subset = None, subset_text = None):
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

        if not subset: # (defaults) to all notecards, but a subset should always be passed, so this shouldn't be executed.
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
    def hide_front(self):
        return self._hide_front
    
    @property
    def hide_back(self):
        return self._hide_back

    @hide_front.setter
    def hide_front(self, value):
        self._hide_front = value
        self.hide_front_changed.emit(value)
    
    @hide_back.setter
    def hide_back(self, value):
        self._hide_back = value
        self.hide_back_changed.emit(value)


# Homework Model
# represents a "quizzer" window where the user is asked one question at a time.
# quiz settings are set in the Questions Wizard beforehand and passed to the homework model
class HomeworkModel(QObject):
    info_update = pyqtSignal()
    answer_pane_update = pyqtSignal(bool, int)
    new_question_update = pyqtSignal(QWidget)

    def __init__(self, note_store, templates, options_store, subset=None, subset_group=-1):
        super().__init__()

        self.note_store = note_store
        self.options_store = options_store

        self.templates = []
        for templ in templates: # double templates for reverses here.
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
        self.curr_question_type = -1 # use index instead of name.
        self.globals = self.options_store.get_globals(self.note_store.deck_name)
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

        self.card_history = set() # set of card indices that have been included.
        # this gets set by view / controller while running; changing this will not turn off summaries.
        self.wait_wrong = self.globals["show_answer_before_next"] # should wait and show answer details before moving onto next question. 

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

    def next_template(self):
        return self.templates[random.randrange(len(self.templates))]

    # TODO: optimize fake random by not moving index every call. this had to be done to avoid some infinite recurrences by accident
    # If not using true random, use a separate (shuffled) deck to order the cards properly
    def next_card(self, move_ind = True, revisit = True):
        if revisit and len(self.to_revisit) > 0 and random.random() < 0.4: # roll the dice...
            card_ind = self.to_revisit[random.randrange(len(self.to_revisit))]
            return self.note_store.notecards[
                self.cards[card_ind]
                ], card_ind
        if self.true_random:
            ind = random.randrange(len(self.cards))
            return self.note_store.notecards[
                self.cards[ind]
            ], ind
        else:
            if self.card_i >= len(self.cards_shuffle):
                random.shuffle(self.cards_shuffle) # reshuffle deck
                self.card_i = self.card_i % len(self.cards_shuffle)
            ind = self.cards_shuffle[self.card_i]
            if move_ind: self.card_i += 1
            return self.note_store.notecards[
                    self.cards[ind]
                ], ind


    def load_new_question(self):
        #self.wait_wrong = False
        templ = self.next_template()
        self.answer_card = None
        self.curr_question_type = q_type = templ["type_ind"]
        self.curr_question.clear()
        self.curr_cards.clear()
        self.curr_question["type"] = templ["type"]
        if q_type == 0 : # multiple choice 
            # TODO: fix bug : card sometimes repeats in answers or from question to answers
            quest, ind = self.next_card()
            while quest.fields[templ["answer"]].casefold() == quest.fields[templ["question"]]: quest,ind = self.next_card()
            # TODO: move card history code to its own method (repeats)
            self.answer_card = quest 
            self.card_history.add(ind)

            if ind in self.to_revisit:
                self.to_revisit.remove(ind)

            #self.card_i += 1
            ans = []
            ans_cards = []
            ans_cards_inds = []
            while len(ans) < templ["number_choices"]:
                card, _ind = self.next_card(revisit=False)
                while card.fields[templ["answer"]].casefold() == card.fields[templ["question"]]: card, _ind= self.next_card(revisit=False) # happens sometimes with the core2k set
                while card.fields[templ["question"]].casefold() == quest.fields[templ["question"]]: card, _ind = self.next_card(revisit=False) # avoiding duplicating question
                #while self._has_card(ans, card, templ["question"]): card, _ind = self.next_card() 
                while self._has_card(ans, card, templ["answer"]): card, _ind = self.next_card(revisit=False)
                #self.card_i += 1
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

        elif q_type == 1: # matching
            # TODO: fix bug : sometimes on core2k set, kana and kanji will be the same - so check if question and answer are the same before using
            quest = []
            ans = []

            cards = []
            cards_inds = []
            while len(quest) < templ["groupsize"]:
                card, _ind = self.next_card()
                while card.fields[templ["answer"]].casefold() == card.fields[templ["question"]]: card, _ind = self.next_card() # happens sometimes with the core2k set
                while self._has_card(quest, card, templ["question"]): card, _ind = self.next_card()
                self.card_history.add(_ind)
                if _ind in self.to_revisit:
                    self.to_revisit.remove(_ind)
                quest.append(card.fields[templ["question"]])
                
                ans.append(card.fields[templ["answer"]])
                cards.append(card)
                cards_inds.append(_ind)
                #self.card_i += 1
            self.curr_question["questions"] = quest
            self.curr_question["answers"] = ans

            self.curr_question["question_field"] = templ["question"]
            self.curr_question["answer_field"] = templ["answer"]

            self.curr_question["cards"] = cards
            self.curr_question["cards_inds"] = cards_inds

            self.curr_cards.extend(cards)

        elif q_type == 2: #write the answer
            card, _ind = self.next_card()
            while card.fields[templ["answer"]].casefold() == card.fields[templ["question"]]: card,ind = self.next_card()

            self.answer_card = card
            self.card_history.add(_ind)
            if _ind in self.to_revisit:
                self.to_revisit.remove(_ind)
            #self.card_i += 1
            quest = card.fields[templ["question"]]
            ans = card.fields[templ["answer"]]
            self.curr_question["question"] = quest
            self.curr_question["answer"] = ans

            self.curr_question["question_field"] = templ["question"]
            self.curr_question["answer_field"] = templ["answer"]

            self.curr_question["card"] = card
            self.curr_question["card_ind"] = _ind

            self.curr_cards.append(card)
            

    def _has_card(self, card_arr, new_card, check_field):
        for stri in card_arr:
            if new_card.fields[check_field] == stri: return True
        return False

    