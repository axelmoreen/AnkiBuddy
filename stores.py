from dataclasses import dataclass
from typing import Any, Dict

from aqt import mw
from anki.cards import Card

# Notecard Store - 
# meant to store all information about the cards and notes from Anki
# including fields, lapses, etc
# 
# currently only supports one card model - (it takes from notecard zero)
#
# should call sort() after initializing if you want this to be sorted by a field.
class NotecardStore:
    def __init__(self):
        self.is_loaded = False
        self.notecards: List[Notecard] = []
        self.deck_dict = None
        self.deck_name = None
    def load(self, did: int):
        #store card info
        res = mw.col.find_cards("did:"+str(did))
        cards = [Card(mw.col, id) for id in res]
        for c in cards:
            c.load()
        
            note = mw.col.get_note(c.nid)
            
            notecard = Notecard(dict(note.items()), c.id,  c.nid, note.mid, c.reps, c.lapses)
            # TODO: we will see if this has a performance impact
            notecard.card = c
            notecard.note = note
            self.notecards.append(notecard)
        
        # store deck info
        self.did = did
        self.deck_dict = mw.col.decks.get(did)
        self.deck_name = self.deck_dict["name"]

        # store model info
        self.model = mw.col.models.get(self.notecards[0].mid)
        self.is_loaded = True

    def sort(self, index: str, reverse = False):
        self.notecards.sort(key = lambda note: int(note.fields[index]), reverse=reverse)

    def is_loaded(self):
        return self.is_loaded

    def length(self):
        return len(self.notecards)
@dataclass
class Notecard:
    fields: Dict[str, str]
    id: int
    nid: int
    mid: int
    reps: int
    lapses: int
    
# bridge to options
class OptionStore:
    def __init__(self, name: str):
        self.name = name
        self.config = mw.addonManager.getConfig(name)
    
    def get_globals(self, deck_name: str):
        if not deck_name in self.config["decks"]:
            self.write_global_defaults(deck_name)
        return self.config["decks"][deck_name]
    
    def get_list_config(self, deck_name: str):
        if not deck_name in self.config["list"]:
            self.write_list_defaults(deck_name)
        return self.config["list"][deck_name]
    
    def get_homework_config(self, deck_name: str):
        if not deck_name in self.config["homework"]:
            self.write_homework_defaults(deck_name)
        return self.config["homework"][deck_name]

    # not yet supported
    def get_test_config(self, deck_name: str):
        if not deck_name in self.config["test"]:
            self.write_test_defaults(deck_name)
        return self.config["test"][deck_name]

    def save(self):
        mw.addonManager.writeConfig(self.name, self.config)
    
    # Defaults
    ####################################
    def write_all_defaults(self, deck_name: str):
        self.write_global_defaults(deck_name)
        self.write_list_defaults(deck_name)
        self.write_homework_defaults(deck_name)
        self.write_test_defaults(deck_name)

    def write_global_defaults(self, deck_name: str):
        c = self.config["decks"]
        if not deck_name in c:
            c[deck_name] = dict()

        ## options menu settings
        self._set_default(deck_name, "decks", "show_answer_before_next", False)
        self._set_default(deck_name, "decks", "do_timer", False)
        self._set_default(deck_name, "decks", "timer_seconds", 60)
        self._set_default(deck_name, "decks", "lesson_size", 20)
        self._set_default(deck_name, "decks", "true_random", False)
        self._set_default(deck_name, "decks", "revisit_mistakes", True)
        self._set_default(deck_name, "decks", "revisit_steps", 2)
        self._set_default(deck_name, "decks", "play_sounds", True)
        #self._set_default(deck_name, "decks", "sort", None)
        self._set_default(deck_name, "decks", "field_settings", dict())
        
        self.save()

    def write_list_defaults(self, deck_name: str):
        c = self.config["list"]
        if not deck_name in c:
            c[deck_name] = dict()

        self._set_default(deck_name, "list", "columns", list())
        self._set_default(deck_name, "list", "front", list())
        self.save()
    
    def write_homework_defaults(self, deck_name: str):
        c = self.config["homework"]
        if not deck_name in c:
            c[deck_name] = dict()

        # Multiple choice defaults
        self._set_default(deck_name, "homework", "choice_confirm_answer", False)
        self._set_default(deck_name, "homework", "choice_question_size", 30)
        self._set_default(deck_name, "homework", "choice_answer_size", 20)

        # Matching defaults
        self._set_default(deck_name, "homework", "matching_answer_size", 20)

        # Write the answer defaults
        self._set_default(deck_name, "homework", "write_show_keyboard",  False)
        self._set_default(deck_name, "homework", "write_keyboard_type", 0)
        self._set_default(deck_name, "homework", "write_question_size", 30)
        self.save()

    def write_test_defaults(self, deck_name: str):
        c = self.config["test"]
        if not deck_name in c:
            c[deck_name] = dict()

        self.save()
    
    def _set_default(self, deck_name: str, cat: str, name: str, val: Any):
        if not name in self.config[cat][deck_name]:
            self.config[cat][deck_name][name] = val
            
