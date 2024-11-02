#!/usr/bin/env python3

import os
import pickle
import nmap
import requests
import logging
import ipaddress
import time

def load_config(filename):
    config = {}
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if line and '=' in line:
                key, value = line.split('=', 1)
                config[key] = value
    return config

# Load configuration
config = load_config('./loop-network-scanner.conf')

# Settings
DATABASE_FILE = config['DATABASE_FILE']
TELEGRAM_TOKEN = config['TELEGRAM_TOKEN']
CHAT_ID = config['CHAT_ID']
IP_RANGES = config['IP_RANGES'].split(',')
LOG_FILE = config['LOG_FILE']
SEND_TELEGRAM_MESSAGES = config.get('SEND_TELEGRAM_MESSAGES', 'False') == 'True'
SCAN_INTERVAL_IN_SECONDS = int(config.get('SCAN_INTERVAL_IN_SECONDS', 60))  

# Set up logging 
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(message)s')

# send messages to Telegram
def send_telegram_message(message):
    if SEND_TELEGRAM_MESSAGES:
        url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
        data = {
            'chat_id': CHAT_ID,
            'text': message,
            'parse_mode': 'Markdown'
        }
        requests.post(url, data=data)

# scan the network using nmap
def scan_network(ip_ranges):
    nm = nmap.PortScanner()
    devices = {}

    for ip_range in ip_ranges:
        nm.scan(ip_range, arguments='-sn -PR')

        for host in nm.all_hosts():
            mac = nm[host]['addresses'].get('mac', 'N/A')
            vendor = nm[host]['vendor'].get(mac, 'N/A') if mac != 'N/A' else 'N/A'
            devices[host] = (mac, vendor)

    return devices

# load the device database
def load_devices():
    if os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, 'rb') as f:
            return pickle.load(f)
    return {}

# save the device database
def save_devices(devices):
    with open(DATABASE_FILE, 'wb') as f:
        pickle.dump(devices, f)

# update the device database with new devices
def update_device_database(old_devices, new_devices):
    new_entries = []
    for ip, (mac, vendor) in new_devices.items():
        if ip not in old_devices:
            new_entries.append((ip, mac, vendor))
            old_devices[ip] = (mac, vendor)
    return new_entries

def main():
    devices = load_devices()  # Load existing database

    while True:
        new_devices = scan_network(IP_RANGES)
        new_entries = update_device_database(devices, new_devices)

        if new_entries:
            new_entries.sort(key=lambda x: ipaddress.ip_address(x[0]))

            timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

            message = f"New devices found:\n\n"

            for ip, mac, vendor in new_entries:
                if mac == 'N/A':
                    message += f'{ip}\n{mac}\n\n'
                else:
                    message += f'{ip}\n{mac}\n{vendor}\n\n'

            message = message.strip()

            log_message = f"\n=== {timestamp} ===\n\n"
            log_message += message
            print(log_message)  # Print message to stdout
            logging.info(log_message)  # Log the message to the file

            send_telegram_message(message)  # Send message to Telegram if enabled

            save_devices(devices)  # Save updated database

        time.sleep(SCAN_INTERVAL_IN_SECONDS)  # Wait for the specified interval


if __name__ == "__main__":
    main()

