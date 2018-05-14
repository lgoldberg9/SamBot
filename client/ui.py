import curses
import sys
import os

HEIGHT_t, WIDTH_t = (int(x) for x in os.popen('stty size', 'r').read().split())

WIDTH = WIDTH_t - 2
CHAT_HEIGHT = HEIGHT_t - 5
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

    # Refresh the display
    mainwin.refresh()

def ui_clear_chat():
    global chatwin
    for i in range(WIDTH):
        for j in range(CHAT_HEIGHT):
            chatwin.addch(1 + j, 1 + i, ' ')

def ui_add_message(username, message, is_bot):
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

    # Handle username cases
    if username == None:
        post_username = '  '
        offset = 2
    elif len(username) > USERNAME_DISPLAY_MAX:
        post_username = username[0:USERNAME_DISPLAY_MAX - 3] + '...: '
        offset = USERNAME_DISPLAY_MAX
    else:
        post_username = username + ': '
        offset = len(username) + len(': ')

    y, x = inputwin.getyx()
    # Handle message cases
    if (len(message) > WIDTH - offset):
        messages.insert(0, post_username + message[0:WIDTH - offset])
        ui_add_message(None, message[(WIDTH - offset):], is_bot)
    else: 
        messages.insert(0, post_username + message)
        [chatwin.addstr(CHAT_HEIGHT - i, 1, messages[i]) for i in range(num_messages)]

    chatwin.refresh()
    inputwin.refresh()
    
    # Move cursor to correct location in input box
    inputwin.move(1, 1)
    
def ui_clear_input():
    global inputwin

    inputwin.addstr(1, 1, (' ' * WIDTH))

def ui_read_input():
    global inputwin
    
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
