import bpy
from bpy.types import AddonPreferences

class EasyAutomationPreferences(AddonPreferences):
    bl_idname = __package__

    ea_global_dir : bpy.props.StringProperty(subtype="DIR_PATH")

    def draw(self, context):
        layout = self.layout

        layout.prop(self, "ea_global_dir")

classes = [EasyAutomationPreferences]

def register():
    for cls in classes:
        bpy.utils.register_class(EasyAutomationPreferences)

def unregister():      
    for cls in classes:
        bpy.utils.unregister_class(EasyAutomationPreferences)
