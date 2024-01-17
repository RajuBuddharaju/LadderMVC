#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

//Wifi Stuff
const char* ssid = "Polmans";     // Replace with your WiFi SSID
const char* password = "0402851544"; // Replace with your WiFi password
const int hardcodedMEID = 1234; // Replace with your hardcoded MEID
const char* serverName = "https://ladder.xsoul.org/get_active_ueid/"; // Replace with your Flask server URL

// Sending Stuff
const int datapin_A = 18;   //outputs
const int datapin_B = 19;

void setup() {
    Serial.begin(9600);

    //Wifi Stuff
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(1000);
        Serial.println("Connecting to WiFi...");
    }
    Serial.println("Connected to WiFi");

    //Sending Stuff
    pinMode(datapin_A, OUTPUT);  //define outputs
    pinMode(datapin_B, OUTPUT);
    digitalWrite(datapin_A, HIGH); //set outputs default
    digitalWrite(datapin_B, LOW);
}

void loop() {
    getActiveUEID();
    delay(1000); // Wait for 2 seconds before fetching again
}

void getActiveUEID() {
    if(WiFi.status() == WL_CONNECTED) {
        HTTPClient http;
        String serverPath = serverName + String(hardcodedMEID);

        http.begin(serverPath.c_str());
        int httpResponseCode = http.GET();

        if (httpResponseCode > 0) {
            String response = http.getString();
            Serial.println("HTTP Response code: " + String(httpResponseCode));

            DynamicJsonDocument doc(1024);
            deserializeJson(doc, response);

            if (doc.containsKey("error")) {
                Serial.println("Error: MEID does not exist");
            } else {
                JsonObject activeUEID = doc["activeUEID"];
                //---------------------------------------------------------------------------------------------------------------------------------
                if (activeUEID.isNull()) {
                    Serial.println("No active UEID");
                } else {
                    // Directly send each goal and its progress 
                    Serial.println(activeUEID["dataValue1"].as<String>() + " at " + activeUEID["progress1"].as<int>()); // Printing goals in serial monitor just for us to see
                    sendGoal(1, activeUEID["dataValue1"].as<String>(), activeUEID["progress1"].as<int>()); // First parameter of each function call is the address change that to the particular address of the Arduino receiving the goal

                    delay(1000); // 2-second delay

                    Serial.println(activeUEID["dataValue2"].as<String>() + " at " + activeUEID["progress2"].as<int>());
                    sendGoal(2, activeUEID["dataValue2"].as<String>(), activeUEID["progress2"].as<int>());

                    delay(1000);

                    Serial.println(activeUEID["dataValue3"].as<String>() + " at " + activeUEID["progress3"].as<int>());
                    sendGoal(2, activeUEID["dataValue3"].as<String>(), activeUEID["progress3"].as<int>());

                    // delay(2000); // We will not use this goal as we only have three spokes on the main ladder

                    //System.out.println(activeUEID["dataValue4"].as<String>() + " at " + activeUEID["progress4"].as<int>());
                    // sendGoal(2, activeUEID["dataValue4"].as<String>(), activeUEID["progress4"].as<int>());
                }
                //---------------------------------------------------------------------------------------------------------------------------------
            }
        }
        else {
            Serial.println("HTTP GET request failed");
        }

        http.end();
    }
    else {
        Serial.println("WiFi Disconnected");
    }
}

void sendGoal(int address, String goal, int progress) {
    // Ensure the string is 32 characters long
    while (goal.length() < 32) {
        goal += " "; // Append spaces
    }

    // Convert String to char array
    char goalCharArray[33];
    goal.toCharArray(goalCharArray, 33);

    // Send the data
    sendData(address, goalCharArray, progress); // Assuming 'colour' is not used, set to 0
}

void sendData(int address, char lines[], int colour) {
  int rate  = 10000 / 8;   //sendspeed x2 microseconds per bit
  char dataarray[280]; //allocate space for binary array
  int chcksm = 0;
 
  // ... Rest of your code goes here ...
 
  //address to bin character list converter
int i = 0;
int j = 128;
int s = address;
while (i < 8){ 
    dataarray[i] = '0';
  if ((s - j) >= 0){
    dataarray[i] = '1';
    chcksm = chcksm + 1;
    s = s - j;
  }
  j= j / 2;  
  i = i + 1;
}
 
//ascii character to bin character list converter
int m = 0;
while (m < 32){
  int i = 0;
  int j = 128;
  int s = (int)lines[m];   //char to ascii
  while (i < 8){ 
      dataarray[i+((m+1)*8)] = '0';
    if ((s - j) >= 0){
      dataarray[i+((m+1)*8)] = '1';
      chcksm = chcksm + 1;
      s = s - j;
    }
    j= j / 2;  
    i = i + 1;
  }
  m = m + 1;
}
 
//ledcolour to bin character list converter
i = 0;
j = 128;
s = colour;
while (i < 8){ 
    dataarray[i+264] = '0';
  if ((s - j) >= 0){
    dataarray[i+264] = '1';
    chcksm = chcksm + 1;
    s = s - j;
  }
  j= j / 2;  
  i = i + 1;
}
 
 
//checksum to bin character list converter
 
chcksm = chcksm % 128;//reduce checksum size to below 128
 
i = 0;
j = 128;
s = chcksm;
while (i < 8){ 
    dataarray[i+272] = '0';
  if ((s - j) >= 0){
    dataarray[i+272] = '1';
    s = s - j;
  }
  j= j / 2;  
  i = i + 1;
}
 
 
//wakeywakey
  digitalWrite(datapin_A, LOW); //set outputs default
delayMicroseconds(rate*3);
  digitalWrite(datapin_A, HIGH); //set outputs default
delayMicroseconds(rate*3);
      i = 0;
      while(i < sizeof(dataarray)){
        if (dataarray[i] == '0') {
          digitalWrite(datapin_A,LOW);
          delayMicroseconds(rate);
          digitalWrite(datapin_A,HIGH);
          delayMicroseconds(rate);
        }
        if (dataarray[i] == '1') {
          digitalWrite(datapin_B,HIGH);
          delayMicroseconds(rate);
          digitalWrite(datapin_B,LOW);
          delayMicroseconds(rate);
        }
        i = i + 1;
      }
 
 
//Serial.print(dataarray);
//Serial.print('\n');
}