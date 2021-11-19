#!/usr/bin/python
import re
import subprocess
import display
import socket


def getDeviceList():
    command = 'aconnect -i -l'
    result = subprocess.run(command.split(' '), stdout=subprocess.PIPE)
    # create a list for each line in the command output and remove lines containing 'Through'
    devices = [i for i in result.stdout.decode('utf-8').split('\n') if 'Through' not in i]
    # find id and name for each device
    deviceDict = []
    for dev in devices:
        match = re.match("client (\d*)\: '(.*)'", dev)
        if match:
            deviceDict.append({'id': match.group(1), 'name': match.group(2)})
    return deviceDict


def getIp():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect(('8.8.8.8', 1))  # connect() for UDP doesn't send packets
    return sock.getsockname()[0]


display = display.Display()
print(getDeviceList())
display.lcd_string(f"IP:{getIp()}", 0)
for dev in getDeviceList():
    display.lcd_string(dev['id'] + ':' + dev['name'], 1)
