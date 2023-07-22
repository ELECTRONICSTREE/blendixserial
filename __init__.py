# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.




bl_info = {
    "name" : "blendixserial",
    "author" : "M.Usman",
    "description" : "3D Object control via Simple UART (Serial Communication)",
    "blender" : (3, 5, 1),
    "version" : (0, 12, 0),
    "location" : "View3D > Properties > blendix serial",
    "doc_url": "https://arduinomagix.blogspot.com/p/blender-serial-control-addon.html",
    "category" : "3D View"
}




import serial
import queue
import math
import bpy
import threading

class SerialConnection:
    """Represents a serial connection.

    This class provides methods to connect and disconnect from a serial port.

    Attributes:
        ser (serial.Serial): The serial connection object.
        port (str): The name of the serial port.
        baud_rate (int): The baud rate for the serial communication.
    """

    def __init__(self):
        self.ser = None
        self.port = ''
        self.baud_rate = 9600

    def connect_serial(self):
        """Connects to the serial port.

        If a serial connection already exists, it is first closed before establishing a new connection.

        Returns:
            None
        """
        if self.ser is not None:
            self.ser.close()
        self.ser = serial.Serial(self.port, self.baud_rate)

    def disconnect_serial(self):
        """Disconnects from the serial port.

        If a serial connection is open, it is closed and the connection object is set to None.

        Returns:
            None
        """
        if self.ser is not None and self.ser.is_open:
            self.ser.flush()
            self.ser.close()
            self.ser = None
            print(f"Disconnected from serial port {self.port}")
        else:
            print("Serial connection is not open")



