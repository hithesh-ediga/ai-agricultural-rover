# AI-Controlled Agricultural Rover

An ESP32-based rover for precision agriculture. It drives through a field, stops at intervals to log soil moisture, air temperature and humidity, and uses a Python/OpenCV vision node to flag possible crop disease from a camera feed (webcam or ESP32-CAM).

The project has two parts:

| Part | Folder | Runs on |
|---|---|---|
| Rover firmware: motor control and field sensors | `firmware/esp32_rover_controller/` | ESP32 |
| Vision node: leaf disease detection | `vision-service/` | PC / laptop / Raspberry Pi |

## Hardware

- ESP32 dev board
- L298N dual motor driver + 2 DC gear motors + battery pack
- DHT22 temperature/humidity sensor
- Analog soil moisture sensor (capacitive recommended)
- Optional: ESP32-CAM for a wireless camera feed

### Wiring

| ESP32 pin | Connects to |
|---|---|
| GPIO 14 | L298N ENA (left motor speed, PWM) |
| GPIO 27 | L298N IN1 |
| GPIO 26 | L298N IN2 |
| GPIO 25 | L298N IN3 |
| GPIO 33 | L298N IN4 |
| GPIO 32 | L298N ENB (right motor speed, PWM) |
| GPIO 34 | Soil moisture sensor AOUT |
| GPIO 4  | DHT22 DATA (10 kΩ pull-up to 3.3 V) |
| GND     | L298N GND, sensor GNDs (common ground) |

Remove the ENA/ENB jumpers on the L298N so the ESP32 controls motor speed. Power the motors from their own battery, not from the ESP32.

## 1. Rover firmware

1. Install the [Arduino IDE](https://www.arduino.cc/en/software).
2. Add the ESP32 boards: **Boards Manager → "esp32" by Espressif Systems** (v3.x).
3. Install the libraries: **Library Manager → "DHT sensor library" by Adafruit**. Accept the prompt to also install "Adafruit Unified Sensor".
4. Open `firmware/esp32_rover_controller/esp32_rover_controller.ino`.
5. Select **Tools → Board → ESP32 Dev Module** and your COM port, then **Upload**.
6. Open the **Serial Monitor** at **115200 baud**:

```
Agricultural Rover Initialized. Ready for Telemetry.
Soil Moisture: 42% (raw 2660)
Air Temperature: 28.4 C, Humidity: 61.0 %
```

**Calibrate the soil sensor.** Note the raw value with the probe in open air and in a glass of water, then set `SOIL_DRY_RAW` and `SOIL_WET_RAW` at the top of the sketch.

## 2. Vision node (disease detection)

The vision node estimates the share of leaf area that is brown or yellow, using HSV colour masking. It raises an alert above a threshold (15 % by default).

```bash
cd vision-service
python -m venv .venv
# Windows:      .venv\Scripts\activate
# macOS/Linux:  source .venv/bin/activate
pip install -r requirements.txt
```

Run it on:

```bash
# Laptop webcam
python detect_disease.py

# ESP32-CAM stream (flash the "CameraWebServer" example first, then use its IP)
python detect_disease.py --source http://192.168.1.50:81/stream

# A single photo
python detect_disease.py --source leaf.jpg

# Custom alert threshold (%)
python detect_disease.py --threshold 10
```

Press **q** in the video window to quit.

### Limitations

Colour masking is a simple baseline, not a trained model. Soil, dry stems or lighting can be counted as "diseased" pixels. Point the camera at the leaves and use consistent lighting. A next step would be a trained classifier, e.g. a CNN on the PlantVillage dataset.

## Roadmap

- [ ] Send sensor readings to a cloud dashboard over Wi-Fi (MQTT)
- [ ] Trigger a vision capture from the rover when it stops
- [ ] Obstacle avoidance with an ultrasonic sensor
- [ ] Trained disease-classification model

## Tech stack

ESP32 · Arduino C++ · L298N · DHT22 · Python · OpenCV · NumPy
