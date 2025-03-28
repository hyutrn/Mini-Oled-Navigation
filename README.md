### Motorcycle Navigation Display with ESP32 and OLED

#### Description
A simple navigation assistant for motorcyclists using an ESP32 and SSD1306 OLED display. This project shows navigation instructions (direction arrows and distance) via Bluetooth Low Energy (BLE) from the Chronos Android app, reducing the need to look at a phone while riding. It leverages the **ChronosESP32** library for time synchronization and data reception. When idle, it displays the current date and time.

#### Features
- **Default Mode**: Shows date and time synced via ChronosESP32 on startup or idle.
- **Connected Mode**: Displays "Connected" and time when paired with the Chronos app.
- **Navigation Mode**: Shows direction arrows (straight, left, right) and distance (e.g., "100m") when receiving navigation data.
- **Timeout**: Automatically reverts to time display after 30 seconds of inactivity.
- **Disconnected Mode**: Shows "Disconnected" and time when unpaired.
- **Manual Input**: Navigation data (e.g., `NAV:straight:100`) is sent manually from Chronos based on Google Maps.

#### Hardware
- **ESP32**: Any BLE-capable variant.
- **SSD1306 OLED**: 128x64 I2C display (SDA -> GPIO 21, SCL -> GPIO 22).
- **Power**: USB or battery for motorcycle use.

#### Software
- **ESP32**: Arduino IDE with:
  - `ChronosESP32` (BLE and time sync).
  - `Adafruit_GFX` and `Adafruit_SSD1306` (OLED control).
- **Android**: Chronos app (by fbiego) for sending custom data via BLE.

#### How It Works
1. Power on: ESP32 waits for BLE connection and shows time.
2. Pair with Chronos app: OLED updates to "Connected" with time.
3. Use Google Maps, manually send commands (e.g., `NAV:left:50`) via Chronos.
4. OLED displays arrow and distance until `STOP_NAV` is sent or 30 seconds pass without new data.

#### Usage
Mount on a motorcycle for a glanceable navigation aid. Pair with Chronos, input navigation data as you ride, and let the timeout handle idle states.

#### Future Improvements


#### License

#### Idea:
https://github.com/appleshaman/CarPlayBLE/tree/main
