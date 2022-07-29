from typing import Tuple
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
    gui_hooks.webview_will_set_content.append(inject_overview)
    gui_hooks.webview_did_receive_js_message.append(receive_pycmd)

def inject_overview(web_content: aqt.webview.WebContent, context: Any):
    if not isinstance(context, aqt.overview.OverviewBottomBar):
        return
    web_content.head += overview_css
    web_content.body += overview_content

def receive_pycmd(handled: Tuple[bool,Any], message: str, context: Any):

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

# note the :hover css doesn't seem to work :()
overview_css = """
<style>
#buddybutton{
    background: transparent; 
    min-height: 20px; 
    border: 5px solid #555; 
    border-radius: 8px;
}
#buddybutton:hover{
    border: 5px solid #32a3fa; 
    background: rgba(250.0,250.0,250.0,0.03);
}
</style>
"""