import serial
import serial.tools.list_ports

def find_arduino():
    ports = list(serial.tools.list_ports.comports())
    for port in ports:
        if "USB Serial Device" in port.description: # change this part to what your arduino appears as under ports in device manager
            return port.device
    return None

def mouse_cmd(x, y, click, m):
    command = f"{x},{y},{click}\n" # x, y to move relative. 1 to click and release.
    m.write(command.encode('utf-8'))
