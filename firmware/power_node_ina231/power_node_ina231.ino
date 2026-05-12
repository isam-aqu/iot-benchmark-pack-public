#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <Preferences.h>
#include <Wire.h>
#include "INA231_WE.h"

#ifdef __has_include
#if __has_include("../secrets.h")
#include "../secrets.h"
#endif
#endif
#include "../firmware_version.h"
#include "../secrets.example.h"

#define I2C_ADDRESS 0x40

// Set to 1 to enable verbose serial diagnostics for sensor samples, I2C scan,
// and raw register dumps while troubleshooting.
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
const char* DEFAULT_EXP_ID  = "W2_wifi_periodic_4s_quiet_telemetry_v2";

// Set to 0 for connected-idle mode (R501)
// Set to 1000 / 5000 / 10000 for R502 / R503 / R504
const unsigned long DEFAULT_PERIODIC_INTERVAL_MS = 4000;

// Enable telemetry/event MQTT publishing.
const bool DEFAULT_ENABLE_MQTT_TELEMETRY = true;

// Keep power samples off MQTT so telemetry traffic remains the workload under study.
const bool ENABLE_MQTT_POWER_REPORTING = false;

// Optional fixed-duration run control for reproducible experiments.
const bool ENABLE_FIXED_DURATION = true;
const unsigned long DEFAULT_EXPERIMENT_DURATION_MS = 300000; // 5 minutes

// Power sample interval (serial output only in W2 v2 design)
const unsigned long DEFAULT_POWER_SAMPLE_INTERVAL_MS = 100;

String expId = DEFAULT_EXP_ID;
unsigned long periodicIntervalMs = DEFAULT_PERIODIC_INTERVAL_MS;
bool enableMqttTelemetry = DEFAULT_ENABLE_MQTT_TELEMETRY;
unsigned long experimentDurationMs = DEFAULT_EXPERIMENT_DURATION_MS;
unsigned long powerSampleIntervalMs = DEFAULT_POWER_SAMPLE_INTERVAL_MS;

// Calibration parameters
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
INA231_WE ina231(I2C_ADDRESS);
Preferences preferences;

uint32_t seqNo = 0;
uint32_t powerSampleSeq = 0;
uint32_t lastTelemetrySeq = 0;
unsigned long lastTelemetryLocalUs = 0;
unsigned long lastPowerMs = 0;
unsigned long lastPublishMs = 0;
unsigned long experimentStartMs = 0;
bool experimentComplete = false;
String serialCommandBuffer;

void connectMQTT();

// -----------------------------------------------------------------------------
// Runtime W2 configuration
// -----------------------------------------------------------------------------
void printConfigState(const char* prefix) {
  Serial.print(prefix);
  Serial.print(",exp="); Serial.print(expId);
  Serial.print(",interval_ms="); Serial.print(periodicIntervalMs);
  Serial.print(",telemetry="); Serial.print(enableMqttTelemetry ? 1 : 0);
  Serial.print(",duration_ms="); Serial.print(experimentDurationMs);
  Serial.print(",power_ms="); Serial.println(powerSampleIntervalMs);
}

void loadRuntimeConfig() {
  preferences.begin("w2cfg", true);
  expId = preferences.getString("exp_id", DEFAULT_EXP_ID);
  periodicIntervalMs = preferences.getULong("interval_ms", DEFAULT_PERIODIC_INTERVAL_MS);
  enableMqttTelemetry = preferences.getBool("telemetry", DEFAULT_ENABLE_MQTT_TELEMETRY);
  experimentDurationMs = preferences.getULong("duration_ms", DEFAULT_EXPERIMENT_DURATION_MS);
  powerSampleIntervalMs = preferences.getULong("power_ms", DEFAULT_POWER_SAMPLE_INTERVAL_MS);
  preferences.end();
}

void saveRuntimeConfig() {
  preferences.begin("w2cfg", false);
  preferences.putString("exp_id", expId);
  preferences.putULong("interval_ms", periodicIntervalMs);
  preferences.putBool("telemetry", enableMqttTelemetry);
  preferences.putULong("duration_ms", experimentDurationMs);
  preferences.putULong("power_ms", powerSampleIntervalMs);
  preferences.end();
}

