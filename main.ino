#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <ChronosESP32.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET    -1
#define TIMEOUT_MS    30000 // 30 giây timeout

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);
ChronosESP32 chronos("ESP32_Navigation"); // Tên BLE của thiết bị

// Biến trạng thái
bool isConnected = false;
bool isNavigating = false;
String currentDirection = "";
String currentDistance = "";
unsigned long lastDataTime = 0; // Thời gian nhận dữ liệu cuối cùng

void setup() {
  Serial.begin(115200);

  // Khởi tạo OLED
  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) { // Địa chỉ I2C mặc định: 0x3C
    Serial.println(F("SSD1306 allocation failed"));
    for (;;);
  }
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);
  display.println("Waiting for connection...");
  display.display();

  // Khởi tạo ChronosESP32
  chronos.begin();
  chronos.setConnectionCallback(connectionCallback); // Callback kết nối
  chronos.setCustomCallback(customCallback);         // Callback dữ liệu tùy chỉnh
}

void loop() {
  chronos.loop(); // Xử lý BLE từ Chronos

  // Kiểm tra timeout
  if (isNavigating && (millis() - lastDataTime > TIMEOUT_MS)) {
    isNavigating = false;
    Serial.println("Navigation timed out, reverting to time display");
  }

  // Hiển thị lên OLED
  display.clearDisplay();
  display.setCursor(0, 0);

  if (!isConnected) {
    display.println("Disconnected");
    showDateTime();
  } else if (isConnected && !isNavigating) {
    display.println("Connected");
    showDateTime();
  } else if (isNavigating) {
    showNavigation();
  }

  display.display();
  delay(100); // Giảm tải CPU
}

// Callback khi kết nối/ngắt kết nối qua BLE
void connectionCallback(bool state) {
  isConnected = state;
  if (state) {
    Serial.println("Device Connected");
  } else {
    Serial.println("Device Disconnected");
    isNavigating = false; // Reset chế độ dẫn đường khi ngắt kết nối
  }
}

// Callback nhận dữ liệu tùy chỉnh từ Chronos app
void customCallback(String data) {
  Serial.println("Received: " + data);
  if (data.startsWith("NAV:")) {
    isNavigating = true;
    lastDataTime = millis(); // Cập nhật thời gian nhận dữ liệu
    int firstColon = data.indexOf(':');
    int secondColon = data.indexOf(':', firstColon + 1);
    currentDirection = data.substring(firstColon + 1, secondColon);
    currentDistance = data.substring(secondColon + 1);
  } else if (data == "STOP_NAV") {
    isNavigating = false;
    Serial.println("Navigation stopped manually");
  }
}

// Hiển thị thời gian và ngày tháng
void showDateTime() {
  String dateTime = chronos.getDateString() + " " + chronos.getTimeString();
  display.setCursor(0, 20); // Đặt vị trí giữa màn hình
  display.println(dateTime);
}

// Hiển thị thông tin dẫn đường
void showNavigation() {
  // Vẽ mũi tên dựa trên hướng
  if (currentDirection == "straight") {
    display.drawLine(60, 40, 60, 20, SSD1306_WHITE); // Thân mũi tên
    display.drawTriangle(55, 20, 65, 20, 60, 10, SSD1306_WHITE); // Đầu mũi tên
  } else if (currentDirection == "left") {
    display.drawLine(60, 30, 40, 30, SSD1306_WHITE);
    display.drawTriangle(40, 25, 40, 35, 30, 30, SSD1306_WHITE);
  } else if (currentDirection == "right") {
    display.drawLine(60, 30, 80, 30, SSD1306_WHITE);
    display.drawTriangle(80, 25, 80, 35, 90, 30, SSD1306_WHITE);
  }

  // Hiển thị khoảng cách
  display.setCursor(0, 50);
  display.print(currentDistance + "m");
}
