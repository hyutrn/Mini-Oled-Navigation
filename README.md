# Motorcycle Navigation Display with ESP32 and OLED
## Description
This project is a simple, low-cost navigation assistant designed for motorcyclists. It uses an ESP32 microcontroller paired with an SSD1306 OLED display to show real-time navigation instructions (direction arrows and distance) without requiring the rider to look at their phone. The system integrates the ChronosESP32 library to sync time via Bluetooth Low Energy (BLE) and receive navigation data from the Chronos Android app. When not in navigation mode, the OLED displays the current date and time.

## Features
- Default Mode: Displays date and time synced via ChronosESP32 when powered on or idle.
- Connected Mode: Shows "Connected" status and time when paired with the Chronos app.
- Navigation Mode: Displays direction arrows (straight, left, right) and distance (e.g., "100m") when navigation data is received.
- Disconnected Mode: Reverts to showing "Disconnected" and time when the phone is unpaired.
- Manual Input: Navigation data (e.g., NAV:straight:100) is sent manually from the Chronos app based on Google Maps instructions.

## Hardware
- ESP32: Any variant with BLE support.
- SSD1306 OLED: 128x64 I2C display (SDA -> GPIO 21, SCL -> GPIO 22).
- Power: USB or battery for motorcycle mounting.

## Software
- ESP32: Programmed with Arduino IDE, using libraries:
- ChronosESP32 for BLE communication and time sync.
- Adafruit_GFX and Adafruit_SSD1306 for OLED control.
- Android: Requires the Chronos app (by fbiego) to send custom navigation data via BLE.

## How It Works
Power on the ESP32; it waits for a BLE connection and shows the current time.
Pair with the Chronos app; the OLED updates to "Connected" with time.
Open Google Maps on your phone, start navigation, and manually send commands (e.g., NAV:left:50) via Chronos based on the instructions.
The OLED displays the corresponding arrow and distance until a STOP_NAV command is sent or the connection is lost.
Usage
Ideal for motorcyclists who want a hands-free, glanceable navigation aid. Mount the ESP32 and OLED on your bike, connect via Chronos, and input navigation data as you ride.

## Future Improvements

