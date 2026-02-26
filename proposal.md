# Project Title - Proposal


## 1. Team Information
- **Team Name:** Catopia
- **Team Members:**
  - **Matthew Yue** (matthewyue@brandeis.edu) – Role  
  - **Garret Rieden** (grieden11@brandeis.edu) – Role  
  - **Adam Rieden** (arieden@brandeis.edu) – Role  
  - **Yuxuan Liu** (yuxuanliu050613@brandeis.edu) – Role  
- **Github Repository:** https://github.com/MatthewYyf/catopia-smart-home.git


## 2. Abstract
Provide a concise summary (150–250 words) describing:
- The problem you are addressing:
We want to help treat and care for your cat more consistently. The problem we have found is that most cats are not cared for enough as owners are either under the misconception that cats are low maintenance or are away for long periods of time. Cats, therefore, become depressed and it's difficult for owners to see changes in their cats health, especially if the changes are small and would only be noticed if they were around their cat more often.
- Brief description about your proposed project:
We are here to make an all-intelligent home for the owners to get for their cats and themselves. The cat home, Catopia, will allow the owner to monitor and care for their cat. Catopia will track and store data each day from each of the many sensors, like water intake, food intake, temperature and humidity tracker, camera's, and mic.
- Key technologies involved:
We will have a lot of sensors to track your cats health and use data that data to display on the app. The cat house will have motors, bluetooth, and audio/visual modules to interact with your cat through the app as well. 
- Expected outcomes or impact:
We think the impact of this project will help lead to more awareness for cat health and making sure they are being properly cared for. A great outcome that we see when you can monitor and play with your cat more is that the cat will be and stay healthy. 


## 3. Objectives
The main objectives of this project are:
- List the specific goals of the project
-   Create working water pump, water weight sensor
-   Create toy controlled by motor
-   Implement working emotion determination
-   


## 4. Proposed Solution
Describe the details about your project

- Health Monitoring:
  - Food) To determine how much food will be in the bowl, a weight will be under the food bowl. Once a certain weight is hit, the food dispenser will halt.
  - Water) To determine how much water will be in the bowl, a water level monitor will be attached to the bowl. Once a certain level is met, the water pump will halt.
   
- Engagement:
  - Laser Pointer) Using a servo motor and attaching a laser pointer, we will be able to move the pointer through the app. This toy will most likely be mounted to the housing enclosure/near a camera, so you can see your cat playing in real time
  
- Emotional Determination:
  - Video) Using a camera and Pi, we will analyze (with the help of DeepCat, mentioned more below) the cat's body language and relay that with audio component. 
  - Audio) Using an audio sensor and Pi, we will analyze (with the help of JL-TFMSFNet, mentioned more below) the cat's vocals and input with the cat's body language to determine the cat's emotional state.
  - Screen) Using a screen, we will display the cat's emotional state through words.
  


### 4.1 Project Description
High-level description of the system.
As detailed as possible.
Catopia is a smart cat home system that integrates automated care, health monitoring, and emotional analysis into one connected platform. The system uses two computing units: a Raspberry Pi Pico W for sensor data collection and actuator control, and a Raspberry Pi 5 for data processing, storage, and backend services.

The Pico collects data from sensors measuring food intake (load cells), water level, temperature, humidity, motion, and audio. It also controls actuators such as the water pump and a servo-powered laser toy. Sensor data is serialized in JSON and sent via USB serial to the Raspberry Pi 5.

The Raspberry Pi 5 stores data in an SQLite database and performs higher-level analysis. For emotional detection, the system uses DeepCat for video-based body language analysis and JL-TFMSFNet for audio-based vocal analysis. These outputs are combined to estimate the cat’s emotional state.

A mobile iOS app connects to the backend through REST APIs and WebSockets, allowing users to monitor real-time data, view historical trends, watch live video via HLS, receive alerts, and remotely control interactive features.

Overall, Catopia separates sensing, processing, and user interaction into clear layers, creating a modular and scalable smart pet care system.

### 4.2 Hardware Components
| Component | Description | Quantity |
|---------|-------------|----------|
| Raspberry Pi + Pico | Main controller | 1 |
| Load Cells | Weight Sensor | 2 |
| Temperature & Humidity Sensor | Measure temp in cat sleeping area | 1 |
| PIR Infrared Sensor | Locate Cat | 1 |
| Camera Module | Watch cat from App | 1 |
| Water Level Monitor | Check how much water is in the bowl | 1 |
| Servo Motor | Move Cat Toy | 1 |
| Water Pump | Pour water into cat bowl | 1 |
| Wi-fi / Bluetooth module | Connect modules and to app | 1 |
| Housing Enclosure | Main structure everything surrounds or mounted on | 1 |
| Food-safe containers | For food and water storage | 2 |
| Tubes | For water system | 2 |
| Mounting brackets + wiring | For all cat equipment | 4 |
| Audio Sensor | To listen to cat | 1 |
| Screen | To relay cat's emotional state | 1 |

