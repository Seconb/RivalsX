# RivalsX

A Marvel Rivals Colorbot with multiple input options

**WARNING: DO NOT LAUNCH OTHER GAMES WITH THIS SOFTWARE OPEN**
**DO NOT ASK FOR HELP/DM ME ON DISCORD I WILL BLOCK YOU.**
**DO NOT EXPECT FREQUENT UPDATES**

## Setup Tutorial
0. Choose between Arduino, Driver, and Logitech for input. The best is Logitech for most users. If you own an Arduino Leonardo pick that. If neither of the others work pick the driver.
1. (ARDUINO USERS ONLY) **My Arduino broke so this might not work until Saturday.** Go to "Arduino Setup" and run the correct bat file according to if your COM port is visible or not. You can check by opening Device Manager and seeing if you have a "USB Serial Device" under Ports. If you do, then run the COM enabled .bat. If not, run the no COM one. Here's a video demonstration for the Arduino setup part: [![Video Tutorial](https://img.youtube.com/vi/1aRrjKzYCG0/0.jpg)](https://www.youtube.com/watch?v=1aRrjKzYCG0)
1. (DRIVER USERS) *WITH THE GAME CLOSED* Go to the "driver" folder, and drag "drag into map.sys" into "map.exe". If it says success you can close that out. 
If it fails or something make sure you disable Secure Boot and Core Isolation on your PC. Only needs to be done once.
1. (LOGITECH USERS) **BEST, NO LOGITECH MOUSE NEEDED** Download: [GHUB](https://download01.logi.com/web/ftp/pub/techsupport/gaming/lghub_installer_2021.3.5164.exe), then after installing uncheck "Automatic Updates"
2. Download Python (any version newer than 3.6 will work), in the installer make sure you check "Add Python.EXE to PATH" in the installer or it won't work.
3. Change your stuff in config.ini, and if using arduino then change MOUSE_TYPE to arduino, if using the driver keep it on driver, if using logitech keep it on logitech or ghub.
4. Open "install_libraries.bat", then when that's done open RunColorbot.bat as admin.
5. Change your ingame enemy outline color to Pinkish-Purple, Green, or Blue-Green, and set your brightness ingame to 100. You can change your monitor's brightness (OUTSIDE OF GAME) if it's too much.
6. Disable Mouse Acceleration from the game files (Google how to do this). It will help tremendously.
7. As you use the colorbot adjust settings so that things work. Edit config.ini to change config, save the file and the colorbot will auto-update it. 
It might aim at random things or bug out after killing someone (can't do anything about it, sorry). Maybe try the other outline color options. Remember to keep the game in Borderless Fullscreen.

Other issues: Ask ChatGPT or Aimmy members. If you DM me, I WILL be blocking you.

## Troubleshooting
- Go to the model-request channel in the Aimmy Discord and find the "marvel rivals pls" thread for help (or just ask in General), That's where most people are talking about this lol. You can also ask in Github Issues.
- Will add more in the future, sit tight.

