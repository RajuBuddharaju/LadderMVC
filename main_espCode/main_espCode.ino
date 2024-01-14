#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

const char* ssid = "Polmans";     // Replace with your WiFi SSID
const char* password = "0402851544"; // Replace with your WiFi password
const int hardcodedMEID = 1234; // Replace with your hardcoded MEID
const char* serverName = "https://ladder.xsoul.org/get_active_ueid/"; // Replace with your Flask server URL


void setup() {
    Serial.begin(9600);
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
                    String goal1 = activeUEID["dataValue1"].as<String>();
                    String goal2 = activeUEID["dataValue2"].as<String>();
                    String goal3 = activeUEID["dataValue3"].as<String>();
                    String goal4 = activeUEID["dataValue4"].as<String>();
                    int progress1 = activeUEID["progress1"].as<int>();
                    int progress2 = activeUEID["progress2"].as<int>();
                    int progress3 = activeUEID["progress3"].as<int>();
                    int progress4 = activeUEID["progress4"].as<int>();
                    Serial.print("Goal1: " + goal1 + " at progress " + progress1);
                    Serial.print("Goal2: " + goal2 + " at progress " + progress2);
                    Serial.print("Goal3: " + goal3 + " at progress " + progress3);
                    Serial.print("Sub Goal: " + goal4 + " at progress " + progress4);
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
