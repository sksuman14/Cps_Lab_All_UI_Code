***

# LTR390 Ambient & UV Light Sensor Interface – 4G Data Logger Board

This repository provides firmware and instructions for interfacing the LTR390 sensor (ambient light and UV index) with the 4G Data Logger board. The solution enables real-time monitoring and logging of light and UV data, visualized via the IoT Serial Monitoring App.

***

## Features

- Measures ambient light intensity and UV index using the LTR390 sensor
- Communicates over I2C with the 4G Data Logger Board (Quectel EC200U-based)
- Real-time charting and log display in the IoT Serial Monitoring App
- Configurable data logging intervals and UART console output

***

## Hardware Requirements

- 4G Data Logger Board (Quectel EC200U recommended)
- LTR390 sensor (I2C interface)
- Programmer (for firmware flashing and UART connection)
- USB cable (for board-PC interface)

***

## Software Requirements

- QPYCom (Python file upload and REPL connection)
- IoT Serial Monitoring App (light/UV dashboard and visualization)
- Python runtime compatible with Quecpython v1.12 or newer

***

## Prerequisites

- Basic Python and embedded hardware skills
- Understanding of I2C and UART protocols
- Proper hardware wiring (pin mapping below)

***

## Pin Configuration

| **Board Pins** | **Sensor Pins** |
|:---:|:---:|
| 3V3 | VDD |
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

1. Connect the LTR390 sensor to the 4G Data Logger board according to the mapping above.
2. Attach the board to your PC and open QPYCom.
3. Choose the correct COM port (Quectel USB REPL), set baud rate (115200), and open the port.
4. Upload the necessary Python files (`main.py` and supporting configs) to the board.
5. Halt any running code in REPL with Ctrl+C before uploading if errors occur.
6. Start the IoT Serial Monitoring App. Enter sensor, COM port, baud rate, and logging interval.
7. The app will display current readings and logs for ambient and UV light.

***

## Sample Output

```
Connected to COM20 at 115200 baud
LTR390 UV Index0
LTR390 UV Index2
UV 2.00 (Low)
...
Sensor Data Visualization
UV Index: 2.00
```
Ambient and UV light measurements are charted and logged in the IoT Serial Monitoring App.

***

## Usage

1. Flash the firmware onto your 4G Data Logger Board.
2. Real-time light and UV index values are displayed in the app and serial console.
3. Change logging intervals, serial settings, and sensor configuration as needed.

***

## Troubleshooting

- **Sensor not detected:**  
  - Verify pin mapping, wiring, and power.
  - Ensure I2C addresses and baud rate are correct.
- **Upload/REPL errors:**  
  - Press Ctrl+C in REPL before uploading new code.
- **Inaccurate readings:**  
  - Confirm sensor placement and initialization.

***

## License

Released under open-source license. See LICENSE file for details.

***
