#include <MQTT.h>
#include <SparkJson.h>

// ===== Hardware setup =====

const int OffButton = D3;    // Turn sytem off
const int OnButton = D4;     // Turn sytem on
const int AlertLed =  D5;    // the number of the LED pin
const int buzzerPin =  D2;   // Audio Alert Buzzer
const int OnLed =  D8;       // Indicate system is on
const int cvErrorLed = D6;   // Indicate error with object detection

// ===== Coms setup and functions =====
// create a JSON object
StaticJsonBuffer<200> jsonBuffer;
JsonObject& root = jsonBuffer.createObject();


// MQTT callback
//void callback(char* topic, byte* payload, unsigned int length);
// MQTT client
MQTT client("test.mosquitto.org", 1883, callback);


// MQTT call back function
void callback(char* topic, byte* payload, unsigned int length) {
    char p[length + 1];
    memcpy(p, payload, length);
    p[length] = NULL;
    // when animal is detected
    if (strcmp(p, "pest_detected") == 0)
    {
        Particle.publish("Particle Publish", "pest detected", 60, PRIVATE); 
        client.publish("pest_connect", "alert recieved by Argon");
        digitalWrite(AlertLed, 1); // leave the alert LED on untill off button is pressed
        digitalWrite(buzzerPin, 1); 

        delay(2000);
        digitalWrite(buzzerPin, 0);
    }
    // when theres is problem with object detection
    if (strcmp(p, "cv2_error") == 0)
    {
        Particle.publish("Particle Publish", "cv2_error", 60, PRIVATE); 
        client.publish("pest_connect", "error recieved by argon");
        digitalWrite(cvErrorLed, 1); // will turn off in main loop
        
    }
    
}
// == Setup ==
void setup() {
    
    pinMode(OnLed, OUTPUT);
    pinMode(AlertLed, OUTPUT);  
    pinMode(cvErrorLed, OUTPUT);
    pinMode(buzzerPin, OUTPUT);
    pinMode(OnButton, INPUT_PULLDOWN);
    pinMode(OffButton, INPUT_PULLDOWN);
}
// == Loop ==
void loop() {
    bool OnState = false;

    if(digitalRead(OnButton) ==1){
        OnState = true;
    }
    while (OnState){
        //Connect to pi messages
        digitalWrite(OnLed, 1);
        client.connect("particle_dust");
        if(client.isConnected()) {
            
            client.subscribe("pest_detect");
        }
        // if connection fails, exit the loop
        else{
            OnState = false;
            break;}
        // run the loop whilst the on button state is true
        // when the off button is presses the state will change and exit the loop
        while(OnState){
            client.loop();
            if (digitalRead(OffButton)== 1){
                OnState = false;
            }
        }
    }
    // turn off all LEDS to indicate the system is off
    digitalWrite(OnLed, 0);
    digitalWrite(AlertLed, 0);
    digitalWrite(cvErrorLed, 0);
    delay(1000);
}