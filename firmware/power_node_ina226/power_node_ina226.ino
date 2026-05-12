#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <Wire.h>
#include "INA226_WE.h"

#ifdef __has_include
#if __has_include("../secrets.h")
#include "../secrets.h"
#endif
#endif
#include "../firmware_version.h"
#include "../secrets.example.h"

#define I2C_ADDRESS 0x40

// Set to 1 to enable verbose serial diagnostics for sensor samples and raw
// register dumps while troubleshooting.
#ifndef POWER_NODE_ENABLE_DEBUG
#define POWER_NODE_ENABLE_DEBUG 0
#endif

const char* WIFI_SSID = IOT_WIFI_SSID;
const char* WIFI_PASS = IOT_WIFI_PASS;
const char* MQTT_HOST = IOT_MQTT_HOST;
const int   MQTT_PORT = IOT_MQTT_PORT;
const char* MQTT_USERNAME = IOT_MQTT_USERNAME;
const char* MQTT_PASSWORD = IOT_MQTT_PASSWORD;

// -----------------------------------------------------------------------------
// W2 configuration
// -----------------------------------------------------------------------------
const char* NODE_ID = "wifi01_power";
const char* EXP_ID  = "W2_wifi_idle_quiet_test";

// Set to 0 for connected-idle mode (R501)
// Set to 1000 / 5000 / 10000 for R502 / R503 / R504
const unsigned long PERIODIC_INTERVAL_MS = 0;

// INA226 publish interval for power samples
const unsigned long POWER_SAMPLE_INTERVAL_MS = 100;

// INA226 calibration parameters
// Adjust if your board uses a different shunt resistor.
const float SHUNT_RESISTOR_OHM = 0.1f;
const float MAX_CURRENT_A = 3.2f;

// -----------------------------------------------------------------------------
// MQTT topics
// -----------------------------------------------------------------------------
String topicPower = String("iotbench/power/") + NODE_ID + "/sample";
String topicEvent = String("iotbench/wifi/") + NODE_ID + "/event";

// -----------------------------------------------------------------------------
// Globals
// -----------------------------------------------------------------------------
WiFiClient espClient;
PubSubClient mqtt(espClient);
INA226_WE ina226(I2C_ADDRESS);

uint32_t seqNo = 0;
unsigned long lastPowerMs = 0;
unsigned long lastPublishMs = 0;

void printPowerSampleDebug(float busV, float shuntmV, float currentmA,
                           float powermW) {
#if POWER_NODE_ENABLE_DEBUG
  Serial.print("busV=");
  Serial.print(busV, 6);
  Serial.print(" V, shunt=");
  Serial.print(shuntmV, 6);
  Serial.print(" mV, current=");
  Serial.print(currentmA, 6);
  Serial.print(" mA, power=");
  Serial.print(powermW, 6);
  Serial.println(" mW");
#else
  (void)busV;
  (void)shuntmV;
  (void)currentmA;
  (void)powermW;
#endif
}

// -----------------------------------------------------------------------------
// Connectivity
// -----------------------------------------------------------------------------
void connectWiFi() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
  }
}

void connectMQTT() {
  mqtt.setServer(MQTT_HOST, MQTT_PORT);

  while (!mqtt.connected()) {
    String clientId = String("esp32-") + NODE_ID;
    bool connected = false;

    if (MQTT_USERNAME[0] != '\0') {
      connected = mqtt.connect(clientId.c_str(), MQTT_USERNAME, MQTT_PASSWORD);
    } else {
      connected = mqtt.connect(clientId.c_str());
    }

    if (!connected) {
      Serial.print("MQTT connect failed, state=");
      Serial.println(mqtt.state());
      delay(1000);
    }
  }
}

// -----------------------------------------------------------------------------
// Publish helpers
// -----------------------------------------------------------------------------
void publishPowerSample() {
  float busV = ina226.getBusVoltage_V();
  float currentmA = ina226.getCurrent_mA();
  float powermW = ina226.getBusPower();

#if POWER_NODE_ENABLE_DEBUG
  float shuntmV = ina226.getShuntVoltage_mV();
  printPowerSampleDebug(busV, shuntmV, currentmA, powermW);
  printINA226RawDebug();
#endif

  StaticJsonDocument<256> doc;
  doc["type"] = "power";
  doc["node"] = NODE_ID;
  doc["protocol"] = "wifi";
  doc["exp"] = EXP_ID;
  doc["t_local_us"] = micros();
  doc["bus_v"] = busV;
  doc["current_mA"] = currentmA;
  doc["power_mW"] = powermW;
  doc["wifi_rssi"] = WiFi.RSSI();
  doc["fw_version"] = IOT_FIRMWARE_VERSION;

  char payload[256];
  size_t n = serializeJson(doc, payload);
  mqtt.publish(topicPower.c_str(), payload, n);
}


