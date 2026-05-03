# Project Title - Proposal


## 1. Team Information
- **Team Name:**
- **Team Members:**
  - **Name** ([yourmail@brandeis.edu](mailto:yourmail@brandeis.edu)) – Role  
- **Github Repository:**
- **Demo Link:** (if any)


## 2. Abstract
Provide a concise summary (150–250 words) describing:
- The problem you are addressing  
- Brief description about your proposed project
- Key technologies involved  
- Final results and impact  

## 3. Project Details
Describe the details about your project

### 3.1 Project Description
High-level description of the system.
As detailed as possible.

### 3.2 Hardware Components
| Component | Description | Quantity |
|---------|-------------|----------|
| Raspberry Pi pico w | Main controller | 1 |
| Sensor / Module | Purpose | X |
| Power Supply | Rating | 1 |

- Schematic 

### 3.3 Software Components
Catopia’s software system is composed of three main layers, embedded firmware on the Raspberry Pi Pico devices, a Python backend server running on the Raspberry Pi, and a browser-based frontend dashboard. 

First of all, the backend layer is implemented in Python using FastAPI and Uvicorn. FastAPI provides the REST API used by both the frontend and the Pico firmware, while Uvicorn runs the application as a local web server on port 8000. The backend serves the main web interface from backend/static/index.html, receives telemetry from the Pico devices, stores the latest device state, records consumption events, manages reports, and queues hardware commands. The server supports both device-specific endpoints and backward-compatible endpoints. 

The backend also includes a lightweight SQLite database. Its primary objective is to permanently store the data regarding user’s cats within the Catopia System. The database schema contains three main tables,  daily_reports, voice_logs, and consumption_events.  Meanwhile, within the backend/db/queries.py, we have implemented functions designed to interact with the database. For example, a function that returns a daily report simply by accepting a specific date as input. This capability allows us to retrieve the desired information from the database more efficiently and conveniently on the frontend. The daily_report  table primarily serves to store daily records of the cat's food intake, water consumption, and body weight. Furthermore, on the frontend reporting page, we utilize functions from the  queries.py to visualize the cat's water intake trends over the preceding seven days. Variations in water intake can serve as an indicator of the cat's renal function status, thereby providing users with timely feedback regarding their cat's health. The voice_logs table is responsible for storing the emotional tags detected from the cat's vocalizations during each run of the affection detection pipeline. Finally, the consumption_events table records the specific food intake quantity determined during each execution of the `backend/services/consumption_tracker.py` script. Its primary objective is to help tracking  the cat's total daily food consumption. 

A key backend service is the consumption tracking system in backend/services/consumption_tracker.py.  We observed that when a cat is eating, the sensor data may be subject to increased noise. For instance, if the cat steps directly onto the sensor. Consequently, we cannot simply determine the amount of food consumed by merely calculating the change between consecutive sensor readings. To address this, we developed `backend/services/consumption_tracker.py`. The tracker begins by recording the five most recent sensor reading. It then utilizes the median value, instead of mean, to prevent sudden spikes or drops in individual readings from skewing the results. If the median values across several consecutive measurement windows remain relatively consistent, the system flags the current state as "stable." Finally, the system compares the readings from two distinct stable states. If a decline is detected, the system validates it as a legitimate instance of food consumption.

MEOW Analysis: 

Camera module:

The frontend is a single-page browser dashboard built with HTML, CSS, and JavaScript. It communicates with the backend using the browser fetch() API. The dashboard includes pages for testing live load sensor readings, viewing food and water status, controlling the feeder, controlling the laser toy, viewing the camera stream, checking vocalization results, recording voice memos, and viewing reports. The frontend polls the backend every second for live state updates, then displays values such as current load, filtered load, stable state, baseline value, session total, and daily total. It also sends control commands, such as DISPENSE, PUMP_ON/OFF.

The embedded software is written in MicroPython and organized under the firmware directory. Each Pico folder represents a specific hardware subsystem.   pico_1 handles the pan/tilt laser toy using PWM-controlled servo motors and a laser module. pico_2 is designed for the kibble dispenser, using a stepper motor and HX711-based load sensor to dispense a target amount of food. pico_3  is the water supply subsystem that refill the water tank by controlling the pump and using a load cell to record the cat’s water intake. The firmware connects to the local Catopia Wi-Fi network, sends JSON telemetry to the backend about once per second, and polls the backend for queued commands. 

Catopia uses a two-direction data flow. Sensor data moves upward from the hardware to the user interface, while user commands move back downward from the dashboard to the physical devices. On the data side, sensors and actuators first interact with the real cat home environment. Load cells measure food or water weight, the pump controls water output, the feeder controls food dispensing, and the servo motors control the laser toy. These components are connected to Raspberry Pi Pico and it will send telemetry as JSON data through HTTP requests over the local Catopia network to the Raspberry Pi Fast API backend. The backend acts as the central communication layer. It stores the latest device state, processes sensor readings, and saves important records.  The frontend dashboard retrieves data from the backend and displays live system status, food and water data, camera feed, vocalization results, and reports. When the user sends a command, such as dispensing food or turning on the pump, the frontend sends it to the backend. The backend queues the command, and the correct Pico retrieves and executes it on the hardware.


### 3.4 Overall Control Flow

## 4. Challenges and Limitations
- Technical challenges
- Design constraints
- What didn’t work as expected
- Potential enhancements
- Features you would add with more time

## 5. Demo Description
Explain your (recorded) demo:
- How the system works in real time
- Key highlights

## 6. Contributions
List each member’s contributions:
- Name: specific tasks completed
  
## 7.Conclusion
Summarize:
- What you built
- What you learned
- Overall success of the project

## References
- Datasheets
- Research papers
- Projects you get ideas from - GitHub repositories

