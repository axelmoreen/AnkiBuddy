from aqt.qt import QLineEdit

# Line edit that passes key press events to its parent
class EventLineEdit(QLineEdit):
    def keyPressEvent(self, event):
        if self.parentWidget():
            self.parentWidget().keyPressEvent(event)
        super().keyPressEvent(event)
    def inputMethodEvent(self, event):
        if self.parentWidget():
            self.parentWidget().inputMethodEvent(event)
        super().inputMethodEvent(event)