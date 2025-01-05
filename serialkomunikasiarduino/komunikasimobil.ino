#include <Wire.h>
#include "menerimaData.h"

const int EnableL = 5;
const int HighL = 6;
const int LowL = 7;

const int EnableR = 10;
const int HighR = 8;
const int LowR = 9;

void setup() {
    pinMode(EnableL, OUTPUT);
    pinMode(HighL, OUTPUT);
    pinMode(LowL, OUTPUT);

    pinMode(EnableR, OUTPUT);
    pinMode(HighR, OUTPUT);
    pinMode(LowR, OUTPUT);

    Serial.begin(9600);
}

void ke_depan() {
    digitalWrite(HighL, LOW);
    digitalWrite(LowL, HIGH);
    analogWrite(EnableL, 80);

    digitalWrite(HighR, LOW);
    digitalWrite(LowR, HIGH);
    analogWrite(EnableR, 60);
}

void ke_belakang() {
    digitalWrite(HighL, HIGH);
    digitalWrite(LowL, LOW);
    analogWrite(EnableL, 50);

    digitalWrite(HighR, HIGH);
    digitalWrite(LowR, LOW);
    analogWrite(EnableR, 50);
}

void ke_kiri() {
    digitalWrite(HighL, LOW);
    digitalWrite(LowL, HIGH);
    analogWrite(EnableL, 0);

    digitalWrite(HighR, LOW);
    digitalWrite(LowR, HIGH);
    analogWrite(EnableR, 100);
}

void ke_kanan() {
    digitalWrite(HighL, LOW);
    digitalWrite(LowL, HIGH);
    analogWrite(EnableL, 100);

    digitalWrite(HighR, LOW);
    digitalWrite(LowR, HIGH);
    analogWrite(EnableR, 0);
}

void stop_motor() {
    digitalWrite(HighL, LOW);
    digitalWrite(LowL, LOW);
    analogWrite(EnableL, 0);

    digitalWrite(HighR, LOW);
    digitalWrite(LowR, LOW);
    analogWrite(EnableR, 0);
}

void loop() {
    char data;

    if (Serial.available() > 0) {
        data = Serial.read();

        if (data == '1') {
            Serial.println("Stop");
            stop_motor();
            delay(1000);
        } else if (data == '2') {
            Serial.println("Kanan");
            ke_kanan();
            delay(1000);
        } else if (data == '3') {
            Serial.println("Kiri");
            ke_kiri();
            delay(1000);
        } else {
            Serial.print("Data tidak dikenali: ");
            Serial.println(data);
        }
    }

    ke_depan();
}
