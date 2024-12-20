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
import threading
import queue

def getMouse():
    try:
        if "arduino" in config.get("Config", "MOUSE_TYPE").lower():
            from utils.arduino_mouse import MouseInstruct
            return MouseInstruct.getMouse()
        elif "driver" in config.get("Config", "MOUSE_TYPE").lower():
            from utils.driver_mouse import mainFunction
            return mainFunction()
        elif "ghub" in config.get("Config", "MOUSE_TYPE").lower() or "logitech" in config.get("Config", "MOUSE_TYPE").lower():
            mouse_open()
            return None
    except Exception as e:
        input(e)
        os.exit()

def loadsettings():

    global config, TOGGLE_HOLD_MODE, SMOOTH_FIX, AIM_KEY, CAM_FOV, AIM_OFFSET_Y, AIM_OFFSET_X, AIM_SPEED_X, AIM_SPEED_Y, upper, lower, AIM_FOV, SHOW_FOV, AIM_FOV_COLOR, TRIGGERBOT_DISTANCE, TRIGGERBOT_KEY, TRIGGERBOT, COLOR

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
    TOGGLE_HOLD_MODE = config.get("Config", "TOGGLE_HOLD_MODE").lower()
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

def activate_key_pressed():
    return win32api.GetAsyncKeyState(get_keycode(AIM_KEY)) < 0 or win32api.GetAsyncKeyState(get_keycode(TRIGGERBOT_KEY))

def aim_key_pressed():
    return win32api.GetAsyncKeyState(get_keycode(AIM_KEY)) < 0

def trig_key_pressed():
    return win32api.GetAsyncKeyState(get_keycode(TRIGGERBOT_KEY)) < 0

class trbot:
    def __init__(self):
        self.aimtoggled = False
        self.trigtoggled = False

    def handle_aim_toggle(self):
        while True:
            if activate_key_pressed():
                if "toggle" in TOGGLE_HOLD_MODE:
                    if activate_key_pressed():
                        time.sleep(0.05)
                        if aim_key_pressed():
                            self.aimtoggled = not self.aimtoggled
                        if trig_key_pressed():
                            self.trigtoggled = not self.trigtoggled
                else:
                    while activate_key_pressed():
                        self.aimtoggled = aim_key_pressed()
                        self.trigtoggled = trig_key_pressed()
            else:
                if not "hold" in TOGGLE_HOLD_MODE and not "toggle" in TOGGLE_HOLD_MODE:
                    os.system("cls")
                    print("[-] Your TOGGLE_HOLD_MODE in config needs to be either toggle or hold.")
                    input();os.exit()
                if "hold" in TOGGLE_HOLD_MODE:
                    self.aimtoggled = False
                    self.trigtoggled = False
                time.sleep(0.01)
            

    def process(self):
        while True:
            if self.aimtoggled or self.trigtoggled:
                img = camera.grab()
                if img is not None:
                    contours = self.get_contours(img)
                    if len(contours) != 0:
                        self.handle_contours(contours)
            else:
                time.sleep(0.1)

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
                if x2 != 0 and y2 != 0 and self.aimtoggled < 0 and -10 < y2 < 10 and distance > SMOOTH_FIX:
                    m.move(int(x2), int(y2))
                if x2 < TRIGGERBOT_DISTANCE and y2 < TRIGGERBOT_DISTANCE and self.trigtoggled:
                    m.press()
                    m.release()
            else:
                if x2 != 1 and y2 != 1 and self.aimtoggled and -10 < y2 < 10 and distance > SMOOTH_FIX:
                    mouse_move(0, int(x2), int(y2), 0)
                if distance < TRIGGERBOT_DISTANCE and self.trigtoggled:
                    mouse_move(1, 0, 0, 0)
                    time.sleep(0.001)
                    mouse_move(0, 0, 0, 0)


