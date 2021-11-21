#!/usr/bin/python

import re
from datetime import timedelta
import time
import subprocess
import socket
import math

import psutil

import RPi.GPIO as GPIO

from PIL import Image, ImageDraw, ImageFont
import display
import LCD_Config

# font
fontpath = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'
font = ImageFont.truetype(fontpath, 10)

KEY_UP_PIN = 19
KEY_DOWN_PIN = 6
KEY_LEFT_PIN = 5
KEY_RIGHT_PIN = 26
KEY_PRESS_PIN = 13
KEY1_PIN = 21
KEY2_PIN = 20
KEY3_PIN = 16
LEFT = True
RIGHT = False



class usbMidiHost():
    devices = []
    currentTime = time.time()
    interval = 5

    def __init__(self):
        pass

    def getDeviceList(self):
        if time.time() - self.currentTime < self.interval and self.devices:
            return self.devices
        self.currentTime = time.time()

        print(time.time() - self.currentTime)
        command = 'aconnect -i -l'
        result = subprocess.run(command.split(' '), stdout=subprocess.PIPE)
        # create a list for each line in the command output and remove lines containing 'Through'
        devices = [i for i in result.stdout.decode('utf-8').split('\n') if 'Through' not in i]
        # find id and name for each device
        self.devices = []
        for dev in devices:
            match = re.match("client (\d*)\: '(.*)'", dev)
            if match:
                self.devices.append({'id': match.group(1), 'name': match.group(2)})
        return self.devices


