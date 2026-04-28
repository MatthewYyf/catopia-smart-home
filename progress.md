## 1. Team Information
- **Team Name:** Catopia
- **Team Members:**
  - **Matthew Yue** (matthewyue@brandeis.edu) – Mechanical Engineer & Data Scientist
  - **Garret Rieden** (grieden11@brandeis.edu) – Hardware Engineer
  - **Adam Rieden** (arieden@brandeis.edu) – Frontend Developer
  - **Yuxuan Liu** (yuxuanliu050613@brandeis.edu) – Backend Developer
- **Github Repository:** https://githu b.com/MatthewYyf/catopia-smart-home.git


## 2. Abstract
- Project Introduction
Catopia is an integrated smart home system designed to automate and monitor essential aspects of cat care. The system enables owners to remotely track and manage their pet’s food intake, water consumption, environmental conditions, and behavior through a connected hardware and software platform.

- Current Progress
At the current stage, we have completed a working prototype that establishes end-to-end communication between hardware components, the backend server, and the user interface. In our setup, a Raspberry Pi provides a local network, while a Raspberry Pi Pico handles sensor data collection and actuator control. The Pico continuously sends device data to the backend and polls for commands, while the backend manages system state and serves the frontend dashboard.

We have successfully implemented and tested several core hardware subsystems, including the water pump, stepper motor-based feeder, pressure sensors, camera streaming, and servo-based interaction system. These components can be individually controlled and monitored through the web interface.

- Future Plans
Over the next few weeks, we will focus on completing full system integration, improving sensor calibration for reliable measurements, implementing persistent data storage, and stabilizing key features such as automated feeding/watering, live video, and basic cat behavior analysis for the final demonstration.

## 3. Project Overview

### 4.1 Project Description

Catopia is a smart cat care system designed to automate feeding, watering, and basic monitoring through a connected hardware and software platform. The system is built around two main components: a Raspberry Pi Pico for low-level hardware control and a backend server that manages data and user interaction.

The Raspberry Pi Pico is responsible for interfacing directly with sensors and actuators. It reads data from force sensors to estimate food and water levels and controls devices such as the water pump, stepper motor-based feeder, and servo motors for the laser toy. The Pico periodically sends sensor readings to the backend and retrieves queued commands for device control.

The system also collects data related to the cat’s behavior and well-being, primarily through measuring its metrics and monitoring food and water intake. This data is transmitted to the backend, where it is stored and processed to generate simple metrics such as daily intake and feeding frequency. These summaries are displayed on the frontend dashboard, enabling users to track patterns and identify potential irregularities in the cat’s physical and psychological wellbeing.

The system includes a preliminary audio-based feature to interpret cat vocalizations. Audio input is analyzed to classify simple categories such as hunger or attention-seeking using a lightweight or rule-based approach. Due to limited data and scope, this feature is implemented using prerecorded samples for demonstration purposes. It serves as a proof of concept for integrating behavioral signals into the system rather than a fully developed model.

The backend server, implemented using FastAPI, acts as the central communication layer between the embedded system and the user interface. It receives incoming data from the Pico, maintains the current system state, and exposes REST endpoints for retrieving data and sending commands. The backend also serves a web-based dashboard that allows users to monitor system status and control devices in real time.

The frontend is a browser-based interface built with HTML, CSS, and JavaScript. It displays live information such as food and water levels and provides controls for interacting with the system, including activating the pump, dispensing food, and controlling the laser toy. The interface communicates with the backend through HTTP requests and updates periodically to reflect the latest system state.

Overall, Catopia is structured as a modular system with clear separation between hardware control, backend processing, and user interaction. This design allows individual components to be developed and tested independently while supporting integration into a unified system.

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
- **Embedded Software:** MicroPython running on the Raspberry Pi Pico 
- **Communication Methods:** local network / hotspot, REST API, JSON data exchange
- **Backend Functions:** Receives data from the Pico, stores the latest system state, and queues commands from the frontend for the Pico 
- **Frontend Functions:** Displays live system and sensor state, sends commands for LED, pump, and dispensing control, and refreshes data every second through polling
- **Embedded Functions:** Reads sensor values, controls hardware such as the LED, water pump, and feeder-related devices, and sends data to the backend while fetching queued commands
- **Software Architecture:** Frontend -> Backend -> Pico communication loop for real-time monitoring and device control

