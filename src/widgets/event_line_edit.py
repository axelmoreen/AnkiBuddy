from aqt.qt import (
    QLineEdit,
    QKeyEvent,
    QInputMethodEvent,
)

# Line edit that passes key press events to its parent
class EventLineEdit(QLineEdit):
    def keyPressEvent(self, event: QKeyEvent):
        """Pass key press event to parent.
        """
        if self.parentWidget():
            self.parentWidget().keyPressEvent(event)
        super().keyPressEvent(event)

    def inputMethodEvent(self, event: QInputMethodEvent):
        """Pass IME event to parent.
        """
        if self.parentWidget():
            self.parentWidget().inputMethodEvent(event)
        super().inputMethodEvent(event)