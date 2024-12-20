import time
import os
import bettercam
import configparser
import cv2
import numpy as np
import time
import win32api
import math
from colorama import Fore, Style
from utils.keybinds import *
from utils.logitech_mouse import *
import tkinter as tk
from PIL import Image, ImageDraw, ImageTk
import ctypes
import threading
import queue

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception as e:
        print(f"Error checking admin privileges: {e}")
        return False

def run_as_admin():
    if not is_admin():
        try:
            import sys
            script = os.path.abspath(__file__)
            params = ' '.join(f'"{arg}"' for arg in sys.argv[1:])
            win32api.ShellExecute(0, "runas", sys.executable, f'"{script}" {params}', None, 1)
            sys.exit(0)
        except Exception as e:
            input(f"[-] Failed to run as admin, open UAC and set it to the lowest option! : {e}")
            sys.exit(1)
    return True

def getMouse():
    if "arduino" in config.get("Config", "MOUSE_TYPE").lower():
        try:
            from utils.arduino_mouse import MouseInstruct
            mouse = MouseInstruct.getMouse()
            return mouse
        except Exception as e:
            input(e)
            os.exit()
    elif "driver" in config.get("Config", "MOUSE_TYPE").lower():
        try:
            from utils.driver_mouse import mainFunction
            run_as_admin()
            mouse = mainFunction()
            return mouse
        except DeviceNotFoundError as e:
            input(e)
            os.exit()
    elif "ghub" or "logitech" in config.get("Config", "MOUSE_TYPE").lower():
        try:
            mouse_move(0, 1, 0, 0) # try to move the mouse 1 pixel to see if shit even works
            return None
        except Exception as e:
            input(e)
            os.exit()

def loadsettings():

    global config, SMOOTH_FIX, AIM_KEY, CAM_FOV, AIM_OFFSET_Y, AIM_OFFSET_X, AIM_SPEED_X, AIM_SPEED_Y, upper, lower, AIM_FOV, SHOW_FOV, AIM_FOV_COLOR, TRIGGERBOT_DISTANCE, TRIGGERBOT_KEY, TRIGGERBOT, COLOR

    sdir = os.path.dirname(os.path.abspath(__file__))
    config_file_path = os.path.join(sdir, "config.ini")
    config = configparser.ConfigParser()
    config.optionxform = str
    config.read(config_file_path)

    AIM_KEY = config.get("Config", "AIM_KEY")
    CAM_FOV = int(config.get("Config", "CAM_FOV"))
    AIM_FOV = int(config.get("Config", "AIM_FOV"))
    AIM_OFFSET_Y = int(config.get("Config", "AIM_OFFSET_Y"))
    AIM_OFFSET_X = int(config.get("Config", "AIM_OFFSET_X"))
    SMOOTH_FIX = int(config.get("Config", "SMOOTH_FIX"))
    AIM_SPEED_X = float(config.get("Config", "AIM_SPEED_X"))
    AIM_SPEED_Y = float(config.get("Config", "AIM_SPEED_Y"))
    SHOW_FOV = config.getboolean("Config", "SHOW_FOV")
    TRIGGERBOT = config.getboolean("Config", "TRIGGERBOT")
    TRIGGERBOT_KEY = config.get("Config", "TRIGGERBOT_KEY")
    TRIGGERBOT_DISTANCE = int(config.get("Config", "TRIGGERBOT_DISTANCE"))
    AIM_FOV_COLOR = tuple(map(int, config.get("Config", "AIM_FOV_COLOR").split(', ')))
    COLOR = config.get("Config", "COLOR")
    COLORS = {
        "bluegreen": (np.array((88, 108, 255)), np.array((76, 50, 220))),
        "pinkishpurple": (np.array((150, 120, 255)), np.array((150, 85, 230))),
        "green": (np.array((71, 131, 255)), np.array((52, 79, 238))),
    }
    upper, lower = COLORS[COLOR.lower()]

loadsettings()
usersize = [win32api.GetSystemMetrics(0), win32api.GetSystemMetrics(1)]
left, top = (usersize[0] - CAM_FOV) // 2, (usersize[1] - CAM_FOV) // 2
right, bottom = left + CAM_FOV, top + CAM_FOV
region = (left, top, right, bottom)
camera = bettercam.create(output_idx=0, output_color="BGR", region=region)
center = CAM_FOV / 2
overlay_window = None

def lclc():
    return win32api.GetAsyncKeyState(get_keycode(AIM_KEY)) < 0 or win32api.GetAsyncKeyState(get_keycode(TRIGGERBOT_KEY))

