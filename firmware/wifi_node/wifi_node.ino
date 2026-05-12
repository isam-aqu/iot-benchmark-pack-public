#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

#ifdef __has_include
#if __has_include("../secrets.h")
#include "../secrets.h"
#endif
#endif
#include "../firmware_version.h"
#include "../secrets.example.h"

const char* WIFI_SSID = IOT_WIFI_SSID;
const char* WIFI_PASS = IOT_WIFI_PASS;
const char* MQTT_HOST = IOT_MQTT_HOST;
const int   MQTT_PORT = IOT_MQTT_PORT;
const char* MQTT_USERNAME = IOT_MQTT_USERNAME;
const char* MQTT_PASSWORD = IOT_MQTT_PASSWORD;

const char* NODE_ID = "wifi01";
const char* EXP_ID  = "W3_wifi_auto_heavy";

// ===== W3 Trigger Configuration =====
#define TRIGGER_MODE_AUTO true    // false = W1 (button), true = W3
#define BASE_INTERVAL_MS 3000     // nominal interval
#define JITTER_MS 250             // ± jitter
#define USE_JITTER true

// ===== W3 Stop Conditions =====
const bool ENABLE_FIXED_DURATION = true;
const unsigned long EXPERIMENT_DURATION_MS = 360000;  // 6 min safety timeout

const bool ENABLE_FIXED_EVENT_COUNT = true;
const uint32_t TARGET_EVENT_COUNT = 100;

unsigned long experimentStartMs = 0;
bool experimentComplete = false;

unsigned long nextTriggerMs = 0;

const int BUTTON_PIN = 18;
const int LED_PIN    = 2;

WiFiClient espClient;
PubSubClient mqtt(espClient);

volatile bool ackReceived = false;
volatile uint32_t ackSeq = 0;
volatile uint32_t ackTLocalUs = 0;
volatile uint32_t ackPendingSeq = 0;

uint32_t seqNo = 0;
uint32_t bootId = 0;

String topicEvent = String("iotbench/wifi/") + NODE_ID + "/event";
String topicAck   = String("iotbench/wifi/") + NODE_ID + "/ack";

long getNextInterval() {
  if (!USE_JITTER) return BASE_INTERVAL_MS;
  long jitter = random(-JITTER_MS, JITTER_MS + 1);
  return BASE_INTERVAL_MS + jitter;
}

void markExperimentComplete(const char* reason) {
  if (experimentComplete) return;

  experimentComplete = true;

  Serial.print("EXPERIMENT_COMPLETE");
  Serial.print(",exp="); Serial.print(EXP_ID);
  Serial.print(",boot_id="); Serial.print(bootId);
  Serial.print(",reason="); Serial.print(reason);
  Serial.print(",duration_ms="); Serial.print(millis() - experimentStartMs);
  Serial.print(",events="); Serial.println(seqNo);

  StaticJsonDocument<224> doc;
  doc["type"] = "experiment_complete";
  doc["node"] = NODE_ID;
  doc["protocol"] = "wifi";
  doc["exp"] = EXP_ID;
  doc["boot_id"] = bootId;
  doc["reason"] = reason;
  doc["duration_ms"] = millis() - experimentStartMs;
  doc["events"] = seqNo;
  doc["fw_version"] = IOT_FIRMWARE_VERSION;

  char payload[224];
  size_t n = serializeJson(doc, payload, sizeof(payload));

  if (!mqtt.connected()) {
    Serial.println("MQTT disconnected before completion publish; attempting reconnect...");
    if (!connectMQTTOnce()) {
      Serial.println("MQTT reconnect failed; completion event not sent");
    }
  }

  if (mqtt.connected()) {
    bool published = mqtt.publish(topicEvent.c_str(), payload, n);
    Serial.print("COMPLETION_PUBLISH=");
    Serial.println(published ? "ok" : "failed");
    mqtt.loop();
    delay(200);
  }

  if (mqtt.connected()) {
    mqtt.disconnect();
  }
}

