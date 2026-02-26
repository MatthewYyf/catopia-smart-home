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
-   We want to help treat and care for your cat more consistently.
-   The problem we have found is that most cats are not cared for enough
-   as owners are either under the misconception that cats are low maintenance or are away for long periods of time.
-   Cats, therefore, become depressed and it's difficult for owners to see changes in their cats health, especially if the changes are small and
-   would only be noticed if they were around their cat more often.
- Brief description about your proposed project:
-   We are here to make an all-intelligent home for the owners to get for their cats and themselves.
-   The cat home, Catopia, will allow the owner to monitor and care for their cat.
-   Catopia will track and store data each day from each of the many sensors, like water intake, food intake, temperature and humidity tracker,
-   camera's, and mic.
-   
- Key technologies involved:
-   We will have a lot of sensors to track your cats health and use data that data to display on the app.
-   The cat house will have motors, bluetooth, and audio/visual modules to interact with your cat through the app as well. 
- Expected outcomes or impact:
-   We think the impact of this project will help lead to more awareness for cat health and making sure they are being properly cared for.
-   A great outcome that we see when you can monitor and play with your cat more is that the cat will be and stay healthy. 


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
  - Video) Using a camera and Pi, we will analyze the cat's body language and relay that with audio component.
  - Audio) Using an audio sensor and Pi, we will analyze the cat's vocals and input with the cat's body language to determine the cat's emotional state.
  - Screen) Using a screen, we will display the cat's emotional state through words.
  


### 4.1 Project Description
High-level description of the system.
As detailed as possible.

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
| Mounting brackets + wiring | For all cat equipment | ? |
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

      
2. Hardware setup
Hardware module will be individually validated before integration. Load cells will be tested using known reference weights. Environmental sensors will be verified through standard thermometers and hygrometers. The actuator will undergo functional and durability testing to ensure its reliability.
3. Software development


    
4. Integration and testing

       
5. Deployment
    


## 6. Timeline
As detail as possible.
| Phase | Activities | Duration |
|------|------------|----------|
| Phase 1 | Research & Planning | X weeks |
| Phase 2 | Development | X weeks |
| Phase 3 | Testing | X weeks |
| Phase 4 | Final Deployment | X weeks |


## 7. Expected Outcomes
- Functional prototype
- Measurable performance metrics
- User or system benefits


## 8. Conclusion
Summarize the project’s value and feasibility.


## References
- Datasheets
- Research papers
- Projects you get ideas from - GitHub repositories

