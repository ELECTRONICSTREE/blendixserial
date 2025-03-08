import time
import serial
import serial.tools.list_ports
import threading
import queue
import bpy


class SerialConnection:

    def __init__(self, port_name='', baud_rate=9600):
        self._serial_connection = None
        self._port_name = port_name
        self._baud_rate = baud_rate

    def connect_serial(self):
        try:
            if self._serial_connection is not None:
                self._serial_connection.close()

            self._serial_connection = serial.Serial(self._port_name, self._baud_rate)
            if bpy.context.scene.serial_debug_mode:
                print(f"Serial Connection Debug:--> Connected to {self._port_name} at {self._baud_rate} baud rate")
        except serial.SerialException as error:
            if bpy.context.scene.serial_debug_mode:
                print(f"Serial Connection Debug:--> Failed to connect to serial port {self._port_name}: {error}")
            self._serial_connection = None

    def disconnect(self, serial_thread):
        if serial_thread:
            serial_thread.stop_serial_thread()  
        
        if self._serial_connection is not None and self._serial_connection.is_open:
            try:
                self._serial_connection.flush()
                self._serial_connection.close()
                self._serial_connection = None
                if bpy.context.scene.serial_debug_mode:
                    print(f"Serial Connection Debug:--> Disconnected from {self._port_name}")
            except serial.SerialException as error:
                if bpy.context.scene.serial_debug_mode:
                    print(f"Serial Connection Debug:--> Error while disconnecting from serial port {self._port_name}: {error}")
            except OSError as os_error:
                if bpy.context.scene.serial_debug_mode:
                    print(f"Serial Connection Debug:--> OSError while disconnecting: {os_error}")


    @staticmethod
    def list_ports():
        return [port.device for port in serial.tools.list_ports.comports()]




class SerialThread:

    def __init__(self, serial_connection):
        self.serial_connection = serial_connection
        self.data_queue = queue.Queue()
        self.pause_movement = True
        self.running = False  
        self.send_queue = queue.Queue() 
        self.mode = None  

    def set_mode(self, mode):
        if mode in ["send", "receive", "both"]:
            if self.mode != mode:  
                self.mode = mode
                if bpy.context.scene.debug_mode:
                    print(f"Serial Thread Debug:--> Mode set to: {self.mode}")
        else:
            raise ValueError("Invalid mode. Choose 'send', 'receive', or 'both'.")




    def serial_thread(self):
        self.running = True  
        while self.running:
            try:
                current_mode = self.mode  

                if self.serial_connection._serial_connection is not None and self.serial_connection._serial_connection.is_open:
                    
                    if current_mode in ['receive', 'both']:
                        if self.serial_connection._serial_connection.in_waiting:
                            data = self.serial_connection._serial_connection.readline().decode().rstrip()

                            if bpy.context.scene.rawData_debug_mode:
                                print(f"Serial Thread Debug:--> Initial data received: {data}")

                            if not data:
                                continue  

                            if self.is_valid_data(data): 
                                if bpy.context.scene.serialThread_debug_mode:
                                    print(f"Serial Thread Debug:--> Valid data {data}")
                                self.data_queue.put(self.parse_serial_data(data))
                    
                    if current_mode in ['send', 'both']:
                        try:
                            if not self.send_queue.empty():  
                                data_to_send = self.send_queue.get_nowait()  
                                if self.is_valid_send_data(data_to_send):  
                                    self.send_serial_data(data_to_send)
                            else:
                                
                                time.sleep(0.01)  

                        except queue.Empty:
                            pass  

                else:
                    break  

            except serial.SerialException as error:
                if bpy.context.scene.serialThread_debug_mode:
                    print(f"Serial Thread Debug:-->  Serial error: {error}")
                break



    def start_serial_thread(self):
        thread = threading.Thread(target=self.serial_thread)
        thread.daemon = True  
        thread.start()

    def stop_serial_thread(self):
        self.running = False

    def get_data_from_queue(self):
        try:
            return self.data_queue.get_nowait()
        except queue.Empty:
            return None
        


    def is_valid_data(self, serial_data):
        if not serial_data:
            if bpy.context.scene.dataValidation_debug_mode:
                print("Data Validation Debug:--> Empty data string")
            return False  

        parts = serial_data.split(';')
        if bpy.context.scene.dataValidation_debug_mode:
            print(f"Data Validation Debug:--> Data split into parts: {parts}")  

        if len(parts[0].strip()) > 0:
            numerical_part = parts[0].strip()
            if bpy.context.scene.dataValidation_debug_mode:
                print(f"Data Validation Debug:--> Numerical part: {numerical_part}") 
            
            try:
                numerical_values = list(map(float, numerical_part.split(',')))
                if bpy.context.scene.dataValidation_debug_mode:
                    print(f"Data Validation Debug:--> Valid Parsed numerical values: {numerical_values}")
            except ValueError as e:
                if bpy.context.scene.dataValidation_debug_mode:
                    print(f"Data Validation Debug:--> Numerical data invalid - {numerical_part}, Error: {e}")
                return False

        if len(parts) > 1:
            text_part = parts[1].strip()
            if bpy.context.scene.dataValidation_debug_mode:
                print(f"Data Validation Debug:--> Text part: {text_part}")  
            if text_part:
                return True  
        return True




    def parse_serial_data(self, serial_data):
        if not serial_data:
            return [], ""

        numerical_values = []
        text_data = ""

        if ';' in serial_data:
            parts = serial_data.split(';', 1)
            numerical_part = parts[0].strip()
            
            if numerical_part:
                try:
                    numerical_values = list(map(float, numerical_part.split(',')))  
                except ValueError as e:
                    if bpy.context.scene.serialThread_debug_mode:
                        print(f"Error parsing numerical data: {numerical_part}, Error: {e}")

            if len(parts) > 1:
                text_data = parts[1].strip()

        elif serial_data.startswith(';'):
            text_data = serial_data[1:].strip()  

        return numerical_values, text_data


    def is_valid_send_data(self, send_data):
        if not send_data.endswith(';'):
            return False  
        
        try:
            numerical_data = send_data[:-1].split(',')

            for value in numerical_data:
                if '.' in value:
                    float_value = float(value)
                    if len(value.split('.')[-1]) > 2:  
                        return False
                else:
                    int(value)  

            return True
        except (ValueError, IndexError):
            return False


    def send_serial_data(self, send_data):
        try:
            if self.serial_connection._serial_connection is not None and self.serial_connection._serial_connection.is_open:

                self.serial_connection._serial_connection.write(f"{send_data}\n".encode())
                if bpy.context.scene.serialThread_debug_mode:
                    print(f"Sent: {send_data}")
            else:
                if bpy.context.scene.serialThread_debug_mode:
                    print("Serial connection is not open.")
        except serial.SerialException as error:
            if bpy.context.scene.serialThread_debug_mode:
                print(f"Failed to send data: {error}")


    def queue_send_data(self, data):
        """Queue data to be sent in the thread."""
        self.send_queue.put(data)



serial_connection = SerialConnection()
serial_thread = SerialThread(serial_connection)
