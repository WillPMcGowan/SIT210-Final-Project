from gpiozero import LED
from gpiozero import MotionSensor

led1 = LED(17)
pir = MotionSensor(4)
led1.off() # start led off


while True:
    pir.wait_for_motion()
    print("Motion detected - Turning detection services on")
    led1.on()    
    pir.wait_for_no_motion() # wait for motion to stop
    led1.off()    
    print("Motion n")