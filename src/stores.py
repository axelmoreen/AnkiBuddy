# Copyright: Axel Moreen, 2022
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""
Stores module for managing data to/from Anki. 
There should be one instance of NotecardStore for each Deck, 
and one instance of OptionStore globally.

The singleton for these is managed in ./const.py.
"""
from __future__ import annotations
from dataclasses import dataclass

from typing import Any

from aqt import mw
from anki.cards import Card

# Notecard Store -
# meant to store all information about the cards and notes from Anki
# including fields, lapses, etc
#
# currently only supports one card model - (it takes from notecard zero)
#
# should call sort() after initializing if you want this to be sorted by a 
# field.


class NotecardStore:
    def __init__(self):
        """Initialize NotecardStore.
        Must call load(deck_id) to load cards.
        """
        self.is_loaded = False
        self.notecards: list[Notecard] = []
        self.deck_dict = None
        self.deck_name = None

    def load(self, did: int):
        """Load all the information from Anki's current collection into a
        NotecardStore for the AnkiBuddy add-on to use.

        Args:
            did (int): The Deck id to pull cards from.
        """

        res = mw.col.find_cards("did:" + str(did))
        cards = [Card(mw.col, id) for id in res]
        for c in cards:
            c.load()

            note = mw.col.get_note(c.nid)

            notecard = Notecard(
                dict(note.items()), c.id, c.nid, note.mid, c.reps, c.lapses
            )
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

    def sort(self, index: str, reverse=False):
        """Sort the store's cards (in-place) by one of the card's model's
        fields.
        For example, these are some of the Core 2000 deck fields:
        - Optimized-Voc-Index
        - Vocabulary-Kanji
        - Vocabulary-English
        - Core-Index
        - Frequency
        If you wanted to sort by the optimized index,
        then you would pass index as "Optimized-Voc-Index". Or,
        you could sort by alphabetical order, and pass "Vocabulary-English",
        etc.

        Args:
            index (str): model field name to sort by
            reverse (bool, optional): reverse (descending) sorting order.
                Defaults to False.
        """
        self.notecards.sort(key=lambda note: int(note.fields[index]),
                            reverse=reverse)

    def is_loaded(self) -> bool:
        """Gets if there is a deck loaded in this notecard store.

        Returns:
            bool: True if there is a deck loaded.
        """
        return self.is_loaded

    def length(self) -> int:
        """Gets how many cards are loaded in this notecard store.
        Individual cards can be accessed with store.cards[0:store.length()]

        Returns:
            int: How many cards are loaded in the store.
        """
        return len(self.notecards)


@dataclass
class Notecard:
    fields: dict[str, str]
    id: int
    nid: int
    mid: int
    reps: int
    lapses: int


# bridge to options
class OptionStore:
    def __init__(self, name: str):
        """Initialize options store."""
        self.name = name
        self.config = mw.addonManager.getConfig(name)

    def get_globals(self, deck_name: str) -> dict[str, Any]:
        """Get "Global" configuration options.
        Anything that applies to the entirety of the add-on can
        be stored here.

        Args:
            deck_name (str): Name of the deck to get. Is the same as
                notecard_store.deck_name.

        Returns:
            dict[str, Any]: Returns the configuration in a dictionary/JSON
                format.
        """
        if deck_name not in self.config["decks"]:
            self.write_global_defaults(deck_name)
        return self.config["decks"][deck_name]

    def get_list_config(self, deck_name: str) -> dict[str, Any]:
        """Get the List configuration options.
        This is for options pertaining to the 'List Preview' function
        that can be found in the main Homework dialog. It basically just
        consists of the fields to use as columns in the table, and whether
        they are front or back.

        Args:
            deck_name (str): Name of the deck to get. It is the same as
                notecard_store.deck_name.

        Returns:
            dict[str, Any]: Returns the configuration in a dictionary/JSON
                format.
        """
        if deck_name not in self.config["list"]:
            self.write_list_defaults(deck_name)
        return self.config["list"][deck_name]

    def get_homework_config(self, deck_name: str) -> dict[str, Any]:
        """Get the Homework configuration options.
        This is for options pertaining to the main Practice feature.
        Options for individual question types like Multiple Choice or Matching
        are meant to be stored here.

        Args:
            deck_name (str): Name of the deck to get. It is the same as
                notecard_store.deck_name.

        Returns:
            dict[str, Any]: Returns the configuration in a dictionary/JSON
                format.
        """
        if deck_name not in self.config["homework"]:
            self.write_homework_defaults(deck_name)
        return self.config["homework"][deck_name]

    # not yet supported
    def get_test_config(self, deck_name: str) -> dict[str, Any]:
        """Get the Test configuration options.
        Not currently implemented, but this will probably be used in the
        future.

        Args:
            deck_name (str): Name of the deck to get. It is the same as
                notecard_store.deck_name.

        Returns:
            dict[str, Any]: Returns the configuration in a dictionary/JSON
                format.
        """
        if deck_name not in self.config["test"]:
            self.write_test_defaults(deck_name)
        return self.config["test"][deck_name]

    def save(self):
        """Write config changes made to file.
        Call this after modifying one of the dicts in:
        get_global_config(),
        get_list_config(),
        get_homework_config(),
        get_test_config().
        """
        mw.addonManager.writeConfig(self.name, self.config)

    # Defaults
    ####################################
    def write_all_defaults(self, deck_name: str):
        """Call this to write config defaults, if they do not exist.

        Args:
            deck_name (str): Name of the deck to get. It is also
                notecard_store.deck_name.
        """
        self._write_global_defaults(deck_name)
        self._write_list_defaults(deck_name)
        self._write_homework_defaults(deck_name)
        self._write_test_defaults(deck_name)

    def _write_global_defaults(self, deck_name: str):
        """Internal function to write global defaults. Called by
            write_all_defaults()."""
        c = self.config["decks"]
        if deck_name not in c:
            c[deck_name] = dict()

        # options menu settings
        self._set_default(deck_name, "decks", "show_answer_before_next", False)
        self._set_default(deck_name, "decks", "do_timer", False)
        self._set_default(deck_name, "decks", "timer_seconds", 60)
        self._set_default(deck_name, "decks", "lesson_size", 20)
        self._set_default(deck_name, "decks", "true_random", False)
        self._set_default(deck_name, "decks", "revisit_mistakes", True)
        self._set_default(deck_name, "decks", "revisit_steps", 2)
        self._set_default(deck_name, "decks", "play_sounds", True)
        # self._set_default(deck_name, "decks", "sort", None)
        self._set_default(deck_name, "decks", "field_settings", dict())

        self.save()

    def _write_list_defaults(self, deck_name: str):
        """Internal function to write list defaults. Called by
        write_all_defaults()."""
        c = self.config["list"]
        if deck_name not in c:
            c[deck_name] = dict()

        self._set_default(deck_name, "list", "columns", list())
        self._set_default(deck_name, "list", "front", list())
        self.save()

    def _write_homework_defaults(self, deck_name: str):
        """Internal function to write homework defaults. Called by
        write_all_defaults()."""
        c = self.config["homework"]
        if deck_name in c:
            c[deck_name] = dict()

        # Multiple choice defaults
        self._set_default(
            deck_name, "homework", "choice_confirm_answer", False)
        self._set_default(deck_name, "homework", "choice_question_size", 30)
        self._set_default(deck_name, "homework", "choice_answer_size", 20)

        # Matching defaults
        self._set_default(deck_name, "homework", "matching_answer_size", 20)

        # Write the answer defaults
        self._set_default(deck_name, "homework", "write_show_keyboard", False)
        self._set_default(deck_name, "homework", "write_keyboard_type", 0)
        self._set_default(deck_name, "homework", "write_question_size", 30)
        self.save()

    def _write_test_defaults(self, deck_name: str):
        """Internal function to write test defaults. Called by
        write_all_defaults()."""
        c = self.config["test"]
        if deck_name not in c:
            c[deck_name] = dict()

        self.save()

    def _set_default(self, deck_name: str, cat: str, name: str, val: Any):
        """Internal function to write an individual default."""
        if name not in self.config[cat][deck_name]:
            self.config[cat][deck_name][name] = val