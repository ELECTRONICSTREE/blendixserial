

# Blendix Serial Control Add-on 

### `Introduction`
The Blendix Serial Control add-on allows you to control 3D objects in Blender using a simple UART (Serial Communication) interface. It enables you to connect to a serial port, receive data from the port, and use that data to control the position and rotation of objects in your Blender scene.

![Logo](https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhSUW9Ai7WR77-c9xw5EFMk6fbZSXovFGtUENYmoKXBSXaE_zXVpHHVfa6fxJEjW7krj1NFAwudCSyluPqveJJ-IXkUSWE9mO_kAe-NWwqyoQBBqkBzdsOAMuCSTHNW9Lm2fAYaK1NfTlTWH-60x-ESiEeunZbqL65uq1JtJT9KRFLQlkR9t4uzr0qH/s1600/image.png)

### `Installation`
1. Download the "blendixserial" folder that contains the add-on files.
2. Launch Blender and go to Edit -> Preferences.
3. In the Preferences window, click on the "Add-ons" tab.
4. Click the "Install..." button at the top right of the window.
5. Browse and select the "blendixserial" folder you downloaded.
6. Enable the "Blendix Serial Control" add-on by ticking the checkbox next to it.

### `Connecting to the Serial Port`
1. Open Blender and go to the "View3D" workspace.
2. In the "Tools" panel, navigate to the "Blendix Serial" tab.
3. Choose the desired baud rate and serial port you want to connect.
4. Click the "Connect Serial" button to establish a connection to the serial port.
6. Once connected, you will see the status message indicating the successful connection.

### `Controlling Object Movement`
1. In the "Blendix Serial" panel, you will find various options for controlling object movement.
2. To start or stop the movement of objects, use the "Start Movement" and "Stop Movement" buttons, respectively.
3. Specify the update delay for the scene by adjusting the "Update Scene Delay" slider. This determines the time interval between scene updates.
4. Configure the movement properties for each object individually.
5. For each object, select the object from the dropdown menu, choose the property to control (e.g., rotation or translation), and specify the axes to move the object along.
6. You can also choose to display the object's coordinates by selecting the corresponding checkboxes.
7. Optionally, you can assign a text object to display the received data. Select the text object from the dropdown menu.
8. Use the "Reset Transforms" button to reset the transformations of the selected object.

### `Updating the Scene`
1. Once you have configured the object movement options, the scene will update automatically based on the received data from the serial port.
2. The movement and rotation of the objects will be adjusted according to the data received.
3. The assigned text objects will display the coordinates of the objects or any other data received from the serial port.

### `Disconnecting from the Serial Port`
1. To disconnect from the serial port, click the "Disconnect Serial" button in the "Blendix Serial" panel.
2. The connection will be closed, and you will see a message confirming the disconnection.

### `Additional Resources`
For more information and examples, you can visit the [Blendix Serial Control documentation](https://electronicstree.com/blendixserial-addon/).

### `License`
The Blendix Serial Control add-on is distributed under the GNU General Public License. Please refer to the license text for more details.

Note: This guide provides a basic overview of the Blendix Serial Control add-on. For more detailed instructions and troubleshooting, refer to the documentation or the add-on's source code.

Remember to comply with the license terms and ensure you have the necessary permissions to use the add-on.
