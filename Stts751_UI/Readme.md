***

# STTS751 Sensor Interface – 4G Data Logger Board

This repository offers firmware and setup instructions to integrate the STTS751 high-precision temperature sensor with the 4G Data Logger board. The project enables accurate, real-time acquisition and visualization of temperature data through the IoT Serial Monitoring App.

***

## Features

- Measures ambient temperature with high precision using the STTS751 sensor
- Reliable I2C communication with the 4G Data Logger hardware (Quectel EC200U-based)
- Real-time data display and plotting in the IoT Serial Monitoring App
- Supports UART logs and logging intervals for robust, flexible monitoring

***

## Hardware Requirements

- 4G Data Logger Board (Quectel EC200U module recommended)
- STTS751 Sensor (I2C interface)
- Programmer (for firmware flashing and UART)
- USB cable (for board-PC connection)

***

## Software Requirements

- QPYCom (for Python flashing, file management, and REPL)
- IoT Serial Monitoring App (for live temperature output and visualization)
- Compatible Python environment (Quecpython v1.12 or newer)

***

## Prerequisites

- Basic Python knowledge
- Familiarity with I2C and UART communication protocols
- Correct hardware wiring (refer to pin configuration below)

***

## Pin Configuration

| **Board Pins** | **Sensor Pins** |
|:---:|:---:|
| 3V3 | VCC |
| GND | GND |
| SDA | SDA |
| SCL | SCL |

| **Board Pins** | **Programmer Pins** |
|:---:|:---:|
| RSTx | RXD |
| RSRx | TXD |
| GND | GND |

***

## Setup & Configuration

1. Connect the STTS751 sensor to the 4G Data Logger Board using I2C as shown above.
2. Use a USB cable to connect the board to your PC, and launch QPYCom.
3. Select the correct COM port for Quectel USB REPL, set baud rate (typically 115200), and open the port.
4. Upload necessary Python sources (`main.py`, `stts751.py`, and system configuration files) to the board.
5. If a file fails to upload, interrupt running code in REPL with Ctrl+C and resend files.
6. Open the IoT Serial Monitoring App, enter correct COM port and baud rate, select sensor type and interval, and connect to view live temperature data.

***

## Sample Output

```
Connected to COM4 at 115200 baud
STTS751 Temperature 23.25°C (73.85°F)
STTS751 Temperature 23.00°C (73.40°F)
STTS751 Temperature 23.00°C (73.40°F)
...
```
Temperature data is displayed and charted live in the IoT Serial Monitoring App.

***

## Usage

1. Flash the STTS751 firmware onto the 4G Data Logger Board.
2. After startup, temperature readings will be logged and visualized in the app and can be viewed via UART/serial console.
3. All intervals, COM port, and settings can be modified within the IoT Serial Monitoring App for tailored data logging.

***

## Troubleshooting

- **Sensor Not Detected:**  
  - Confirm all wiring and physical connections.
  - Ensure correct baud rate, COM port, and I2C address.
- **Upload/REPL Problems:**  
  - Stop previous code execution (Ctrl+C in QPYCom REPL) before re-uploading files.
- **Abnormal Readings:**  
  - Check sensor placement, initialization steps, and firmware configuration settings.

***

## License

This project is released under an open-source license. Please refer to the LICENSE file for details.

***