## 5. Progress
Significant progress has been made on both the hardware and software components of Catopia. On the hardware side, key devices including the water pump, force sensors, servo motors, and camera module have been successfully tested and are functioning independently.

On the software side, we have developed the core system architecture consisting of three main layers: the backend server, Pico firmware, and frontend dashboard. The FastAPI backend supports REST endpoints for data transfer, command handling, and real-time state updates. The Pico firmware is modularized to manage sensors and actuators while transmitting data at a regular interval (~1 Hz). The frontend dashboard displays live system data and allows users to send control commands through the web interface.

At this stage, we have achieved a working prototype with end-to-end communication between the frontend and several hardware components. While individual subsystems are operational, ongoing work is focused on fully integrating all components into a single cohesive system.
### 5.1 Hardware Progress
Got the water pump, force sensors, servo motors, video camera working.
An issue we are encountering is the power supply. If we are not connecting the power through the wall outlet (to the Pi), our externals might not have the correct power. Looking through the hardware specifications for each external (such as our servos or water pump), we can figure out how much the external draws. Understanding voltage and current, as well as being able to understand if our circuit is giving enough power (we can check this with a multimeter), will allow our Catopia project to be independent on the wall outlet (allowing free placement anywhere in the house).

### 5.2 Software Progress
On the software side, we have built the core software architecture of Catopia around three connected layers, the backend, the Pico firmware, and the frontend web template. The backend is developed in Python using FastAPI and is served with Uvicorn as the ASGI server. It acts as the communication layer between the frontend browsers and the embedded devices, handling sensor data, queueing commands, and maintaining the latest real-time system state through difference devices.At this stage, the backend already supports the key REST endpoints needed for the prototype. GET / to serve the frontend(index.html), POST /api/data to receive sensor data from the Pico, GET /api/state to return the latest system state, and POST /api/command plus GET /api/command to queue and deliver commands. On the embedded side, we write the Pico firmware in an object-oriented structure that interfaces with GPIO and ADC ports, controls the LED, water pump, and kibble dispenser, and sends sensor readings to the backend every second over HTTP. We have also defined modular device abstractions such as PumpDevice, LoadSensor, and KibbleDispenser to keep the firmware organized. After that , for our frontend, we have developed a web dashboard using HTML, CSS, and JavaScript that communicates with the backend through the REST API, sends commands for LED, pump, and dispensing control, and fetches live system state per second. Overall, we have already developed the main software system architecture of Catopia, connecting the frontend, backend, and Pico into one working communication pipeline.

### 5.3 Current Results
At this point, we have end-to-end communication working between the frontend and several hardware components — the water pump and the video camera. We also have a number of individual components working on their own, with completed abstractions on the software side, though they still need to be fully wired together into one cohesive system. The web application itself runs as expected; it's mainly waiting on the remaining hardware connections to be completed before everything functions together as intended.

## 6. Challenges and Solutions
One major challenge is accurately processing sensor data from the pressure sensors used to measure food and water weight. The raw sensor outputs do not directly correspond to standard weight units, requiring calibration and conversion. Additionally, the sensor readings exhibit high variance due to noise and sensitivity to small disturbances. To address this, we are developing calibration procedures and applying filtering techniques to stabilize readings and improve measurement accuracy.

Another key challenge is the lack of persistent data storage. Currently, the backend maintains only the latest system state, which limits the ability to analyze long-term trends or generate historical reports. To address this, we plan to integrate a lightweight SQLite database to store time-stamped sensor data, command logs, and daily summaries. This will enable features such as trend visualization and behavioral analysis over time.

We are also exploring approaches for interpreting cat vocalizations, which presents challenges in both data collection and model integration. For the purposes of the demo, we plan to implement a simplified version using prerecorded audio inputs and basic classification.


## 7. Updated Plans

