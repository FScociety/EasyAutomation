import bpy
from . import script_item
from . import functions

import os

class EA_UL_script_list(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row(align=True)
        if item.script != None:
            run_script_op = row.operator("easyautomation.run_script", text="", icon="PLAY")
            run_script_op.index = index
            row.prop(item, "batchrun", text="", icon="ONIONSKIN_ON")

            if item.script.filepath != "":
                row.label(text="", icon="LINKED")

            row.prop(item.script, "name", text="", emboss=False)

            open_editor_op = row.operator("easyautomation.openeditor", text="", icon="CURRENT_FILE")
            open_editor_op.index = index

        else:
            row.alignment = "CENTER"
            row.label(text="No Script Found")

def findGlobal(_scene, context):
    preferences = context.preferences
    addon_prefs = preferences.addons[__package__].preferences
    global_script_path = addon_prefs.ea_global_dir

    if global_script_path == "":
        return None

    ea_scripts = []
    for root, dirs, files in os.walk(global_script_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                with open(file_path, "r") as f:
                    first_line = f.readline().strip()
                    if first_line == "#EA-Script":
                        ea_scripts.append(file_path)

    items = []

    for i, ea_script in enumerate(ea_scripts):
        items.append((ea_script, os.path.basename(ea_script), "Link a new EasyAutomation Script", i))

    return items

class EA_MT_advanced_menu(bpy.types.Menu):
    bl_idname = "EA_MT_advanced_menu"
    bl_label = "Open Advanced Operations List"

    def draw(self, context):
        layout = self.layout

        layout.operator("easyautomation.import_script", icon="IMPORT")
        layout.operator("easyautomation.export_script", icon="EXPORT")
        layout.operator("easyautomation.refresh_scripts", icon="FILE_REFRESH")

class EA_OT_import_global(bpy.types.Operator):
    bl_idname = "easyautomation.import_script"
    bl_label = "Import global Script"
    bl_property = "global_scripts"

    global_scripts : bpy.props.EnumProperty(
        name="",
        description="Select an script for import",
        items=findGlobal
    )

    def invoke(self, context, event):
        script_list = findGlobal(None, context)
        
        if script_list == None:
            self.report({'ERROR'}, "No script path defined. Please define one in the addon preferences")
            return {"CANCELLED"}

        if len(script_list) > 0:
            context.window_manager.invoke_search_popup(self)
            return {"FINISHED"}
        else:
            self.report({'ERROR'}, "No scripts in the defined path found")
            return {"CANCELLED"}

    def execute(self, context):
        bpy.data.texts.load(self.global_scripts)
        bpy.ops.easyautomation.refresh_scripts()

        return {"FINISHED"}

class EA_OT_make_global(bpy.types.Operator):
    bl_idname = "easyautomation.export_script"
    bl_label = "Make current Script global"

    name : bpy.props.StringProperty()
    filepath : bpy.props.StringProperty()

    def draw(self, context):
        layout = self.layout
        layout.label(text="The file already exists. Override?")

    def invoke(self, context, event):
        script_list = context.scene.ea_script_list

        # Scriptlist is empty?
        if len(script_list) == 0:
            self.report({"INFO"}, "Scripting list is empty, no script to export")
            return {"CANCELLED"}

        script = script_list[context.scene.ea_script_list_index].script

        # Get name and filepath of the export script
        self.name = script.name if script.name.endswith(".py") else (script.name + ".py")
        self.filepath = functions.get_prefs(context).ea_global_dir + self.name

        # Check if the script is already global
        for script_enum_item in findGlobal(None, context):
            if script_enum_item[0] == self.filepath:
                self.report({"INFO"}, "Script is already global")
                return {"CANCELLED"}

        # Promp dialog, when the file already exists
        if os.path.exists(self.filepath):
            return context.window_manager.invoke_props_dialog(self)
        else:
            return self.execute(context)

    def execute(self, context):
        script_list = context.scene.ea_script_list
        script = script_list[context.scene.ea_script_list_index].script

        # Change the area type to text editor, so we can run text editor specific operators
        areatype_buffer = context.area.type
        context.area.type = "TEXT_EDITOR"
        context.area.spaces[0].text = script

        bpy.ops.text.save_as(filepath=self.filepath, check_existing=True)

        context.area.type = areatype_buffer

        self.report({'INFO'}, ("Stored script as " + self.name))
        return {"FINISHED"}

class EA_OT_refresh_scripts(bpy.types.Operator):
    bl_idname = "easyautomation.refresh_scripts"
    bl_label = "Update Script List"

    def checkText(self, text):
        return text if text.lines[0].body == "#EA-Script" else None

    def execute(self, context):
        ui_script_groups = context.scene.ea_script_list
        old_index = context.scene.ea_script_list_index
        new_scripts = []
        context.scene.ea_script_list_index = 0

        #Filter all and save #EA-Scripts
        for text in bpy.data.texts:
            script = self.checkText(text)

            if script != None:
                new_scripts.append(script)

        #Check for Elements that have been manually removed
        for old_script_item in ui_script_groups:
            in_list = False

            if old_script_item.script != None:
                for script in new_scripts:
                    if script.name == old_script_item.script.name:
                        in_list = True

            if in_list == False:
                for i, item in enumerate(ui_script_groups):
                    if item == old_script_item:
                        ui_script_groups.remove(i)

        #Check for Elements that have been manually added
        for script in new_scripts:
            in_list = False

            for old_script_item in ui_script_groups:
                if old_script_item.script.name == script.name:
                    in_list = True

            if in_list == False:
                ui_script_groups.add()
                ui_script_groups[len(ui_script_groups)-1].script = script

        #Update all scripts
        for i, script_item in enumerate(ui_script_groups):
            functions.reload_external_script(script_item.script)
            context.scene.ea_script_list_index = i
            bpy.ops.easyautomation.refresh_script()

        #Try to Recover old Index
        if old_index <= len(ui_script_groups)-1:
            context.scene.ea_script_list_index = old_index

        return {"FINISHED"}

class EA_OT_move_script(bpy.types.Operator):
    bl_idname = "easyautomation.move_script"
    bl_label = "Move Script"

    up : bpy.props.BoolProperty()

    def execute(self, context):

        length = len(context.scene.ea_script_list)
        index = context.scene.ea_script_list_index

        if self.up == True and index > 0:        #UP
            context.scene.ea_script_list.move(index, index-1)
            context.scene.ea_script_list_index -=1
        elif self.up == False and index < length-1:  #DOWN
            context.scene.ea_script_list.move(index, index+1)
            context.scene.ea_script_list_index +=1

        return {"FINISHED"}

class EA_OT_batch_run_scripts(bpy.types.Operator):
    bl_idname = "easyautomation.batch_run_scripts"
    bl_label = "Batch Run"

    def execute(self, context):

        index = 0
        amount = 0

        for script in context.scene.ea_script_list:
            if script.batchrun:
                bpy.ops.easyautomation.run_script(index=index)
                amount += 1

            index += 1

        self.report({'INFO'}, ("Executed " + str(amount) + " scripts"))

        return {"FINISHED"}

class EA_OT_open_editor(bpy.types.Operator):
    bl_idname = "easyautomation.openeditor"
    bl_label = "Open Code Editor"

    index : bpy.props.IntProperty(name="index")

    def execute(self, context):
        # Edit script in available text editor
        for window in bpy.context.window_manager.windows:
            for area in window.screen.areas:
                if area.type == "TEXT_EDITOR":
                    space_data = area.spaces.active
                    space_data.text = context.scene.ea_script_list[self.index].script

                    return {"FINISHED"}

        # Duplicate current view into a new window and configure it to be ea text editor
        bpy.ops.screen.area_dupli('INVOKE_DEFAULT')
        area = bpy.context.window_manager.windows[-1].screen.areas[0]
        area.type = "TEXT_EDITOR"
        area.spaces[0].text = context.scene.ea_script_list[self.index].script

        return {"FINISHED"}

class EA_OT_add_script(bpy.types.Operator):
    bl_idname = "easyautomation.add_script"
    bl_label = "Add Script"

    def execute(self, context):
        script_list = context.scene.ea_script_list

        script = bpy.data.texts.new("EA-Script.py")
        script.lines.data.write("#EA-Script")

        script_list.add()
        script_list[len(script_list)-1].script = script
        context.scene.ea_script_list_index = len(script_list)-1

        return {"FINISHED"}

class EA_OT_delete_script(bpy.types.Operator):
    bl_idname = "easyautomation.delete_script"
    bl_label = "Delete Script"

    def execute(self, context):
        script_list = context.scene.ea_script_list

        if len(script_list) == 0: return {"CANCELLED"}

        index = context.scene.ea_script_list_index

        script = script_list[index].script
 
        if script != None: bpy.data.texts.remove(script)
        script_list.remove(index)

        context.scene.ea_script_list_index = max(index-1,0)

        return {"FINISHED"}

classes = [
    EA_UL_script_list,
    EA_MT_advanced_menu, 
    EA_OT_import_global,
    EA_OT_make_global,
    EA_OT_refresh_scripts,
    EA_OT_move_script,
    EA_OT_batch_run_scripts,
    EA_OT_open_editor,
    EA_OT_add_script,
    EA_OT_delete_script
]

def register():
    script_item.register()
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.ea_script_list = bpy.props.CollectionProperty(type = script_item.EA_ListItem)
    bpy.types.Scene.ea_script_list_index = bpy.props.IntProperty(name = "Index for Script List", default = 0)
    pass

def unregister(): 
    del bpy.types.Scene.ea_script_list
    del bpy.types.Scene.ea_script_list_index

    for cls in classes:
        bpy.utils.unregister_class(cls)
    script_item.unregister()
    pass