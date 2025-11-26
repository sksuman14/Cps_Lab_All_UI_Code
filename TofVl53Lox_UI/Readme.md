***

# VL53L0X Time-of-Flight Sensor Interface – 4G Data Logger Board

This repository includes firmware and setup instructions for integrating the VL53L0X TOF distance/proximity sensor with the 4G Data Logger board. It enables real-time measurement, logging, and visualization of distance using the IoT Serial Monitoring App.

***

## Features

- Measures proximity/distance with VL53L0X TOF sensor (high precision, digital output)
- Communicates via I2C with 4G Data Logger Board (Quectel EC200U)
- Displays real-time distance on IoT Serial Monitoring App (live chart and logs)
- Configurable logging intervals and UART console output

***

## Hardware Requirements

- 4G Data Logger Board (Quectel EC200U recommended)
- VL53L0X TOF sensor module (I2C interface)
- Programmer (for firmware upload and UART connection)
- USB cable (for PC-board interface)

***

## Software Requirements

- QPYCom (for Python firmware upload and REPL access)
- IoT Serial Monitoring App (distance visualization and charting)
- Python runtime compatible with Quecpython v1.12 or newer

***

## Prerequisites

- Basic Python programming skills
- Familiarity with digital sensors and I2C/UART protocols
- Sensor-to-board wiring as listed below

***

## Pin Configuration

| **Board Pins** | **Sensor Pins** |
|:---:|:---:|
| 3V3 | VCC |
| SDA | SDA |
| SCL | SCL |
| GND | GND |

| **Board Pins** | **Programmer Pins** |
|:---:|:---:|
| RSTx | RXD |
| RSRx | TXD |
| GND | GND |

***

## Setup & Configuration

1. Wire the VL53L0X sensor to the 4G Data Logger board per the pin mappings above.
2. Connect your board to the PC via USB and open QPYCom.
3. Select the appropriate COM port (Quectel USB REPL), baud rate (e.g., 115200), and open port.
4. Upload project files (`main.py`, systemconfig.json, driver files) to the board.
5. Stop any running code in REPL (Ctrl+C) before retrying uploads if needed.
6. Launch IoT Serial Monitoring App, configure COM port, baud rate, sensor selection, and interval.
7. Monitor live distance readings and event logs via the UART console and app.

***

## Sample Output

```
Connected to COM4 at 115200 baud
VL53L0X Distance 2.00 cm
VL53L0X Distance 12.30 cm
...
Sensor Data Visualization
Distance: 2.00 cm
Distance: 12.30 cm
```
Distances are continuously logged and graphed in the IoT Serial Monitoring App.

***

## Usage

1. Flash VL53L0X TOF sensor firmware to the 4G Data Logger Board.
2. Monitor real-time distance readings through the app and UART console.
3. Adjust measurement interval, COM port, and settings to fit your use case.

***

## Troubleshooting

- **Sensor not detected:**  
  - Check all wiring connections and pin allocations.
  - Ensure I2C address and configuration are correct.
- **Upload/REPL errors:**  
  - Use Ctrl+C in QPYCom to interrupt running code before uploads.
- **Erratic readings:**  
  - Verify sensor orientation, placement, and initialization procedures.

***

## License

Project is released under open-source license. See LICENSE for terms.

***
