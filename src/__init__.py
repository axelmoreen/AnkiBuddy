# Copyright: Axel Moreen, 2022
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
"""
Main entry point for the Anki add-on.
"""
from .stores import *
from .hooks import patch_all
from .const import *

patch_all()