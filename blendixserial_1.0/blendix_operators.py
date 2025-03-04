import bpy
from bpy_types import Operator
from .blendix_connection import serial_connection, serial_thread


class AddCustomObject(Operator):
    """Click to Add Custom Object"""
    bl_idname = "object.add_object"
    bl_label = "Add Custom Object"

    def execute(self, context):
        scene = context.scene

        new_item = scene.custom_object_collection.add()
        new_item.sel_object = None  
        self.report({'INFO'}, "Object Added")
        return {'FINISHED'}

class RemoveCustomObject(Operator):
    """Click to Remove Custom Object"""
    bl_idname = "object.remove_custom_object"
    bl_label = "Remove Custom Object"

    index: bpy.props.IntProperty() # type: ignore

    def execute(self, context):
        scene = context.scene
        scene.custom_object_collection.remove(self.index)
        self.report({'INFO'}, "Object Removed")
        return {'FINISHED'}


class ShowSettingsPopup(bpy.types.Operator):
    """Show Settings Popup"""
    bl_idname = "wm.object_prop_window"
    bl_label = "PREFERENCES" 

    index: bpy.props.IntProperty()  # type: ignore

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        item = scene.custom_object_collection[self.index]

        object_number = self.index + 1

        layout.label(text=f"Animate Transform Data of Object {object_number}", icon="OUTLINER_DATA_MESH")
        layout.separator() 

  
        box = layout.box()
        box.label(text="Transform Properties", icon="FILE_3D")
        
        split = box.split(factor=0.6) 

        col = split.column()
        row = col.row(align=True)
        row.label(text="Property:")
        row.prop(item, "property_name", text="")

        col = split.column()
        row = col.row(align=True)
        row.label(text="Axes:")
        row.prop(item, "selected_axes", text="")
        
        box.separator() 

        box = layout.box()
        box.label(text="Show Axes", icon="ORIENTATION_GLOBAL")
        box.prop(item, "text_object_axis", text="Text Object")
        
        row = box.row()
        row.prop(item, "show_x", text="X")
        row.prop(item, "show_y", text="Y")
        row.prop(item, "show_z", text="Z")

        box.separator()  

        reset_operator = layout.operator(ResetTransformsOperator.bl_idname, text="Reset Transforms", icon="LOOP_BACK")
        reset_operator.object_name = item.sel_object.name if item.sel_object else ""

        layout.separator()  



class ResetTransformsOperator(bpy.types.Operator):
    """Click to reset the transforms of an object to default values."""
    bl_idname = "object.reset_transforms_base"
    bl_label = "Reset Transforms Base"

    object_name: bpy.props.StringProperty() # type: ignore

    def execute(self, context):
        obj = context.scene.objects.get(self.object_name)
        
        if obj is not None:
            obj.location = (0, 0, 0)
            obj.rotation_euler = (0, 0, 0)
            obj.scale = (1, 1, 1)
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, f"Object '{self.object_name}' not found.")
            return {'CANCELLED'}



class StartMovementOperator(Operator):
    """Click to start object movement."""
    bl_idname = "object.start_movement"
    bl_label = "Start Movement"

    def execute(self, context):

        serial_thread.pause_movement = False
        self.report({'INFO'}, "Movement started")
        return {'FINISHED'}


class StopMovementOperator(Operator):
    """Click to stop object movement."""
    bl_idname = "object.stop_movement"
    bl_label = "Stop Movement"

    def execute(self, context):

        serial_thread.pause_movement = True
        self.report({'INFO'}, "Movement stopped")
        return {'FINISHED'}


class ConnectSerialOperator(Operator):
    """Click to connect to a serial port."""
    bl_idname = "serial.connect"
    bl_label = "Connect to Serial"

    def execute(self, context):
        props = context.scene.serial_connection_properties
        serial_connection._port_name = props.port_name
        serial_connection._baud_rate = int(props.baud_rate)

        serial_connection.connect_serial()
        serial_thread.start_serial_thread() 

        try:

            if serial_connection._serial_connection and serial_connection._serial_connection.is_open:
                props.is_connected = True
                props.connection_status = "Connected"
                self.report({'INFO'}, "Connected")

        except:
            self.report({'ERROR'}, f"Failed to connect to serial port {serial_connection._port_name}")
        return {'FINISHED'}


