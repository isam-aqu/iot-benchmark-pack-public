#ifndef INA231_WE_H
#define INA231_WE_H

#include <Arduino.h>
#include <Wire.h>

class INA231_WE {
public:
  explicit INA231_WE(uint8_t address, TwoWire* wire = &Wire);

  bool init();
  void setResistorRange(float shuntResistanceOhm, float maxCurrentA);

  float getBusVoltage_V();
  float getShuntVoltage_mV();
  float getCurrent_mA();
  float getBusPower();

private:
  static constexpr uint8_t REG_CONFIG = 0x00;
  static constexpr uint8_t REG_SHUNT_VOLTAGE = 0x01;
  static constexpr uint8_t REG_BUS_VOLTAGE = 0x02;
  static constexpr uint8_t REG_POWER = 0x03;
  static constexpr uint8_t REG_CURRENT = 0x04;
  static constexpr uint8_t REG_CALIBRATION = 0x05;

  // Continuous shunt + bus conversions with a sane default timing profile.
  // INA231 uses the same core measurement/calibration register map as INA226
  // for the paths used in this project.
  static constexpr uint16_t DEFAULT_CONFIG = 0x4127;

  bool writeRegister16(uint8_t reg, uint16_t value);
  bool readRegister16(uint8_t reg, uint16_t& value);
  int16_t readSignedRegister16(uint8_t reg);
  uint16_t readUnsignedRegister16(uint8_t reg);

  uint8_t address_;
  TwoWire* wire_;
  float shuntResistanceOhm_;
  float currentLsbA_;
};

#endif
