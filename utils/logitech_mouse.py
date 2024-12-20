import ctypes
import win32file
import ctypes
import ctypes.wintypes as wintypes
from ctypes import windll

handle = 0
found = False
root_id = None

def _DeviceIoControl(devhandle, ioctl, inbuf, inbufsiz, outbuf, outbufsiz):
    """See: DeviceIoControl function
    http://msdn.microsoft.com/en-us/library/aa363216(v=vs.85).aspx
    """
    DeviceIoControl_Fn = windll.kernel32.DeviceIoControl
    DeviceIoControl_Fn.argtypes = [wintypes.HANDLE, wintypes.DWORD, wintypes.LPVOID,wintypes.DWORD,wintypes.LPVOID,wintypes.DWORD,ctypes.POINTER(wintypes.DWORD),wintypes.LPVOID]                   
    DeviceIoControl_Fn.restype = wintypes.BOOL

    dwBytesReturned = wintypes.DWORD(0)
    lpBytesReturned = ctypes.byref(dwBytesReturned)

    status = DeviceIoControl_Fn(int(devhandle),ioctl,inbuf,inbufsiz,outbuf,outbufsiz,lpBytesReturned,None)

    return status, dwBytesReturned


class MOUSE_IO(ctypes.Structure):
    _fields_ = [("button", ctypes.c_char),("x", ctypes.c_char),("y", ctypes.c_char),("wheel", ctypes.c_char),("unk1", ctypes.c_char),]


def device_initialize(device_name: str) -> bool:
    global handle
    try:
        handle = win32file.CreateFileW(device_name, win32file.GENERIC_WRITE, 0, None, win32file.OPEN_ALWAYS, win32file.FILE_ATTRIBUTE_NORMAL, 0)
    except:
        pass
    return bool(handle)

def find_root_id() -> bool:
    global root_id
    for i in range(1, 10):
        device_name = f'\\??\\ROOT#SYSTEM#{i:04d}#{{1abc05c0-c378-41b9-9cef-df1aba82b015}}'
        if device_initialize(device_name):
            root_id = f'{i:04d}'
            return True
    return False

def mouse_open() -> bool:
    global found
    global handle
    global root_id

    if handle:
        return found
    
    if root_id:
        device_name = f'\\??\\ROOT#SYSTEM#{root_id}#{{1abc05c0-c378-41b9-9cef-df1aba82b015}}'
        if device_initialize(device_name):
            found = True
            return found

    if find_root_id():
        found = True
        return found
    
    return found

def call_mouse(buffer) -> bool:
    global handle
    return _DeviceIoControl(handle, 0x2a2010, ctypes.c_void_p(ctypes.addressof(buffer)), ctypes.sizeof(buffer),  0, 0)[0] == 0


def mouse_close() -> None:
    global handle
    win32file.CloseHandle(int(handle))
    handle = 0

def mouse_move(button, x, y, wheel) -> None:
    global handle

    io = MOUSE_IO()
    io.x = bytes([x % 256])
    io.y = bytes([y % 256])
    io.unk1 = 0
    io.button = bytes([button % 256])
    io.wheel = bytes([wheel % 256])
    if not call_mouse(io):
        mouse_close()
        mouse_open()

if not mouse_open():
    print("[-] G Hub is not open, or there is another issue! Download LG HUB (download on the repo page) and disable automatic updates.")