void mqttCallback(char* topic, byte* payload, unsigned int length) {
  StaticJsonDocument<256> doc;
  DeserializationError err = deserializeJson(doc, payload, length);
  if (err) return;

  const char* msgType = doc["type"] | "";
  if (strcmp(msgType, "ack") != 0) return;

  const char* node = doc["node"] | "";
  if (strcmp(node, NODE_ID) != 0) return;

  const char* exp = doc["exp"] | "";
  if (strcmp(exp, EXP_ID) != 0) return;

  if (!doc.containsKey("boot_id")) return;
  uint32_t incomingBootId = doc["boot_id"].as<uint32_t>();
  if (incomingBootId != bootId) return;

  uint32_t incomingSeq = doc["seq"].as<uint32_t>();
  if (incomingSeq == 0 || incomingSeq != ackPendingSeq) return;
  if (ackReceived) return;

  ackSeq = incomingSeq;
  ackTLocalUs = micros();
  ackReceived = true;
}

void connectWiFi() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
  }
}

bool connectMQTTOnce() {
  mqtt.setServer(MQTT_HOST, MQTT_PORT);
  mqtt.setCallback(mqttCallback);

  String clientId = String("esp32-") + NODE_ID;
  bool connected = false;

  if (MQTT_USERNAME[0] != '\0') {
    connected = mqtt.connect(clientId.c_str(), MQTT_USERNAME, MQTT_PASSWORD);
  } else {
    connected = mqtt.connect(clientId.c_str());
  }

  if (connected) {
    mqtt.subscribe(topicAck.c_str());
    return true;
  }

  Serial.print("MQTT connect failed, state=");
  Serial.println(mqtt.state());
  return false;
}

void connectMQTT() {
  while (!connectMQTTOnce()) {
    delay(1000);
  }
}

void publishEvent(const char* triggerType) {
  seqNo++;
  uint32_t t0 = micros();
  ackReceived = false;
  ackSeq = 0;
  ackTLocalUs = 0;
  ackPendingSeq = seqNo;

  StaticJsonDocument<320> doc;
  doc["type"] = "event";
  doc["node"] = NODE_ID;
  doc["protocol"] = "wifi";
  doc["exp"] = EXP_ID;
  doc["boot_id"] = bootId;
  doc["seq"] = seqNo;
  doc["trigger"] = triggerType;
  doc["t_local_us"] = t0;
  doc["wifi_rssi"] = WiFi.RSSI();
  doc["fw_version"] = IOT_FIRMWARE_VERSION;

  char payload[320];
  size_t n = serializeJson(doc, payload, sizeof(payload));
  mqtt.publish(topicEvent.c_str(), payload, n);

  uint32_t startWait = millis();
  while (!ackReceived && (millis() - startWait < 2000)) {
    mqtt.loop();
    delay(1);
  }

  Serial.print("EVENT");
  Serial.print(",seq="); Serial.print(seqNo);
  Serial.print(",exp="); Serial.print(EXP_ID);
  Serial.print(",boot_id="); Serial.print(bootId);
  Serial.print(",trigger="); Serial.print(triggerType);
  Serial.print(",t_local_us="); Serial.print(t0);
  Serial.print(",wifi_rssi="); Serial.println(WiFi.RSSI());

  if (ackReceived && ackSeq == seqNo) {
    uint32_t rtt = ackTLocalUs - t0;

    StaticJsonDocument<224> rttDoc;
    rttDoc["type"] = "rtt";
    rttDoc["node"] = NODE_ID;
    rttDoc["protocol"] = "wifi";
    rttDoc["exp"] = EXP_ID;
    rttDoc["boot_id"] = bootId;
    rttDoc["seq"] = seqNo;
    rttDoc["rtt_us"] = rtt;
    rttDoc["fw_version"] = IOT_FIRMWARE_VERSION;

    char rttPayload[224];
    size_t rn = serializeJson(rttDoc, rttPayload, sizeof(rttPayload));
    mqtt.publish((String("iotbench/wifi/") + NODE_ID + "/rtt").c_str(), rttPayload, rn);

    Serial.print("RTT");
    Serial.print(",seq="); Serial.print(seqNo);
    Serial.print(",boot_id="); Serial.print(bootId);
    Serial.print(",rtt_us="); Serial.println(rtt);
  } else {
    Serial.print("ACK_TIMEOUT");
    Serial.print(",seq="); Serial.print(seqNo);
    Serial.print(",boot_id="); Serial.println(bootId);
  }

  if (ENABLE_FIXED_EVENT_COUNT && seqNo >= TARGET_EVENT_COUNT) {
    markExperimentComplete("target_event_count");
  }
}

