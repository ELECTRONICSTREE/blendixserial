
from bpy_types import Panel
from .blendix_connection import serial_thread


class SerialConnectionPanel(Panel):
    bl_label = "BLENDIX SERIAL"
    bl_idname = "SCENE_PT_serial_connection"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "blendixserial"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        serial_props = scene.serial_connection_properties

        layout.label(text="Connection Settings", icon='PLUGIN')
        main_box = layout.box()
        row = main_box.row(align=True)
        if not serial_props.is_connected:
            row.operator("serial.connect", text="Connect", icon='LINKED')
        else:
            row.operator("serial.disconnect", text="Disconnect", icon='UNLINKED')

        settings_box = main_box.box()
        settings_box.label(text="Serial Settings", icon='SETTINGS')
        split = settings_box.split(factor=0.3)
        split.label(text="Port")
        split.prop(serial_props, "port_name", text="")
        split = settings_box.split(factor=0.3) 
        split.label(text="Baud Rate")
        split.prop(serial_props, "baud_rate", text="")
        
        settings_box.enabled = not serial_props.is_connected
        status_row = main_box.row(align=True)
        status_row.label(icon='INFO')
        status_row.label(text=f"{serial_props.connection_status}")
        layout = row.operator("wm.object_prop_window_debug", text="", icon="CONSOLE")
        layout = row.operator("wm.object_prop_window_info", text="", icon="QUESTION")

    

class UserInterfacePanel(Panel):
    bl_label = "3D Object Control"
    bl_idname = "OBJECT_PT_blendix_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Blendix Serial"
    bl_parent_id = "SCENE_PT_serial_connection"  

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        serial_mode = scene.serial_thread_modes  

        row = layout.row()
        row.label(icon='SCENE_DATA', text="Update Scene")
        row.prop(scene, "updateSceneDelay", text="Time(s)", slider=True)
        row = layout.row()
        row.prop(scene, "serial_thread_modes", text="Mode")
        serial_thread.set_mode(scene.serial_thread_modes) 
        if serial_thread.pause_movement:
            row.operator("object.start_movement", text="Start Movement")
        else:
            row.operator("object.stop_movement", text="Stop Movement")

 

        row = layout.row()
        row.label(text=f"Current Mode: {scene.serial_thread_modes}" , icon="INFO")

        if serial_mode == 'send':
            self.draw_send_tab(layout, scene)
        elif serial_mode == 'receive':
            self.draw_receive_tab(layout, scene)
        elif serial_mode == 'both':
            layout.prop(scene.my_ui_tabs, "tabs", expand=True)  
            if scene.my_ui_tabs.tabs == 'TAB1':
                self.draw_receive_tab(layout, scene)
            elif scene.my_ui_tabs.tabs == 'TAB2':
                self.draw_send_tab(layout, scene)


    def draw_receive_tab(self, layout, scene):
        layout.label(text="Receive Text Data in 3D View", icon='FILE_FONT')
        font_box = layout.box()
        row = font_box.row()
        row.label(text="Select Font")
        row = font_box.row()
        row.prop_search(scene, "received_text", scene, "objects", text="Text")

        layout.separator()

        layout.label(text="Animate Object", icon='ANIM')
        animate_box = layout.box()
        animate_box.operator("object.add_object", text="Add New Custom Object")

        layout.separator()

        for i, item in enumerate(scene.custom_object_collection):
            item_box = animate_box.box()
            row = item_box.row()
            row.prop(item, "sel_object", text="Object {}".format(i + 1))

            settings_button = row.operator("wm.object_prop_window", text="", icon="PRESET")
            settings_button.index = i

            remove_button = row.operator("object.remove_custom_object", text="", icon='X')
            remove_button.index = i

    def draw_send_tab(self, layout, scene):
        mainbox = layout.box()  
        mainbox.prop(scene, "send_data_method")
        if scene.send_data_method == 'KEYFRAME':
            mainbox.prop(scene, "frame_skip_interval")
        mainbox.operator("object.add_send_object", text="Add New Object to Send")
        mainbox.separator()

        for i, item in enumerate(scene.send_object_collection):
            item_box = mainbox.box()
            row = item_box.row()
            row.prop(item, "sel_object", text="Object {}".format(i + 1))

            settings_button = row.operator("wm.object_prop_window_send", text="", icon="PRESET")
            settings_button.index = i

            remove_button = row.operator("object.remove_send_object", text="", icon='X')
            remove_button.index = i
