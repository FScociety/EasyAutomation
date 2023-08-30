import bpy

from . import functions

class EA_VariableItem(bpy.types.PropertyGroup):
    type : bpy.props.IntProperty(default=0)
    type = 0

    types = [
        "int_type",
        "string_type",
        "bool_type",
        "float_type",
        "object_type",
        "collection_type",
        "material_type",
        "texture_type"
    ]

    seperate: bpy.props.BoolProperty(default=False)
    new_line: bpy.props.BoolProperty(default=True)
    show_name: bpy.props.BoolProperty(default=True)
    show_value: bpy.props.BoolProperty(default=True)

    name : bpy.props.StringProperty()
    
    int_type : bpy.props.IntProperty(default=0)                                   
    string_type : bpy.props.StringProperty(default="")                              
    bool_type : bpy.props.BoolProperty(default=False)                                
    float_type : bpy.props.FloatProperty(default=0.0)          
    object_type : bpy.props.PointerProperty(type=bpy.types.Object)      
    collection_type : bpy.props.PointerProperty(type=bpy.types.Collection)
    material_type = bpy.props.PointerProperty(type=bpy.types.Material)
    
class EA_ListItem(bpy.types.PropertyGroup):
    script : bpy.props.PointerProperty(type=bpy.types.Text)
    batchrun : bpy.props.BoolProperty(name="Batch Run")   

class EA_OT_RunScript(bpy.types.Operator):
    bl_idname = "easyautomation.run_script"
    bl_label = "Run Script"

    index : bpy.props.IntProperty(name="index")

    def execute(self, context):

        script_list = context.scene.ea_script_list
        script_item = script_list[self.index]
        script = script_item.script

        functions.reload_external_script(script)

        script_line_list = script.as_string().splitlines()
        script_line_list_temp = script_line_list[:]

        variables = script_item.variables

        added_i = 0

        globlsparam = {}
        localsparam = {}

        #Run through all variables and define variables
        for var_item in variables:
            name = var_item.name

            for i, line in enumerate(script_line_list_temp):
                if "#Global" in line and line.startswith(name):
                    value = getattr(var_item, var_item.types[var_item.type])
                    globlsparam[name] = value
                    script_line_list[i] = ""
                    break
                

        final_script = ""

        #Convert list to String Script back and add the new assignments
        for line in script_line_list:
            final_script = final_script + line + "\n"    

        exec(final_script, globlsparam, globlsparam) #Komisch aber wenn ich sonst localparams drin hab kommen fehler

        self.report({'INFO'}, ("Executed '" +script.name+"'"))

        return {"FINISHED"}

class EA_OT_RefreshVariables(bpy.types.Operator):
    bl_idname = "easyautomation.refresh_script"
    bl_label = "Update the Script's Variables"

    var_attribs = ["#Global", "#Seperator", "#NoLine", "#NoName", "#NoValue"]

    def execute(self, context):
        script_list = context.scene.ea_script_list
        scriptItem = script_list[context.scene.ea_script_list_index]

        if scriptItem.script == None: 
            scriptItem.variables.clear()
            return {"FINISHED"}

        functions.reload_external_script(scriptItem.script)
        
        ui_lines = list()

        i = 0

        for variable_line in scriptItem.script.lines:
            line = variable_line.body
            for var_attrib in self.var_attribs:
                if var_attrib in line:
                    ui_lines.append([line, i])
                    i+=1
                    print("Found Line: ", line)
                    break
        
        variables = scriptItem.variables
        old_list = list()
        for variable in variables:
            var_copy = [variable.name, getattr(variable, variable.types[variable.type])]
            old_list.append(var_copy)

        variables.clear()

        for lineComb in ui_lines:
            raw_line = lineComb[0]
            i = lineComb[1]

            processed_line = raw_line.replace(" ", "")
            for var_attrib in self.var_attribs:
                processed_line = processed_line.replace(var_attrib, "")

            if ":" in processed_line or "=" in processed_line:
                var_value = None

                if ":" in processed_line:
                    split_line = processed_line.split(":")
                    var_type = split_line[1]
                    var_type_eval = eval(var_type)
                    if var_type_eval.__module__ == 'builtins':
                        var_value = var_type_eval() # Create empty variable of the type
                    else:
                        var_value = None
                elif "=" in processed_line:
                    split_line = processed_line.split("=")
                    var_value = eval(split_line[1])
                    var_type = type(var_value).__name__

                var = variables.add()
                var.name = split_line[0]

                if (var_type == "int"):
                    var.type = 0
                elif (var_type == "str"):
                    var.type = 1
                elif (var_type == "bool"):
                    var.type = 2
                elif (var_type == "float"):
                    var.type = 3
                elif ("Object" in var_type):
                    var.type = 4
                elif ("Collection" in var_type):
                    var.type = 5
                elif ("Material" in var_type):
                    var.type = 6
                match_found = False

                for old_variable in old_list:

                    #Check if the names match and the types of the values match or the value is generic
                    if old_variable[0] == var.name and (type(old_variable[1]) == type(var_value) or var_value == None):
                        matched_old_value = old_variable[1]
                        match_found = True
                        break

                if match_found and matched_old_value == var_value:
                    print("Found Old Variable and Matched the values")
                    setattr(var, var.types[var.type], var_value)
                elif match_found:
                    print("Just Found Old Variable")
                    setattr(var, var.types[var.type], matched_old_value)
                else:
                    print("not matched")
                    setattr(var, var.types[var.type], var_value)

            var = variables[len(variables)-1]

            if "#NoName" in raw_line[0]:
                variables[i].show_name = False

            for i, var_attrib in enumerate(self.var_attribs):
                if var_attrib in raw_line:
                    if i == 1:
                        var.seperate = True
                    elif i == 2:
                        var.new_line = False
                    elif i == 3:
                        var.show_name = False
                    elif i == 4:
                        var.show_value = False

        return {"FINISHED"}

classes = [
    EA_VariableItem,
    EA_ListItem,
    EA_OT_RunScript,
    EA_OT_RefreshVariables
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    EA_ListItem.variables = bpy.props.CollectionProperty(type=EA_VariableItem)

def unregister():

    del EA_ListItem.variables

    for cls in classes:
        bpy.utils.unregister_class(cls)
