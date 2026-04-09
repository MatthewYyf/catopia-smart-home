# Project Title - Proposal


## 1. Team Information
- **Team Name:** Catopia
- **Team Members:**
  - **Matthew Yue** (matthewyue@brandeis.edu) – Mechanical Engineer & Data Scientist
  - **Garret Rieden** (grieden11@brandeis.edu) – Hardware Engineer
  - **Adam Rieden** (arieden@brandeis.edu) – Frontend Developer
  - **Yuxuan Liu** (yuxuanliu050613@brandeis.edu) – Backend Developer
- **Github Repository:**https://github.com/MatthewYyf/catopia-smart-home.git


## 2. Abstract
Provide a concise summary (150–250 words) describing:
- your project:
We are here to make an all-intelligent home for the owners to get for their cats and themselves. The cat home, Catopia, will allow the owner to monitor and care for their cat. Catopia will track and store data each day from each of the many sensors, like water intake, food intake, temperature and humidity tracker, camera's, and mic.
- progress:
A decent amount of hardware has been figured out and will be integrated into the catopia system in the coming weeks. The web app has come along very well and 
- future plans:




## 3. Project Overview

### 4.1 Project Description
High-level description of the system.
As detailed as possible.
Catopia is a smart cat home system that integrates automated care, health monitoring, and emotional analysis into one connected platform. The system uses two computing units: a Raspberry Pi Pico W for sensor data collection and actuator control, and a Raspberry Pi 5 for data processing, storage, and backend services.

The Pico collects data from sensors measuring food intake (pressure sensor), water level, temperature, humidity, motion, and audio. It also controls actuators such as the water pump and a servo-powered laser toy. Sensor data is serialized in JSON and sent via USB serial to the Raspberry Pi 5.

The Raspberry Pi 5 stores data in an SQLite database and performs higher-level analysis. For emotional detection, the system uses DeepCat for video-based body language analysis and JL-TFMSFNet for audio-based vocal analysis. These outputs are combined to estimate the cat’s emotional state.

A mobile iOS app connects to the backend through REST APIs and WebSockets, allowing users to monitor real-time data, view historical trends, watch live video via HLS, receive alerts, and remotely control interactive features.

Overall, Catopia separates sensing, processing, and user interaction into clear layers, creating a modular and scalable smart pet care system.

### 4.2 Hardware Components
| Component | Description | Quantity |
|---------|-------------|----------|
| Raspberry Pi + Pico | Main controller | 1 |
| Pressure Sensor| Weight Sensor | 2 |
| Temperature & Humidity Sensor | Measure temp in cat sleeping area | 1 |
| PIR Infrared Sensor | Locate Cat | 1 |
| Camera Module | Watch cat from App | 1 |
| Water Level Monitor | Check how much water is in the bowl | 1 |
| Servo Motor | Move Cat Toy | 1 |
| Water Pump | Pour water into cat bowl | 1 |
| Wi-fi / Bluetooth module | Connect modules and to app | 1 |
| Housing Enclosure | Main structure everything surrounds or mounted on | 1 |
| Food-safe containers | For food and water storage | 2 |
| Tubes | For water system | 1 |
| Mounting brackets + wiring | For all cat equipment | 4 |
| Audio Sensor | To listen to cat | 1 |
| Screen | To relay cat's emotional state | 1 |
### 4.3 Software Components
- Libraries / Frameworks
- -  JL-TFMSFNet: https://www.sciencedirect.com/science/article/pii/S0957417424014878#d1e1222
- -  DeepCat: https://github.com/Arwa-Fawzy/Cat-Emotional-Analysis?tab=readme-ov-file
OpenCV (optional video processing)
- Communication Protocols (e.g., I2C, SPI, MQTT)
- - USB Serial (Pico → Pi 5)

- - WiFi (Pi 5 → Mobile)

- - HTTP REST API

- - RTSP / HLS (video streaming)

- - JSON (data format)
- Software structure
- - MicroPython (Pico W)
- - libcamera (Pi 5)
- - Flask / FastAPI (backend)
- - SQLite (database)
- Data flow
- - Sensors
    -> Pico(MicroPython)
    -> Pi 5 (Backend)
    -> Data Base
    -> API
- User interface
- - Real-time sensor dashboard
- - Daily health reports
- - Alerts notifications
- - Live video feed
## 5. Progress
Progress Summary

### 5.1 Hardware Progress
Got the water pump, force sensors, ....etc working

### 5.2 Software Progress

### 5.3 Current Results

## 6. Challenges and Solutions
Some challenges are still recording and interpreting the cats meows. 

## 7. Updated Plans

### 7.1 Updated Timeline
As detail as possible.
3 weeks left
| Phase | Activities | Duration |
|------|------------|----------|
| Phase 1| Research | 1/2 weeks|
| Phase 2| Development | 1 1/2 weeks |
| Phase 3| Testing | 1/2 week |
| Phase 4| Final Deployment | 1/2 week |

### 7.2 Updated Workload Distributions


## 8. Demo Plan
Explain your live demonstration plan in details

## 9. Contributions
Adam
- Water pump and code
- Force Sensor and code
- Researching cat meows

## 10. Conclusion
Brief reflection on current status, remaining challenges and plans.

## References
- Datasheets
- Research papers
  - JL-TFMSFNet: https://www.sciencedirect.com/science/article/pii/S0957417424014878#d1e1222
- Projects you get ideas from - GitHub repositories-
  - DeepCat: https://github.com/Arwa-Fawzy/Cat-Emotional-Analysis?tab=readme-ov-file

