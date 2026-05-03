# Final Report: Catopia Smart Cat Care System


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


### 3.1 Project Description

Catopia is a smart cat care system designed to help owners monitor and support their cat’s daily needs when they are not physically present. The system combines automated feeding, water tracking, live video monitoring, interactive play, and vocalization analysis into one connected platform. The goal of the project is to create a proof-of-concept embedded system that collects useful health and behavior data while giving the owner a way to remotely interact with the cat.

The system is centered around a Raspberry Pi, which acts as the main computing and coordination unit. It runs the backend server, hosts the frontend dashboard, manages the database, and handles higher-level features such as the camera stream and audio processing. Multiple Raspberry Pi Pico microcontrollers are used for lower-level hardware control. Each Pico is assigned to a specific subsystem, such as the food dispenser, water pump, load cell sensing, or pan-tilt laser toy. This division makes the system easier to organize, debug, and expand.

The food subsystem uses a motorized dispenser to move kibble into the bowl. A load cell measures the food weight, allowing the system to estimate current food level and track consumption over time. The water subsystem uses a pump and load cell to monitor the water bowl and estimate drinking behavior. The laser play subsystem uses two servos to move a laser pointer in randomized patterns, providing mental stimulation and interactive play. The camera stream allows the owner to visually check on the cat through the web dashboard.

Catopia also includes a microphone-based vocalization recognition system. The system records cat sounds, extracts audio features, and classifies vocalizations into behavioral contexts such as food-seeking, isolation, or brushing-related sounds. While this feature was not tested on real cats during the final prototype, it demonstrates how audio analysis could be used as another signal for understanding a cat’s behavior or emotional state.

Overall, Catopia is more than a collection of hardware modules. It is an integrated monitoring and automation platform that connects physical devices, sensor data, software control, and analytics into one prototype. Although the system was not validated with real cats, it demonstrates the potential for a future smart pet care product that supports both physical care and mental enrichment.

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
Catopia’s software system has four main parts: the Raspberry Pi backend, the SQLite database, the frontend dashboard, and the MicroPython firmware running on the Pico devices.

The backend is implemented in Python using FastAPI and Uvicorn. It runs locally on the Raspberry Pi and acts as the central communication layer for the system. The backend receives telemetry from Pico devices, stores the latest system state, manages hardware commands, serves the frontend interface, and provides API endpoints for reports, voice logs, and consumption data. This allows the frontend and hardware devices to communicate without connecting directly to each other.

The SQLite database stores longer-term records generated by the system. The main tables include daily_reports, voice_logs, and consumption_events. The daily_reports table stores summary information such as food intake, water intake, and body weight measurements. The voice_logs table stores detected vocalization labels from the audio classification pipeline. The consumption_events table records food or water intake events detected from changes in load cell readings. Helper functions in backend/db/queries.py allow the frontend to retrieve this data and display trends, such as water intake over the past seven days.

A key backend service is the consumption tracker, implemented in backend/services/consumption_tracker.py. Directly comparing consecutive load cell readings can be unreliable because the sensor data may fluctuate when the cat touches the bowl, steps near the sensor, or causes vibration. To reduce this noise, the tracker uses recent sensor readings and calculates median values instead of relying on a single raw reading. When the readings become stable across several windows, the system marks the current weight as a stable state. If the next stable state shows a meaningful decrease, the system records the change as a consumption event. This approach makes food and water tracking more reliable than simple frame-to-frame subtraction.

The frontend is a browser-based dashboard built with HTML, CSS, and JavaScript. It communicates with the backend using the fetch() API. The dashboard displays live food and water readings, device status, camera feed, vocalization results, reports, and control buttons. Users can send commands such as dispensing food, turning the pump on or off, starting laser play, or recording voice memos. The frontend updates regularly by requesting the latest state from the backend.

The embedded firmware is written in MicroPython and organized by hardware subsystem. Each Pico connects to the local Catopia network, sends JSON telemetry to the backend, and checks for queued commands. For example, one Pico handles the pan-tilt laser toy using PWM-controlled servos and a laser module. Another controls the kibble dispenser with a stepper motor and HX711 load cell. A third manages the water pump and water bowl load cell. This firmware structure keeps low-level hardware timing and control separate from the higher-level backend logic.

The vocalization recognition system uses audio recordings to classify cat meows into three behavioral contexts: food-seeking, isolation, and brushing. The system extracts Mel-Frequency Cepstral Coefficient, or MFCC, features from each recording and feeds them into class-specific Hidden Markov Models. Each HMM models how a meow changes over time and produces a likelihood score for the input sound. The class with the highest score is selected as the predicted context. To avoid classifying background noise, the system uses an energy threshold and voice activity detection before feature extraction.

### 3.4 Overall Control Flow

