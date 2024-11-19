# Easy Automation

bl_info = {
    "name": "Easy Automation",
    "author": "Sören Schmidt-Clausen",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "3DView",
    "description": "Ein kleines Script das Ausführen von Script vereinfach",
    "warning": "Beta",
    "support": "COMMUNITY",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Scripting"
}

class bcolors:
    SUCCESS = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    RESET = '\033[0m'

import subprocess
import importlib.util
import sys

import bpy

from . import preferences
from . import ui
from . import functions
from . import script_list

def register():
    preferences.register()
    script_list.register()
    functions.register()
    ui.register()
    print("[",bcolors.SUCCESS,"OK",bcolors.RESET,"] EasyAutomation registered")
    pass

def unregister():
    ui.unregister()
    functions.unregister()
    script_list.unregister()
    preferences.unregister()
    print("[",bcolors.SUCCESS,"OK",bcolors.RESET,"] EasyAutomation unregistered")
    pass