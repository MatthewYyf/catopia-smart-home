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

Cats can experience boredom, stress, and loneliness when their owners are away for long periods. These issues may appear through changes in eating, drinking, activity, or vocalization, but owners often cannot observe these behaviors in real time. This creates a gap between a cat’s daily needs and the owner’s ability to monitor or respond while not at home.

Our proposed project is a smart cat house that supports remote cat care through monitoring, automation, and interactive features. The system tracks food and water intake, provides a live camera feed, detects cat vocalizations, and allows the owner to remotely trigger actions such as feeding or laser play. The goal is to create a more responsive environment that supports the cat’s routine and mental stimulation.

The system uses a Raspberry Pi as the central controller, running the FastAPI backend, frontend dashboard, camera stream, database, and audio processing. Raspberry Pi Pico microcontrollers control hardware modules such as load cells, the water pump, food dispenser, and pan-tilt laser system. The system also uses REST APIs, HX711 load cell amplifiers, servos, a stepper motor, microphone input, and HMM-based vocalization recognition.

The final prototype demonstrates successful integration of these components into one connected system. However, it was not tested on real cats, so its real-world impact is unclear. The project is best understood as a proof of concept for future smart pet care systems.

## 3. Project Details
Describe the details about your project


### 3.1 Project Description

Catopia is a smart cat care system designed to help owners monitor and support their cat’s daily needs when they are not physically present. The system combines food dispensing, water tracking, live monitoring, interactive play, and cat vocalization analysis into one connected platform. The main goal is to create a proof-of-concept embedded system that can collect useful behavioral and health-related data while also allowing the owner to remotely interact with the cat.

At the center of the system is a Raspberry Pi, which acts as the main server and control hub. The Raspberry Pi runs a FastAPI backend that receives sensor data, stores system state, serves the frontend dashboard, and sends commands to the hardware devices. It also controls higher-level components such as the camera, microphone, and audio processing system. The web dashboard allows the user to view live system data, check food and water levels, access the camera stream, review reports, and send commands such as dispensing food, turning on the water fountain, or starting the laser play system.

The hardware is divided across multiple Raspberry Pi Pico microcontrollers. Each Pico is responsible for a specific subsystem so that the workload is separated and easier to manage. One Pico controls the food system, including a stepper motor-driven kibble dispenser and a load cell that measures the amount of food in the bowl. Another Pico controls the water system, including a pump and a load cell that tracks changes in water weight. A separate control module handles the pan-tilt laser system, which uses servos to move a laser pointer in randomized patterns for interactive play. Additional load cells can be used to estimate cat body weight when the cat steps onto a platform or designated area.

The food dispenser uses a motorized auger mechanism to move kibble from a storage container into the bowl. A load cell measures the current food weight, allowing the system to stop dispensing once the target amount is reached. The dispenser can also slow down as the measured food weight approaches the target, reducing overshoot and making the system more accurate. The water system follows a similar idea. The pump can refill or circulate water, while the load cell tracks how much water is present and how much the cat may have consumed over time.

The system also includes a camera stream so the owner can visually check on the cat through the web interface. This is especially useful for confirming whether the cat is eating, drinking, playing, or resting. The microphone component is used to record and analyze cat vocalizations. Audio features such as MFCCs can be extracted from recorded sounds, and machine learning models can classify vocalizations into contexts such as food-related, isolation-related, or brushing-related sounds. This is intended to give the owner a rough sense of the cat’s emotional or behavioral state, especially when the owner is away.

Communication between devices is handled through local HTTP API endpoints. The Pico devices send telemetry data to the backend, such as food weight, water weight, pump state, motor state, and other sensor readings. The backend stores the latest values in memory and may also save longer-term events in a database. The frontend requests state data from the backend to keep the dashboard updated. Commands flow in the opposite direction: the user sends a command from the dashboard to the backend, and the Pico devices periodically check for pending commands. This structure allows the system to support both real-time monitoring and remote control.

The backend organizes the data into several categories. Telemetry refers to raw readings sent from the devices to the server. State refers to the latest system values shown on the dashboard. Consumption data is derived from telemetry and includes food and water intake events, totals, and trends. Reports summarize daily activity and may include feeding behavior, water intake, vocalization events, and system usage. This makes the project more than just a hardware controller; it also acts as a data collection and analytics platform for cat care.

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