void clearRuntimeConfig() {
  preferences.begin("w2cfg", false);
  preferences.clear();
  preferences.end();
  expId = DEFAULT_EXP_ID;
  periodicIntervalMs = DEFAULT_PERIODIC_INTERVAL_MS;
  enableMqttTelemetry = DEFAULT_ENABLE_MQTT_TELEMETRY;
  experimentDurationMs = DEFAULT_EXPERIMENT_DURATION_MS;
  powerSampleIntervalMs = DEFAULT_POWER_SAMPLE_INTERVAL_MS;
}

bool parseBoolValue(const String& value, bool* out) {
  String normalized = value;
  normalized.toLowerCase();

  if (normalized == "1" || normalized == "true" || normalized == "on" ||
      normalized == "yes" || normalized == "enabled" ||
      normalized == "telemetry") {
    *out = true;
    return true;
  }

  if (normalized == "0" || normalized == "false" || normalized == "off" ||
      normalized == "no" || normalized == "disabled" ||
      normalized == "control" || normalized == "ctrl") {
    *out = false;
    return true;
  }

  return false;
}

bool parseUnsignedLongValue(const String& value, unsigned long* out) {
  if (value.length() == 0) {
    return false;
  }

  unsigned long parsed = 0;
  for (size_t i = 0; i < value.length(); ++i) {
    char ch = value.charAt(i);
    if (ch < '0' || ch > '9') {
      return false;
    }
    parsed = parsed * 10UL + (unsigned long)(ch - '0');
  }

  *out = parsed;
  return true;
}

void resetExperimentState() {
  seqNo = 0;
  powerSampleSeq = 0;
  lastTelemetrySeq = 0;
  lastTelemetryLocalUs = 0;
  lastPowerMs = 0;
  lastPublishMs = 0;
  experimentStartMs = millis();
  experimentComplete = false;
}

void stopExperimentWithoutCompleteLine() {
  experimentComplete = true;
  if (mqtt.connected()) {
    mqtt.disconnect();
  }
}