### 7.1 Updated Timeline
| Phase | Activities | Duration |
|------|------------|----------|
| Phase 1 | Hardware integration (pump, feeder, toy) into one system | 3–4 days |
| Phase 2 | Implement automated refill logic + sensor calibration | 3–4 days |
| Phase 3 | Backend/frontend synchronization and system stabilization | 2–3 days |
| Phase 4 | Database + basic data analytics implementation | 2–3 days |
| Phase 5 | Add remaining sensors (temp/humidity, PIR) + camera integration | 3–4 days |
| Phase 6 | Implement basic audio/emotion detection | 2–3 days |
| Phase 7 | UI/UX polish and system reliability improvements | 2–3 days |
| Phase 8 | Testing, debugging, and full system validation | 2–3 days |
| Phase 9 | Demo preparation, rehearsal, and backup materials | 2 days |

### 7.2 Updated Workload Distributions

Matthew Yue
- Lead integration of hardware, backend, and frontend into a unified system  
- Finalize and polish the frontend user interface  
- Design and fabricate 3D models and physical components (e.g., feeder system)  
- Develop and implement cat sentiment detection (model research, training, and integration)  
- Research feline health metrics and behavioral indicators  
- Implement data analytics features (daily reports, trends, insights)  

Garret Rieden
- Design and refine circuitry for servo motors and Raspberry Pi Pico (laser toy system)  
- Assist with general hardware wiring and circuit integration across components  
- Implement PIR motion sensor for cat detection and activity tracking  
- Support development of cat sentiment analysis (hardware and integration support)  

Yuxuan Liu
- Implement database layer for persistent data storage  
- Support integration between hardware and backend systems
- Research feline health metrics and behavioral indicators 
- Implement data analytics features (daily reports, trends, insights)  

### Adam Rieden
- Implement cat body weight tracking system (scale integration)  
- Develop water level sensing system (separate from weight-based measurement)  
- Build audio system for meow detection and voice playback  
- Implement temperature and humidity monitoring system  

## 8. Demo Plan
The demo will simulate a real user scenario where the system detects and responds to changes in food and water levels.”

1. Hardware Modules (Individual Demonstrations)
- Demonstrate water bowl auto-refill to target weight
- Demonstrate food bowl auto-refill to target weight
- Showcase auger-based food dispensing mechanism

2. Real-Time Web Interface
- Display live food and water levels on the website
- Show values updating as bowls are filled/emptied

3. Livestream + Remote Interaction
- Show live camera feed
- Demonstrate controlling laser toy via servo motors through the interface

4. Audio-Based Behavior Detection
- Play prerecorded cat meows
- Show system classifying cat mood based on audio input

5. Full System Integration
- Remove food/water → system detects change
- Web app updates in real time
- System automatically refills to target level 


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

Yuxuan
- Helped build and test the software system

## 10. Conclusion
Brief reflection on current status, remaining challenges and plans.
At the current stage, Catopia has successfully progressed from a conceptual design into a working prototype with both hardware and software subsystems in place. The project now includes a functioning communication pipeline between the frontend dashboard, backend server, and Raspberry Pi Pico, along with operational hardware components such as the water pump, force sensors, servo motors, and camera module. These milestones demonstrate that the core smart-home infrastructure for automated cat care is functioning as intended.

Despite this progress, several important challenges remain. Sensor calibration, particularly for accurate weight measurement, still requires refinement to ensure reliable food and water tracking. In addition, the integration of long-term data storage, live video streaming, and cat emotion analysis through audio and visual inputs remains an ongoing development focus. Power management and ensuring stable hardware performance independent of a wall outlet are also key technical issues that must be resolved.

Moving forward, the team plans to complete full hardware integration, improve system reliability, implement database support for historical data analysis, and finalize the remaining smart features for the live demonstration. Overall, the project is on track toward delivering a stable and comprehensive smart cat home system by the final presentation.
## References
- Datasheets
- Research papers
  - JL-TFMSFNet: https://www.sciencedirect.com/science/article/pii/S0957417424014878#d1e1222
- Projects you get ideas from - GitHub repositories-
  - DeepCat: https://github.com/Arwa-Fawzy/Cat-Emotional-Analysis?tab=readme-ov-file