class ObjectMovement:
    """Represents an object movement controller.

    This class provides methods to update the position, rotation, and text of objects in Blender based on data received from a serial connection.

    Attributes:
        data_queue (queue.Queue): A queue to store the incoming data.
        pause_movement (bool): A flag indicating whether object movement is paused or not.
    """

    def __init__(self):
        self.data_queue = queue.Queue()
        self.pause_movement = True
    

    def update_text_object(self, obj, text):
        """Updates the text of a text object.

        Args:
            obj (bpy.types.Object): The text object to update.
            text (str): The new text to assign to the object.
        """
        if obj is not None and obj.type == 'FONT':
            obj.data.body = text
            
    def update_text_string(self, obj, text):
        """Updates the text string of an object.

        Args:
            obj (bpy.types.Object): The object to update.
            text (str): The new text string to assign to the object.
        """
        if obj is not None and obj.type == 'FONT':
            obj.data.body = text
                
    def move_object(self, obj, x, y, z, property_name, selected_axes):
        """Moves an object in the scene.

        Args:
            obj (bpy.types.Object): The object to move.
            x (float): The new x-coordinate value.
            y (float): The new y-coordinate value.
            z (float): The new z-coordinate value.
            property_name (str): The name of the property to update ('rotation_euler' or any other property).
            selected_axes (str): A string specifying the selected axes ('X', 'Y', 'Z', or a combination of them).
        """
        if obj is not None:
            if property_name == 'rotation_euler':
                # Scale incoming values to match the rotation range in Blender
                x_scaled = x / 360 * 2 * math.pi
                y_scaled = y / 360 * 2 * math.pi
                z_scaled = z / 360 * 2 * math.pi
                rotation = list(obj.rotation_euler)
                if 'X' in selected_axes:
                    rotation[0] = x_scaled
                if 'Y' in selected_axes:
                    rotation[1] = y_scaled
                if 'Z' in selected_axes:
                    rotation[2] = z_scaled
                obj.rotation_euler = rotation
            else:
                location = list(getattr(obj, property_name))
                if 'X' in selected_axes:
                    location[0] = x
                if 'Y' in selected_axes:
                    location[1] = y
                if 'Z' in selected_axes:
                    location[2] = z
                setattr(obj, property_name, location)

    def update_scene(self):
        """Updates the Blender scene based on the received data.

        Returns:
            float: The time delay between scene updates.
        """
        if serial_connection.ser is not None and not self.pause_movement:
            # Clear the data queue before processing new data
            try:
                data_queue_length = self.data_queue.qsize()
                if data_queue_length > 1:
                    self.data_queue.queue.clear()
                elif data_queue_length == 1:
                    data = self.data_queue.get()
                    movement_data, text_data = data.split(';')  # Separate movement and text data
                    x1, y1, z1, x2, y2, z2, x3, y3, z3 = map(float, movement_data.split(','))  # Separate data for both objects
                    property_name_1 = bpy.context.scene.property_name_1
                    property_name_2 = bpy.context.scene.property_name_2
                    property_name_3 = bpy.context.scene.property_name_3
                    obj1 = bpy.context.scene.objects.get(bpy.context.scene.object_name_1)
                    obj2 = bpy.context.scene.objects.get(bpy.context.scene.object_name_2)
                    obj3 = bpy.context.scene.objects.get(bpy.context.scene.object_name_3)
                    selected_axes_1 = bpy.context.scene.selected_axes_1
                    selected_axes_2 = bpy.context.scene.selected_axes_2
                    selected_axes_3 = bpy.context.scene.selected_axes_3
                    self.move_object(obj1, x1, y1, z1, property_name_1, selected_axes_1)
                    self.move_object(obj2, x2, y2, z2, property_name_2, selected_axes_2)
                    self.move_object(obj3, x3, y3, z3, property_name_3, selected_axes_3)

                   
                    text_obj1 = bpy.context.scene.objects.get(bpy.context.scene.text_object_name_1)
                    text_obj2 = bpy.context.scene.objects.get(bpy.context.scene.text_object_name_2)
                    text_obj3 = bpy.context.scene.objects.get(bpy.context.scene.text_object_name_3)
                    self.update_text_object(text_obj1, "x1: {}, y1: {}, z1: {}".format(x1, y1, z1))
                    self.update_text_object(text_obj2, "x2: {}, y2: {}, z2: {}".format(x2, y2, z2))
                    self.update_text_object(text_obj3, "x3: {}, y3: {}, z3: {}".format(x3, y3, z3))




                    
                    text_content1 = ""
                    text_content2 = ""
                    text_content3 = ""

                    if bpy.context.scene.show_x1:
                        text_content1 += "{}\n".format(x1)
                    if bpy.context.scene.show_y1:
                        text_content1 += "{}\n".format(y1)
                    if bpy.context.scene.show_z1:
                        text_content1 += "{}\n".format(z1)

                    if bpy.context.scene.show_x2:
                        text_content2 += "{}\n".format(x2)
                    if bpy.context.scene.show_y2:
                        text_content2 += "{}\n".format(y2)
                    if bpy.context.scene.show_z2:
                        text_content2 += "{}\n".format(z2)

                    if bpy.context.scene.show_x3:
                        text_content3 += "{}\n".format(x3)
                    if bpy.context.scene.show_y3:
                        text_content3 += " {}\n".format(y3)
                    if bpy.context.scene.show_z3:
                        text_content3 += "{}\n".format(z3)

                    self.update_text_object(text_obj1, text_content1.strip())
                    self.update_text_object(text_obj2, text_content2.strip())
                    self.update_text_object(text_obj3, text_content3.strip())

                    text_string = bpy.context.scene.objects.get(bpy.context.scene.received_text)
                    self.update_text_string(text_string, text_data)

            except ValueError:
                print("Invalid data received from serial port")
        return bpy.context.scene.blendix_serial_props.update_scene_delay



    def serial_thread(self):
        """Thread for reading data from the serial port."""
        while True:
            try:
                if serial_connection.ser is not None and serial_connection.ser.is_open:
                    if serial_connection.ser.in_waiting:
                        data = serial_connection.ser.readline().decode().rstrip()
                        if data:
                            self.data_queue.put(data)
                else:
                    break
            except serial.SerialException:
                break



    def start_serial_thread(self):
        """Starts the serial thread."""
        thread = threading.Thread(target=self.serial_thread)
        thread.daemon = True
        thread.start()




class SceneProperties(bpy.types.PropertyGroup):
    update_scene_delay: bpy.props.FloatProperty(
        name="Update Scene Delay",
        default=0.01,
        min=0.001,
        max=2,
        description="Delay between scene updates",
        step=0.001
    )


