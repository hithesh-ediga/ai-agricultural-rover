/*
 * AI Agricultural Rover - Core Firmware
 * Hardware: ESP32, L298N Motor Driver, DHT22, Soil Moisture Sensor
 *
 * Board:     "ESP32 Dev Module" (esp32 board package by Espressif, v3.x)
 * Libraries: "DHT sensor library" by Adafruit (+ "Adafruit Unified Sensor")
 *
 * Every cycle the rover drives forward, stops, and logs soil moisture,
 * air temperature and humidity over Serial (115200 baud).
 */

#include <DHT.h>

// Motor control pins (L298N)
#define ENA 14
#define IN1 27
#define IN2 26
#define IN3 25
#define IN4 33
#define ENB 32

// Sensor pins
#define SOIL_MOISTURE_PIN 34   // ADC1 input-only pin (ADC2 is unavailable while Wi-Fi is on)
#define DHT_PIN 4
#define DHT_TYPE DHT22

// Soil sensor calibration: raw ADC readings (0-4095) in open air and in water.
// Measure these with your own sensor and update them.
#define SOIL_DRY_RAW 3500
#define SOIL_WET_RAW 1500

#define DRIVE_SPEED 150        // PWM duty 0-255
#define DRIVE_TIME_MS 2000
#define PAUSE_TIME_MS 5000

DHT dht(DHT_PIN, DHT_TYPE);

void setup() {
  Serial.begin(115200);

  pinMode(ENA, OUTPUT); pinMode(IN1, OUTPUT); pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT); pinMode(IN4, OUTPUT); pinMode(ENB, OUTPUT);
  stopMotors();

  pinMode(SOIL_MOISTURE_PIN, INPUT);
  dht.begin();

  Serial.println("Agricultural Rover Initialized. Ready for Telemetry.");
}

void loop() {
  moveForward(DRIVE_SPEED);
  delay(DRIVE_TIME_MS);
  stopMotors();

  // Read sensors while stationary (also the moment for a vision capture)
  readSoilMoisture();
  readAirConditions();

  delay(PAUSE_TIME_MS);
}

void readSoilMoisture() {
  int raw = analogRead(SOIL_MOISTURE_PIN);
  int percent = map(raw, SOIL_DRY_RAW, SOIL_WET_RAW, 0, 100);
  percent = constrain(percent, 0, 100);

  Serial.print("Soil Moisture: ");
  Serial.print(percent);
  Serial.print("% (raw ");
  Serial.print(raw);
  Serial.println(")");
}

void readAirConditions() {
  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();

  if (isnan(humidity) || isnan(temperature)) {
    Serial.println("DHT22 read failed - check wiring");
    return;
  }

  Serial.print("Air Temperature: ");
  Serial.print(temperature, 1);
  Serial.print(" C, Humidity: ");
  Serial.print(humidity, 1);
  Serial.println(" %");
}

void moveForward(int speed) {
  analogWrite(ENA, speed); analogWrite(ENB, speed);
  digitalWrite(IN1, HIGH); digitalWrite(IN2, LOW);
  digitalWrite(IN3, HIGH); digitalWrite(IN4, LOW);
}

void stopMotors() {
  analogWrite(ENA, 0); analogWrite(ENB, 0);
  digitalWrite(IN1, LOW); digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW); digitalWrite(IN4, LOW);
}
