//#include <Wire.h>
//#include "menerimaData.h"
//
//void setup() {
//    Serial.begin(9600);               
//    pinMode(LED_BUILTIN, OUTPUT);     
//}
//
//void loop() {
//    char data;                        
//    if (Serial.available() > 0) {    
//        data = Serial.read();         
//    } else {
//        return;                       
//    }
//
//    // Logika berdasarkan karakter yang diterima
//    if (data == 'a') {              
//        digitalWrite(LED_BUILTIN, HIGH);  
//        Serial.println("Karakter diterima: a");
//    } else if (data == 'b') {         
//        digitalWrite(LED_BUILTIN, LOW);   
//        Serial.println("Karakter diterima: b");
//    } else {
//        Serial.print("Karakter lain diterima: ");
//        Serial.println(data);         
//    }
//
//    delay(500);                      
//}
