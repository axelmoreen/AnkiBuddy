# Subset represents subsets of notecards for studying
# each subset here - is a "group" of actual subsets!, not just one subset!
# for example, for an evenly spaced group of subsets, such as
# 0-19, 20-39, 40-59, etc.....
# this will be represented by one subset class.
# the cards within a subset are sorted by indices, so the index for this example would be
# arr[0]: 0-19, arr[1] = 20-39, arr[2] = 40-59, etc.
#
# get_subset_name() to pass to combobox for selecting subsets
# get_max_index() returns the maximum index for this subset. it can be 0, if there is just
#      one group (i.e. a custom selection of cards)
# get_cards(index) returns the cards associated with the index of this subset [int]
#       note: the cards returned are integer indices for the notecard store, not the cards themselves-
# get_group_text(index) description of the "group" within the subset that is represented by index
#       this is useful for subsets with unique groups, for example grouping by the number of lapses or reviews
class Subset:
    # get the name of this subset (group)
    def get_subset_name(self):
        pass
    def get_cards(self, index):
        pass
    def get_all_cards(self):
        pass
    def get_max_index(self):
        pass
    def get_group_text(self, index):
        return "Group "+ str(index + 1) +" / "+str(self.get_max_index() + 1)

# linear subset = evenly spaced group of cards for grouping into lessons
# notecard_store is a reference to the current deck.
# lesson_size is the number of cards that should be present in one lesson.
class LinearSubset(Subset):
    def __init__(self, notecard_store, lesson_size = 20):
        self.notecard_store = notecard_store
        self.lesson_size = lesson_size
        
        self.full_arr = [i for i in range(len(self.notecard_store.notecards))] # [0, 1, 2, 3, 4, 5. ....]

    def get_subset_name(self):
        return "All"
    
    def get_cards(self, index):
        return self.full_arr[self.lesson_size * index:
            min((self.lesson_size * ( index + 1)),
            len(self.full_arr))]

    def get_all_cards(self):
        return self.full_arr

    def get_max_index(self):
        return len(self.full_arr) // self.lesson_size

class LearnedSubset(Subset):
    def __init__(self, notecard_store, lesson_size = 20):
        self.notecard_store = notecard_store
        self.lesson_size = lesson_size
        self.arr = [i for i in range(len(notecard_store.notecards)) if notecard_store.notecards[i].reps > 0]
        self.arr.reverse() # make most recently learned first.
    def get_subset_name(self):
        return "Learned"
    
    def get_cards(self, index):
        return self.arr[self.lesson_size * index :min((self.lesson_size  * (index+ 1)), len(self.arr)) ]
    
    def get_all_cards(self):
        return self.arr

    def get_max_index(self):
        return len(self.arr) // self.lesson_size


class LapsedSubset(Subset):
    def __init__(self, notecard_store, lesson_size = 20):
        self.notecard_store = notecard_store
        self.lesson_size = lesson_size
        for i in range(len(notecard_store.notecards)):
            notecard_store.notecards[i]._lpos = i # field reserved for lapsed subset to easily find indices after resorting
        self.sorted_ = sorted(self.notecard_store.notecards, key=lambda card: card.lapses, reverse=True)
        self.arr = [card._lpos for card in self.sorted_ if card.reps > 0]
    
    def get_subset_name(self):
        return "Lapsed"
    
    def get_cards(self, index):
        return self.arr[self.lesson_size * index:min((self.lesson_size *  (index+1)), len(self.arr)) ]
    
    def get_all_cards(self):
        return self.arr

    def get_max_index(self):
        return len(self.arr) // self.lesson_size
    
class NewSubset(Subset):
    def __init__(self, notecard_store, lesson_size = 20):
        self.notecard_store = notecard_store
        self.lesson_size = lesson_size
        self.arr = [i for i in range(len(notecard_store.notecards)) if notecard_store.notecards[i].reps == 0]

    def get_subset_name(self):
        return "Unlearned"
    
    def get_cards(self, index):
        return self.arr[self.lesson_size * index :min((self.lesson_size  * (index+ 1)), len(self.arr)) ]
    
    def get_all_cards(self):
        return self.arr

    def get_max_index(self):
        return len(self.arr) // self.lesson_size