class trbot:
    def __init__(self):
        self.aimtoggled = False

    def handle_aim_toggle(self):
        while lclc():
            if not self.aimtoggled:
                self.aimtoggle()
                print_banner(self)
            while self.aimtoggled and lclc():
                self.process()
            if self.aimtoggled:
                self.aimtoggle()
                print_banner(self)

    def process(self):
        img = camera.grab()
        if img is not None:
            contours = self.get_contours(img)
            if len(contours) != 0:
                self.handle_contours(contours)

    def get_contours(self, img):
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower, upper)
        kernel = np.ones((3, 3), np.uint8)
        dilated = cv2.dilate(mask, kernel, iterations=6)
        thresh = cv2.threshold(dilated, 60, 255, cv2.THRESH_BINARY)[1]
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        return contours

    def handle_contours(self, contours):
        contour = max(contours, key=cv2.contourArea)
        topmost = tuple(contour[contour[:, :, 1].argmin()][0])
        x = topmost[0] - center + AIM_OFFSET_X
        y = topmost[1] - center + AIM_OFFSET_Y
        distance = math.sqrt(x ** 2 + y ** 2)

        if distance <= AIM_FOV:
            x2 = x * AIM_SPEED_X
            y2 = y * AIM_SPEED_Y
            if m:
                if x2 != 0 and y2 != 0 and win32api.GetAsyncKeyState(get_keycode(AIM_KEY)) < 0 and -10 < y2 < 10 and distance > SMOOTH_FIX:
                    m.move(int(x2), int(y2))
                if x2 < TRIGGERBOT_DISTANCE and y2 < TRIGGERBOT_DISTANCE and win32api.GetAsyncKeyState(get_keycode(TRIGGERBOT_KEY)) < 0:
                    m.press()
                    m.release()
            else:
                if x2 != 1 and y2 != 1 and win32api.GetAsyncKeyState(get_keycode(AIM_KEY)) < 0 and -10 < y2 < 10 and distance > SMOOTH_FIX:
                    mouse_move(0, int(x2), int(y2), 0)
                if distance < TRIGGERBOT_DISTANCE and win32api.GetAsyncKeyState(get_keycode(TRIGGERBOT_KEY)) < 0:
                    mouse_move(1, 0, 0, 0)
                    time.sleep(0.001)
                    mouse_move(0, 0, 0, 0)

    def aimtoggle(self):
        self.aimtoggled = not self.aimtoggled

def print_banner(bot: trbot):
    os.system("cls")
    print(Style.BRIGHT + Fore.CYAN + "RivalsX by Seconb" + Style.RESET_ALL)

    info = [
        ("Activate aimbot", AIM_KEY),
        ("Activate triggerbot", TRIGGERBOT_KEY),
        ("Aim FOV", AIM_FOV),
        ("Cam FOV", CAM_FOV),
        ("Aim Speed", f"X: {AIM_SPEED_X} Y: {AIM_SPEED_Y}"),
        ("Aim Offset", f"X: {AIM_OFFSET_X} Y: {AIM_OFFSET_Y}"),
        ("Enemy Color", COLOR),
        ("Activated", Fore.GREEN if bot.aimtoggled else Fore.RED + str(bot.aimtoggled))
    ]
    
    print("====== Controls ======")
    for label, value in info[:2]:
        print(f"{label:<20}: {Fore.YELLOW}{value}{Style.RESET_ALL}")
    
    print("==== Information =====")
    for label, value in info[2:]:
        print(f"{label:<20}: {Fore.CYAN}{value}{Style.RESET_ALL}")

def create_square_outline_image(side_length, color, alpha, outline_width):
    image = Image.new('RGBA', (side_length, side_length), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rectangle(
        [
            (outline_width // 2, outline_width // 2),
            (side_length - outline_width // 2, side_length - outline_width // 2),
        ],
        outline=color + (alpha,),
        width=outline_width,
    )
    return image

def create_square(side_length, color, alpha):
    global overlay_window

    if overlay_window is not None:
        overlay_window.destroy()

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    square_alpha = alpha
    square_outline_width = 2
    square_outline_image = create_square_outline_image(
        side_length, color, square_alpha, square_outline_width
    )

    square_outline_photo = ImageTk.PhotoImage(square_outline_image)

    overlay_window = tk.Toplevel(root)
    overlay_window.overrideredirect(True)
    overlay_window.attributes("-topmost", True)
    overlay_window.attributes("-transparentcolor", "black")
    overlay_window.geometry(
        f"+{screen_width // 2 - side_length // 2}+{screen_height // 2 - side_length // 2}"
    )

    square_outline_label = tk.Label(overlay_window, image=square_outline_photo, bg="black")
    square_outline_label.image = square_outline_photo
    square_outline_label.pack()

def auto_update_config():
    last_modified_time = os.path.getmtime(os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.ini"))
    
    while True:
        current_modified_time = os.path.getmtime(os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.ini"))
        current_aim_fov = AIM_FOV
        if current_modified_time != last_modified_time:
            loadsettings()
            print_banner(bot)
            if SHOW_FOV and AIM_FOV != current_aim_fov:
                task_queue.put(lambda: create_square(AIM_FOV, AIM_FOV_COLOR, 255))
            last_modified_time = current_modified_time
        time.sleep(1)


if __name__ == "__main__":
    bot = trbot()
    root = tk.Tk()
    root.withdraw()
    task_queue = queue.Queue()
    config_thread = threading.Thread(target=auto_update_config, daemon=True)
    config_thread.start()
    if SHOW_FOV:
        create_square(AIM_FOV, AIM_FOV_COLOR, 255)
    m = getMouse()
    print_banner(bot)
    while True:
        root.update()
        time.sleep(0.02)
        if lclc():
            bot.handle_aim_toggle()
        while not task_queue.empty():
            task = task_queue.get_nowait()
            task() 
