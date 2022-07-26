from aqt import mw, gui_hooks
from .stores import *
from .hooks import patch_all
from .const import *

patch_all()