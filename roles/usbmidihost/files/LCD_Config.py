import time
import spidev
import RPi.GPIO as GPIO

# Pin definition
LCD_RST_PIN = 27
LCD_DC_PIN = 25
LCD_CS_PIN = 8
LCD_BL_PIN = 24

# SPI device, bus = 0, device = 0
SPI = spidev.SpiDev(0, 0)


def epd_digital_write(pin, value):
    GPIO.output(pin, value)


def Driver_Delay_ms(xms):
    time.sleep(xms / 1000.0)


def SPI_Write_Byte(data):
    SPI.writebytes(data)


def GPIO_Init():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(LCD_RST_PIN, GPIO.OUT)
    GPIO.setup(LCD_DC_PIN, GPIO.OUT)
    GPIO.setup(LCD_CS_PIN, GPIO.OUT)
    GPIO.setup(LCD_BL_PIN, GPIO.OUT)
    SPI.max_speed_hz = 9000000
    SPI.mode = 0b00
    return 0