void handleConfigCommand(String command) {
  command.trim();
  if (command.length() == 0) {
    return;
  }

  String commandUpper = command;
  commandUpper.toUpperCase();
  int syncPos = -1;
  const char* knownCommands[] = {"CONFIG", "SHOW_CONFIG", "CLEAR_CONFIG", "START", "STOP"};
  for (size_t i = 0; i < sizeof(knownCommands) / sizeof(knownCommands[0]); ++i) {
    int pos = commandUpper.indexOf(knownCommands[i]);
    if (pos >= 0 && (syncPos < 0 || pos < syncPos)) {
      syncPos = pos;
    }
  }
  if (syncPos > 0) {
    command = command.substring(syncPos);
    command.trim();
  }

  int firstSpace = command.indexOf(' ');
  String verb = firstSpace < 0 ? command : command.substring(0, firstSpace);
  String rest = firstSpace < 0 ? "" : command.substring(firstSpace + 1);
  verb.toUpperCase();

  if (verb == "SHOW_CONFIG") {
    printConfigState("CONFIG_STATE");
    return;
  }

  if (verb == "CLEAR_CONFIG") {
    clearRuntimeConfig();
    stopExperimentWithoutCompleteLine();
    printConfigState("CONFIG_CLEARED");
    return;
  }

  if (verb == "STOP") {
    stopExperimentWithoutCompleteLine();
    Serial.println("STOP_OK");
    return;
  }

  if (verb == "START") {
    if (!mqtt.connected()) {
      connectMQTT();
    }
    resetExperimentState();
    printConfigState("START_OK");
    return;
  }

  if (verb != "CONFIG") {
    Serial.print("CONFIG_ERROR,reason=unknown_command,command=");
    Serial.println(verb);
    return;
  }

  String nextExpId = expId;
  unsigned long nextIntervalMs = periodicIntervalMs;
  bool nextTelemetry = enableMqttTelemetry;
  unsigned long nextDurationMs = experimentDurationMs;
  unsigned long nextPowerMs = powerSampleIntervalMs;

  while (rest.length() > 0) {
    rest.trim();
    if (rest.length() == 0) {
      break;
    }

    int tokenEnd = rest.indexOf(' ');
    String token = tokenEnd < 0 ? rest : rest.substring(0, tokenEnd);
    rest = tokenEnd < 0 ? "" : rest.substring(tokenEnd + 1);

    int equals = token.indexOf('=');
    if (equals <= 0) {
      Serial.print("CONFIG_ERROR,reason=bad_token,token=");
      Serial.println(token);
      return;
    }

    String key = token.substring(0, equals);
    String value = token.substring(equals + 1);
    key.toLowerCase();

    if (key == "exp" || key == "exp_id" || key == "run_id") {
      if (value.length() == 0 || value.length() > 96) {
        Serial.println("CONFIG_ERROR,reason=bad_exp");
        return;
      }
      nextExpId = value;
    } else if (key == "interval" || key == "interval_ms") {
      if (!parseUnsignedLongValue(value, &nextIntervalMs) ||
          nextIntervalMs > 3600000UL) {
        Serial.println("CONFIG_ERROR,reason=bad_interval_ms");
        return;
      }
    } else if (key == "telemetry" || key == "mqtt_telemetry" ||
               key == "mode") {
      if (!parseBoolValue(value, &nextTelemetry)) {
        Serial.println("CONFIG_ERROR,reason=bad_telemetry");
        return;
      }
    } else if (key == "duration_ms") {
      if (!parseUnsignedLongValue(value, &nextDurationMs) ||
          nextDurationMs > 86400000UL) {
        Serial.println("CONFIG_ERROR,reason=bad_duration_ms");
        return;
      }
    } else if (key == "duration_sec") {
      unsigned long durationSec = 0;
      if (!parseUnsignedLongValue(value, &durationSec) ||
          durationSec > 86400UL) {
        Serial.println("CONFIG_ERROR,reason=bad_duration_sec");
        return;
      }
      nextDurationMs = durationSec * 1000UL;
    } else if (key == "power_ms" || key == "power_sample_ms") {
      if (!parseUnsignedLongValue(value, &nextPowerMs) ||
          nextPowerMs < 10UL || nextPowerMs > 60000UL) {
        Serial.println("CONFIG_ERROR,reason=bad_power_ms");
        return;
      }
    } else {
      Serial.print("CONFIG_ERROR,reason=unknown_key,key=");
      Serial.println(key);
      return;
    }
  }

  expId = nextExpId;
  periodicIntervalMs = nextIntervalMs;
  enableMqttTelemetry = nextTelemetry;
  experimentDurationMs = nextDurationMs;
  powerSampleIntervalMs = nextPowerMs;
  saveRuntimeConfig();
  stopExperimentWithoutCompleteLine();
  printConfigState("CONFIG_OK");
}

void pollSerialConfig() {
  while (Serial.available() > 0) {
    char ch = (char)Serial.read();
    if (ch == '\n' || ch == '\r') {
      if (serialCommandBuffer.length() > 0) {
        handleConfigCommand(serialCommandBuffer);
        serialCommandBuffer = "";
      }
    } else if (serialCommandBuffer.length() < 256) {
      serialCommandBuffer += ch;
    } else {
      serialCommandBuffer = "";
      Serial.println("CONFIG_ERROR,reason=command_too_long");
    }
  }
}

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
    pollSerialConfig();
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
      pollSerialConfig();
      delay(1000);
    }
  }
}