class DisconnectSerialOperator(Operator):
    """Click to disconnect from a serial port."""
    bl_idname = "serial.disconnect"
    bl_label = "Disconnect from Serial"

    def execute(self, context):
        serial_connection.disconnect(serial_thread)
        props = context.scene.serial_connection_properties
        if not serial_connection._serial_connection or not serial_connection._serial_connection.is_open:
            props.is_connected = False
            props.connection_status = "Disconnected"
            self.report({'INFO'}, "Disconnected")
        return {'FINISHED'}




class ShowSettingsPopupSend(bpy.types.Operator):
    """Show Settings Popup"""
    bl_idname = "wm.object_prop_window_send"
    bl_label = "PREFERENCES" 

    index: bpy.props.IntProperty()  # type: ignore

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        item = scene.send_object_collection [self.index]

        object_number = self.index + 1

        layout.label(text=f"Send Keyframe Data {object_number}", icon='ANIM')
        layout.separator() 


        box = layout.box()
        box.label(text="Transform Properties", icon="FILE_3D")
        
        split = box.split(factor=0.6) 

        col = split.column()
        row = col.row(align=True)
        row.label(text="Property:")
        row.prop(item, "property_name", text="")

        col = split.column()
        row = col.row(align=True)
        row.label(text="Axes:")
        row.prop(item, "selected_axes", text="")
        
        box.separator() 

       

class AddSendObject(Operator):
    bl_idname = "object.add_send_object"
    bl_label = "Add Object to Send"

    def execute(self, context):
        scene = context.scene
        new_item = scene.send_object_collection.add()
        new_item.sel_object = None  
        self.report({'INFO'}, "Object Added for Sending")
        return {'FINISHED'}

class RemoveSendObject(Operator):
    bl_idname = "object.remove_send_object"
    bl_label = "Remove Object to Send"

    index: bpy.props.IntProperty() # type: ignore

    def execute(self, context):
        scene = context.scene
        scene.send_object_collection.remove(self.index)
        self.report({'INFO'}, "Object Removed")
        return {'FINISHED'}


class SerialThreadModeOperator(bpy.types.Operator):
    """Operator to select serial thread mode"""
    bl_idname = "serial_thread.select_mode"
    bl_label = "Select Serial Thread Mode"

    modes: bpy.props.StringProperty() # type: ignore

    def execute(self, context):
        selected_mode = self.modes
        serial_thread.set_mode(selected_mode)  
        self.report({'INFO'}, f"Serial Thread mode set to: {selected_mode}")
        return {'FINISHED'}
    


class ShowDebugPopup(bpy.types.Operator):
    """Show Debug Popup"""
    bl_idname = "wm.object_prop_window_debug"
    bl_label = "Debug Mode" 

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.prop(scene, "serial_debug_mode")
        layout.prop(scene, "debug_mode")
        layout.prop(scene, "rawData_debug_mode")
        layout.prop(scene, "dataValidation_debug_mode")
        layout.prop(scene, "serialThread_debug_mode")
        layout.prop(scene, "data_processing_received_debug_mode")
        layout.prop(scene, "data_processing_send_debug_mode")

       

class ShowInfoPopup(bpy.types.Operator):
    """Show Info Popup"""
    bl_idname = "wm.object_prop_window_info"
    bl_label = "About" 

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        row = layout.row()


        main_box = layout.box()
        row = main_box.row(align=True)
        row.label(text="BlendixSerial is a user-friendly Blender addon")
        row = main_box.row(align=True)
        row.label(text="that allows you to control 3D objects via serial")
        row = main_box.row(align=True)
        row.label(text="communication using a simple CSV format.")
        main_box = layout.box()
        row = main_box.row(align=True)
        row.label(text="Made by M.Usman with")
        row.label(icon="FUND")  
        row.label(text=" from Pakistan") 
    