class BlendixUIPanel(bpy.types.Panel):
    """Represents a panel for controlling object movement in Blender.

    This panel provides options to connect/disconnect from a serial port, start/stop object movement, and control the movement of multiple objects in the scene.

    Inherits from bpy.types.Panel.
    """

    bl_label = "Blendix Serial Control"
    bl_idname = "OBJECT_PT_movement_control_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Blendix Serial"


    
    

    def draw(self, context):
        """Draws the movement control panel.

        Args:
            context (bpy.types.Context): The context object.
        """
        layout = self.layout
        scene_props = context.scene.blendix_serial_props
        if serial_connection.ser is None:
            layout.operator("object.connect_serial", text="Connect Serial")
            layout.prop(context.scene, "port")
            layout.prop(context.scene, "baud_rate")
        else:

            layout.separator()
            layout.operator("object.disconnect_serial", text="Disconnect Serial")

            if object_movement.pause_movement:
                layout.operator("object.start_movement", text="Start Movement")
            else:
                layout.operator("object.stop_movement", text="Stop Movement")

            

            

            row = layout.row()
            row.prop(context.scene, "tab_index", expand=True)    

            if context.scene.tab_index == 'SCENE':
                self.draw_tab1(context)
            elif context.scene.tab_index == 'TEXTOB':
                self.draw_tab2(context)
            elif context.scene.tab_index == 'OB_ONE':
                self.draw_tab3(context)

            elif context.scene.tab_index == 'OB_TWO':
                self.draw_tab4(context)
            elif context.scene.tab_index == 'OB_THREE':
                self.draw_tab5(context)           

            
            
    def draw_tab1(self, context):
        layout = self.layout
        scene_props = context.scene.blendix_serial_props
                    
        

        # Update Scene Delay
        box = layout.box()
        row = box.row()
        row.label(icon='SCENE_DATA',text="Update Scene Delay")
        row = box.row()
        row.prop(scene_props, "update_scene_delay", text="Delay (s)", slider=True)           

            
            
    def draw_tab2(self, context):
        layout = self.layout
        

        # Received Text Data
        box = layout.box()
        row = box.row()
        row.label(icon='FILE_FONT',text="Received Text Data")
        row = box.row()
        row.prop_search(context.scene, "received_text", context.scene, "objects", text="Text")
        
                

    def draw_tab3(self, context):
        layout = self.layout
        # Object 1
        box = layout.box()
        row = box.row()
        row.label(icon='OBJECT_DATA',text="Movement Control Object 1")
        row = box.row()
        row.prop_search(context.scene, "object_name_1", context.scene, "objects", text="Object 1")
        row = box.row()
        row.prop(context.scene, "property_name_1", text="")
        row.prop(context.scene, "selected_axes_1", text="")
        row = box.row()
        row.label(text="Select Text to see Values")
        row = box.row()
        row.prop(context.scene, "show_x1", text="x1")
        row.prop(context.scene, "show_y1", text="y1")
        row.prop(context.scene, "show_z1", text="z1")
        row = box.row()
        row.prop_search(context.scene, "text_object_name_1", context.scene, "objects", text="")
        row = box.row()
        row.operator("object.reset_transforms_1", text="Reset Transforms")    

          
    
            
    def draw_tab4(self, context):
        layout = self.layout        
        # Object 2
        box = layout.box()
        row = box.row()
        row.label(icon='OBJECT_DATA',text="Movement Control Object 2")
        row = box.row()
        row.prop_search(context.scene, "object_name_2", context.scene, "objects", text="Object 2")
        row = box.row()
        row.prop(context.scene, "property_name_2", text="")
        row.prop(context.scene, "selected_axes_2", text="")
        row = box.row()
        row.label(text="Select Text to see Values")
        row = box.row()
        row.prop(context.scene, "show_x2", text="x2")
        row.prop(context.scene, "show_y2", text="y2")
        row.prop(context.scene, "show_z2", text="z2")
        row = box.row()
        row.prop_search(context.scene, "text_object_name_2", context.scene, "objects", text="")
        row = box.row()
        row.operator("object.reset_transforms_2", text="Reset Transforms")
            

    def draw_tab5(self, context):
        layout = self.layout
        # Object 3
        box = layout.box()
        row = box.row()
        row.label(icon='OBJECT_DATA',text="Movement Control Object 3")
        row = box.row()
        row.prop_search(context.scene, "object_name_3", context.scene, "objects", text="Object 3")
        row = box.row()
        row.prop(context.scene, "property_name_3", text="")
        row.prop(context.scene, "selected_axes_3", text="")
        row = box.row()
        row.label(text="Select Text to see Values")
        row = box.row()
        row.prop(context.scene, "show_x3", text="x3")
        row.prop(context.scene, "show_y3", text="y3")
        row.prop(context.scene, "show_z3", text="z3")
        row = box.row()
        row.prop_search(context.scene, "text_object_name_3", context.scene, "objects", text="")
        row = box.row()
        row.operator("object.reset_transforms_3", text="Reset Transforms")




