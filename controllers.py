from aqt.qt import *

class ListController(QObject):
    def __init__(self, model):
        super().__init__()
        self.model = model

    @pyqtSlot(int)
    def on_hide_front_changed(self, value):
        self.model.hide_front = bool(value)

    @pyqtSlot(int)
    def on_hide_back_changed(self, value):
        self.model.hide_back = bool(value)

    @pyqtSlot(int)
    def on_all_lessons_changed(self, value):
        self.model.show_all = bool(value)

    # deprecated
    @pyqtSlot(bool)
    def on_options(self, value):
        pass

    # deprecated
    @pyqtSlot(bool)
    def on_forward(self, value):
        if not self.model.show_all:
            self.model.lesson = self.model.lesson + 1
    
    # deprecated
    @pyqtSlot(bool)
    def on_backward(self, value):
        if not self.model.show_all:
            self.model.lesson = self.model.lesson - 1

class HomeworkController(QObject):
    def __init__(self, model):
        super().__init__()
        self.model = model
