#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEAdvertising.h>
#include "../firmware_version.h"

const char* NODE_ID = "ble01";
const char* EXP_ID  = "W3_ble_auto";
const char EXP_CODE[5] = "W3BL";

const uint8_t NODE_NUM = 0x01;

// ===== W3 Trigger Configuration =====
const bool TRIGGER_MODE_AUTO = true;   // false = W1 (button), true = W3
const unsigned long BASE_INTERVAL_MS = 3000;
const long JITTER_MS = 250;
const bool USE_JITTER = true;

// ===== W3 Stop Conditions =====
const bool ENABLE_FIXED_DURATION = true;
const unsigned long EXPERIMENT_DURATION_MS = 360000;  // 6 min safety timeout

const bool ENABLE_FIXED_EVENT_COUNT = true;
const uint32_t TARGET_EVENT_COUNT = 100;

const int BUTTON_PIN = 18;
const int LED_PIN = 2;
const unsigned long debounceMs = 200;

BLEAdvertising* pAdvertising = nullptr;

uint32_t seqNo = 0;
uint32_t bootId = 0;
unsigned long experimentStartMs = 0;
bool experimentComplete = false;
unsigned long nextTriggerMs = 0;
unsigned long lastButtonPressMs = 0;

long getNextInterval() {
  if (!USE_JITTER) return BASE_INTERVAL_MS;
  long jitter = random(-JITTER_MS, JITTER_MS + 1);
  long interval = (long)BASE_INTERVAL_MS + jitter;
  return interval > 0 ? interval : 1;
}

void markExperimentComplete(const char* reason) {
  if (experimentComplete) return;

  experimentComplete = true;

  if (pAdvertising != nullptr) {
    pAdvertising->stop();
  }

  Serial.print("EXPERIMENT_COMPLETE");
  Serial.print(",exp="); Serial.print(EXP_ID);
  Serial.print(",boot_id="); Serial.print(bootId);
  Serial.print(",reason="); Serial.print(reason);
  Serial.print(",duration_ms="); Serial.print(millis() - experimentStartMs);
  Serial.print(",events="); Serial.println(seqNo);
}

void advertiseEvent(const char* triggerType) {
  if (experimentComplete) return;

  seqNo++;
  uint32_t tLocalUs = micros();

  uint8_t payload[16];
  payload[0] = 0x34;
  payload[1] = 0x12;
  payload[2] = 0x02;
  payload[3] = NODE_NUM;

  memcpy(&payload[4], EXP_CODE, 4);
  memcpy(&payload[8], &seqNo, 4);
  memcpy(&payload[12], &tLocalUs, 4);

  BLEAdvertisementData advData;
  String mfgData((char*)payload, sizeof(payload));
  advData.setManufacturerData(mfgData);

  pAdvertising->stop();
  pAdvertising->setAdvertisementData(advData);
  pAdvertising->start();

  delay(500);
  pAdvertising->stop();

  Serial.print("Advertised seq=");
  Serial.print(seqNo);
  Serial.print(" exp=");
  Serial.print(EXP_ID);
  Serial.print(" boot_id=");
  Serial.print(bootId);
  Serial.print(" trigger=");
  Serial.print(triggerType);
  Serial.print(" t_local_us=");
  Serial.println(tLocalUs);

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
  delay(500);

  Serial.println("Booting W3 BLE benchmark node...");
  Serial.print("Firmware version: ");
  Serial.println(IOT_FIRMWARE_VERSION);
  Serial.print("NODE_ID: ");
  Serial.println(NODE_ID);
  Serial.print("EXP_ID: ");
  Serial.println(EXP_ID);
  Serial.print("EXP_CODE: ");
  Serial.println(EXP_CODE);
  Serial.print("BOOT_ID: ");
  Serial.println(bootId);
  Serial.print("BASE_INTERVAL_MS: ");
  Serial.println(BASE_INTERVAL_MS);
  Serial.print("JITTER_MS: ");
  Serial.println(JITTER_MS);
  Serial.print("USE_JITTER: ");
  Serial.println(USE_JITTER ? "true" : "false");
  Serial.print("ENABLE_FIXED_DURATION: ");
  Serial.println(ENABLE_FIXED_DURATION ? "true" : "false");
  Serial.print("EXPERIMENT_DURATION_MS: ");
  Serial.println(EXPERIMENT_DURATION_MS);
  Serial.print("ENABLE_FIXED_EVENT_COUNT: ");
  Serial.println(ENABLE_FIXED_EVENT_COUNT ? "true" : "false");
  Serial.print("TARGET_EVENT_COUNT: ");
  Serial.println(TARGET_EVENT_COUNT);

  BLEDevice::init("BLE_BENCH_ble01");
  pAdvertising = BLEDevice::getAdvertising();

  pAdvertising->setScanResponse(false);
  pAdvertising->setMinPreferred(0x06);
  pAdvertising->setMinPreferred(0x12);

  Serial.println("BLE advertising ready.");

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

  static int lastButtonState = HIGH;
  int currentButtonState = digitalRead(BUTTON_PIN);

  if (!TRIGGER_MODE_AUTO && lastButtonState == HIGH && currentButtonState == LOW) {
    unsigned long nowMs = millis();
    if (nowMs - lastButtonPressMs >= debounceMs) {
      lastButtonPressMs = nowMs;

      digitalWrite(LED_PIN, HIGH);
      advertiseEvent("button");
      delay(50);
      digitalWrite(LED_PIN, LOW);
    }
  }
  lastButtonState = currentButtonState;

  if (TRIGGER_MODE_AUTO && (long)(millis() - nextTriggerMs) >= 0) {
    unsigned long scheduledTriggerMs = nextTriggerMs;
    long interval = getNextInterval();
    nextTriggerMs = scheduledTriggerMs + interval;

    digitalWrite(LED_PIN, HIGH);
    advertiseEvent("auto");
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
