#!/usr/bin/env python


##############
#    INIT
##############

# Import General Stuff
import os
from config import *  
import math
from time import sleep
import threading

# Only output on windows
debug=(os.name == "nt")

# Initialize LEDs
ledHandlers=[]

# Import GPIO if not on windows
if(not debug):
    from gpiozero import PWMLED
    from gpiozero import Button

# Vars used for later
inputNr=1
doLoop = True

##############
#  FUNCTIONS
##############

def log(level,message):
    if(CONFIG["loglevel"] >= level):
        logEntry ="%-4s - %s" % ( "#" * level, message )
        if(CONFIG["log2console"]):
            print(logEntry)
        if(CONFIG["log2file"]):
            f = open(CONFIG['logFile'], 'a')
            f.write("%s\n" % logEntry)
            f.close()

# Initializes all LED handlers
def initializeLEDs():

    log(2,"Initializing LED Array")

    # go through all sets    
    for setID,set in enumerate(CONFIG["sets"]):
        log(3,"# Initializing set %s" % setID)
        
        # Initialize Array for this set
        ledSET=[]
            
        # Go through all leds in set
        for ledID,led in enumerate(set):

            log(4, "Initializing led %s:%s" % (setID,ledID))
            
            # Add new handler to set-array
            if(debug):
                ledSET.append(led)
            else:
                ledSET.append(PWMLED(led))
        # END: for ledID,led in enumerate(set):

        # add set-array to global array
        ledHandlers.append(ledSET)
    # END: for setID,set in enumerate(CONFIG["sets"]):
# END: def initializeLEDs():


# turns off all leds
def disableAll():
    log(2,"Disable All")

    # go through all sets    
    for setID, set in enumerate(ledHandlers):
        log(3,"Disable SET %s" % (setID))

        # Go through all leds in set
        for ledID,led in enumerate(set):

            log(4,"Disable LED %s:%s" % (setID,ledID))

            if(not debug):
                led.off()
        # END: for ledID,led in enumerate(set):
    # END: for setID, set in enumerate(ledHandlers):
# END: def disableAll():



# pulse leds in a given set
def pulseSet(setID):
    # Calculate pulse duration
    pulseDuration=math.floor(CONFIG["interval"] / 2)

    log(2,"Pulse SET %s" % setID)

    # Go through all leds in set
    for ledID,led in enumerate(ledHandlers[setID-1]):

        if(not debug):
            log(4, "Pulse LED %s:%s for %s" % (setID,ledID, pulseDuration))
            # Pulse LED
            led.pulse(fade_in_time=pulseDuration, fade_out_time=pulseDuration)
        else:
            log(4, "Pulse LED %s:%s for %s on pin %s" % (setID,ledID, pulseDuration, led))
    # END: for ledID,led in enumerate(ledHandlers[setID-1]):
# END: def pulseSet():


# pulse leds in a given set
def turnonSet(setID):
  
    log(2,"TurOn SET %s" % setID)

    # Go through all leds in set
    for ledID,led in enumerate(ledHandlers[setID-1]):

        if(not debug):
            log(4, "TurnOn LED %s:%s" % (setID,ledID))
            # TurnOn LED
            led.on()
        else:
            log(4, "TurnOn LED %s:%s on pin %s" % (setID,ledID, led))
    # END: for ledID,led in enumerate(ledHandlers[setID-1]):
# END: def turnonSet():



# Pulses all LED
def runPulseAll():
    log(2,"Starting up runPulseAll")
    while doLoop:
        for setID,set in enumerate(ledHandlers):
            # Turn off all
            disableAll()
            # Turn on LEDs in set
            pulseSet(setID)
            # Wait for interval to pass
            sleep(CONFIG["interval"])
    log(3,"Ending runPulseAll")
# END: def runPulseAll():

# Pulses a set
def runPulseSet(setID):
    log(2,"Starting up runPulseSet")
    # Turn off all
    disableAll()
    # Turn on LEDs in set
    pulseSet(setID)
    log(3,"Ending up runPulseSet")
# END: def runPulseSet():

# Pulses a set
def runLightupSet(setID):
    log(2,"Starting up runLightupSet")
    # Turn off all
    disableAll()
    # Turn on LEDs in set
    turnonSet(setID)
    log(3,"Ending up runLightupSet")
# END: def runLightupSet():


##############
#   SCRIPT
##############


log(1,"Starting LED Controller")
log(2, "Number of Sets: %s" % len(CONFIG["sets"]))
log(2, "Interval:       %s" % CONFIG["interval"])
log(2, "Button GPIO:    %s" % CONFIG["button_id"])

# Initialize LEDs
initializeLEDs()

# Initialize Button
if(not debug):
    modeButton = Button(CONFIG["button_id"])

while True:
    try:
        # Gets on which set we are on
        setID=((inputNr-1)%len(CONFIG["sets"]))+1
        # Gets wich mode we are on
        mode=(math.floor((inputNr-1)/len(CONFIG["sets"])) % 3) + 1
        # meaning for 4 sets:
        # Input = 1-4 / Mode = 1 / Set = x  | Pulse All
        # Input = 5   / Mode = 2 / Set = 1  | Pulse Set 1
        # Input = 10  / Mode = 3 / Set = 2  | Light up set 2
        log(2,"Running mode %s with set %s" % (mode,setID))

        # Run mode in seperate thread
        if(mode == 1):
            currentThread = threading.Thread ( target=runPulseAll )
        if(mode == 2):
            currentThread = threading.Thread ( target=runPulseSet, args=(setID,)  )
        if(mode == 3):
            currentThread = threading.Thread ( target=runLightupSet, args=(setID,)  )

        # Startup thread
        doLoop = True
        currentThread.start()

        # Wait for the button to be pressed
        if(debug):
            # for debuging just press every 10 seconds
            sleep(10)
        else:
            modeButton.wait_for_press()

        log(1,"Button has been pressed")

        # Stop Loop and wait for it to end
        doLoop = False
        disableAll()
        if(currentThread.is_alive()):
            currentThread.join()

        # Increase for the set if mode = 1
        if(mode==1):
            inputNr += len(CONFIG["sets"])
        else: # just increase it
            inputNr += 1

    except KeyboardInterrupt:
        log(4,"Handle KeyboardInterrupt")
        doLoop = False
        if(currentThread.is_alive()):
            currentThread.join()
        raise SystemExit
