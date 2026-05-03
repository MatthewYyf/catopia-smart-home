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
- Libraries / Frameworks
- Software structure
  - code structure
- Data flow
- User interface
- Communication Protocols (e.g., I2C, SPI, MQTT)

### 3.4 Overall Control Flow

## 4. Challenges and Limitations
- Technical challenges
Wiring and getting the correct amount of power to each of the hardware components was quite challenging. Also connecting the individual picos to the pi was difficult as sometimes they would connect and the pi would succesfully send them a signal, but sometimes it wouldn't work. 

- Design constraints
Some design constraints is that ...

- What didn’t work as expected
We couldn't get the laser to be controlled by the owner through the website, so we instead made the laser mounted on the servo move randomly. We couldn't get the water pump to successfuly be turned off by the pi, it could only be turned on and then the signal to stop it wouldn't work. This still resulted in what we wanted, a continuous flow of water, but not being able to turn off the water pump was not as planned.

- Potential enhancements
Some enhancements would be getting the laser to move through the owners control. Another enhancement would be getting the food dispenser to be quieter as when it ran it was very loud and startling. 

- Features you would add with more time
We would add with more time a fully automated litter box. Another feature would be more toys for the cat to play with as just a laser isn't going to always get your cat to play. 

## 5. Demo Description
Explain your (recorded) demo:
- How the system works in real time
- Key highlights

## 6. Contributions
List each member’s contributions:
- Name: specific tasks completed
- Adam: Pressure Sensor wiring and starter code(outdated)
        Water pump wiring and starter code
        Load cells wiring/starter code/found 3d model
        Assembled the cat house
        Found dataset for cat meows
        Website/microphone code to record and store owners voice memos
        Bluetooth speaker setup
    
## 7.Conclusion
Summarize:
- What you built
We built a modular cat house for the owner to be able to keep track of their cats health through many different sensors and keep them happy.

- What you learned


- Overall success of the project



## References
- Datasheets
  https://zenodo.org/records/4008297 - cat meows
- Research papers
  - JL-TFMSFNet: https://www.sciencedirect.com/science/article/pii/S0957417424014878#d1e1222
- Projects you get ideas from - GitHub repositories-
  - DeepCat: https://github.com/Arwa-Fawzy/Cat-Emotional-Analysis?tab=readme-ov-file