void publishTelemetryEvent(const char* triggerType) {
  seqNo++;

  StaticJsonDocument<256> doc;
  doc["type"] = "event";
  doc["node"] = NODE_ID;
  doc["protocol"] = "wifi";
  doc["exp"] = EXP_ID;
  doc["seq"] = seqNo;
  doc["trigger"] = triggerType;
  doc["t_local_us"] = micros();
  doc["wifi_rssi"] = WiFi.RSSI();
  doc["fw_version"] = IOT_FIRMWARE_VERSION;

  char payload[256];
  size_t n = serializeJson(doc, payload);
  mqtt.publish(topicEvent.c_str(), payload, n);

#if POWER_NODE_ENABLE_DEBUG
  Serial.print("Published telemetry seq=");
  Serial.println(seqNo);
#endif
}

uint16_t readINA226Register16(uint8_t reg) {
  Wire.beginTransmission(I2C_ADDRESS);
  Wire.write(reg);
  uint8_t txStatus = Wire.endTransmission(false);
  if (txStatus != 0) {
    return 0xFFFF;
  }

  uint8_t requested = Wire.requestFrom((uint8_t)I2C_ADDRESS, (uint8_t)2);
  if (requested != 2 || Wire.available() < 2) {
    return 0xFFFF;
  }

  uint16_t msb = Wire.read();
  uint16_t lsb = Wire.read();
  return (msb << 8) | lsb;
}

void printINA226RawDebug() {
#if !POWER_NODE_ENABLE_DEBUG
  return;
#endif

  uint16_t reg_config  = readINA226Register16(0x00);
  uint16_t reg_shunt   = readINA226Register16(0x01);
  uint16_t reg_bus     = readINA226Register16(0x02);
  uint16_t reg_power   = readINA226Register16(0x03);
  uint16_t reg_current = readINA226Register16(0x04);
  uint16_t reg_calib   = readINA226Register16(0x05);

  Serial.print("RAW cfg=0x");   Serial.print(reg_config, HEX);
  Serial.print(" shunt=0x");    Serial.print(reg_shunt, HEX);
  Serial.print(" bus=0x");      Serial.print(reg_bus, HEX);
  Serial.print(" power=0x");    Serial.print(reg_power, HEX);
  Serial.print(" current=0x");  Serial.print(reg_current, HEX);
  Serial.print(" calib=0x");    Serial.println(reg_calib, HEX);
}


// -----------------------------------------------------------------------------
// Setup
// -----------------------------------------------------------------------------
void setup() {
  Serial.begin(115200);
  Serial.println("Booting power benchmark node...");
  Serial.print("Firmware version: ");
  Serial.println(IOT_FIRMWARE_VERSION);
  Serial.print("NODE_ID: ");
  Serial.println(NODE_ID);
  Serial.print("EXP_ID: ");
  Serial.println(EXP_ID);
  Serial.print("POWER_SAMPLE_INTERVAL_MS: ");
  Serial.println(POWER_SAMPLE_INTERVAL_MS);
  Serial.print("PERIODIC_INTERVAL_MS: ");
  Serial.println(PERIODIC_INTERVAL_MS);

  Wire.begin();

  connectWiFi();
  Serial.print("WiFi connected, IP: ");
  Serial.println(WiFi.localIP());

  connectMQTT();
  Serial.println("MQTT connected");

  if (!ina226.init()) {
    Serial.println("INA226 init failed");
  } else {
    Serial.println("INA226 initialized");
  }

  ina226.setResistorRange(SHUNT_RESISTOR_OHM, MAX_CURRENT_A);
  delay(200);
}

// -----------------------------------------------------------------------------
// Main loop
// -----------------------------------------------------------------------------
void loop() {
  if (!mqtt.connected()) {
    connectMQTT();
  }
  mqtt.loop();

  unsigned long now = millis();

  if (now - lastPowerMs >= POWER_SAMPLE_INTERVAL_MS) {
    lastPowerMs = now;
    publishPowerSample();
  }

  if (PERIODIC_INTERVAL_MS > 0 &&
      now - lastPublishMs >= PERIODIC_INTERVAL_MS) {
    lastPublishMs = now;
    publishTelemetryEvent("periodic");
  }
}