Catopia operates as a two-direction control system. Sensor data moves upward from the hardware devices to the Raspberry Pi backend and frontend dashboard, while user commands move downward from the dashboard to the appropriate Pico-controlled subsystem.

When the system starts, the Raspberry Pi launches the FastAPI backend, database services, frontend dashboard, camera stream, and audio processing tools. Each Pico connects to the local Wi-Fi network and begins its own control loop. During each loop, the Pico reads its sensors, sends telemetry to the backend, checks for pending commands, executes any received command, and then repeats the cycle.

Telemetry data includes values such as food weight, water weight, pump status, motor status, servo position, and laser state. The backend receives these readings and updates the latest system state. If the readings show a meaningful change, such as a stable decrease in food or water weight, the backend can record a consumption event in the database. The frontend then requests the latest state from the backend and displays the updated information to the user.

User actions follow the opposite direction. When the user clicks a button on the dashboard, such as “dispense food” or “start laser play,” the frontend sends a request to the backend. The backend places the command in a queue for the correct Pico. The Pico checks its command endpoint during its next loop, retrieves the command, and performs the physical action.

This structure keeps the system modular. The frontend does not need to know how each sensor or actuator is wired, and the Pico devices do not need to manage the full web application or database. The backend acts as the central bridge between the user interface, stored data, and physical hardware. This design made the prototype easier to test in separate modules and provides a clear path for adding more devices in the future.

## 4. Challenges and Limitations
One of the main technical challenges in this project was building a reliable hardware system with many different embedded components working together. The system used multiple Raspberry Pi Pico controllers, load cells, servo motors, a water pump, a food dispenser, a Raspberry Pi, and a web-based backend. Each part worked differently and required its own wiring, power, and software logic. Power management was especially difficult because some components, such as the water pump and motors, required more current than the Pico or Raspberry Pi could safely provide directly. This meant that external power sources, shared grounds, relays, and careful wiring were necessary. During testing, unstable power or unreliable circuit connections sometimes caused devices to behave inconsistently.

Another major challenge was communication between the Raspberry Pi and the Pico devices. The system depended on the Picos connecting to the local network, sending telemetry to the backend, and polling for commands. In some cases, the Picos connected successfully and received commands, but in other cases the connection was inconsistent. This made debugging harder because the issue could come from the Wi-Fi connection, the backend endpoint, the device polling loop, or the hardware itself. Calibrating the load cells was also challenging because the sensors output raw values that do not directly correspond to real weight. Each load cell had to be calibrated using known weights, and even after calibration, sensor noise made it difficult to identify accurate food or water consumption events.

The project also had several design constraints. Because this was a prototype, the system had to be built with affordable and accessible components rather than fully product-ready hardware. The physical structure also had to fit the available storage bin, bowls, wiring, sensors, and mounting parts. This limited how cleanly each subsystem could be placed and made cable management more difficult. The system was also designed around local network communication, which worked for a controlled demo environment but would need additional security and remote access features before it could be used as a real consumer product. Another important limitation is that the prototype was not tested on real cats, so its actual usefulness, safety, and effect on cat behavior remain unclear.

Some parts of the system did not work exactly as expected. The laser toy could not be fully controlled by the owner through the website, so the final version used randomized servo movement instead of direct manual control. This still demonstrated interactive play, but it did not provide the level of user control originally planned. The water pump also had reliability issues. The system could turn the pump on, but turning it off through the Pico was inconsistent during testing. As a result, the pump worked more like a continuous-flow water fountain than a fully controllable refill system. The food dispenser worked as a proof of concept, but it was loud during operation, which could startle a cat in a real setting. On presentation day, the load cells also stopped working reliably, which affected the ability to demonstrate live sensing and consumption tracking.

There are several improvements that could make Catopia more reliable and useful. The first improvement would be stronger hardware integration, including cleaner wiring, more stable power distribution, better motor drivers, protective circuit components, and a more permanent enclosure. The load cell system could also be improved with better mounting, more robust calibration, and additional filtering to reduce noise. The laser system could be upgraded so that the user can manually control the laser position through the dashboard, while still keeping the randomized automatic play mode. The food dispenser could be redesigned to reduce noise and dispense kibble more smoothly. The backend and frontend could also be expanded with better error handling, clearer device status indicators, and alerts when a device disconnects or a sensor reading becomes unreliable.

With more time, we would add more complete pet care features. A fully automated litter box would be useful because it could track bathroom behavior, which is another important indicator of cat health. We would also add more interactive toys beyond the laser, since not every cat responds to the same kind of play. The system could include safer toy motion patterns, scheduled play sessions, and different enrichment modes. Another future feature would be a more advanced scheduling system that lets the owner plan feeding, water circulation, voice memo playback, and play sessions throughout the day. Finally, real-world testing with cats would be necessary to evaluate whether the system is safe, useful, and actually improves the owner’s ability to care for the cat remotely.

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