class ResetTransformsOperator(bpy.types.Operator):
    """Operator to reset the transforms of an object to default values."""
    bl_idname = "object.reset_transforms_base"
    bl_label = "Reset Transforms Base"

    def reset_transforms(self, obj):
        """Reset the transforms of the specified object to default values.

        Args:
            obj (bpy.types.Object): The object to reset transforms for.
        """
        obj.location = (0, 0, 0)
        obj.rotation_euler = (0, 0, 0)
        obj.scale = (1, 1, 1)

    def execute(self, context):
        """Execute the operator.

        Args:
            context (bpy.types.Context): The context object.

        Returns:
            dict: The result of the operator execution.
        """
        return {'FINISHED'}


class ResetTransformsObject1Operator(ResetTransformsOperator):
    """Operator to reset the transforms of Object 1 to default values."""
    bl_idname = "object.reset_transforms_1"
    bl_label = "Reset Transforms Object 1"

    def execute(self, context):
        """Execute the operator to reset transforms for Object 1.

        Args:
            context (bpy.types.Context): The context object.

        Returns:
            dict: The result of the operator execution.
        """
        obj = bpy.context.scene.objects[bpy.context.scene.object_name_1]
        self.reset_transforms(obj)
        self.report({'INFO'}, "Object 1 transforms reset")
        return {'FINISHED'}


class ResetTransformsObject2Operator(ResetTransformsOperator):
    """Operator to reset the transforms of Object 2 to default values."""
    bl_idname = "object.reset_transforms_2"
    bl_label = "Reset Transforms Object 2"

    def execute(self, context):
        """Execute the operator to reset transforms for Object 2.

        Args:
            context (bpy.types.Context): The context object.

        Returns:
            dict: The result of the operator execution.
        """
        obj = bpy.context.scene.objects[bpy.context.scene.object_name_2]
        self.reset_transforms(obj)
        self.report({'INFO'}, "Object 2 transforms reset")
        return {'FINISHED'}


class ResetTransformsObject3Operator(ResetTransformsOperator):
    """Operator to reset the transforms of Object 3 to default values."""
    bl_idname = "object.reset_transforms_3"
    bl_label = "Reset Transforms Object 3"

    def execute(self, context):
        """Execute the operator to reset transforms for Object 3.

        Args:
            context (bpy.types.Context): The context object.

        Returns:
            dict: The result of the operator execution.
        """
        obj = bpy.context.scene.objects[bpy.context.scene.object_name_3]
        self.reset_transforms(obj)
        self.report({'INFO'}, "Object 3 transforms reset")
        return {'FINISHED'}


class StartMovementOperator(bpy.types.Operator):
    """Operator to start object movement."""
    bl_idname = "object.start_movement"
    bl_label = "Start Movement"

    def execute(self, context):
        """Execute the operator to start object movement.

        Args:
            context (bpy.types.Context): The context object.

        Returns:
            dict: The result of the operator execution.
        """
        object_movement.pause_movement = False
        self.report({'INFO'}, "Movement started")
        return {'FINISHED'}


class StopMovementOperator(bpy.types.Operator):
    """Operator to stop object movement."""
    bl_idname = "object.stop_movement"
    bl_label = "Stop Movement"

    def execute(self, context):
        """Execute the operator to stop object movement.

        Args:
            context (bpy.types.Context): The context object.

        Returns:
            dict: The result of the operator execution.
        """
        object_movement.pause_movement = True
        self.report({'INFO'}, "Movement stopped")
        return {'FINISHED'}


