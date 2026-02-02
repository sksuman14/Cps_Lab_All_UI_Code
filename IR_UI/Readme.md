***

# IR Sensor Interface – 4G Data Logger Board

This repository provides firmware and instructions for interfacing an IR sensor (object detection) with the 4G Data Logger board. The project enables real-time object detection and status logging via the IoT Serial Monitoring App.

***

## Features

- Detects object presence using an IR (infrared) sensor
- Digital output and status logging on a 4G Data Logger Board (Quectel EC200U-based)
- Real-time state display (object detected/not detected) in IoT Serial Monitoring App
- Configurable data logging intervals and UART log output

***

## Hardware Requirements

- 4G Data Logger Board (Quectel EC200U recommended)
- IR Sensor (digital output)
- Programmer (for firmware and UART connection)
- USB cable (for board-PC link)

***

## Software Requirements

- QPYCom (for Python file upload and REPL access)
- IoT Serial Monitoring App (live status display and charting)
- Python environment compatible with Quecpython v1.12 or newer

***

## Prerequisites

- Basic Python and embedded hardware knowledge
- Familiarity with digital signals and UART communication
- Correct sensor and board connections (see pinout below)

***

## Pin Configuration

| **Board Pins** | **Sensor Pins** |
|:---:|:---:|
| 3V3 | VCC |
| ADCO | DO (digital output) |
| GND | GND |

| **Board Pins** | **Programmer Pins** |
|:---:|:---:|
| RSTx | RXD |
| RSRx | TXD |
| GND | GND |

***

## Setup & Configuration

1. Connect the IR sensor to the 4G Data Logger Board using the mapping above.
2. Use a USB cable to connect the board to your PC and launch QPYCom.
3. Select the correct COM port (Quectel USB REPL) and set baud rate (e.g., 115200), then open port.
4. Upload the project files (`main.py`, any system configs) to the board.
5. If fail to upload, press Ctrl+C in QPYCom REPL to halt running code, then re-upload.
6. Open IoT Serial Monitoring App, enter COM port, baud rate, sensor, and interval.
7. Monitor object detection status and logs in live view.

***

## Sample Output

```
Connected to COM4 at 115200 baud
IR Sensor Infrared 0
IR Sensor Infrared 1
IR Sensor On Detected
...
```
IR sensor status ("Infrared 1" = detected, "Infrared 0" = not detected) is plotted and logged in the IoT Serial Monitoring App.

***

## Usage

1. Flash firmware to the board.
2. Run the system to log real-time IR sensor status to the serial terminal and monitoring app.
3. Adjust interval, port, and settings in the app to suit use case.

***

## Troubleshooting

- **Sensor Not Detected:**  
  - Confirm power, wiring, and pin mapping.
  - Check and correct COM port/baud rate settings.
- **Upload/REPL Issues:**  
  - Use Ctrl+C to interrupt previous runs before re-uploading.
- **Unexpected Status:**  
  - Verify environment and sensor placement for accurate detection.

***

## License

Released under an open-source license. See LICENSE file for terms.

***
