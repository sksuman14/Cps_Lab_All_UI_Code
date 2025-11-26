***

# Ultrasonic Wind Sensor Interface – 4G Data Logger Board

This repository provides firmware and setup instructions for integrating an Ultrasonic Wind Sensor with the 4G Data Logger board. The project measures and displays both wind speed and wind direction in real time using the IoT Serial Monitoring App.

***

## Features

- Measures wind speed and wind direction using an Ultrasonic Wind Sensor
- Communicates via RS232/UART with the 4G Data Logger Board (Quectel EC200U-based)
- Real-time display and visualization using the IoT Serial Monitoring App
- Configurable logging intervals and UART log support

***

## Hardware Requirements

- 4G Data Logger Board (Quectel EC200U recommended)
- Ultrasonic Wind Sensor (RS232/UART output)
- Programmer (for firmware upload and UART link)
- USB cable (for PC-board connection)

***

## Software Requirements

- QPYCom (for uploading Python firmware and REPL access)
- IoT Serial Monitoring App (live wind speed/direction charting)
- Compatible Python runtime (Quecpython v1.12 or newer)

***

## Prerequisites

- Basic Python programming knowledge
- Familiarity with UART/RS232/serial protocols
- Correct hardware wiring and project setup

***

## Pin Configuration

| **Board Pins** | **Sensor Pins** |
|:---:|:---:|
| 3V3 | VCC |
| RSTx | Rx |
| RSRx | Tx |
| GND | GND |

| **Board Pins** | **Programmer Pins** |
|:---:|:---:|
| Tx | RXD |
| Rx | TXD |
| GND | GND |

***

## Setup & Configuration

1. Connect the Ultrasonic Wind Sensor to the 4G Data Logger Board as per the pin mapping above.
2. Use a USB cable to attach the board to your PC and launch QPYCom.
3. Select the proper COM port (Quectel USB REPL), set baud rate (e.g., 115200), and open the port.
4. Upload project files (e.g., `main.py`, supporting configs) to the board.
5. If a file fails to upload, interrupt the current run with Ctrl+C in QPYCom REPL and retry.
6. Open the IoT Serial Monitoring App, set the COM port, baud rate, sensor, and interval configuration.
7. View and analyze live wind speed and direction readings in the app.

***

## Sample Output

```
Connected to COM18 at 115200 baud
Wind speed 0.41, Wind direction 151.30
Wind speed 0.40, Wind direction 151.30
...
Sensor Data Visualization
Wind Direction 151
Wind Speed 0.4 ms
```
Wind speed and direction are continuously logged, plotted, and displayed in the IoT Serial Monitoring App.

***

## Usage

1. Flash the Ultrasonic Wind Sensor firmware onto your 4G Data Logger Board.
2. Monitor live wind measurements on the serial terminal and in the IoT Serial Monitoring App.
3. Adjust interval, COM port, and settings in the app to your preferences.

***

## Troubleshooting

- **No Data/Detection:**  
  - Confirm physical wiring, sensor-to-board pin mapping, and power.
  - Verify proper port and baud rate settings.
- **Upload/REPL Issues:**  
  - Use Ctrl+C to interrupt previous firmware runs before new uploads.
- **Incorrect Measurements:**  
  - Confirm correct calibration and sensor installation for accurate readings.

***

## License

Project is released under open-source license. See LICENSE file for details.

***
