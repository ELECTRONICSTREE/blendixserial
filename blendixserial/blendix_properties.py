import bpy
from bpy.types import PropertyGroup
from bpy.props import EnumProperty, BoolProperty, StringProperty, PointerProperty, CollectionProperty, FloatProperty
from .blendix_connection import SerialConnection, serial_thread


class SerialConnectionProperties(PropertyGroup):
    port_name: EnumProperty(
        name="Port Name",
        description="Select a serial port",
        items=lambda self, context: [(port, port, "") for port in SerialConnection.list_ports()]
    ) # type: ignore

    baud_rate: EnumProperty(
        name="Baud Rate",
        description="Select baud rate for serial communication",
        items=[
            ("9600", "9600 bps", ""),
            ("14400", "14400 bps", ""),
            ("19200", "19200 bps", ""),
            ("38400", "38400 bps", ""),
            ("57600", "57600 bps", ""),
            ("115200", "115200 bps", "")
        ]
    ) # type: ignore

    is_connected: BoolProperty(
        name="Connected",
        default=False,
        description="Indicates if the serial connection is established"
    ) # type: ignore

    connection_status: StringProperty(
        name="Connection Status",
        default="Disconnected",
        description="Shows the current connection status"
    ) # type: ignore



class DynamicObjectProperties(PropertyGroup):
    sel_object: PointerProperty(
        name="Object",
        type=bpy.types.Object
    ) # type: ignore

    property_name: EnumProperty(
    name="Property",
    items=[
        ("location", "Location", ""),
        ("rotation_euler", "Rotation", ""),
        ("scale", "Scale", ""),
    ],
    default="location"
    ) # type: ignore

    selected_axes: EnumProperty(
            name="Selected Axes",
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
    )  # type: ignore


    
    text_object_axis: PointerProperty(
    name="Text Object for Axis",
    type=bpy.types.Object,
    poll=lambda self, obj: obj.type == 'FONT'  
    ) # type: ignore

    show_x: BoolProperty(default=False) # type: ignore
    show_y: BoolProperty(default=False) # type: ignore
    show_z: BoolProperty(default=False) # type: ignore



class MyUIPanelTabs(bpy.types.PropertyGroup):
    tabs: bpy.props.EnumProperty(
        name="Tabs",
        items=[
            ('TAB1', "Receive", "Receive Data"),
            ('TAB2', "Send", "Send Data"),
        ],
        default='TAB1',
    ) # type: ignore



class DynamicSendObjectProperties(PropertyGroup):
    sel_object: PointerProperty(
        name="Object",
        type=bpy.types.Object
    ) # type: ignore

    property_name: EnumProperty(
        name="Property",
        items=[
            ("location", "Location", ""),
            ("rotation_euler", "Rotation", ""),
            ("scale", "Scale", ""),
        ],
        default="location"
    ) # type: ignore

    selected_axes: EnumProperty(
        name="Selected Axes",
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
    ) # type: ignore



bpy.types.Scene.received_text = bpy.props.PointerProperty(
    name="Font", 
    type=bpy.types.Object,
    poll=lambda self, obj: obj.type == 'FONT' 
    )


def update_mode(self, context):
    serial_thread.set_mode(self.serial_thread_modes)

bpy.types.Scene.serial_thread_modes = bpy.props.EnumProperty(
    name="Serial Thread Mode",
    description="Choose the mode for the serial thread",
    items=[
        ('send', "Send", "Only send data"),
        ('receive', "Receive", "Only receive data"),
        ('both', "Both", "Send and receive data"),
    ],
    default='send',
    update=update_mode, 
)


bpy.types.Scene.serial_debug_mode = bpy.props.BoolProperty(
    name="Connection Statements",
    description="Toggle debug mode for serial connection",
    default=False
)


bpy.types.Scene.debug_mode = bpy.props.BoolProperty(
    name="Mode Selection",
    description="Toggle debug mode for Mode Selection",
    default=False
)



bpy.types.Scene.rawData_debug_mode = bpy.props.BoolProperty(
    name="Show Received Data",
    description="Toggle debug mode for showing received data",
    default=False
)

bpy.types.Scene.dataValidation_debug_mode = bpy.props.BoolProperty(
    name="Data Validation Checks",
    description="Toggle debug mode for data validation checks",
    default=False
)


bpy.types.Scene.serialThread_debug_mode = bpy.props.BoolProperty(
    name="Serial Thread Checks",
    description="Toggle debug mode for serial thread data handling",
    default=False
)

bpy.types.Scene.data_processing_received_debug_mode = bpy.props.BoolProperty(
    name="Data Process Checks - Received",
    description="Toggle debug mode for monitoring data processing during transmission",
    default=False
)

bpy.types.Scene.data_processing_send_debug_mode = bpy.props.BoolProperty(
    name="Data Process Checks - Send",
    description="Toggle debug mode for monitoring data processing during transmission and reception",
    default=False
)


bpy.types.Scene.updateSceneDelay = FloatProperty(
        name="Update Scene",
        default=1,
        min=0.001,
        max=2,
        description="Delay between scene anination updates",
        step=0.001
    ) # type: ignore


bpy.types.Scene.frame_skip_interval = bpy.props.IntProperty(
        name="Frame Skip Interval",
        description="Number of frames to skip before sending data again (set to 0 to send data every frame)",
        default=1,  
        min=0  
    )

bpy.types.Scene.axis_text_newline = bpy.props.BoolProperty(
    name="Display Axis on New Lines",
    description="Display each axis value on a new line instead of a single line",
    default=False
)

bpy.types.Scene.send_data_method = bpy.props.EnumProperty(
        name="Send Method",
        description="Choose how to send data: on frame change or using timer",
        items=[
            ('KEYFRAME', "Keyframe Based", "Send data using frame change events"),
            ('TIMER', "Timer Based", "Send data using a timer function")
        ],
        default='KEYFRAME'
    )

def register():
    bpy.types.Scene.serial_connection_properties = bpy.props.PointerProperty(type=SerialConnectionProperties)
    bpy.types.Scene.custom_object_collection = CollectionProperty(type=DynamicObjectProperties)
    bpy.types.Scene.received_text
    bpy.types.Scene.my_ui_tabs = bpy.props.PointerProperty(type=MyUIPanelTabs)
    bpy.types.Scene.send_object_collection = CollectionProperty(type=DynamicSendObjectProperties)
    bpy.types.Scene.serial_thread_modes
    bpy.types.Scene.frame_skip_interval
 

def unregister():
    del bpy.types.Scene.received_text
    del bpy.types.Scene.serial_thread_modes