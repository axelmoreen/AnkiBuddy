# Copyright: Axel Moreen, 2022
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""
Subsets module. Used for creating subsets of the deck, these get passed
to either the List or the Homework UI for picking cards. 
"""
from __future__ import annotations
from .stores import NotecardStore

# Subset represents subsets of notecards for studying
# each subset here - is a "group" of actual subsets!, not just one subset!
# for example, for an evenly spaced group of subsets, such as
# 0-19, 20-39, 40-59, etc.....
# this will be represented by one subset class.
# the cards within a subset are sorted by indices, so the index for this
# example would be
# arr[0]: 0-19, arr[1] = 20-39, arr[2] = 40-59, etc.


class Subset:
    def get_subset_name(self) -> str:
        """Get the name of this subset.

        Returns:
            str: Name of the subset.
        """
        return None

    def get_cards(self, index: int) -> list[int]:
        """Get list of cards under subgroup "index". See class docstring for
        more info.

        Args:
            index (int): subgroup to get cards from.

        Returns:
            List[int]: list of indices corresponding to subgroup's cards in
            the notecard store.
        """
        return []

    def get_all_cards(self) -> list[int]:
        """Get all cards under all subgroups. See class docstring for more
        info.

        Returns:
            List[int]: list of indices corresponding to subset's cards in the
            notecard store.
        """
        return []

    def get_max_index(self) -> int:
        """Get max subgroup index that can be used in self.get_cards(index).

        Returns:
            int: Max subgroup index to be used.
        """
        return -1

    def get_group_text(self, index: int) -> str:
        """Get text string with subgroup information for display.

        Args:
            index (int): Subgroup index

        Returns:
            str: Subgroup information
        """
        return "Group " + str(index + 1) + " / " + str(self.get_max_index()
                                                       + 1)


# linear subset = evenly spaced group of cards for grouping into lessons
# notecard_store is a reference to the current deck.
# lesson_size is the number of cards that should be present in one lesson.
class LinearSubset(Subset):
    def __init__(self, notecard_store: NotecardStore, lesson_size: int = 20):
        """Initializes subset with information from the notecard store.
        Does not need to be ordered any differently.

        Args:
            notecard_store (NotecardStore): instance of notecard store to pull
                notecards from.
            lesson_size (int, optional): how many cards are in a group.
                Defaults to 20.
        """
        self.notecard_store = notecard_store
        self.lesson_size = lesson_size

        self.full_arr = [
            i for i in range(len(self.notecard_store.notecards))
        ]  # [0, 1, 2, 3, 4, 5. ....]

    def get_subset_name(self) -> str:
        """See super-class."""
        return "All"

    def get_cards(self, index: int) -> list[int]:
        """See super-class."""
        return self.full_arr[
            self.lesson_size
            * index:min((self.lesson_size * (index + 1)), len(self.full_arr))
        ]

    def get_all_cards(self) -> list[int]:
        """See super-class."""
        return self.full_arr

    def get_max_index(self) -> int:
        """See super-class."""
        return len(self.full_arr) // self.lesson_size


class LearnedSubset(Subset):
    def __init__(self, notecard_store: NotecardStore, lesson_size: int = 20):
        """Initializes subset with information from the notecard store.
        Then, prune cards that have not been learned yet, and order them
            so that the most recently learned are first.

        Args:
            notecard_store (NotecardStore): instance of notecard store to pull
                notecards from.
            lesson_size (int, optional): how many cards are in a group.
                Defaults to 20.
        """
        self.notecard_store = notecard_store
        self.lesson_size = lesson_size
        self.arr = [
            i
            for i in range(len(notecard_store.notecards))
            if notecard_store.notecards[i].reps > 0
        ]
        self.arr.reverse()  # make most recently learned first.

    def get_subset_name(self) -> str:
        """See super-class."""
        return "Learned"

    def get_cards(self, index: int) -> list[int]:
        """See super-class."""
        return self.arr[
            self.lesson_size
            * index:min((self.lesson_size * (index + 1)), len(self.arr))
        ]

    def get_all_cards(self) -> list[int]:
        """See super-class."""
        return self.arr

    def get_max_index(self) -> int:
        """See super-class."""
        return len(self.arr) // self.lesson_size


class LapsedSubset(Subset):
    def __init__(self, notecard_store: NotecardStore, lesson_size: int = 20):
        """Initializes subset with information from the notecard store.
        Prune cards that have not been learned yet, then order them
        in order of most lapses (descending).

        Args:
            notecard_store (NotecardStore): instance of notecard store to pull
                notecards from.
            lesson_size (int, optional): how many cards are in a group.
                Defaults to 20.
        """
        self.notecard_store = notecard_store
        self.lesson_size = lesson_size
        for i in range(len(notecard_store.notecards)):
            notecard_store.notecards[i]._lpos = i  # field reserved for this
        self.sorted_ = sorted(
            self.notecard_store.notecards, key=lambda card: card.lapses,
            reverse=True
        )
        self.arr = [card._lpos for card in self.sorted_ if card.reps > 0]

    def get_subset_name(self) -> str:
        """See super-class."""
        return "Lapsed"

    def get_cards(self, index: int) -> list[int]:
        """See super-class."""
        return self.arr[
            self.lesson_size
            * index:min((self.lesson_size * (index + 1)), len(self.arr))
        ]

    def get_all_cards(self) -> list[int]:
        """See super-class."""
        return self.arr

    def get_max_index(self) -> int:
        """See super-class."""
        return len(self.arr) // self.lesson_size


class NewSubset(Subset):
    def __init__(self, notecard_store: NotecardStore, lesson_size: int = 20):
        """Initializes subset with information from the notecard store.
        Prune cards that have already been learned, so that only new cards
        remain.

        Args:
            notecard_store (NotecardStore): instance of notecard store to pull
                notecards from.
            lesson_size (int, optional): how many cards are in a group.
                Defaults to 20.
        """
        self.notecard_store = notecard_store
        self.lesson_size = lesson_size
        self.arr = [
            i
            for i in range(len(notecard_store.notecards))
            if notecard_store.notecards[i].reps == 0
        ]

    def get_subset_name(self) -> str:
        """See super-class."""
        return "Unlearned"

    def get_cards(self, index: int) -> list[int]:
        """See super-class."""
        return self.arr[
            self.lesson_size
            * index:min((self.lesson_size * (index + 1)), len(self.arr))
        ]

    def get_all_cards(self) -> list[int]:
        """See super-class."""
        return self.arr

    def get_max_index(self) -> int:
        """See super-class."""
        return len(self.arr) // self.lesson_size
