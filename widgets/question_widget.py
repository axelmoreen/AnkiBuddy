from aqt.qt import QWidget, pyqtSignal, QKeyEvent
from ..stores import Notecard, OptionStore
from ..models import Model

# abstract class for question types (multiple choice, matching, write the answer)
#   to set up their UI. 
#   options = {} dict with specific schema for each type of question.
#       assumes that the right dict is passed and that the program knows how to handle it. 
class QuestionWidget(QWidget):
    # arg1 = [True, False] => "Correct", "Incorrect"
    # arg2 = [True, False] True if should continue to next question, False if should stay on the current widget. 
    questionAnswered = pyqtSignal(bool, bool)
    def __init__(self, options: OptionStore, model: Model):
        super().__init__()

        self.options = options
        self.model = model
        self.load()
    
    def load(self):
        pass
        
    # deprecated: use handle_font 
    def set_font_size(self, ele: QWidget, size: int):
        font = ele.font()
        font.setPointSize(size)
        ele.setFont(font)
        
    def handle_font(self, ele: QWidget, base_size: int, field_name: str):
        font = ele.font()
        size = base_size
        field_opts = self.model.options_store.get_globals(self.model.note_store.deck_name)["field_settings"]
        if field_name in field_opts:
            settings = field_opts[field_name]
            size += settings[1] # font size offset
            font.setFamily(settings[0])
        font.setPointSize(size)
        ele.setFont(font)

    def handle_field_sound(self, ele: QWidget, field_name: str, card: Notecard):
        field_opts = self.model.options_store.get_globals(self.model.note_store.deck_name)["field_settings"]
        if field_name in field_opts:
            audio_name = field_opts[field_name][2]
            if audio_name in card.fields:
                ele.set_sound(card.fields[audio_name])

    def on_key(self, event: QKeyEvent): # event passed from parent
        pass

    def get_answer(self) -> str:
        return None

    def show_answer(self):
        pass