![Hardware Architecture](Hardware_Schematic.png)

Raspberry Pi represents the main computing and coordination layer of the system. It runs the backend server, manages communication with the Pico, processes sensor and device data, and connects higher-level peripherals such as the camera, microphone, and speaker.

The Pico controllers represent the hardware control layer. Each Pico is assigned to a specific subsystem. Pico 1 represents the interactive laser toy subsystem, controlling the pan-tilt servos and laser module. Pico 2 represents the feeding subsystem, controlling the kibble dispenser mechanism. Pico 3 represents the water subsystem, controlling the water pump and a load cell to track the water intake. Pico 4 represents the weight-sensing subsystem, reading data from a dedicated load cell.

The green connections represent peripherals that are connected directly to the Raspberry Pi. The camera provides the live video feed, the microphone collects audio for cat vocalization recognition, and the speaker supports audio output or voice playback.




### 3.3 Software Components
Catopia’s software system is composed of three main layers, embedded firmware on the Raspberry Pi Pico devices, a Python backend server running on the Raspberry Pi, and a browser-based frontend dashboard. 

First of all, the backend layer is implemented in Python using FastAPI and Uvicorn. FastAPI provides the REST API used by both the frontend and the Pico firmware, while Uvicorn runs the application as a local web server on port 8000. The backend serves the main web interface from backend/static/index.html, receives telemetry from the Pico devices, stores the latest device state, records consumption events, manages reports, and queues hardware commands. The server supports both device-specific endpoints and backward-compatible endpoints.

The backend also includes a lightweight SQLite database. Its primary objective is to permanently store the data regarding user’s cats within the Catopia System. The database schema contains three main tables,  daily_reports, voice_logs, and consumption_events.  Meanwhile, within the backend/db/queries.py, we have implemented functions designed to interact with the database. For example, a function that returns a daily report simply by accepting a specific date as input. This capability allows us to retrieve the desired information from the database more efficiently and conveniently on the frontend. The daily_report  table primarily serves to store daily records of the cat's food intake, water consumption, and body weight. Furthermore, on the frontend reporting page, we utilize functions from the  queries.py to visualize the cat's water intake trends over the preceding seven days. Variations in water intake can serve as an indicator of the cat's renal function status, thereby providing users with timely feedback regarding their cat's health. The voice_logs table is responsible for storing the emotional tags detected from the cat's vocalizations during each run of the affection detection pipeline. Finally, the consumption_events table records the specific food intake quantity determined during each execution of the `backend/services/consumption_tracker.py` script. Its primary objective is to help tracking  the cat's total daily food consumption. 

A key backend service is the consumption tracking system in backend/services/consumption_tracker.py.  We observed that when a cat is eating, the sensor data may be subject to increased noise. For instance, if the cat steps directly onto the sensor. Consequently, we cannot simply determine the amount of food consumed by merely calculating the change between consecutive sensor readings. To address this, we developed `backend/services/consumption_tracker.py`. The tracker begins by recording the five most recent sensor reading. It then utilizes the median value, instead of mean, to prevent sudden spikes or drops in individual readings from skewing the results. If the median values across several consecutive measurement windows remain relatively consistent, the system flags the current state as "stable." Finally, the system compares the readings from two distinct stable states. If a decline is detected, the system validates it as a legitimate instance of food consumption.

Vocalization Recognition:

The goal of this system is to recognize and classify cat meows into three behavioral contexts: food-seeking, isolation, and brushing. To do this, we trained a separate Hidden Markov Model (HMM) for each context using audio recordings labeled under that category. The reason we chose HMMs is that a meow isn't a single, static sound — it evolves over time in terms of pitch, intensity, and spectral content, and HMMs are well-suited to modeling this kind of temporal structure.

To prepare the audio for classification, we extracted Mel-Frequency Cepstral Coefficient (MFCC) features from each recording. The audio was divided into short 30 ms frames with a 10 ms hop between them, and each frame was represented as a 52-dimensional feature vector consisting of 13 MFCC coefficients along with their first and second derivatives. Together, these frame-level vectors form a sequence that captures how the sound changes from start to finish. Before feeding this into the model, we applied z-score normalization to each sequence, which helps reduce variability caused by differences in microphone gain or recording conditions.

