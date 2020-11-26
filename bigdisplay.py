import lcddriver
from time import *
 
lcd = lcddriver.lcd()
lcd.lcd_clear()
 
lcd.lcd_display_string("Tutorials-", 1)
lcd.lcd_display_string("      RaspberryPi.de", 2)
