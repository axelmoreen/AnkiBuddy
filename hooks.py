from __future__ import annotations
from typing import Any

from aqt import gui_hooks
import aqt

from .views import *
from .stores import *
from .models import *
from .controllers import *
from .const import *
from .dialogs import *
from .style import button_style

def patch_all():
    """Do all the patches together. Should be called from the addon's __init__.py. 
    """
    gui_hooks.webview_will_set_content.append(_inject_overview)
    gui_hooks.webview_did_receive_js_message.append(_receive_pycmd)

def _inject_overview(web_content: aqt.webview.WebContent, context: Any):
    """Handle webview_will_set_content by injecting an html button 
        into the the deck's BottomBar.
    The BottomBar is used, because currently if you finish your daily
        repetitions, the overview hook doesn't get called. So this seems to
        be the easiest way to guarantee that the Study Buddy button appears
        all the time.
    """
    if not isinstance(context, aqt.overview.OverviewBottomBar):
        return
    web_content.head += overview_css
    web_content.body += overview_content

def _receive_pycmd(handled: tuple[bool,Any], message: str, context: Any) -> tuple[bool, Any]:
    """Handle webview_did_receive_js_message, i.e. the pycmd hooks from html.
    Checks if the button that was added in _inject_overview was pressed, as it has the pycmd("BuddyWizard") onclick command.

    If our add-on's button was pressed, then it will open the questions dialog for the user to select templates / subset / start practicing.
    """
    if message == "BuddyWizard":
        curr_did = mw.col.decks.current()["id"]
        nstore = notecards.get(curr_did)

        mw._bHwView = wiz = QuestionsDialog(nstore, options)
        wiz.deck = curr_did
        wiz.notecard_store = nstore
        wiz.show()

        return (True, None)

    return handled


overview_content = """
<div style="position: absolute; bottom: 15px; right: 15px;">
<button id="buddybutton" style="background: transparent; min-height: 20px; border: 5px solid #32a3fa; border-radius: 8px;" onclick="pycmd(\'BuddyWizard\')">Study Buddy</button>
</div>
"""

overview_css = """
<style>
#buddybutton{
    background: transparent; 
    min-height: 20px; 
    border: 5px solid #555; 
    border-radius: 8px;
}
</style>
"""