Each HMM models the meow as a progression through a series of hidden acoustic states, where each state corresponds to a distinct spectral pattern in the vocalization. To model the feature distribution within each state more accurately, we used a Gaussian Mixture Model (GMM) rather than a single Gaussian, which gives the system more flexibility to capture complex acoustic variation. The models were trained using the Baum-Welch algorithm, which iteratively updates the state transition probabilities and GMM parameters to best fit the training data for each class.

When classifying a new meow, the audio sequence is passed through all three HMMs, and each model computes a log-likelihood score representing how well it explains the observed features. The class whose model produces the highest score is selected as the predicted context — so if the food-related HMM returns the highest log-likelihood, the meow is classified as food-seeking behavior.

One practical challenge we had to address was preventing the system from trying to classify silence or background noise. To handle this, we set an energy threshold on the microphone input: the system continuously monitors incoming audio and calculates the root mean square (RMS) energy of each frame as a proxy for loudness. Frames that fall below the threshold are discarded before any feature extraction takes place, reducing unnecessary computation. Once the energy level exceeds the threshold, the system begins buffering audio until either a minimum clip duration is reached or silence is detected again. We then applied WebRTC voice activity detection to trim any remaining silence from the beginning or end of the clip. This ensures that the HMM receives a clean, complete vocalization rather than a truncated or noisy fragment.

Camera module:

The frontend is a single-page browser dashboard built with HTML, CSS, and JavaScript. It communicates with the backend using the browser fetch() API. The dashboard includes pages for testing live load sensor readings, viewing food and water status, controlling the feeder, controlling the laser toy, viewing the camera stream, checking vocalization results, recording voice memos, and viewing reports. The frontend polls the backend every second for live state updates, then displays values such as current load, filtered load, stable state, baseline value, session total, and daily total. It also sends control commands, such as DISPENSE, PUMP_ON/OFF.

The embedded software is written in MicroPython and organized under the firmware directory. Each Pico folder represents a specific hardware subsystem.   pico_1 handles the pan/tilt laser toy using PWM-controlled servo motors and a laser module. pico_2 is designed for the kibble dispenser, using a stepper motor and HX711-based load sensor to dispense a target amount of food. pico_3  is the water supply subsystem that refill the water tank by controlling the pump and using a load cell to record the cat’s water intake. The firmware connects to the local Catopia Wi-Fi network, sends JSON telemetry to the backend about once per second, and polls the backend for queued commands. 

Catopia uses a two-direction data flow. Sensor data moves upward from the hardware to the user interface, while user commands move back downward from the dashboard to the physical devices. On the data side, sensors and actuators first interact with the real cat home environment. Load cells measure food or water weight, the pump controls water output, the feeder controls food dispensing, and the servo motors control the laser toy. These components are connected to Raspberry Pi Pico and it will send telemetry as JSON data through HTTP requests over the local Catopia network to the Raspberry Pi Fast API backend. The backend acts as the central communication layer. It stores the latest device state, processes sensor readings, and saves important records.  The frontend dashboard retrieves data from the backend and displays live system status, food and water data, camera feed, vocalization results, and reports. When the user sends a command, such as dispensing food or turning on the pump, the frontend sends it to the backend. The backend queues the command, and the correct Pico retrieves and executes it on the hardware.


### 3.4 Overall Control Flow

The system is built around the Raspberry Pi, which acts as the central controller, and several Raspberry Pi Pico microcontrollers, each responsible for managing a specific hardware subsystem. The Pi handles all the higher-level software — including the FastAPI backend, the frontend dashboard, the database, the camera stream, and audio processing — while each Pico focuses on one physical subsystem, such as food dispensing, water control, load sensing, or the pan-tilt laser module.

On startup, each Pico connects to the Wi-Fi network and enters a continuous operating loop. In each cycle, it reads from its local sensors, sends telemetry data to the backend, checks whether any new commands have been issued, and actuates its hardware accordingly. The telemetry payload varies by device but typically includes values like food weight, water weight, pump status, servo position, and dispenser activity. The backend stores the most recent state from each device and logs significant events, such as a drop in food or water levels indicating consumption.

