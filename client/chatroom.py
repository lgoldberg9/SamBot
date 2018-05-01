from ui import *
import sys
import numpy as np

def main():
    if len(sys.argv) != 3:
        print("Usage: %s <username> <character>", sys.argv[0])
        exit()

    # Load username and character chat name
    username = sys.argv[1]
    dat_character = sys.argv[2]

    # Initialize UI with basic text
    ui_init()
    ui_add_message(None, "Type your message and hit <ENTER> to post.");
    
    while True:
        message = ui_read_input()
        if (message == '\\quit'):
            break
        elif (len(message) > 0):
            ui_add_message(username, message)
            # send message to character as well

    ui_shutdown()
    
if __name__ == '__main__':
    main()
