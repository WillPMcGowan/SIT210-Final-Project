import cv2
import paho.mqtt.publish as publish
import requests
import RPi.GPIO as GPIO
from gpiozero import LED
from gpiozero import MotionSensor
from gpiozero import Buzzer
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import time

# hardware setup
green_led = LED(23)
red_led = LED(24)
buzzer = Buzzer(18)



#thres = 0.50 # detection accuracy threshold
"""
This section cotains object detection setup
"""
classNames = []
classFile = "/home/pi/Pest_Detection_Alert/Pest_Detection_Files/coco.names"
with open(classFile,"rt") as f:
    classNames = f.read().rstrip("\n").split("\n")

configPath = "/home/pi/Pest_Detection_Alert/Pest_Detection_Files/ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt"
weightsPath = "/home/pi/Pest_Detection_Alert/Pest_Detection_Files/frozen_inference_graph.pb"

net = cv2.dnn_DetectionModel(weightsPath,configPath)
net.setInputSize(320,320)
net.setInputScale(1.0/ 127.5)
net.setInputMean((127.5, 127.5, 127.5))
net.setInputSwapRB(True)

def detect_object(img, thres, nms, draw=True, objects=[]):
    classIds, confs, bbox = net.detect(img,confThreshold=thres,nmsThreshold=nms)
    if len(objects) == 0: objects = classNames
    accuracy = []
    class_name = []
    if len(classIds) != 0:
        for classId, confidence,box in zip(classIds.flatten(),confs.flatten(),bbox):
            className = classNames[classId - 1]
            if className in objects:
                accuracy.append(round(confidence*100,2)) # capture the class name. In this case we will want to capture dog
                class_name.append(className) # capture the accuracy of the detection
                if (draw):
                    cv2.rectangle(img,box,color=(0,0,255),thickness=2)
                    cv2.putText(img,classNames[classId-1].upper(),(box[0]+10,box[1]+30),
                    cv2.FONT_HERSHEY_COMPLEX,1,(0,0,255),2)
                    cv2.putText(img,str(round(confidence*100 + 10,2)),(box[0]+200,box[1]+30),
                    cv2.FONT_HERSHEY_COMPLEX,1,(0,0,255),2)

    return img, accuracy, class_name 


"""
This section conatins communication setup
"""




"""
This section is the main function/loop
"""

try:
    
    if __name__ == "__main__":
        
        cap = cv2.VideoCapture(0)
        cap.set(4,480)
        count = 0 # temp count to only send 1 text
        while True:

            
            success, img = cap.read()
            #result, accuracy, class_name = detect_object(img,0.45,0.2, objects=['dog']) # UN-COMMENT FOR DOG
            result, accuracy, class_name = detect_object(img,0.45,0.2, objects=['dog'])
                    # Alarm functionality

            # Un-comment to display output.  
            cv2.imshow("Output",img)
            cv2.waitKey(1)
        
except cv2.error as e:
    print("Error with object detection. Check camera is plugged in properly")
except KeyboardInterrupt:
    print("Exiting")
finally:
    GPIO.cleanup()
    