The frontend never communicates directly with the hardware. Instead, all user interactions go through the backend. When a user triggers an action, for example manually dispensing food, the frontend sends a request to the backend, which places the appropriate command into a queue associated with the target Pico. The Pico periodically polls its command endpoint, picks up any pending instructions, executes them locally, and then resumes sending updated telemetry as usual.

This creates a clean, repeating cycle: sensors feed data to the backend, the backend maintains the current system state, the frontend reflects that state to the user, user or automated actions generate commands, and the Picos carry those commands out. Structuring the system this way keeps each component loosely coupled, which makes the overall system easier to debug and straightforward to extend if additional devices or subsystems need to be added in the future.

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
- Adam: Pressure Sensor wiring and starter code(outdated)<br>
        Water pump wiring and starter code<br>
        Load cells wiring/starter code/found 3d model<br>
        Assembled the cat house<br>
        Found dataset for cat meows<br>
        Website/microphone code to record and store owners voice memos<br>
        Bluetooth speaker setup<br>
- Yuxuan: Implemented database layer and consumption_tracker service for backend<br>
          Help build and test the backend server and frontend dashboard<br>
          Help developed the Pico firmware<br>
          Caliboration for Load cell<br>
          3D printing<br>
    
## 7.Conclusion
Summarize:
- What you built
  - For this project, we built a fully integrated prototype of a smart cat care system that combines hardware, software, sensing, automation, and data analytics into one connected platform. The system was designed to support both the physical and mental health of a cat, especially when the owner is not present. On the hardware side, we connected multiple embedded components, including Raspberry Pi Pico microcontrollers, load cells, servos, a water pump, a food dispensing mechanism, a camera, a microphone, and other supporting circuitry. These components worked together to monitor the cat’s environment and control different care features.

  - A major part of the project was the data collection and analytics pipeline. The system collects physical health data such as food consumption, water consumption, and weight-related measurements. It also collects behavioral and mental health indicators through audio input and interactive play features. The backend receives telemetry from the devices, stores or updates the latest state, and makes the data available to the frontend dashboard. This allows the user to view recent activity, monitor trends, and better understand the cat’s condition over time.

  - We also built a physical structure for the cat that brings the different modules together. This included the feeding system, water system, camera setup, and interactive laser play area. While the prototype was not tested on real cats, it served as a proof of concept for how a future smart pet care system could combine automated care, monitoring, and enrichment in a single platform.

- What you learned
  - engineering project. Since the system had many separate parts, different team members had to work on hardware, backend, frontend, data storage, machine learning, and physical design at the same time. This helped us move faster, but it also made integration more challenging. We learned that communication is especially important when different modules depend on each other.

  - We also learned that hardware projects need much more testing time than expected. Individual components may work during small tests, but behave differently once they are connected to the full system. Power issues, wiring problems, unstable sensors, and unreliable circuit components can all appear during integration. Because of this, we learned that features should be tested well before the final presentation, not just right before the demo.

  - Another important lesson was that integration should happen earlier. Even if each feature works separately, the final system only succeeds if all parts work together smoothly.

- Overall success of the project
  - Overall, the project was fairly successful. We were able to build a working prototype that demonstrated the main ideas of the system: automated feeding and water control, live monitoring, data collection, a dashboard interface, and interactive features for cat enrichment. The project showed that our concept is technically possible and gave us a strong foundation for future improvement.

  - However, the final presentation could have gone more smoothly if we had integrated the full system earlier. Some issues appeared late in the process, especially with unreliable circuit components. On presentation day, the load cells stopped working, which affected our ability to demonstrate the sensing and consumption tracking features. This showed us that hardware reliability is just as important as software functionality.

  - Even with these issues, the project was a meaningful proof of concept. It combined embedded systems, web development, physical design, and data analytics into one system, and it helped us understand both the potential and the challenges of building a real smart pet care product.

## References
- Datasheets
  - https://zenodo.org/records/4008297 - cat meows
- Research papers
  - JL-TFMSFNet: https://www.sciencedirect.com/science/article/pii/S0957417424014878#d1e1222
- Projects you get ideas from - GitHub repositories-
  - DeepCat: https://github.com/Arwa-Fawzy/Cat-Emotional-Analysis?tab=readme-ov-file

