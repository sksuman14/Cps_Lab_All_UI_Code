# 4G_DataLogger_All_UI_Code

This repository contains experiments, firmware samples, and UI code for sensor integration with the 4G Data Logger development board. Each folder includes code for interfacing different sensors, optimized for real-time data display on serial monitor software. The examples demonstrate how to interface, acquire data, and process readings from each component.

## Table of Contents

- [Bme680_UI](#bme680_ui)
- [Hall_Effect_UI](#hall_effect_ui)
- [IR_UI](#ir_ui)
- [Lis3dh_UI](#lis3dh_ui)
- [Rain_Gauge_UI](#rain_gauge_ui)
- [Sht40_UI](#sht40_ui)
- [Sts30_UI](#sts30_ui)
- [Stts751_UI](#stts751_ui)
- [Tlv493D](#tlv493d)
- [TofVl53Lox_UI](#tofvl53lox_ui)
- [UvLtr390_UI](#uvltr390_ui)
- [Veml7700_UI](#veml7700_ui)
- [Weather_Shield_UI](#weather_shield_ui)
- [Wind_Sensor_UI](#wind_sensor_ui)

***

## Bme680_UI
A sample application to measure temperature, humidity, and pressure data from the BME680 sensor. The results are displayed for visualization on serial terminal software.

## Hall_Effect_UI
Code for detecting magnetic field changes using a Hall Effect sensor. Designed for real-time event detection and data capture on serial terminal software.

## IR_UI
Integrates IR sensors for proximity or object detection. The module continuously monitors and logs sensor readings on serial terminal software.

## Lis3dh_UI
Firmware for interfacing the LIS3DH accelerometer sensor. It periodically collects three-axis acceleration data for motion and vibration monitoring on serial terminal software.

## Rain_Gauge_UI
Reads data from a rain gauge sensor, converting the analog signal to a digital measurement shown on serial terminal software.

## Sht40_UI
Measures temperature and humidity using the SHT40 sensor. The sensor provides readings for environmental analysis on serial terminal software

## Sts30_UI
Sample code for temperature measurement with the STS30 sensor, supporting fast and accurate digital readout on serial terminal software.

## Stts751_UI
Uses the STTS751 sensor to acquire high precision temperature data on serial terminal software.

## Tlv493D
Magnetometer module code for detecting magnetic field strength and direction using the TLV493D sensor, displayed on serial terminal software.

## TofVl53Lox_UI
Integrates the VL53L0X time-of-flight sensor to measure proximity or distance. Data acquisition and reporting routines are included on serial terminal software.

## UvLtr390_UI
Firmware for reading UV index data from the LTR390 sensor, ideal for environmental and safety monitoring on serial terminal software.

## Veml7700_UI
Acquires lux (light intensity) readings from the VEML7700 sensor. Logs ambient light data for diagnostics on serial terminal software.

## Weather_Shield_UI
Demonstrates use of a multi-sensor weather shield to acquire comprehensive meteorological parameters, including temperature, humidity, atmospheric pressure, and lux (light intensity), all on serial terminal software.

## Wind_Sensor_UI
Samples data from wind speed or direction sensors for monitoring on serial terminal software.

***

## Getting Started

### Prerequisites

- 4G Data Logger Development Board
- Necessary sensor modules (see above)
- Required libraries/drivers for each sensor

### Installation

Clone the repository, install dependencies as per each folder’s README, and connect the required sensors to the 4G Data Logger development board.

***

## License

This project is released under an open-source license. Refer to the LICENSE file for specific terms and conditions.

***
