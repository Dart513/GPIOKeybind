import keyboard
import sys
import RPi.GPIO as GPIO
import time
import threading
import yaml
import Adafruit_ADS1x15



GPIO.setmode(GPIO.BCM)

path = 'keymap.txt'
keymapFile = open(path, 'r')

global binds
global halted
running = True

binds = {}

keybinds = []

global i2cDevices
i2cDevices = []
hasI2c = False


for line in keymapFile.readlines():
    line = line.replace("\n", "")
    if line.startswith("#"):
        continue

    temp = line.split('>')

    # If it's an i2c device on the ads1015
    if "i2c" in temp[0]:
        hasI2c = True

        temp2 = {}
        
        if "double:" in temp[1]:
            temp2['type'] = "double"
            t3 = temp[1].replace("double:", "").split("&&")
            temp2['minKey'] = t3[0]
            temp2['maxKey'] = t3[1]

        else:
            temp2['type'] = "single"
            temp2['key'] = temp[1]

        i2cDevices.append(temp2)

    else:
        keybinds.append(temp)


# Spawn a new thread to deal with i2c if we have any i2c joystickss

# i2c pwm loop

def pwmLoop():
    try:
        adc = Adafruit_ADS1x15.ADS1015()
        GAIN = 2

        while True:
            print()
    except KeyboardInterrupt:
    




if hasI2c:
    t = threading.Thread(target=pwmLoop)
    t.start()

for element in keybinds:
    GPIO.setup(int(element[0]), GPIO.IN)


try:
    while True:
        for element in keybinds:
            if GPIO.input(int(element[0])):
                keyboard.press(element[1])

            else:
                keyboard.release(element[1])

        time.sleep(0.05)


except KeyboardInterrupt:
    print("Terminated.")

finally:
    GPIO.cleanup()

