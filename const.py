from .stores import OptionStore, NotecardStore

class NotecardStoreManager:
    def __init__(self):
        self.stores = {}

    def has_store(self, did: int):
        if did in self.stores:
            return True
    
    def get(self, did: int):
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
                except:
                    print("Warning: AnkiBuddy could not sort deck")
            self.stores[did] = store
            return store


options = OptionStore(__name__)
notecards = NotecardStoreManager()