class ConnectSerialOperator(bpy.types.Operator):
    """Operator to connect to a serial port."""
    bl_idname = "object.connect_serial"
    bl_label = "Connect Serial"

    def execute(self, context):
        """Execute the operator to connect to a serial port.

        Args:
            context (bpy.types.Context): The context object.

        Returns:
            dict: The result of the operator execution.
        """
        serial_connection.port = context.scene.port
        serial_connection.baud_rate = context.scene.baud_rate
        try:
            serial_connection.connect_serial()
            object_movement.start_serial_thread()
            self.report({'INFO'}, f"Connected to serial port {serial_connection.port}")
        except:
            self.report({'ERROR'}, f"Failed to connect to serial port {serial_connection.port}")
        return {'FINISHED'}


class DisconnectSerialOperator(bpy.types.Operator):
    """Operator to disconnect from a serial port."""
    bl_idname = "object.disconnect_serial"
    bl_label = "Disconnect Serial"

    def execute(self, context):
        """Execute the operator to disconnect from a serial port.

        Args:
            context (bpy.types.Context): The context object.

        Returns:
            dict: The result of the operator execution.
        """
        serial_connection.disconnect_serial()
        self.report({'INFO'}, f"Disconnected from serial port {serial_connection.port}")
        return {'FINISHED'}

def register():
    """Register the necessary classes and properties."""

    bpy.utils.register_class(BlendixUIPanel)
    bpy.utils.register_class(StartMovementOperator)
    bpy.utils.register_class(StopMovementOperator)
    bpy.utils.register_class(ConnectSerialOperator)
    bpy.utils.register_class(DisconnectSerialOperator)
    bpy.utils.register_class(ResetTransformsOperator)
    bpy.utils.register_class(ResetTransformsObject1Operator)
    bpy.utils.register_class(ResetTransformsObject2Operator)
    bpy.utils.register_class(ResetTransformsObject3Operator)
    bpy.utils.register_class(SceneProperties)
    bpy.types.Scene.blendix_serial_props = bpy.props.PointerProperty(type=SceneProperties)


    bpy.types.Scene.tab_index = bpy.props.EnumProperty(
        items=[
            ('SCENE', "Scene", "Scene"),
            ('TEXTOB', "Text OB", "Text OB"),
            ('OB_ONE', "OB1", "OB1"),
            ('OB_TWO', "OB2", "OB2"),
            ('OB_THREE', "OB3", "OB3"),
        ],
        default='OB_ONE'
    )

    bpy.types.Scene.property_name_1 = bpy.props.EnumProperty(
        name="Property (Object 1)",
        items=[
            ("location", "Location", ""),
            ("rotation_euler", "Rotation", ""),
            ("scale", "Scale", ""),
        ],
        default="location",
    )

    bpy.types.Scene.property_name_2 = bpy.props.EnumProperty(
        name="Property (Object 2)",
        items=[
            ("location", "Location", ""),
            ("rotation_euler", "Rotation", ""),
            ("scale", "Scale", ""),
        ],
        default="location",
    )

    bpy.types.Scene.property_name_3 = bpy.props.EnumProperty(
        name="Property (Object 3)",
        items=[
            ("location", "Location", ""),
            ("rotation_euler", "Rotation", ""),
            ("scale", "Scale", ""),
        ],
        default="location",
    )

    bpy.types.Scene.selected_axes_1 = bpy.props.EnumProperty(
        name="Selected Axes (Object 1)",
        items=[
            ("X", "X", ""),
            ("Y", "Y", ""),
            ("Z", "Z", ""),
            ("XY", "XY", ""),
            ("XZ", "XZ", ""),
            ("YZ", "YZ", ""),
            ("XYZ", "XYZ", ""),
        ],
        default="XYZ",
    )

    bpy.types.Scene.selected_axes_2 = bpy.props.EnumProperty(
        name="Selected Axes (Object 2)",
        items=[
            ("X", "X", ""),
            ("Y", "Y", ""),
            ("Z", "Z", ""),
            ("XY", "XY", ""),
            ("XZ", "XZ", ""),
            ("YZ", "YZ", ""),
            ("XYZ", "XYZ", ""),
        ],
        default="XYZ",
    )

    bpy.types.Scene.selected_axes_3 = bpy.props.EnumProperty(
        name="Selected Axes (Object 3)",
        items=[
            ("X", "X", ""),
            ("Y", "Y", ""),
            ("Z", "Z", ""),
            ("XY", "XY", ""),
            ("XZ", "XZ", ""),
            ("YZ", "YZ", ""),
            ("XYZ", "XYZ", ""),
        ],
        default="XYZ",
    )

    bpy.types.Scene.port = bpy.props.StringProperty(
        name="Port", default=serial_connection.port)

    bpy.types.Scene.baud_rate = bpy.props.IntProperty(
        name="Baud Rate", default=serial_connection.baud_rate)

    bpy.types.Scene.object_name_1 = bpy.props.StringProperty(
        name="Object Name (Object 1)", default="")

    bpy.types.Scene.object_name_2 = bpy.props.StringProperty(
        name="Object Name (Object 2)", default="")

    bpy.types.Scene.object_name_3 = bpy.props.StringProperty(
        name="Object Name (Object 3)", default="")

    bpy.types.Scene.text_object_name_1 = bpy.props.StringProperty(
        name="Text Object Name (Object 1)", default="")

    bpy.types.Scene.text_object_name_2 = bpy.props.StringProperty(
        name="Text Object Name (Object 2)", default="")

    bpy.types.Scene.text_object_name_3 = bpy.props.StringProperty(
        name="Text Object Name (Object 3)", default="")

    bpy.types.Scene.received_text = bpy.props.StringProperty(
        name="Received Text (String)", default="")
    
    bpy.types.Scene.show_x1 = bpy.props.BoolProperty(default=False)
    bpy.types.Scene.show_y1 = bpy.props.BoolProperty(default=False)
    bpy.types.Scene.show_z1 = bpy.props.BoolProperty(default=False)
    bpy.types.Scene.show_x2 = bpy.props.BoolProperty(default=False)
    bpy.types.Scene.show_y2 = bpy.props.BoolProperty(default=False)
    bpy.types.Scene.show_z2 = bpy.props.BoolProperty(default=False)
    bpy.types.Scene.show_x3 = bpy.props.BoolProperty(default=False)
    bpy.types.Scene.show_y3 = bpy.props.BoolProperty(default=False)
    bpy.types.Scene.show_z3 = bpy.props.BoolProperty(default=False)


