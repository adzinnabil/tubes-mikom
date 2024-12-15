
#include <string.h>

void menerima(float *data){
  char receivedData[20]; 
    int dataIndex = 0;
    bool newDataReceived = false;

    while (Serial.available() > 0) {
        char incomingByte = Serial.read();
        if (incomingByte == ' ') { 
            receivedData[dataIndex] = '\0';
            dataIndex = 0; 
            newDataReceived = true; 
        } else {
            receivedData[dataIndex] = incomingByte;
            dataIndex++;
            if (dataIndex >= sizeof(receivedData) - 1) { 
                dataIndex = 0;
                memset(receivedData, 0, sizeof(receivedData));
            }
        }
    }

    *data = atof(receivedData);
    

    

  
}