- Schematic 

### 4.3 Software Components
- Libraries / Frameworks
-   JL-TFMSFNet: https://www.sciencedirect.com/science/article/pii/S0957417424014878#d1e1222
-   DeepCat: https://github.com/Arwa-Fawzy/Cat-Emotional-Analysis?tab=readme-ov-file
- - MicroPython (Pico W)
- - libcamera (Pi 5)
- - Flask / FastAPI (backend)
- - SQLite (database)
OpenCV (optional video processing)
- Communication Protocols (e.g., I2C, SPI, MQTT)
- - USB Serial (Pico → Pi 5)

- - WiFi (Pi 5 → Mobile)

- - HTTP REST API

- - RTSP / HLS (video streaming)

- - JSON (data format)
- Software structure
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

The Catopia system consists of two computing units: a Raspberry Pi Pico as an embedded controller and a Raspberry Pi 5 as a backend server. The Pico, primarily programmed using Micro Python, is responsible for sensor data acquisition and actuator control. Sensor readings are serialized in JSON format and transmitted to the Raspberry Pi 5 via USB serial communication.  

Multiple communication protocols are employed to separate functions across system components. USB Serial is used for reliable data transmission between the Raspberry Pi 5 and Pico. HTTP enables retrieval of the historical data and control commands across the server and mobile application. WebSocket is able to support real-time sensor updates and alert notifications.
HLS (HTTP Live Streaming) is used for video delivery and HLS is easier to implement through IOS system.
JSON is used as the standardized data exchange format across all software layers.  

The designed interface for user is through mobile app under IOS system environment. Users can view real-time environmental and  daily intake data, historical trend visualizations, and system healthy alerts. Also, the interactive controls allow remote activation of actuators such as the laser point. A media view enables live video streaming through HLS playback using AVPlayer.

Frst of all, Pico will collect data from each sensors and serialized into JSON data object. After that, the data is transmitted through USB serial to the Raspberry Pi 5. Then it will be stored in the SQLite database, and processed for analysis.
When the mobile application requests historical data, it retrieves data through RESTful API endpoints. For real-time monitoring, the backend pushes live updates to the client via WebSocket connections. Simultaneously, the Raspberry Pi Camera captures video, which is served through HLS streaming to the mobile app. This structured data flow ensures clear separation between acquisition, processing, storage, and presentation layers.


## 5. Methodology
Explain how the project will be developed:
  1. Requirement analysis
Functional requirements include automatic food and water replenishment, automatic litter box cleaning, and stable data and video transmission to the mobile client. The client also needs to support data analysis, remote actuator control, and real-time video calls. Non-functional requirements include a load cell for accurate weight detection with an error range of ±10g, and an air quality sensor. The camera must provide stable video input.

  2. Hardware setup
Hardware module will be individually validated before integration. Load cells will be tested using known reference weights. Environmental sensors will be verified through standard thermometers and hygrometers. The actuator will undergo functional and durability testing to ensure its reliability.

  3. Software development


  4. Integration and testing

       
  5. Deployment


## 6. Timeline
As detail as possible.
7 weeks left to make this project
| Phase | Activities | Duration |
|------|------------|----------|
| Phase 1 | Research & Planning | 1 weeks |
| Phase 2 | Development | 3 weeks |
| Phase 3 | Testing | 2 week |
| Phase 4 | Final Deployment | 1 week |


## 7. Expected Outcomes
- Functional prototype:
We definetly think we will have a functional prototype and can refine the app and logic. 
- Measurable performance metrics:
Our database will store all the data from the sensors and all other modules that collect data. This will be displayed on the app and made easy to see for the user. Perfomance metrics that will be included is water intake, food intake, temperature, humidity, cat weight, toy playing time, and cat emotional determination. 
- User or system benefits:
The benefits for the user is that they can track their cat's health easier and can see flucuations in data even if it is not noticable just by looking at your cat. This can keep the cat healthy and the user informed on their cats health. 


## 8. Conclusion
Summarize the project’s value and feasibility.
The pet industry is a huge market, with a global valuation of $273 billion market cap. Clearly, the pet owners will spend some serious dough when trying to make their pet's lives happy and healthy. Due to pet owner's wanting the best for their pet, the value of Catopia will be massive, as our project helps solve potential issues any cat owner might face: Busy or unpredictable day-to-day schedules, non-perfect monitoring of their pet, inability to interact with their pet when the owner is away etc.
Due to the fact that most of our components are modular and will eventually be integrated into a full system, the modular components are extremely feasbile. We are using them exactly how they were designed, but connecting these modular components to the app will be a harder challenge. If we can figure out how to create an app with connections to our module's, we believe we can fully push out Catopia.

## References
- Datasheets
- Research papers
- Projects you get ideas from - GitHub repositories

