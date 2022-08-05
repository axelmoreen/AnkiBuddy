# Copyright: Axel Moreen, 2022
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""
Handles singleton instances of NotecardStore
and OptionStore. Used specifically in hooks.py to pass these
instances to the rest of the code.
"""
from .stores import OptionStore, NotecardStore


class NotecardStoreManager:
    """Notecard store manager manages one notecard store per
    each deck, into a dict with the deck id as a key.

    This is used as a singleton so that the notecard information
    is only loaded once within the add-on.
    """
    def __init__(self):
        """Initialize manager."""
        self.stores = {}

    def has_store(self, did: int) -> bool:
        """Check if notecard store exists.

        Args:
            did (int): Deck id.

        Returns:
            bool: True if the notecard store is loaded, False if not.
        """
        if did in self.stores:
            return True

    def get(self, did: int) -> NotecardStore:
        """Get notecard store of "did" if it exists, else
        load it from the current Anki collection. Acts as a singleton
        and only loads NotecardStore when it is requested.

        Args:
            did (int): Deck id.

        Returns:
            NotecardStore: instantiated notecard store for use within the
                add-on.
        """
        if self.has_store(did):
            return self.stores[did]
        else:
            store = NotecardStore()
            store.load(did)
            options.write_all_defaults(store.deck_name)

            # sort deck, if needed
            if "sort" in options.get_globals(store.deck_name):
                try:
                    store.sort(options.get_globals(store.deck_name)["sort"])
                except RuntimeError:
                    print("Warning: AnkiBuddy could not sort deck")
            self.stores[did] = store
            return store


options = OptionStore(__name__)
notecards = NotecardStoreManager()
