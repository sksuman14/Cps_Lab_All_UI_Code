***

# TLV493D Sensor Interface – 4G Data Logger Board

This repository includes firmware and setup instructions for integrating the TLV493D magnetic field sensor with the 4G Data Logger board. The project detects magnetic field strength and direction in real time and visualizes sensor data with the IoT Serial Monitoring App.

***

## Features

- Measures magnetic field strength and direction (X, Y, Z axes) using the TLV493D sensor
- Reliable I2C data transfer with the 4G Data Logger Board (Quectel EC200U-based)
- Real-time data output and charting using the IoT Serial Monitoring App
- Customizable logging intervals and UART logging support

***

## Hardware Requirements

- 4G Data Logger Board (Quectel EC200U recommended)
- TLV493D magnetic field sensor (I2C)
- Programmer (for firmware upload and UART connection)
- USB cable (for connecting board to PC)

***

## Software Requirements

- QPYCom (for Python firmware upload, file management, and REPL access)
- IoT Serial Monitoring App (for live data display and charting)
- Supported Python environment (Quecpython v1.12 or newer)

***

## Prerequisites

- Basic Python programming skills
- Familiarity with I2C and UART protocols
- Correct sensor-to-board wiring (see pinout below)

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

1. Connect the TLV493D sensor to the 4G Data Logger Board using I2C as shown above.
2. Plug the board into your PC via USB and open QPYCom.
3. Select the appropriate COM port for Quectel USB REPL, set the baud rate (e.g., 115200), and open the port.
4. Upload source files (`main.py`, `tlv493d.py`, system configs) to the board.
5. If upload fails, use Ctrl+C to interrupt running code in QPYCom's REPL, then retry.
6. In the IoT Serial Monitoring App, pick the correct COM port, baud rate, sensor, and interval setting, then connect to view live magnetic field data.

***

## Sample Output

```
Connected to COM4 at 115200 baud
TLV493D X0.00 mT, Y-200.70 mT, Z3.23 mT
TLV493D X24.99 mT, Y0.00 mT, Z23.72 mT
TLV493D X0.00 mT, Y125.34 mT, Z-24.79 mT
...
```
Magnetic field vector data is displayed and graphed in the IoT Serial Monitoring App.

***

## Usage

1. Flash the TLV493D firmware onto your 4G Data Logger Board.
2. The application will output magnetic field readings for all three axes in the app or serial terminal.
3. Adjust the COM port, baud rate, sensor selection, and data intervals as required.

***

## Troubleshooting

- **Sensor Not Detected:**  
  - Confirm all wiring connections and configuration settings.
  - Check I2C pin mapping and baud rate.
- **Upload/REPL Issues:**  
  - Stop previous code execution with Ctrl+C before re-uploading.
- **Unexpected Readings:**  
  - Verify sensor orientation, placement, and proper initial setup.

***

## License

This repository is released under an open-source license. Consult the LICENSE file for legal terms.

***
