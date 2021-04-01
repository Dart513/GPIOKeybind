import keyboard
import RPi.GPIO as GPIO
import time
import threading
import json
from enum import Enum
import Adafruit_ADS1x15

PATH_TO_FILE = "keymap.json"

global running, binds, ads1015
ads1015 = None
running = True
binds = {}


# ------------------------------ Misc functions ------------------------------ #

def mapValues(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;


#def simKeyUp(key) :
    #print(key + " up")


def pwmKey(key, pulseWidth, pulseMax):
    print(str(key) + "down")
    keyboard.press(key)
    if pulseWidth < pulseMax*0.96: keyboard.call_later(keyboard.release, args=[key], delay=pulseWidth)



# ---------------------------- Read the json file ---------------------------- #

with open(PATH_TO_FILE, 'r') as stream:

    jsonFile = json.loads(stream.read())


# ----------------------------------- Setup ---------------------------------- #

GPIO.setmode(GPIO.BCM)

# Interface types:
""" GPIO
    ADS1015""" 


# Mapping types:
""" BUTTON
    DOUBLE_AXIS_BUTTON
    SINGLE_AXIS
    DOUBLE_AXIS 
    """




def GPIOSetup(entry):
    global binds
    
    if 'GPIO' not in binds: binds['GPIO'] = []

    GPIO.setup(entry['source'], GPIO.IN)
    binds[entry['interface']].append(entry)

def ads1015Setup(entry):
    global binds, ads1015

    if ads1015 is None:
        ads1015 = Adafruit_ADS1x15.ADS1015()
        binds['ADS1015'] = []
    

    binds[entry['interface']].append(entry)

default = GPIOSetup

setupSwitcher = {
    'GPIO': GPIOSetup,
    'ADS1015': ads1015Setup,
}


for entry in jsonFile:
    print("Binding " + entry["name"])
    setupSwitcher.get(entry['interface'], default)(entry)


# ------------------------------- Main loop(s) ------------------------------- #

# Switcher for thread choice yay

def GPIOThread():
    global binds, running

    while running:
        
        for element in binds['GPIO']:

            if GPIO.input(element['source']) ^ element['inverted']:
                #print(str(element['binding']) + " up")
                keyboard.press(element['binding'])

            else:
                keyboard.release(element['binding'])

        time.sleep(0.05)

def ads1015Thread():

    global binds, running
    lastTime = time.perf_counter()

    PERIOD = 0.016  
    SLEEP_TIME = PERIOD/5
    while running:
        if time.perf_counter() - lastTime >= PERIOD:
            for x in binds['ADS1015']:
                # Measure each
                value = ads1015.read_adc(x['source'], gain=x['GAIN'])

                deadZone = x['deadZone']

                # PWM keydown
                if (x['type'] == "DOUBLE_AXIS"):
                    
                    value = mapValues(value, x['inMin'], x['inMax'], -1, 1)
                    #print(x['name'] + str(value))
                    middle = 0

                
                    if value >= middle - deadZone/2 and value <= middle + deadZone/2:
                        keyboard.release(x['bindMin'])
                        keyboard.release(x['bindMax'])
                        continue;
                    
                    elif value < middle:
                        pulseWidth = abs(value) * PERIOD
                        keyboard.release(x['bindMax'])
                        pwmKey(x['bindMin'], pulseWidth, PERIOD)

                    else:
                        pulseWidth = abs(value) * PERIOD
                        keyboard.release(x['bindMin'])
                        pwmKey(x['bindMax'], pulseWidth, PERIOD)
                    

                elif (x['type'] == "SINGLE_AXIS"):
                    value = mapValues(value, x['inMin'], x['inMax'], 0, 1)
                    pulseWidth = value * PERIOD
                    if value > deadZone: pwmKey(x['binding'], pulseWidth)


                elif(x['type'] == "DOUBLE_AXIS_BUTTON"):
                    value = mapValues(value, x['inMin'], x['inMax'], -1, 1)
                    #print(x['name'] + str(value))
                    middle = 0
                    
                    if value <= x['threshold']:
                        pulseWidth = abs(value) * PERIOD
                        pwmKey(x['bindMin'], pulseWidth)

                    elif value >= 1 - x['threshold']:
                        pulseWidth = abs(value) * PERIOD
                        pwmKey(x['bindMax'], pulseWidth)

            lastTime = time.perf_counter()    

        time.sleep(SLEEP_TIME)
    

threadSwitcher = {
    'GPIO': GPIOThread,
    'ADS1015': ads1015Thread
}

# Setup threads
binds['threads'] = []

for x in binds:
    y = threading.Thread(target=threadSwitcher.get(x))
    binds['threads'].append(y)
    y.start()
    

try:
    while True:
        time.sleep(100)

except KeyboardInterrupt:
    print("Shutting down!")
    running = False
    for x in binds['threads']:
        x.join()

finally:
    GPIO.cleanup()

