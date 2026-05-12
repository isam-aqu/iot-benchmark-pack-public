#include "INA231_WE.h"

namespace {
constexpr float kShuntVoltageLsbMv = 0.0025f;
constexpr float kBusVoltageLsbV = 0.00125f;
constexpr float kCalibrationFactor = 0.00512f;
constexpr float kPowerRegisterFactor = 25.0f;
}

INA231_WE::INA231_WE(uint8_t address, TwoWire* wire)
    : address_(address),
      wire_(wire),
      shuntResistanceOhm_(0.1f),
      currentLsbA_(1.0f / 1000.0f) {}

bool INA231_WE::init() {
  wire_->beginTransmission(address_);
  if (wire_->endTransmission() != 0) {
    return false;
  }

  return writeRegister16(REG_CONFIG, DEFAULT_CONFIG);
}

void INA231_WE::setResistorRange(float shuntResistanceOhm, float maxCurrentA) {
  if (shuntResistanceOhm <= 0.0f || maxCurrentA <= 0.0f) {
    return;
  }

  shuntResistanceOhm_ = shuntResistanceOhm;

  float desiredCurrentLsbA = maxCurrentA / 32768.0f;
  if (desiredCurrentLsbA <= 0.0f) {
    return;
  }

  uint32_t calibration =
      static_cast<uint32_t>(kCalibrationFactor /
                            (desiredCurrentLsbA * shuntResistanceOhm_));
  if (calibration == 0u) {
    calibration = 1u;
  } else if (calibration > 0xFFFFu) {
    calibration = 0xFFFFu;
  }

  currentLsbA_ =
      kCalibrationFactor / (static_cast<float>(calibration) * shuntResistanceOhm_);
  writeRegister16(REG_CALIBRATION, static_cast<uint16_t>(calibration));
}

float INA231_WE::getBusVoltage_V() {
  return static_cast<float>(readUnsignedRegister16(REG_BUS_VOLTAGE)) *
         kBusVoltageLsbV;
}

float INA231_WE::getShuntVoltage_mV() {
  return static_cast<float>(readSignedRegister16(REG_SHUNT_VOLTAGE)) *
         kShuntVoltageLsbMv;
}

float INA231_WE::getCurrent_mA() {
  return static_cast<float>(readSignedRegister16(REG_CURRENT)) * currentLsbA_ *
         1000.0f;
}

float INA231_WE::getBusPower() {
  float powerLsbW = kPowerRegisterFactor * currentLsbA_;
  return static_cast<float>(readUnsignedRegister16(REG_POWER)) * powerLsbW *
         1000.0f;
}

bool INA231_WE::writeRegister16(uint8_t reg, uint16_t value) {
  wire_->beginTransmission(address_);
  wire_->write(reg);
  wire_->write(static_cast<uint8_t>(value >> 8));
  wire_->write(static_cast<uint8_t>(value & 0xFFu));
  return wire_->endTransmission() == 0;
}

bool INA231_WE::readRegister16(uint8_t reg, uint16_t& value) {
  wire_->beginTransmission(address_);
  wire_->write(reg);
  if (wire_->endTransmission(false) != 0) {
    return false;
  }

  if (wire_->requestFrom(static_cast<int>(address_), 2) != 2) {
    return false;
  }

  value = static_cast<uint16_t>(wire_->read()) << 8;
  value |= static_cast<uint16_t>(wire_->read());
  return true;
}

int16_t INA231_WE::readSignedRegister16(uint8_t reg) {
  uint16_t value = 0;
  if (!readRegister16(reg, value)) {
    return 0;
  }
  return static_cast<int16_t>(value);
}

uint16_t INA231_WE::readUnsignedRegister16(uint8_t reg) {
  uint16_t value = 0;
  readRegister16(reg, value);
  return value;
}