void setup() {
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);

  Serial.begin(115200);
  bootId = esp_random() & 0x7fffffffUL;
  if (bootId == 0) {
    bootId = 1;
  }
  randomSeed(bootId);

  Serial.println("Booting W3 Wi-Fi latency node...");
  Serial.print("Firmware version: "); Serial.println(IOT_FIRMWARE_VERSION);
  Serial.print("NODE_ID: "); Serial.println(NODE_ID);
  Serial.print("EXP_ID: "); Serial.println(EXP_ID);
  Serial.print("BOOT_ID: "); Serial.println(bootId);
  Serial.print("BASE_INTERVAL_MS: "); Serial.println(BASE_INTERVAL_MS);
  Serial.print("JITTER_MS: "); Serial.println(JITTER_MS);
  Serial.print("USE_JITTER: "); Serial.println(USE_JITTER ? "true" : "false");
  Serial.print("ENABLE_FIXED_DURATION: "); Serial.println(ENABLE_FIXED_DURATION ? "true" : "false");
  Serial.print("EXPERIMENT_DURATION_MS: "); Serial.println(EXPERIMENT_DURATION_MS);
  Serial.print("ENABLE_FIXED_EVENT_COUNT: "); Serial.println(ENABLE_FIXED_EVENT_COUNT ? "true" : "false");
  Serial.print("TARGET_EVENT_COUNT: "); Serial.println(TARGET_EVENT_COUNT);

  connectWiFi();
  Serial.print("WiFi connected, IP: ");
  Serial.println(WiFi.localIP());

  connectMQTT();
  Serial.println("MQTT connected");

  experimentStartMs = millis();

  if (TRIGGER_MODE_AUTO) {
    nextTriggerMs = millis() + getNextInterval();
  }
}

void loop() {
  if (experimentComplete) {
    delay(1000);
    return;
  }

  if (ENABLE_FIXED_DURATION &&
      millis() - experimentStartMs >= EXPERIMENT_DURATION_MS) {
    markExperimentComplete("duration_timeout");
    return;
  }

  if (!mqtt.connected()) {
    connectMQTT();
  }
  mqtt.loop();

  static int lastButton = HIGH;
  int currentButton = digitalRead(BUTTON_PIN);

  if (!TRIGGER_MODE_AUTO && lastButton == HIGH && currentButton == LOW) {
    digitalWrite(LED_PIN, HIGH);
    publishEvent("button");
    delay(150);
    digitalWrite(LED_PIN, LOW);
  }
  lastButton = currentButton;

  if (TRIGGER_MODE_AUTO && (long)(millis() - nextTriggerMs) >= 0) {
    unsigned long scheduledTriggerMs = nextTriggerMs;
    long interval = getNextInterval();
    nextTriggerMs = scheduledTriggerMs + interval;

    digitalWrite(LED_PIN, HIGH);
    publishEvent("auto");
    digitalWrite(LED_PIN, LOW);

    if (!experimentComplete) {
      if ((long)(millis() - nextTriggerMs) >= 0) {
        long recoveryInterval = getNextInterval();
        nextTriggerMs = millis() + recoveryInterval;

        Serial.print("SCHEDULER_OVERRUN");
        Serial.print(",seq="); Serial.print(seqNo);
        Serial.print(",recovery_interval_ms="); Serial.println(recoveryInterval);
      }

      Serial.print("NEXT_INTERVAL");
      Serial.print(",interval_ms="); Serial.println(interval);
    }
  }
}
