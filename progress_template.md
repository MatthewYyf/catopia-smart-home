## 1. Team Information
- **Team Name:** Catopia
- **Team Members:**
  - **Matthew Yue** (matthewyue@brandeis.edu) – Mechanical Engineer & Data Scientist
  - **Garret Rieden** (grieden11@brandeis.edu) – Hardware Engineer
  - **Adam Rieden** (arieden@brandeis.edu) – Frontend Developer
  - **Yuxuan Liu** (yuxuanliu050613@brandeis.edu) – Backend Developer
- **Github Repository:** https://github.com/MatthewYyf/catopia-smart-home.git


## 2. Abstract
Provide a concise summary (150–250 words) describing:
- project introduction:
We are here to make an all-intelligent home for the owners to get for their cats and themselves. The cat home, Catopia, will allow the owner to monitor and care for their cat. Catopia will track and store data each day from each of the many sensors, like water intake, food intake, temperature and humidity tracker, camera's, and mic.
- current progress:
At the current stage, we have completed the core prototype communication loop between the hardware components, backend, and user interface. In our current development setup, the laptop runs the backend server, while the Raspberry Pi provides the hotspot and the Raspberry Pi Pico W connects through that network to exchange data with the server. The Pico W can send device data to the backend and poll for commands. Then the backend serves the dashboard and manages control requests. We have also made strong progress on several hardware subsystems, including the stepper motor, water pump, pressure sensor, camera streaming tests, and interactive servo control.
- future plans: Over the next few weeks, we plan to finish hardware integration, calibrate sensors, improve data storage and reliability, and connect unfinished features such as live video, automated feeding and watering behavior, and cat emotion analysis into a stable demo.



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
| Servo Motor | Move Cat Toy/Laser | 2 |
| Water Pump | Pour water into cat bowl | 1 |
| Wi-fi / Bluetooth module | Connect modules and to app | 1 |
| Housing Enclosure | Main structure everything surrounds or mounted on | 1 |
| Food-safe containers | For food and water storage | 2 |
| Tubes | For water system | 1 |
| Mounting brackets + wiring | For all cat equipment | 4 |
| Audio Sensor | To listen to cat | 1 |
| Screen | To relay cat's emotional state | 1 |
### 4.3 Software Components
- **Backend:** FastAPI (Python), served with Uvicorn
- **Frontend:** Browser-based dashboard built with HTML, CSS, and JavaScript
- **Embedded Software:** MicroPython running on the Raspberry Pi Pico W
- **Communication Methods:** Wi-Fi local network / hotspot, HTTP REST API, JSON data exchange
- **Backend Functions:** Receives telemetry data from the Pico W, stores the latest system state in memory, and queues commands from the frontend for the Pico W
- **Frontend Functions:** Displays live system and sensor state, sends commands for LED, pump, and dispensing control, and refreshes data every second through polling
- **Embedded Functions:** Reads sensor values, controls hardware such as the LED, water pump, and feeder-related devices, and sends data to the backend while fetching queued commands
- **Software Architecture:** Frontend -> Backend -> Pico W communication loop for real-time monitoring and device control
## 5. Progress
Progress Summary

### 5.1 Hardware Progress
Got the water pump, force sensors, servo motors, ..etc working

### 5.2 Software Progress
On the software side, we have built the core software architecture of Catopia around three connected layers, the backend, the Pico firmware, and the frontend web template. The backend is developed in Python using FastAPI and is served with Uvicorn as the ASGI server. It acts as the communication layer between the frontend browsers and the embedded devices, handling sensor data, queueing commands, and maintaining the latest real-time system state through difference devices.At this stage, the backend already supports the key REST endpoints needed for the prototype. GET / to serve the frontend(index.html), POST /api/data to receive sensor data from the Pico, GET /api/state to return the latest system state, and POST /api/command plus GET /api/command to queue and deliver commands. On the embedded side, we write the Pico firmware in an object-oriented structure that interfaces with GPIO and ADC ports, controls the LED, water pump, and kibble dispenser, and sends sensor readings to the backend every second over HTTP. We have also defined modular device abstractions such as PumpDevice, LoadSensor, and KibbleDispenser to keep the firmware organized. After that , for our frontend, we have developed a web dashboard using HTML, CSS, and JavaScript that communicates with the backend through the REST API, sends commands for LED, pump, and dispensing control, and fetches live system state per second. Overall, we have already developed the main software system architecture of Catopia, connecting the frontend, backend, and Pico into one working communication pipeline.

### 5.3 Current Results

## 6. Challenges and Solutions
Our first current challenges is processing sensor data accurately, especially from the pressure sensor. We found that the pressure sensor does not directly output values in standard weight units, so we cannot use its raw data reading as actual food or water weight measurements. Consequently, we need to calibrate the sensor through testing and convert the raw data into real weight values. On top of that, the pressure sensor is highly sensitive, and even very small forces can cause large fluctuations in the data readings. Our current approach is to use an available conversion formula. But because this conversion function is not linear, we still need to refine the calibration process and improve measurement stability. Solving this problem is important because accurate food and water weight tracking is one of the most basic and essential functions of the Catopia.
The second major challenge is implementing a database for the Catopia software system. At present, our server can receive live data from the Raspberry Pi Pico W and return the latest system state, but it does not permanently store the cat’s daily data. This means that our system could not provide permanent storage for user’s daily data. We also cannot analyze long-term trends, generate daily reports, or compare changes in the cat’s behavior and health over time without a database. Another challenge is deciding how to structure the data. Since the system need to store different kinds of information, including time-stamped sensor readings, device states, feeding and,  and possibly future camera or emotion-analysis results.
Our current solution is to add a lightweight database layer to the backend, most likely using SQLite first because it is simple to integrate with Python. We plan to design tables for sensor readings, command logs, and daily summaries so that every important event can be recorded with a timestamp. Once this is implemented, the backend will maintain historical records that can support graphs, reports, and future health analysis features. This will make the system much more reliable and useful, since storing daily data is one of the core goals of Catopia.
Also, some challenges are still recording and interpreting the cats meows. 


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

Explain your live demonstration plan in details
- Garret's Ideas:
- In class:
- Show off the modules separately, demonstrating the water bowl and food bowl are refilled to the set weight.
- Show off the food auger.
- In our website, show the water/food data live updating as more water/food is added to the bowls (and vice versa).
- Show off the livestream.
- Show off the play feature, controlling the laser with the servo motors through the livestream.
- Prerecord cat meows (as we probably wont have a live cat on hand) and demonstrate our audio sensor and cat meow research can correctly interpret the cat's mood.
- Potentially prerecorded video, to present in class:
- A cat's movement/posture/behavior being correctly identified through our research.

## 9. Contributions
Adam
- Water pump and code
- Force Sensor and code
- Researching cat meows

Matthew
- Built the frontend and backend and abstraction for additional devices
- Wrote Pico firmware for device controls
- Connected frontend ↔ backend ↔ hardware into one system
- Set up device/command structure for controlling components
- Designed a 3D auger feeder for automatic food dispensing

Garret
- Video streaming and code
- Servo motors for pan/tilt and code

## 10. Conclusion
Brief reflection on current status, remaining challenges and plans.

## References
- Datasheets
- Research papers
  - JL-TFMSFNet: https://www.sciencedirect.com/science/article/pii/S0957417424014878#d1e1222
- Projects you get ideas from - GitHub repositories-
  - DeepCat: https://github.com/Arwa-Fawzy/Cat-Emotional-Analysis?tab=readme-ov-file
