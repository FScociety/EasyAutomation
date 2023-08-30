import bpy
import os

def reload_external_script(script):
    #Ensure  context area is not None
    old_type = bpy.context.area.type

    bpy.context.area.type = "TEXT_EDITOR"

    for t in bpy.data.texts:
        if t == script:
            if t.is_modified and not t.is_in_memory:
                bpy.context.area.spaces[0].text = t
                if os.path.exists(t.filepath):
                    bpy.ops.text.resolve_conflict(resolution='RELOAD')  
                else:
                    bpy.ops.text.unlink()

    bpy.context.area.type = old_type

def get_prefs(context):
    preferences = context.preferences
    return preferences.addons[__package__].preferences

def register():

    pass

def unregister():

    pass