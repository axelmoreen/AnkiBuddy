from aqt import gui_hooks
from .views import *
from .stores import *
from .models import *
from .controllers import *
from .const import *
from .dialogs import *
from .style import button_style

#from . import notecards, options

# do all patches to aqt
def patch_all():
    # Overview page injection (buddy buttons)
    #overview links?
    gui_hooks.webview_will_set_content.append(inject_overview)
    # Pycmd listener (to respond on button clicks)
    gui_hooks.webview_did_receive_js_message.append(receive_pycmd)

############################################
# Overview page injection 
############################################
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

############################################
# Inject our Study Buddy button 
# Uses webview hook and check for the bottom bar
#  - that way it can be seen when the deck is complete for the day.   
############################################
def inject_overview(web_content, context):
    if not isinstance(context, aqt.overview.OverviewBottomBar):
        return
    web_content.head += overview_css
    web_content.body += overview_content


############################################
# Pycmd listener for overview page
############################################
def receive_pycmd(handled, message, context):

    """    
if message == "BuddyList":
        curr_did = mw.col.decks.current()["id"]
        nstore = notecards.get(curr_did)
        model = ListModel()
        controller = ListController(model)
        
        view = ListView(nstore, options, model, controller)
        mw._bListView = view

        return (True, None) 
    """
    if message == "BuddyWizard":
        curr_did = mw.col.decks.current()["id"]
        nstore = notecards.get(curr_did)

        # show questions wizard
        mw._bHwView = wiz = QuestionsDialog(nstore, options)
        wiz.deck = curr_did
        wiz.notecard_store = nstore
        #print(wiz.getResults())
        wiz.show()
    return handled




