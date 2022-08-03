# Copyright: Axel Moreen, 2022
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""
Contains the event line edit widget, which gets used specifically in the
Write the Answer layout so that the parent layout can get IME
events when it is focused, for the virtual keyboard. 
"""
from aqt.qt import (
    QLineEdit,
    QKeyEvent,
    QInputMethodEvent,
)

# Line edit that passes key press events to its parent
class EventLineEdit(QLineEdit):
    def keyPressEvent(self, event: QKeyEvent):
        """Pass key press event to parent."""
        if self.parentWidget():
            self.parentWidget().keyPressEvent(event)
        super().keyPressEvent(event)

    def inputMethodEvent(self, event: QInputMethodEvent):
        """Pass IME event to parent."""
        if self.parentWidget():
            self.parentWidget().inputMethodEvent(event)
        super().inputMethodEvent(event)
