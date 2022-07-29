from aqt.qt import Qt, QLabel

# Table widget (originally used to subclass QWidgetItem, but moved to QLabel for rich text)
# - Can hide and show text without changing the layout of the table. 
class BTableWidgetItem(QLabel):
    def __init__(self, text):
        text = text.strip()
        super().__init__(text)
        self._text = text
        self._isBlank = False

        self.setTextFormat(Qt.RichText)
        
    def hide_value(self):
        self._isBlank = True
        self.setText("")

    def show_value(self):
        self._isBlank = False
        self.setText(self._text)