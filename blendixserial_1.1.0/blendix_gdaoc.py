import bpy
from .blendix_connection import serial_thread, serial_connection
import math
import serial



def timer_func():
    if not hasattr(timer_func, "last_numerical_data"):
        timer_func.last_numerical_data = None
    if not hasattr(timer_func, "last_text_data"):
        timer_func.last_text_data = None

    if serial_connection._serial_connection is not None and not serial_thread.pause_movement:
        latest_data = None
        while not serial_thread.data_queue.empty():
            latest_data = serial_thread.get_data_from_queue()  
        if latest_data:
            numerical_data, text_data = latest_data  

            if numerical_data != timer_func.last_numerical_data or text_data != timer_func.last_text_data:
                if bpy.context.scene.data_processing_received_debug_mode:
                    print(f"Data Processing Received:--> Data in Queue - Numerical: {numerical_data}, Text: '{text_data}'")
                process_data(bpy.context, numerical_data, text_data)

                timer_func.last_numerical_data = numerical_data
                timer_func.last_text_data = text_data
            else:
                if bpy.context.scene.data_processing_received_debug_mode:
                    print("Data Processing Received:--> Duplicate data, discarded")
        else:
            if bpy.context.scene.data_processing_received_debug_mode:
                print("Data Processing Received:--> No data available in the queue")
    
    return  bpy.context.scene.updateSceneDelay   



def process_data(context, numerical_data, text_data):
    scene = context.scene
    if numerical_data:
        update_objects(scene, numerical_data)
    if text_data:
        update_text_objects(scene, text_data, numerical_data)  


def update_objects(scene, numerical_data):
    for i, item in enumerate(scene.custom_object_collection):

        if i * 3 + 2 >= len(numerical_data):
            continue

        selected_object = item.sel_object
        property_name = item.property_name
        selected_axes = item.selected_axes

        if selected_object:
            base_index = i * 3
            if property_name == "location":
                update_location(selected_object, selected_axes, numerical_data, base_index)
            elif property_name == "rotation_euler":
                update_rotation(selected_object, selected_axes, numerical_data, base_index)
            elif property_name == "scale":
                update_scale(selected_object, selected_axes, numerical_data, base_index)



def update_location(obj, selected_axes, numerical_data, base_index):
    if "X" in selected_axes and base_index < len(numerical_data):
        obj.location.x = numerical_data[base_index]
    if "Y" in selected_axes and base_index + 1 < len(numerical_data):
        obj.location.y = numerical_data[base_index + 1]
    if "Z" in selected_axes and base_index + 2 < len(numerical_data):
        obj.location.z = numerical_data[base_index + 2]



def update_rotation(obj, selected_axes, numerical_data, base_index):
    if base_index < len(numerical_data) and "X" in selected_axes:
        obj.rotation_euler.x = numerical_data[base_index] / 360 * 2 * math.pi
    if base_index + 1 < len(numerical_data) and "Y" in selected_axes:
        obj.rotation_euler.y = numerical_data[base_index + 1] / 360 * 2 * math.pi
    if base_index + 2 < len(numerical_data) and "Z" in selected_axes:
        obj.rotation_euler.z = numerical_data[base_index + 2] / 360 * 2 * math.pi


def update_scale(obj, selected_axes, numerical_data, base_index):
    if "X" in selected_axes and base_index < len(numerical_data):
        obj.scale.x = numerical_data[base_index]
    if "Y" in selected_axes and base_index + 1 < len(numerical_data):
        obj.scale.y = numerical_data[base_index + 1]
    if "Z" in selected_axes and base_index + 2 < len(numerical_data):
        obj.scale.z = numerical_data[base_index + 2]


def update_text_objects(scene, text_data, numerical_data):  
    for i, item in enumerate(scene.custom_object_collection):
        text_object_axis = item.text_object_axis
        show_x = item.show_x
        show_y = item.show_y
        show_z = item.show_z

        if text_object_axis:
            axis_text = build_axis_text(i, show_x, show_y, show_z, numerical_data)  
            text_object_axis.data.body = axis_text

    if text_data:
        received_text_obj = bpy.context.scene.received_text
        if received_text_obj and received_text_obj.type == 'FONT':
            received_text_obj.data.body = text_data


def build_axis_text(index, show_x, show_y, show_z, numerical_data):
    axis_text_parts = []
    
    if show_x and (index * 3 < len(numerical_data)):
        axis_text_parts.append(f" {numerical_data[index * 3]:.2f}")
    if show_y and (index * 3 + 1 < len(numerical_data)):
        axis_text_parts.append(f" {numerical_data[index * 3 + 1]:.2f}")
    if show_z and (index * 3 + 2 < len(numerical_data)):
        axis_text_parts.append(f" {numerical_data[index * 3 + 2]:.2f}")
    
    use_newline = bpy.context.scene.axis_text_newline
    separator = "\n" if use_newline else " "
    
    return separator.join(axis_text_parts)





def on_frame_change_post(scene):

    frame_skip_interval = scene.frame_skip_interval if hasattr(scene, "frame_skip_interval") else 1

    if frame_skip_interval == 0:
        send_data = True
    else:
        send_data = bpy.context.scene.frame_current % frame_skip_interval == 0

    if send_data:
        if (
            serial_connection._serial_connection is not None
            and serial_connection._serial_connection.is_open
            and serial_thread.pause_movement is False
            and serial_thread.mode in ['send', 'both']  
        ):
            try:
                data_to_send = ""
                
                for i, item in enumerate(scene.send_object_collection):
                    obj = item.sel_object
                    property_name = item.property_name
                    selected_axes = item.selected_axes
                    
                    data_to_send += format_data_for_object(obj, property_name, selected_axes)

                    if i < len(scene.send_object_collection) - 1:
                        data_to_send += ", "

                data_to_send += ";"

                serial_thread.queue_send_data(data_to_send)

                if bpy.context.scene.data_processing_send_debug_mode:
                    print(f"Data Processing Debugging:--> Data queued to send: {data_to_send}")

            except serial.SerialException:
                if bpy.context.scene.data_processing_send_debug_mode:
                    print("Data Processing Debugging:--> Error writing data to serial port")
                serial_connection.disconnect(serial_thread)


                
def format_data_for_object(obj, transform_property, selected_axes):

    if obj is None:
        return "0.00, 0.00, 0.00"
    
    x_value = "0.00"
    y_value = "0.00"
    z_value = "0.00"
    

    if transform_property == 'location':
        if 'X' in selected_axes:
            x_value = f"{obj.location.x:.2f}"
        if 'Y' in selected_axes:
            y_value = f"{obj.location.y:.2f}"
        if 'Z' in selected_axes:
            z_value = f"{obj.location.z:.2f}"
            
    elif transform_property == 'rotation_euler':
        rotation_degrees = [math.degrees(angle) for angle in obj.rotation_euler]
        if 'X' in selected_axes:
            x_value = f"{rotation_degrees[0]:.2f}"
        if 'Y' in selected_axes:
            y_value = f"{rotation_degrees[1]:.2f}"
        if 'Z' in selected_axes:
            z_value = f"{rotation_degrees[2]:.2f}"
            
    elif transform_property == 'scale':
        if 'X' in selected_axes:
            x_value = f"{obj.scale.x:.2f}"
        if 'Y' in selected_axes:
            y_value = f"{obj.scale.y:.2f}"
        if 'Z' in selected_axes:
            z_value = f"{obj.scale.z:.2f}"

    return f"{x_value}, {y_value}, {z_value}"



bpy.app.handlers.frame_change_post.append(on_frame_change_post)
bpy.app.timers.register(timer_func, persistent=True)

