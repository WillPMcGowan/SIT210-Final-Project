import cv2
import paho.mqtt.publish as publish
import requests
import RPi.GPIO as GPIO
from gpiozero import Buzzer
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import time

"""
This section cotains object detection setup
"""
subject = "wolf" # Change this to the animal you wish to detect. Check the coco.names file to see if the animal is on there
accuracy_thresh = 80

classNames = []
classFile = "/home/pi/Pest_Detection_Alert/Pest_Detection_Files/coco.names"

with open(classFile,"rt") as f:
    classNames = f.read().rstrip("\n").split("\n")
    try:
        if subject not in classNames:
            raise ValueError("This animal can not be detected. Try Checking spelling")
    except ValueError as e:
        print(e)
        print("Exiting")
        quit()

configPath = "/home/pi/Pest_Detection_Alert/Pest_Detection_Files/ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt"
weightsPath = "/home/pi/Pest_Detection_Alert/Pest_Detection_Files/frozen_inference_graph.pb"

net = cv2.dnn_DetectionModel(weightsPath,configPath)
net.setInputSize(320,320)
net.setInputScale(1.0/ 127.5)
net.setInputMean((127.5, 127.5, 127.5))
net.setInputSwapRB(True)

# Main object detection function 
def detect_object(img, thres, nms, objects=[]):
    classIds, confs, bbox = net.detect(img,confThreshold=thres,nmsThreshold=nms)
    if len(objects) == 0: objects = classNames
    accuracy = []
    class_name = []
    if len(classIds) != 0:
        for classId, confidence,box in zip(classIds.flatten(),confs.flatten(),bbox):
            className = classNames[classId - 1]
            if className in objects:
                accuracy.append(round(confidence*100,2)) # capture the class name.
                class_name.append(className) # capture the accuracy of the detection
                
    return img, accuracy, class_name 

# hardware setup
buzzer = Buzzer(18)

# Simulate alarm
def alarm_function():
    for i in range(10):
        buzzer.on()
        time.sleep(.3)
        buzzer.off()

"""
This section conatins communication setup
"""
# flag to track if MQTT is connected
flag_connected = 0
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    if rc == 1:
        print("Failed Connection")
    # Subscribing in on_connect() - if we lose the connection -> reconnect then subscriptions will be renewed.
    client.subscribe("pest_connect")
    global flag_connected
    flag_connected = 1
    
def on_disconnect(client, userdata, rc):
    global flag_connected
    flag_connected = 0
    
# The callback for when a PUBLISH message is received from the MQTT server.
def on_message(client, userdata, msg):
    print("Topic:" + msg.topic+ " "+str(msg.payload))
    return str(msg.payload)

"""
This section is the main function/loop
""" 

try:
 
    if __name__ == "__main__":
        
        # assign camera
        cap = cv2.VideoCapture(0)
        cap.set(4,480)
        count = 0 # temp count to only send 1 email
        
        while True:
            # if not connected, connect.
            if flag_connected == 0:
                client = mqtt.Client()
                client.on_connect = on_connect
                client.on_disconnect = on_disconnect
                client.on_message = on_message
                client.connect("test.mosquitto.org", 1883, 60)
                client.loop_start()
                print("Scanning...") 
                                                                                                                       
            success, img = cap.read() 
            result, accuracy, class_name = detect_object(img,0.45,0.2, objects=[subject]) # run object detection

            if len(accuracy) > 0: # check if there is pest detected 
                if max(accuracy) > accuracy_thresh and subject in class_name: # check if the accuracy is good enough and the class name is dog
                    
    
                    # post message to IFTTT
                    if count == 0:
                        r = requests.post('https://maker.ifttt.com/trigger/dog_detected/json/with/key/cstmwvfLhRe9rKGhZ58pVl')
                        count = 1
                    # publish message which argon is subscribed to 
                    publish.single("pest_detect", "pest_detected", hostname="test.mosquitto.org")
                   
                    print("Positive Detection")
                    # Create an MQTT client and attach our routines to it.
                    # Alarm functionality
                    alarm_function()
                    client.on_connect = on_connect
                    client.on_disconnect = on_disconnect
                    client.on_message = on_message

# handle if there is error with object detection, usually this is a problem with the camera
except cv2.error as e:
    publish.single("pest_detect", "cv2_error", hostname="test.mosquitto.org")
    print("Error with object detection. Check camera is plugged in properly")
    print(e)
except KeyboardInterrupt as e:
    print(e)
# cleanly exit the program
finally:
    GPIO.cleanup()
    client.loop_stop()
    print("Exiting")
    

    
