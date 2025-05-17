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
    "name": "blendixserial",
    "author": "Usman",
    "description": "3D Object control via Simple UART (Serial Communication)",
    "blender": (4, 2, 0),
    "version": (1, 2, 0),
    "location": "View3D > Properties > blendixserial",
    "category": "3D View",
}

# 17/5/2025 - M.Usman - electronicstree.com
#------------------------------------------
# Cross-platform serial port detection | Automatic PySerial installation | Text data receiving issue fix in receiving mode



import bpy
import os
import sys
import platform
import subprocess


# Operator: Uninstall addon (without quitting Blender)

class WM_OT_UninstallAddon(bpy.types.Operator):
    bl_idname = "wm.uninstall_addon"
    bl_label = "Uninstall Addon"

    def execute(self, context):
        try:
            #  Adjust repo_index and pkg_id as needed.
            bpy.ops.extensions.package_uninstall(repo_index=1, pkg_id="blendixserial")
        except Exception as e:
            print("Error uninstalling addon:", e)
        self.report({'INFO'}, "Addon uninstalled. Please restart Blender.")
        return {'FINISHED'}


# Fallback Popup: Blender native (non‑modal on other platforms)

def show_install_error_popup_native():
    def draw_ok_popup(self, context):
        self.layout.label(text="Failed to install pyserial.")
        self.layout.label(text="Please run Blender as Administrator")
        self.layout.label(text="and try again.")
        row = self.layout.row()
        row.operator("wm.uninstall_addon", text="OK", icon="CHECKMARK")
    
    bpy.context.window_manager.popup_menu(
        draw_ok_popup,
        title="pyserial Installation Error",
        icon='ERROR'
    )

# OS‑Level MessageBox for Windows (truly modal, always on top)

def show_install_error_popup_windows():
    try:
        import ctypes
        # MB_OK = 0x00000000, MB_ICONERROR = 0x00000010, MB_SYSTEMMODAL = 0x00001000
        flags = 0x00000000 | 0x00000010 | 0x00001000
        msg = ("Failed to install pyserial.\n"
               "Please run Blender as Administrator and try again.\n"
               "Click OK to uninstall the addon.")
        result = ctypes.windll.user32.MessageBoxW(0, msg, "pyserial Installation Error", flags)
        # If user clicks OK (result == 1), call the uninstall operator.
        if result == 1:
            bpy.ops.wm.uninstall_addon('INVOKE_DEFAULT')
    except Exception as e:
        print("Error displaying Windows MessageBox:", e)
        # Fallback to native popup if something goes wrong
        show_install_error_popup_native()

# Dependency Functions
def get_module_target():
    paths = bpy.utils.script_paths()
    if paths:
        target = os.path.join(paths[0], "modules")
        if os.path.isdir(target):
            print("Using Blender modules folder:", target)
            return target
    if platform.system() == "Windows":
        target = os.path.join(sys.prefix, "Lib", "site-packages")
    else:
        python_version = "python{}.{}".format(sys.version_info.major, sys.version_info.minor)
        target = os.path.join(sys.prefix, "lib", python_version, "site-packages")
    print("Fallback target folder:", target)
    return target

def ensure_pyserial_installed():
    try:
        import serial
        print("pyserial is already installed.")
    except ImportError:
        target = get_module_target()
        print("pyserial not found. Installing into:", target)
        try:
            subprocess.check_call([sys.executable, "-m", "ensurepip"])
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "--upgrade", "pyserial", "--target", target]
            )
            if target not in sys.path:
                sys.path.insert(0, target)
            import serial  # Try importing again after installation
            print("pyserial installed successfully and imported.")
        except Exception as e:
            print("Error installing pyserial:", e)
            # Use Windows system modal popup if on Windows, otherwise use native popup.
            if platform.system() == "Windows":
                bpy.app.timers.register(lambda: (show_install_error_popup_windows(), None)[1], first_interval=0.1)
            else:
                bpy.app.timers.register(lambda: (show_install_error_popup_native(), None)[1], first_interval=0.1)


def register_custom_operators():
    bpy.utils.register_class(WM_OT_UninstallAddon)

def unregister_custom_operators():
    bpy.utils.unregister_class(WM_OT_UninstallAddon)


register_custom_operators()
ensure_pyserial_installed()

from . import auto_load


auto_load.init()


def register():
    auto_load.register()



def unregister():
    auto_load.unregister()
