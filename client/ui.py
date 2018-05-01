import curses
import sys

WIDTH = 78
CHAT_HEIGHT = 24
INPUT_HEIGHT = 1
USERNAME_DISPLAY_MAX = 8

global mainwin
global chatwin
global inputwin

messages = [''] * CHAT_HEIGHT
num_messages = 0

BACKSPACE = 8


def ui_init():
    global mainwin
    global chatwin
    global inputwin
    global messages
    global num_messages
    # Create the main window
    mainwin = curses.initscr()
    if mainwin == None:
        print("Failed to initialize screen")
        exit()

    # Don't display characters when they're pressed
    curses.noecho()

    # Create the chat window
    chatwin = mainwin.subwin(CHAT_HEIGHT + 2, WIDTH + 2, 0, 0)
    chatwin.box(0, 0)

    # Create the input window
    inputwin = mainwin.subwin(INPUT_HEIGHT + 2, WIDTH + 2, CHAT_HEIGHT + 2, 0)
    inputwin.box(0, 0)

    # Refresh the dysplay
    mainwin.refresh()

def ui_clear_chat():
    global mainwin
    global chatwin
    global inputwin
    global messages
    global num_messages
    for i in range(WIDTH):
        for j in range(CHAT_HEIGHT):
            chatwin.addch(1 + j, 1 + i, ' ')

def ui_add_message(username, message):
    global mainwin
    global chatwin
    global inputwin
    global messages
    global num_messages

    ui_clear_chat()

    if num_messages == CHAT_HEIGHT:
        messages.pop(num_messages)
    else:
        num_messages += 1

    offset = 0

    if username == None:
        post_username = '  '
        offset = 2
    elif len(username) > USERNAME_DISPLAY_MAX:
        post_username = username[0:USERNAME_DISPLAY_MAX - 3] + '...: '
        offset = USERNAME_DISPLAY_MAX
    else:
        post_username = username + ': '
        offset = len(username) + len(': ')

    if (len(message) > WIDTH - offset):
        messages.insert(0, post_username + message[0:WIDTH - offset])
        ui_add_message(None, message[WIDTH - offset])
    else: 
        messages.insert(0, post_username + message)

        for i in range(num_messages):
            chatwin.addstr(CHAT_HEIGHT - i, 1, messages[i])

    chatwin.refresh()
    inputwin.refresh()
    
def ui_clear_input():
    global mainwin
    global chatwin
    global inputwin
    global messages
    global num_messages
    
    for i in range(WIDTH):
        inputwin.addch(1, 1+i, ' ')

def ui_read_input():
    global mainwin
    global chatwin
    global inputwin
    global messages
    global num_messages
    
    length = 0
    buffer = ['' for string in range(WIDTH)]

    while True:
        key = chr(inputwin.getch())
        if key == '\n':
            break
        if key in ['\x7f', 127, curses.KEY_DC]:
            if (length > 0):
                length -= 1
                buffer[length] = ''
        elif (length < WIDTH):
            buffer[length] = key
            length += 1

        ui_clear_input()
        inputwin.addstr(1, 1, ''.join(buffer))
        inputwin.refresh()
        
    ui_clear_input()
    inputwin.refresh()
    return ''.join(buffer)


def ui_shutdown():
    curses.endwin()
