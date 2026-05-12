#pragma once

// Copy this file to firmware/secrets.h and replace the placeholder values
// with your local Wi-Fi and MQTT settings. firmware/secrets.h is gitignored.

#ifndef IOT_WIFI_SSID
#define IOT_WIFI_SSID "YOUR_SSID"
#endif

#ifndef IOT_WIFI_PASS
#define IOT_WIFI_PASS "YOUR_PASSWORD"
#endif

#ifndef IOT_MQTT_HOST
#define IOT_MQTT_HOST "192.168.x.x"
#endif

#ifndef IOT_MQTT_PORT
#define IOT_MQTT_PORT 1883
#endif

#ifndef IOT_MQTT_USERNAME
#define IOT_MQTT_USERNAME ""
#endif

#ifndef IOT_MQTT_PASSWORD
#define IOT_MQTT_PASSWORD ""
#endif