class usbMidiHostUi():
    buttons = [{'points': [(127, 20), (90, 40)], 'key': KEY1_PIN, 'text': 'in'},
               {'points': [(127, 50), (90, 70)], 'key': KEY2_PIN, 'text': 'out'},
               {'points': [(127, 80), (90, 100)], 'key': KEY3_PIN, 'text': 'sys'}]
    # devices
    connectedDevices = []
    currentDeviceLeft = 0
    currentDeviceRight = 0
    currentSide = LEFT
    # info
    currentInfo = 0
    pins = [KEY_UP_PIN,
            KEY_DOWN_PIN,
            KEY_LEFT_PIN,
            KEY_RIGHT_PIN,
            KEY_PRESS_PIN,
            KEY1_PIN,
            KEY2_PIN,
            KEY3_PIN]

    def __init__(self):
        self.usbMidiHost = usbMidiHost()
        self.infos = [f"status", f"ip:{self.getIp()}", f"uptime:{self.get_uptime()}", f'cpu:{psutil.cpu_percent()}%', f'ram:{psutil.virtual_memory().percent}%', 'creator: lukn303']
        # init GPIO
        GPIO.setmode(GPIO.BCM)
        for pin in self.pins:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(pin, GPIO.FALLING,
                                  callback=self.pinHandler,
                                  bouncetime=300)

        # 240x240 display with hardware SPI:
        self.disp = display.LCD()
        Lcd_ScanDir = display.SCAN_DIR_DFT  # SCAN_DIR_DFT = D2U_L2R
        self.disp.LCD_Init(Lcd_ScanDir)
        self.disp.LCD_Clear()

        # Create blank image for drawing.
        # Make sure to create image with mode '1' for 1-bit color.
        width = 128
        height = 128
        self.image = Image.new('RGB', (width, height))

        # Get drawing object to draw on image.
        self.draw = ImageDraw.Draw(self.image)

        # Draw a black filled box to clear the image.
        self.draw.rectangle((0, 0, width, height), outline=0, fill=0)
        self.disp.LCD_ShowImage(self.image, 0, 0)

    def pinHandler(self, pin):
        if pin == KEY_DOWN_PIN:
            print("up")
            if self.currentSide == LEFT:
                self.currentDeviceLeft = self.decrease(self.currentDeviceLeft, len(self.usbMidiHost.getDeviceList()))
            else:
                self.currentDeviceRight = self.decrease(self.currentDeviceRight, len(self.usbMidiHost.getDeviceList()))
        if pin == KEY_UP_PIN:
            print("down")
            if self.currentSide == LEFT:
                self.currentDeviceLeft = self.increase(self.currentDeviceLeft, len(self.usbMidiHost.getDeviceList()))
            else:
                self.currentDeviceRight = self.increase(self.currentDeviceRight, len(self.usbMidiHost.getDeviceList()))

        if pin in [KEY_LEFT_PIN, KEY_RIGHT_PIN, KEY_PRESS_PIN]:
            self.currentSide = not self.currentSide

        # Key1: switch informations
        if pin == KEY1_PIN:
            print("Key1")
            self.currentInfo = self.currentInfo + 1 if self.currentInfo < len(self.infos) - 1 else 0
        # Key2: Connect Currently selected devices
        if pin == KEY2_PIN:
            print("Key2")
            if {'in': self.currentDeviceLeft, 'out': self.currentDeviceRight} in self.connectedDevices:
                self.statusMessage("nothing to do")
            else:
                self.connectedDevices.append({'in': self.currentDeviceLeft, 'out': self.currentDeviceRight})
                self.statusMessage(f"connected({self.currentDeviceLeft},{self.currentDeviceRight})")
        # Key3: Disconnect Currently selected devices
        if pin == KEY3_PIN:
            print("Key2")
            if {'in': self.currentDeviceLeft, 'out': self.currentDeviceRight} in self.connectedDevices:
                self.connectedDevices.remove({'in': self.currentDeviceLeft, 'out': self.currentDeviceRight})
                self.statusMessage(f"disconnected({self.currentDeviceLeft},{self.currentDeviceRight})")
            else:
                self.statusMessage("nothing to do")

    @staticmethod
    def midpoint(p1, p2):
        return (int((p1[0]+p2[0])/2), int((p1[1]+p2[1])/2))

    @staticmethod
    def getTextPos(p1, p2):
        return (p2[0] + 2, p1[1] + 2)

    def drawDevices(self):
        # left
        for i, dev in enumerate(self.usbMidiHost.getDeviceList()):
            self.draw.rectangle([(0, (i+1)*20), (40, (i+2)*20)], outline="red", fill=0)
            self.draw.text((0, (i+1)*20), dev['name'][0:6], font=font)
        # right
        for i, dev in enumerate(self.usbMidiHost.getDeviceList()):
            self.draw.rectangle([(87, (i+1)*20), (127, (i+2)*20)], outline="red", fill=0)
            self.draw.text((87, (i+1)*20), dev['name'][0:6], font=font)

    def drawInformations(self):
        if self.currentInfo != 0:
            self.infos = [f"status", f"ip:{self.getIp()}", f"uptime:{self.get_uptime()}", f'cpu:{psutil.cpu_percent()}%', f'ram:{psutil.virtual_memory().percent}%', 'creator: lukn303']
        self.draw.rectangle([(0,0), (127, 15)], outline='red', fill=0)
        self.draw.text((5, 0), self.infos[self.currentInfo], font=font)

    @staticmethod
    def get_uptime():
        with open('/proc/uptime', 'r') as f:
            seconds = float(f.readline().split()[0])
        return str(timedelta(seconds=seconds)).split('.', maxsplit=1)[0]

    @staticmethod
    def getIp():
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(('8.8.8.8', 1))  # connect() for UDP doesn't send packets
        return sock.getsockname()[0]

    def statusMessage(self, text):
        self.infos[0] = f"{text}"
        self.currentInfo = 0

    def linedashed(self, x0, y0, x1, y1, dashlen=4, ratio=3):
        # get deltas
        deltax = x1 - x0
        deltay = y1 - y0
        # check whether we can avoid sqrt
        if deltay == 0:
            length = deltax
        elif deltax == 0:
            length = deltay
        else:
            # length of line
            length = math.sqrt(deltax*deltax+deltay*deltay)
        # x add for 1px line length
        xa = deltax / length
        # y add for 1px line length
        ya = deltay / length
        # step to the next dash
        step = dashlen * ratio
        a0 = 0
        while a0 < length:
            a1 = a0 + dashlen
            a1 = min(a1, length)
            self.draw.line((x0+xa*a0, y0+ya*a0, x0+xa*a1, y0+ya*a1))
            a0 += step

    def drawLines(self):
        # draw cursor line with a dot on the current Side
        p1 = (40, (self.currentDeviceLeft + 1) * 20 + 10)
        p2 = (87, (self.currentDeviceRight + 1) * 20 + 10)
        if self.currentSide == LEFT:
            self.draw.ellipse((p1[0], p1[1] - 3, p1[0] + 6, p1[1] + 3), fill='white', outline='white')
        else:
            self.draw.ellipse((p2[0] - 6, p2[1] - 3, p2[0], p2[1] + 3), fill='white', outline='white')
        self.linedashed(p1[0], p1[1], p2[0], p2[1])

        # draw solid lines for connected Devices
        for connected in self.connectedDevices:
            p1 = (40, (connected['in'] + 1) * 20 + 10)
            p2 = (87, (connected['out'] + 1) * 20 + 10)
            self.draw.line((p1, p2))

    @staticmethod
    def decrease(num, maxNum):
        return num - 1 if num > 0 else maxNum

    @staticmethod
    def increase(num, maxNum):
        return num + 1 if num < maxNum - 1 else 0

    def drawUi(self):
        self.draw.rectangle([(0, 0), (127, 127)], fill=0)
        self.drawInformations()
        self.drawDevices()
        self.drawLines()
        self.disp.LCD_ShowImage(self.image, 0, 0)


if __name__ == "__main__":
    ui = usbMidiHostUi()
    try:
        while 1:
            ui.drawUi()
    except Exception as e:
        GPIO.cleanup()
        raise e
