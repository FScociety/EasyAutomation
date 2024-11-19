import bpy
from . import script_list
from . import script_item
import time 

class EA_PT_side_panel(bpy.types.Panel):
    bl_category = "EA"
    bl_region_type = "UI"
    bl_space_type = "VIEW_3D"

    bl_idname = "VIEW3D_EA_PT_side_panel"
    bl_label = "EasyAutomation"
    bl_options = {'DEFAULT_CLOSED'}

    def drawItemBox(self, context):
        scriptItem = context.scene.ea_script_list[context.scene.ea_script_list_index]
        script = scriptItem.script

        layout = self.layout
        
        row = layout.row()
        left_side_list = row.column()
        right_side_list = row.column()
        right_side_list.operator("easyautomation.refresh_script", text="", icon="FILE_REFRESH")
        settings_box = left_side_list.box()
        box = settings_box.box()
        row = box.row()

        if len(scriptItem.variables) > 0:
            left_side_list.alignment = "CENTER"

            for var in scriptItem.variables:
                l_newline = var.new_line
                l_seperate = var.seperate
                l_show_name = var.show_name
                l_show_value = var.show_value

                if l_show_name and len(var.name) > 0:
                    left_side = row.column()
                    left_side.label(text=var.name)

                if l_show_value:
                    type_string = var.types[var.type]
                    right_side = row.column()
                    right_side.prop(var, type_string, text="")

                if l_newline:
                    row = box.row()
                if l_seperate:
                    box = settings_box.box()
                    row = box.row()

        else:
            row = row.row()
            row.label(text="No exposed vars found!")

    def draw(self, context):
        layout = self.layout

        scene = context.scene

        row = layout.row()
        script_column = row.column()
        button_column = row.column()

        script_column.template_list("EA_UL_script_list", "Script List", scene, "ea_script_list", scene, "ea_script_list_index")

        button_column.operator("easyautomation.add_script", text="", icon="ADD")
        button_column.operator("easyautomation.delete_script", text="", icon="REMOVE")
        button_column.menu("EA_MT_advanced_menu", text="", icon="DOWNARROW_HLT")

        if len(context.scene.ea_script_list) > 1:
            up = button_column.operator("easyautomation.move_script", text="", icon="TRIA_UP")
            up.up = True

            down = button_column.operator("easyautomation.move_script", text="", icon="TRIA_DOWN")
            down.up = False

        if len(context.scene.ea_script_list) > 0:

            self.drawItemBox(context)

        for script in context.scene.ea_script_list:
            if script.batchrun:
                row = layout.row()
                row.operator("easyautomation.batch_run_scripts", icon="PLAY")
                break

def register():
    bpy.utils.register_class(EA_PT_side_panel)
    pass

def unregister():
    bpy.utils.unregister_class(EA_PT_side_panel)
    pass