uint16_t readINA231Register16(uint8_t reg) {
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

void scanI2CBus() {
#if !POWER_NODE_ENABLE_DEBUG
  return;
#endif

  uint8_t foundCount = 0;
  bool expectedAddressFound = false;

  Serial.println("Scanning I2C bus...");

  for (uint8_t address = 0x03; address <= 0x77; ++address) {
    Wire.beginTransmission(address);
    uint8_t error = Wire.endTransmission();

    if (error == 0) {
      foundCount++;

      Serial.print("I2C device found at 0x");
      if (address < 0x10) {
        Serial.print('0');
      }
      Serial.println(address, HEX);

      if (address == I2C_ADDRESS) {
        expectedAddressFound = true;
      }
    }
  }

  if (foundCount == 0) {
    Serial.println("No I2C devices found");
  }

  if (!expectedAddressFound) {
    Serial.print("Expected INA231 address 0x");
    if (I2C_ADDRESS < 0x10) {
      Serial.print('0');
    }
    Serial.print(I2C_ADDRESS, HEX);
    Serial.println(" was not detected");
  }
}

void printINA231RawDebug() {
#if !POWER_NODE_ENABLE_DEBUG
  return;
#endif

  uint16_t reg_config  = readINA231Register16(0x00);
  uint16_t reg_shunt   = readINA231Register16(0x01);
  uint16_t reg_bus     = readINA231Register16(0x02);
  uint16_t reg_power   = readINA231Register16(0x03);
  uint16_t reg_current = readINA231Register16(0x04);
  uint16_t reg_calib   = readINA231Register16(0x05);

  Serial.print("RAW cfg=0x");   Serial.print(reg_config, HEX);
  Serial.print(" shunt=0x");    Serial.print(reg_shunt, HEX);
  Serial.print(" bus=0x");      Serial.print(reg_bus, HEX);
  Serial.print(" power=0x");    Serial.print(reg_power, HEX);
  Serial.print(" current=0x");  Serial.print(reg_current, HEX);
  Serial.print(" calib=0x");    Serial.println(reg_calib, HEX);
}

// -----------------------------------------------------------------------------
// Publish helpers
// -----------------------------------------------------------------------------
void publishPowerSample() {
  float busV = ina231.getBusVoltage_V();
  float currentmA = ina231.getCurrent_mA();
  float powermW = ina231.getBusPower();
  float shuntmV = ina231.getShuntVoltage_mV();
  unsigned long sampleTimeUs = micros();
  long dtSinceEventUs = (lastTelemetryLocalUs == 0)
      ? -1L
      : (long)(sampleTimeUs - lastTelemetryLocalUs);
  powerSampleSeq++;

  printPowerSampleDebug(busV, shuntmV, currentmA, powermW);

  // Serial-only power stream for W2 v2: machine-friendly and event-alignable
  Serial.print("POWER_SAMPLE");
  Serial.print(",power_seq="); Serial.print(powerSampleSeq);
  Serial.print(",exp="); Serial.print(expId);
  Serial.print(",t_local_us="); Serial.print(sampleTimeUs);
  Serial.print(",bus_v="); Serial.print(busV, 6);
  Serial.print(",shunt_mV="); Serial.print(shuntmV, 6);
  Serial.print(",current_mA="); Serial.print(currentmA, 6);
  Serial.print(",power_mW="); Serial.print(powermW, 6);
  Serial.print(",wifi_rssi="); Serial.print(WiFi.RSSI());
  Serial.print(",last_event_seq="); Serial.print(lastTelemetrySeq);
  Serial.print(",last_event_t_local_us="); Serial.print(lastTelemetryLocalUs);
  Serial.print(",dt_since_event_us="); Serial.println(dtSinceEventUs);

  if (ENABLE_MQTT_POWER_REPORTING) {
    StaticJsonDocument<256> doc;
    doc["type"] = "power";
    doc["power_seq"] = powerSampleSeq;
    doc["node"] = NODE_ID;
    doc["protocol"] = "wifi";
    doc["exp"] = expId;
    doc["t_local_us"] = sampleTimeUs;
    doc["bus_v"] = busV;
    doc["current_mA"] = currentmA;
    doc["power_mW"] = powermW;
    doc["wifi_rssi"] = WiFi.RSSI();
    doc["last_event_seq"] = lastTelemetrySeq;
    doc["last_event_t_local_us"] = lastTelemetryLocalUs;
    doc["dt_since_event_us"] = dtSinceEventUs;
    doc["fw_version"] = IOT_FIRMWARE_VERSION;

    char payload[320];
    size_t n = serializeJson(doc, payload);
    mqtt.publish(topicPower.c_str(), payload, n);
  }
}

void publishTelemetryEvent(const char* triggerType) {
  seqNo++;
  unsigned long eventTimeUs = micros();
  lastTelemetrySeq = seqNo;
  lastTelemetryLocalUs = eventTimeUs;

  // Serial mirror for debugging and cross-checking against MQTT event logs
  Serial.print("EVENT");
  Serial.print(",seq="); Serial.print(seqNo);
  Serial.print(",exp="); Serial.print(expId);
  Serial.print(",trigger="); Serial.print(triggerType);
  Serial.print(",t_local_us="); Serial.print(eventTimeUs);
  Serial.print(",wifi_rssi="); Serial.println(WiFi.RSSI());

  if (enableMqttTelemetry) {
    StaticJsonDocument<256> doc;
    doc["type"] = "event";
    doc["seq"] = seqNo;
    doc["node"] = NODE_ID;
    doc["protocol"] = "wifi";
    doc["exp"] = expId;
    doc["trigger"] = triggerType;
    doc["t_local_us"] = eventTimeUs;
    doc["wifi_rssi"] = WiFi.RSSI();
    doc["fw_version"] = IOT_FIRMWARE_VERSION;

    char payload[256];
    size_t n = serializeJson(doc, payload);
    mqtt.publish(topicEvent.c_str(), payload, n);
  }
}

// -----------------------------------------------------------------------------
// Setup
// -----------------------------------------------------------------------------
void setup() {
  Serial.begin(115200);
  loadRuntimeConfig();
  Serial.println("Booting power benchmark node (INA231)...");
  Serial.print("Firmware version: ");
  Serial.println(IOT_FIRMWARE_VERSION);
  Serial.print("NODE_ID: ");
  Serial.println(NODE_ID);
  Serial.print("EXP_ID: ");
  Serial.println(expId);
  Serial.print("POWER_SAMPLE_INTERVAL_MS: ");
  Serial.println(powerSampleIntervalMs);
  Serial.print("PERIODIC_INTERVAL_MS: ");
  Serial.println(periodicIntervalMs);
  Serial.print("ENABLE_MQTT_TELEMETRY: ");
  Serial.println(enableMqttTelemetry ? "true" : "false");
  Serial.print("ENABLE_MQTT_POWER_REPORTING: ");
  Serial.println(ENABLE_MQTT_POWER_REPORTING ? "true" : "false");
  Serial.print("ENABLE_FIXED_DURATION: ");
  Serial.println(ENABLE_FIXED_DURATION ? "true" : "false");
  Serial.print("EXPERIMENT_DURATION_MS: ");
  Serial.println(experimentDurationMs);
  printConfigState("CONFIG_STATE");

  Wire.begin();
  scanI2CBus();

  connectWiFi();
  Serial.print("WiFi connected, IP: ");
  Serial.println(WiFi.localIP());

  connectMQTT();
  Serial.println("MQTT connected");

  if (!ina231.init()) {
    Serial.println("INA231 init failed");
  } else {
    Serial.println("INA231 initialized");
  }

  ina231.setResistorRange(SHUNT_RESISTOR_OHM, MAX_CURRENT_A);
  delay(200);

  experimentStartMs = millis();
}

// -----------------------------------------------------------------------------
// Main loop
// -----------------------------------------------------------------------------
void loop() {
  pollSerialConfig();

  if (ENABLE_FIXED_DURATION && experimentDurationMs > 0 && !experimentComplete) {
    if (millis() - experimentStartMs >= experimentDurationMs) {
      experimentComplete = true;

      Serial.print("EXPERIMENT_COMPLETE");
      Serial.print(",exp="); Serial.print(expId);
      Serial.print(",duration_ms="); Serial.println(experimentDurationMs);

      if (mqtt.connected()) {
        mqtt.disconnect();
      }
    }
  }

  if (experimentComplete) {
    delay(1000);
    return;
  }

  if (!mqtt.connected()) {
    connectMQTT();
  }
  mqtt.loop();

  unsigned long now = millis();

  if (now - lastPowerMs >= powerSampleIntervalMs) {
    lastPowerMs = now;
    publishPowerSample();
  }

  if (periodicIntervalMs > 0 &&
      now - lastPublishMs >= periodicIntervalMs) {
    lastPublishMs = now;
    publishTelemetryEvent("periodic");
  }
}
