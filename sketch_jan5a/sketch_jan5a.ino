#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

const char* ssid = "AoA";     // Replace with your WiFi SSID
const char* password = "An@s20032003"; // Replace with your WiFi password
const int hardcodedMEID = 69420; // Replace with your hardcoded MEID
const char* serverName = "http://192.168.0.101:6922/get_active_ueid/"; // Replace with your Flask server URL


void setup() {
    Serial.begin(115200);
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(1000);
        Serial.println("Connecting to WiFi...");
    }
    Serial.println("Connected to WiFi");
}

void loop() {
    getActiveUEID();
    delay(30000); // Wait for 30 seconds before fetching again
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
                if (activeUEID.isNull()) {
                    Serial.println("No active UEID");
                } else {
                    // do stuff here
                    Serial.print("Active UEID Data: ");
                    Serial.print("UEID: "); Serial.println(activeUEID["id"].as<int>()); // Assuming 'id' is an integer
                    Serial.print("Name: "); Serial.println(activeUEID["name"].as<String>());
                    Serial.print("Data Value 1: "); Serial.println(activeUEID["dataValue1"].as<String>());
                    Serial.print("Data Value 2: "); Serial.println(activeUEID["dataValue2"].as<String>());
                    Serial.print("Data Value 3: "); Serial.println(activeUEID["dataValue3"].as<String>());
                    Serial.print("Data Value 4: "); Serial.println(activeUEID["dataValue4"].as<String>());
                }
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
