# Final - Proposal


## 1. Team Information
- **Team Name:** Catopia
- **Team Members:**
  - **Matthew Yue** (matthewyue@brandeis.edu) – Mechanical Engineer & Data Scientist
  - **Garret Rieden** (grieden11@brandeis.edu) – Hardware Engineer
  - **Adam Rieden** (arieden@brandeis.edu) – Frontend Developer
  - **Yuxuan Liu** (yuxuanliu050613@brandeis.edu) – Backend Developer
- **Github Repository:** https://github.com/MatthewYyf/catopia-smart-home.git
- **Demo Link:** (if any)


## 2. Abstract
Provide a concise summary (150–250 words) describing:
- The problem you are addressing
  -  We want to help treat and care for your cat more consistently. The problem we have found is that most cats are not cared for enough as owners are either under the misconception that cats are low maintenance or are away for long periods of time. Cats, therefore, become depressed and it's difficult for owners to see changes in their cats health, especially if the changes are small and would only be noticed if they were around their cat more often.
- Brief description about your proposed project
  - Catopia is an integrated smart home system designed to automate and monitor essential aspects of cat care. The system enables owners to remotely track and manage their pet’s food intake, water consumption, environmental conditions, and behavior through a connected hardware and software platform.
- Key technologies involved
  - 
- Final results and impact
  - 

## 3. Project Details
Describe the details about your project

### 3.1 Project Description
High-level description of the system.
As detailed as possible.

### 3.2 Hardware Components
| Component | Description | Quantity |
|---------|-------------|----------|
| Raspberry Pi | Main controller | 1 |
| Raspberry Pico | Perform specific tasks | 4 |
| Load Cell | Weight Sensor | 3 |
| Camera Module | Watch cat from App | 1 |
| Servo Motor | Move Cat Toy/Laser | 2 |
| Water Pump | Pour water into cat bowl | 1 |
| Wi-fi / Bluetooth module | Connect modules and to app | 1 |
| Housing Enclosure | Main structure everything surrounds or mounted on | 1 |
| Food-safe containers | For food and water storage | 2 |
| Tube | For water system | 1 |
| Mounting brackets + wiring | For all cat equipment | 4 |
| Mic Array | To listen to cat's emotional state | 1 |
| Bluetooth Speaker | Play owners voice memos | 1 |
| Breadboard | Have multiple components for 1 pico | 3 |



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
  - Wiring and getting the correct amount of power to each of the hardware components was quite challenging. Also connecting the individual picos to the pi was difficult as sometimes they would connect and the pi would succesfully send them a signal, but sometimes it wouldn't work. Calibrating the load cell was also difficult since the load cells only output raw data that doens't actually make sense so we had to use a known weight to calibrate what the load cell was outputting to a known weight. 

- Design constraints
  - Some design constraints is that ...

- What didn’t work as expected
  - We couldn't get the laser to be controlled by the owner through the website, so we instead made the laser mounted on the servo move randomly. We couldn't get the water pump to successfuly be turned off by the pi, it could only be turned on and then the signal to stop it wouldn't work. This still resulted in what we wanted, a continuous flow of water, but not being able to turn off the water pump was not as planned.

- Potential enhancements
  - Some enhancements would be getting the laser to move through the owners control. Another enhancement would be getting the food dispenser to be quieter as when it ran it was very loud and startling. 

- Features you would add with more time
  - We would add with more time a fully automated litter box. Another feature would be more toys for the cat to play with as just a laser isn't going to always get your cat to play. 

## 5. Demo Description
Explain your (recorded) demo:
- How the system works in real time
- Key highlights
  
- Laser Demo:
  - https://drive.google.com/file/d/1DWTcacsNxB1oIhDAYuLIpRMXL6QAB6eC/view?usp=sharing
  - 
- Water Bowl Pic:
  - https://drive.google.com/file/d/1kDaP6NASZN5hE8LF6nr4L-T4qRU9bAZl/view?usp=sharing
  - The water bowl has a 1 channel relay along with a load cell with hx711 board wired to a breadboard connected to an external power source. The system works by the owner on the website clicking a button to have the pi send a signal to the pico to turn the water pump on, then the water pump recieves the signal and turns on then the load cell is tracking the weight of the water bowl.
 
  
## 6. Contributions
List each member’s contributions:
- Name: specific tasks completed
- Adam: Pressure Sensor wiring and starter code(outdated), Water pump wiring and starter code, Load cells wiring/starter code/found 3d model, Assembled the cat house, Found dataset for cat meows, Website/microphone code to record and store owners voice memos, Bluetooth speaker setup

## 7.Conclusion
Summarize:
- What you built
  - We built a modular cat house for the owner to be able to keep track of their cats health through many different sensors and keep them happy.

- What you learned
  - We learned many things. One is that 3d printing takes a long time, and sometimes the first attempt doesn't work but on the second try it does. Another thing is that we learned how circuits work. That was really important in our project as we had many many hardware components that needed to be wired together and each have enough power to work. We also learned that waiting to test our system later was what caused many problems as we didn't have enough time to troubleshoot all the issues and get everything fully working together. 

- Overall success of the project
  - We think the project was relatively pretty succesful since we did get every module to work fully, but we weren't able to attach everything to the cat house. 

## References
- Datasheets
  - https://zenodo.org/records/4008297 - cat meows
- Research papers
  - JL-TFMSFNet: https://www.sciencedirect.com/science/article/pii/S0957417424014878#d1e1222
- Projects you get ideas from - GitHub repositories-
  - DeepCat: https://github.com/Arwa-Fawzy/Cat-Emotional-Analysis?tab=readme-ov-file