def print_banner(bot: trbot):
    last_values = {
        "aimbot_activated": bot.aimtoggled,
        "triggerbot_activated": bot.trigtoggled,
        "aim_key": AIM_KEY,
        "triggerbot_key": TRIGGERBOT_KEY,
        "aim_fov": AIM_FOV,
        "cam_fov": CAM_FOV,
        "aim_speed_x": AIM_SPEED_X,
        "aim_speed_y": AIM_SPEED_Y,
        "aim_offset_x": AIM_OFFSET_X,
        "aim_offset_y": AIM_OFFSET_Y,
        "enemy_color": COLOR,
        "toggle_hold_mode": TOGGLE_HOLD_MODE
    }
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
        ("Toggle Hold Mode", TOGGLE_HOLD_MODE),
        ("Aim Activated", f"{Fore.GREEN if bot.aimtoggled else Fore.RED}{bot.aimtoggled}"),
        ("Trigger Activated", f"{Fore.GREEN if bot.trigtoggled else Fore.RED}{bot.trigtoggled}")
    ]
    
    print("====== Controls ======")
    for label, value in info[:2]:
        print(f"{label:<20}: {Fore.YELLOW}{value}{Style.RESET_ALL}")
    
    print("==== Information =====")
    for label, value in info[2:]:
        print(f"{label:<20}: {Fore.CYAN}{value}{Style.RESET_ALL}")
    
    while True:
        if (last_values["aimbot_activated"] != bot.aimtoggled or
            last_values["triggerbot_activated"] != bot.trigtoggled or 
            last_values["aim_key"] != AIM_KEY or
            last_values["triggerbot_key"] != TRIGGERBOT_KEY or
            last_values["aim_fov"] != AIM_FOV or
            last_values["cam_fov"] != CAM_FOV or
            last_values["aim_speed_x"] != AIM_SPEED_X or
            last_values["aim_speed_y"] != AIM_SPEED_Y or
            last_values["aim_offset_x"] != AIM_OFFSET_X or
            last_values["aim_offset_y"] != AIM_OFFSET_Y or
            last_values["enemy_color"] != COLOR or
            last_values["toggle_hold_mode"] != TOGGLE_HOLD_MODE):

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
                ("Toggle Hold Mode", TOGGLE_HOLD_MODE),
                ("Aim Activated", f"{Fore.GREEN if bot.aimtoggled else Fore.RED}{bot.aimtoggled}"),
                ("Trigger Activated", f"{Fore.GREEN if bot.trigtoggled else Fore.RED}{bot.trigtoggled}")
            ]
            
            print("====== Controls ======")
            for label, value in info[:2]:
                print(f"{label:<20}: {Fore.YELLOW}{value}{Style.RESET_ALL}")
            
            print("==== Information =====")
            for label, value in info[2:]:
                print(f"{label:<20}: {Fore.CYAN}{value}{Style.RESET_ALL}")

            last_values["aimbot_activated"] = bot.aimtoggled
            last_values["triggerbot_activated"] = bot.trigtoggled
            last_values["aim_key"] = AIM_KEY
            last_values["triggerbot_key"] = TRIGGERBOT_KEY
            last_values["aim_fov"] = AIM_FOV
            last_values["cam_fov"] = CAM_FOV
            last_values["aim_speed_x"] = AIM_SPEED_X
            last_values["aim_speed_y"] = AIM_SPEED_Y
            last_values["aim_offset_x"] = AIM_OFFSET_X
            last_values["aim_offset_y"] = AIM_OFFSET_Y
            last_values["enemy_color"] = COLOR
            last_values["toggle_hold_mode"] = TOGGLE_HOLD_MODE

        time.sleep(0.1)

def create_square_outline_image(side_length, color, alpha, outline_width):
    image = Image.new('RGBA', (side_length, side_length), (0, 0, 0, 0))
    ImageDraw.Draw(image).rectangle(
        [(outline_width // 2, outline_width // 2), 
         (side_length - outline_width // 2, side_length - outline_width // 2)], 
        outline=color + (alpha,), width=outline_width)
    return image

def create_square(side_length, color, alpha):
    global overlay_window

    if overlay_window is not None:
        overlay_window.destroy()

    screen_width, screen_height = root.winfo_screenwidth(), root.winfo_screenheight()
    overlay_window = tk.Toplevel(root)
    overlay_window.overrideredirect(True)
    overlay_window.attributes("-topmost", True)
    overlay_window.attributes("-transparentcolor", "black")
    overlay_window.geometry(f"+{screen_width // 2 - side_length // 2}+{screen_height // 2 - side_length // 2}")

    square_outline_image = create_square_outline_image(side_length, color, alpha, 2)
    square_outline_photo = ImageTk.PhotoImage(square_outline_image)

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
    banner_thread = threading.Thread(target=print_banner, args=(bot,), daemon=True)
    banner_thread.start()
    processing_thread = threading.Thread(target=bot.process, daemon=True)
    processing_thread.start()
    toggle_thread = threading.Thread(target=bot.handle_aim_toggle, daemon=True)
    toggle_thread.start()
    if SHOW_FOV:
        create_square(AIM_FOV, AIM_FOV_COLOR, 255)
    m = getMouse()
    while True:
        root.update()
        time.sleep(0.02)
        while not task_queue.empty():
            task = task_queue.get_nowait()
            task() 