def unregister():
    """Unregister the classes and remove properties."""

    bpy.utils.unregister_class(BlendixUIPanel)
    bpy.utils.unregister_class(StartMovementOperator)
    bpy.utils.unregister_class(StopMovementOperator)
    bpy.utils.unregister_class(ConnectSerialOperator)
    bpy.utils.unregister_class(DisconnectSerialOperator)
    bpy.utils.unregister_class(ResetTransformsOperator)
    bpy.utils.unregister_class(ResetTransformsObject1Operator)
    bpy.utils.unregister_class(ResetTransformsObject2Operator)
    bpy.utils.unregister_class(ResetTransformsObject3Operator)

    del bpy.types.Scene.tab_index
    del bpy.types.Scene.property_name_1
    del bpy.types.Scene.property_name_2
    del bpy.types.Scene.property_name_3
    del bpy.types.Scene.selected_axes_1
    del bpy.types.Scene.selected_axes_2
    del bpy.types.Scene.selected_axes_3
    del bpy.types.Scene.port
    del bpy.types.Scene.baud_rate
    del bpy.types.Scene.object_name_1
    del bpy.types.Scene.object_name_2
    del bpy.types.Scene.object_name_3
    del bpy.types.Scene.text_object_name_1
    del bpy.types.Scene.text_object_name_2
    del bpy.types.Scene.text_object_name_3
    del bpy.types.Scene.received_text

    del bpy.types.Scene.show_x1
    del bpy.types.Scene.show_y1
    del bpy.types.Scene.show_z1
    del bpy.types.Scene.show_x2
    del bpy.types.Scene.show_y2
    del bpy.types.Scene.show_z2
    del bpy.types.Scene.show_x3
    del bpy.types.Scene.show_y3
    del bpy.types.Scene.show_z3

serial_connection = SerialConnection()
object_movement = ObjectMovement()

bpy.app.timers.register(object_movement.update_scene,persistent=True)

if __name__ == "__main__":
    register()

