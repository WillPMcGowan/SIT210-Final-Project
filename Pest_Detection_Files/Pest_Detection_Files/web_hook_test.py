#! /usr/bin/python

# Imports
import RPi.GPIO as GPIO
import time
import requests



try:
    print("Waiting for PIR to settle ...")

    # Loop until PIR output is 0
    while GPIO.input(pinpir) == 1:

        currentstate = 0

    print(" Ready")

    # Loop until users quits with CTRL-C
    while True:

        # Read PIR state
        currentstate = GPIO.input(pinpir)

        # If the PIR is triggered
        if currentstate == 1 and previousstate == 0:

            print("Motion detected!")

            # Your IFTTT URL with event name, key and json parameters (values)
            r = requests.post('https://maker.ifttt.com/trigger/YOUR_EVENT_NAME/with/key/cstmwvfLhRe9rKGhZ58pVI', params={"value1":"none","value2":"none","value3":"none"})

            # Record new previous state
            previousstate = 1

            #Wait 120 seconds before looping again
            print("Waiting 120 seconds")
            time.sleep(120)

        # If the PIR has returned to ready state
        elif currentstate == 0 and previousstate == 1:

            print("Ready")
            previousstate = 0

        # Wait for 10 milliseconds
        time.sleep(0.01)

except KeyboardInterrupt:
    print(" Quit")

    # Reset GPIO settings
    GPIO.cleanup()
