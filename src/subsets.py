# Copyright: Axel Moreen, 2022
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""
Subsets module. Used for creating subsets of the deck, these get passed
to either the List or the Homework UI for picking cards.
"""
from __future__ import annotations
from .stores import NotecardStore


class Subset:
    """Parent class for subset.

    Each subset represents groups of notecards for studying, organized by
    some criteria. For an evenly spaced group of subsets, such as cards
    0-19, 20-39, 40-59, etc... this is represented by one subset class
    (Linear Subset, in this case). These subgroups (in this case of 20
    cards each) are each represented by an index, going from 0 to
    get_max_index().
    """
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


class LinearSubset(Subset):
    """Evenly spaced group of cards for grouping into lessons.
    See Subset.
    """
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
    """Cards only that have already been learned.
    The subset is ordered by recency. See Subset.
    """
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
    """Learned cards, ordered by the amount of mistakes during regular
    Anki review. See Subset.
    """
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
    """New cards that haven't been learned yet in the Anki review.
    See subset.
    """
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
