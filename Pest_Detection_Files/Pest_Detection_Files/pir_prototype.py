import cv2
import paho.mqtt.publish as publish
import requests
from gpiozero import LED
from gpiozero import MotionSensor
import time 

led = LED(17)
pir = MotionSensor(4)
led.off() # start led off



thres = 0.50 # detection accuracy threshold
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
                    cv2.rectangle(img,box,color=(255,0,0),thickness=2)
                    cv2.putText(img,classNames[classId-1].upper(),(box[0]+10,box[1]+30),
                    cv2.FONT_HERSHEY_COMPLEX,1,(255,0,0),2)
                    cv2.putText(img,str(round(confidence*100,2)),(box[0]+200,box[1]+30),
                    cv2.FONT_HERSHEY_COMPLEX,1,(255,0,0),2)

    return img, accuracy, class_name 


if __name__ == "__main__":

    cap = cv2.VideoCapture(0)
    cap.set(4,480)
    count = 0

    while True:
        if pir.motion_detected == True:
            print("Motion detected - Turning detection services on")
            led.on()
            success, img = cap.read()
            #result, accuracy, class_name = detect_object(img,0.45,0.2, objects=['dog'])
            result, accuracy, class_name = detect_object(img,0.45,0.2, objects=['cup'])
            
            if len(accuracy) > 0:# and:  count < 1: # 
                if max(accuracy) > 70 and "cup" in class_name: # check if the accuracy is good enough and the class name is dog
                    # post message to ifttt
                    #r = requests.post('https://maker.ifttt.com/trigger/dog_detected/json/with/key/cstmwvfLhRe9rKGhZ58pVl', params={"value1":"test","value2":"test2","value3":"test2"})
                    print("sent test ")
                    #count += 1
            
            #cv2.imshow("Output",img)
            #cv2.waitKey(1)
            #cv2.destroyAllWindows()  

             
        
        else:                                                                 
            led.off()

            
            #cv2.imshow("Output",img)
                     
            #cv2.waitKey(1)
            #cv2.destroyAllWindows()  

            #pir.wait_for_no_motion() # wait for motion to stop
            #led.off()

