# Greeny

Tutorial on how to assemble and build an IoT device to monitor a plant's soil as well as ambient temperature and lighting conditions. 
This tutorial is part of the Applied IoT course given by Linnaeus University durnig summer 2023.
## Table of content
- [Greeny](#greeny)
  - [Table of content](#table-of-content)
  - [Author and credentials](#author-and-credentials)
  - [Description](#description)
  - [Estimated time:](#estimated-time)
  - [Objective](#objective)
  - [Material](#material)
  - [Computer setup](#computer-setup)
    - [Preparing the development environment](#preparing-the-development-environment)
    - [Preparing the Pico W for Micropython (More info here)](#preparing-the-pico-w-for-micropython-more-info-here)
    - [Uploading the code onto the Pico W](#uploading-the-code-onto-the-pico-w)
  - [Putting everything together](#putting-everything-together)
  - [Platform](#platform)
  - [The code](#the-code)
    - [Class Diagram](#class-diagram)
    - [AnalogSensor class](#analogsensor-class)
    - [WifiConnector class](#wificonnector-class)
    - [MQTTclient class](#mqttclient-class)
    - [my\_secrets](#my_secrets)
    - [boot and main](#boot-and-main)
  - [Transmitting the data / connectivity](#transmitting-the-data--connectivity)
  - [Presenting the data](#presenting-the-data)
  - [Finalizing the design](#finalizing-the-design)


## Author and credentials
Name: Alexandre Rancati-Palmer
Student credentials: ar224hw

## Description
This projects aims to provide a tool to monitor a plant's soil and its environmental conditions. 
The sensors used in this project are the following: 
|Sensor name|Purpose|
|---|---|
|DHT11|Provide data on the ambient temperature and himidity|
|Capacitive soil sensor|Provide data on the humidity in the soil|
|Light sensor|Provide data on the lighting conditions|

More information about the sensors available [here](#material)
## Estimated time: 
<TODO: ADD ESTIMATED TIME>

## Objective
I am not extaclty the best gardener and I always struggle to water my plants at good time. As a responsible plant owner, I had to be better and IoT can help me reaching my goal. Beside giving me direct indication on when my plants need to be watered, I plan to use the combination of data from the environment and the soil to help me undertsand how my plants react to these different factors. When do they drink the most, in which conditions. This is more of a long term goal but with time, I hope to collect enough data to be able to map a unique hydrolic behaviour for each plant. 

## Material

|Material|Purpose|Price|Purchase|User guide|Specification|
|---|---|---|---|---|---|
|Raspberry Pico W| Micro controller with wifi chip|98 kr|[Electrokit](https://www.electrokit.com/produkt/raspberry-pi-Pico-w/)|[Raspberry website](https://www.raspberrypi.com/documentation/microcontrollers/raspberry-pi-Pico.html)|Wireless (WiFi and Bluetooth), 256kb RAM, ARM architecture, RP2040 CPU, 2Mb flash memory|
|Breadboard|For cleaner wiring|69 kr|[Electrokit](https://www.electrokit.com/produkt/kopplingsdack-840-anslutningar/)| - | - |
|Jumper cables MM|For wiring|29 kr|[Electrokit](https://www.electrokit.com/en/product/jumper-wires-1-pin-male-male-150mm-10-pack/)|-|-|
|Jumper cables MF|For wiring|29 kr|[Electrokit](https://www.electrokit.com/en/product/jumper-wires-1-pin-female-female-150mm-10-pack/)|-|-|
|USB to micro usb cable|Connecting micro controller to computer|19 kr|[Electrokit](https://www.electrokit.com/en/product/usb-cable-a-male-micro-b-male-30cm/)|-|-|
|DHT11|Temperature and humidity sensor|49 kr|[Electrokit](https://www.electrokit.com/en/product/digital-temperature-and-humidity-sensor-dht11/)|[PDF](https://www.electrokit.com/uploads/productfile/41015/41015728_-_Digital_Temperature_Humidity_Sensor.pdf)|Analog, 3.3V to 5.5V, Humidity range 20% to 90% RH with +-5% RH error. Temperature range 0°C to 50°C with +-2° error|
Capacitive Soil Sensor|Soil humidity sensor|67.99 kr|[AZ-Delivery via Amazon](https://www.amazon.se/-/en/dp/B07V6M5C4H?psc=1&ref=ppx_yo2ov_dt_b_product_details)|[Free ebook](https://www.az-delivery.de/en/products/bodenfeuchte-v1-2-kostenfreies-e-book)|Analog, 3.3V to 5V. (Although the user guide mentions only 5V, 3.3V works)|
|Light sensor|Resistor reacting to lighting conditions|39 kr|[Electrokit](https://www.electrokit.com/produkt/ljussensor/)|[PDF](https://www.electrokit.com/uploads/productfile/41015/41015727_-_Photoresistor_Module.pdf)|Analog, 3.3V to 5.5V, built-in 10Koms resistor|
|Push button|Button for calibration of sensors|5.50 kr|[Electrokit](https://www.electrokit.com/en/product/push-button-pcb-3mm-black/)|-|-|
|1kohm resistor|Resistance to use with button|1 kr|[Electrokit](https://www.electrokit.com/en/product/resistor-carbon-film-0-25w-1kohm-1k/)|-|1Koms resistance


**Total estimated price: 406.49 kr**

![picture](./Assets/material.jpg)

## Computer setup
The workflow I used is on a **Mac** with **ARM architecture (M1)**. 
The steps for other OS can differ slightly, especially for Windows users. 

### Preparing the development environment
The next table provides a list of steps to run the code on the Pico W micro-controller.
The commands are to be run in a terminal. 
The links provide an alternative way to install the required software. If you do not want to use the `brew`commands, you cam skip step one and use the links to download the executable.
For the Integrated Development environment (IDE), I use Visual Studio Code (VS code) because it is higly modular and customisable as well as has a lot of community pluggins available. Moreover, it is a free software.
 
|Step|Dependency|Usage|Command|Link|
|---|---|---|---|---|
|**1**|Install Homebrew|Mac package manager|`/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`|[Website](https://brew.sh)|
|**2**|Install Node js|Programming language - Required for IDE plugin|`brew install node`|[Brew formulae](https://formulae.brew.sh/formula/node), [Node website](https://nodejs.org/en)|
|**3**|Instal IDE: Visual studio code|Integrated Development Environment. The software we will use to program|`brew install --cask visual-studio-code`|[VS code website](https://code.visualstudio.com)|
|**4**|Install `pymakr` plugin in VS code| Plugin that will allow us to import the code to the micro controller| - | [Pymakr extension](https://marketplace.visualstudio.com/items?itemName=pycom.Pymakr)|

### Preparing the Pico W for Micropython ([More info here](https://www.raspberrypi.com/documentation/microcontrollers/micropython.html#drag-and-drop-micropython))
The Pico W, by default, does not work out of the box with micropython. We need first to upload a firmware that will allow it to map our micropython code to the hardware. 

|Step|Dependency|Usage|Command|Link|
|---|---|---|---|---|
|**1**|Download the latest micropython firmware|The envionment for the micro controller to run the code| - | [Raspberry website](https://micropython.org/download/rp2-Pico-w/rp2-Pico-w-latest.uf2)
|**2**|Maintain pressed the `BOOTSEL` button on the Pico|Enter the flash mode|-|-|
|**3**|Connect the Pico via USB to the computer|-|-|-|
|**4**|Enter the Pico Memory|This should appear similar to a usb key|-|-|
|**5**|Drag and drop the downloaded firmware from step **1** into the Pico memory|This will install the firmware|-|-|
|**6**|When the device has dissapeared, disconnect and reconnect the Pico|-|-|-|
### Uploading the code onto the Pico W
Now that the Pico W can interprate micro python code, we need to upload our code to it so that it can be executed. 

|Step|Dependency|Usage|Command|Link|
|---|---|---|---|---|
|**1**|Using the terminal, go to the folder of your choice|Select a folder for downloading the project|`cd <path/where/to/download>`| - |
|**2**|Clone the current repository|Download the code on your computer|`git clone git@github.com:alrapal/sleeptight.git` (recommended) **or** `git clone https://github.com/alrapal/sleeptight.git` |[Github repository with micropython code](https://github.com/alrapal/sleeptight/tree/main/)
|**3**|Enter the Python folder from the repository|This where the micropython code is|`cd Python`|-|
|**4**|Open the folder in VS code|This is to be able to upload the code into the controller using pymakr|`code .`|-|
||
|**3.alt**|Open the Python folder manually via VS code|It is possible that the previous command does not work and needs to be activated. In this case, you can also open the Python folder directly using VS code| - | - |
||
|**5**|

How is the device programmed. Which IDE are you using. Describe all steps from flashing the firmware, installing plugins in your favorite editor. How flashing is done on MicroPython. The aim is that a beginner should be able to understand.

- [ ] Chosen IDE
- [ ] How the code is uploaded
- [ ] Steps that you needed to do for your computer. Installation of Node.js, extra drivers, etc.

## Putting everything together
The picture below shows how the different components should be wired. 

![picture](./Assets/greeny_wiring_bb.jpg)

- The Pico W micro-controller powers the breadboard via `3v3` pin (`pin 37`) 
- The Pico W connects the breadboard to ground via `pin 38`
- All sensors are then powered via the breadboard power and ground lines
- The button has a resistor connected to the ground because it is not included in unlike the other sensors. This is to avoide picking up electrical noise when not pressed. 
- Since all sensors are compatible with 5V, it is possible to use `pin 40` (`VBUS`) or `pin 39`(VSYS) to power the bredboard instead of the `3v3`. However, in my testings, I found that the Light sensor would provide higher values since higher voltage, but the soil moisture sensor would be constant despite having it alternatively emerged in water an dried in the air. `3.3V` seems to be recommended in this case. Or alternatively, we would need to use some extra resistors to use `VBUS` or `VSYS`. 
- For data reading, all sensors are analog. This means that we use `Pin 34`, `32` and `31` to read the analog inputs. In the provided circuit diagram, the sensors are connected as the following: 
   
|Sensor|Pin Controller Number|Pin ADC Name|Pin GPIO name|
|---|---|---|---|
|DHT11|`32`|`ADC1`|`GP27`|
|Light sensor|`31`|`ADC0`|`GP26`|
|Soil sensor|`34`|`ADC2`|`GP28`|

- The button can be connected to any `GPIO` pin since it is used to detect digital signal. In this case, it was connected to `pin 29` / `GP22`
  
This setup is not suitable for production since it is using a bread board and the connections are not soldered. Also, it is sensitive to voltage depending on the quality of the sensor, requiring to use the USB for powering the device.  Furthermore, the wiring is exposed which can be problematic when wiring the plant. Extra care should be applied in this case, which should be avoided for production standard product. 

## Platform

Describe your choice of platform. If you have tried different platforms it can be good to provide a comparison.

Is your platform based on a local installation or a cloud? Do you plan to use a paid subscription or a free? Describe the different alternatives on going forward if you want to scale your idea.

- [ ] Describe platform in terms of functionality
- [ ] *Explain and elaborate what made you choose this platform <HIGHER GRADE>

## The code
### Class Diagram

The code is build using [`MicroPython`](https://micropython.org) and relies on two different paradigm: Object Oriented Programming (OOP) and procedural programming. 
The diagram below shows how the code is articulated. 
`Pin`, `ADC` and `DHT11` are libraries included in  `MicroPython` and are not represented in the diagram for clarity (or not fully for DHT11). 

![picture](./Assets/class_diagram.png)

### AnalogSensor class
Since the `Greeny` project relies only on analog sensor, I decided to wrap the `ADC` class from `MicroPython` within the `AnalogSensor` class. 
This class allows better control over which pins are used since it will check the given pin agains a tuple of valid pins (Currently the 3 ADC pins that are built in with the PicoW). This  makes custom error control easier with custom exceptions that are contained in `custom_exceptions.py`, providing meaningful error messages when debuging.

**Tuple and check when calling the constructor**:
````
valid_pico_w_analog_pins = (26,27,28) # list of the valid pico w analog pins

class AnalogSensor():
    def __init__(self, pin, name):
        if not name.strip():
            raise InvalidSensorNameException(message="The name of the sensor should not be empty or contain only white spaces")
        if pin not in valid_pico_w_analog_pins:
            raise InvalidPinException(message="Invalid Pin provided. The valid analog pins for pico W are 26, 27 or 28")
````

If the circuit is adapted with and ADC converter, there is just the need to update the tuple with the pins attached to the converter. Similarely, if the code is used with another micro controller, a tuple can be added with the specification of the new microcontroller.

The `AnalogSensor` class provide a standardised set of methods easy to use that allow to calibrate the sensor to retrieve a percentage based on the readings. Several checks are performed to make sure the values provided are consistent with the class' expectations. 
**Example of error handling and control of accepted data for the min value**:
````
@min.setter
    def min(self, value: int):
        # check if the value is <= to 0 -> negatives are not allowed
        if value < 0:
            raise InvalidMinMaxException(message="The minimum boundary for " + self._name + " should be >= 0")
        # Check if the max has been defined and in that case if the value is superior or equal to the max -> there should be a gap between min and max with min < max
        if self._max is not None and value >= self._max:
            raise InvalidMinMaxException(message="The minimum boundary for " + self._name + " should be < to the maximum boundary")
        self._min = value
````

### WifiConnector class
This class is an OOP version of the [provided file](https://hackmd.io/@lnu-iot/rJVQizwUh). It has been adapted with some extra attributes and the method to disconnect from the network. This has been done originally to be able to send a clean event to the MQTT broker and eventually trigger an event, giving the possibility to differenciate a clean disconnection from an unexcpected one. 

### MQTTclient class
The MQTT client class is taken from [Rui Santos](https://github.com/RuiSantosdotme), and is available [here](https://raw.githubusercontent.com/RuiSantosdotme/ESP-MicroPython/master/code/MQTT/umqttsimple.py)

The code lacks documentation but is pretty straight forward if you have MQTT knowledge. We use it to instanciate a client and connect it to a given broker. Then we use the client in `main` to publish messages. 

### my_secrets
A file containing all the credentials is missing from this repository. This is to avoid exposing credentials to an public place. This file contains several dictionnaries with different credientials (wifi, mqtt) to be able to connect to the different services. 
a dummy file named `change_my_secrets.py` is provided instead. The credential to use should be put there and the file should be renamed to `my_secrets.py` to be able to connect.

### boot and main
`boot`and `main` are not classes but uses the previous classes with a procedural paradigm. 
`boot` is in charge of connecting to the wifi and to the mqtt broker using `WifiConnector` and  `MQTTClient` and their respective methods. 
`main` is where the sensors are instanciated. It uses the `MQTTClient` in `boot` to publish the different messages to the MQTT broker. 

In `main.py`, we instanciate the ligh sensor, soil moisture sensor and DHT11 sensor. Then, we set the min and max to be able to retrieve a percentage value which is more inelligible than a raw value. To define those value, we read the raw value in both extremes conditions (raw value in sun light and in complete darkness for the light sensor and in the air and in water for the soil moisture sensor). 
However, the way the sensor work implies that the retrieve pecentage is the percentage of darkness and dryness. This is wy we reverse that percentage before sending it because it is more intuitive to the user to receive a percentage of moisture and lightning than their nemesis. 

More information about the connectivity and the data formats is available in the [next section](#transmitting-the-data--connectivity)

## Transmitting the data / connectivity

How is the data transmitted to the internet or local server? Describe the package format. All the different steps that are needed in getting the data to your end-point. Explain both the code and choice of wireless protocols.

- [ ] How often is the data sent?
- [ ] Which wireless protocols did you use (WiFi, LoRa, etc …)?
- [ ] Which transport protocols were used (MQTT, webhook, etc …)
- [ ] *Elaborate on the design choices regarding data transmission and wireless protocols. That is how your choices affect the device range and battery consumption.
## Presenting the data

Describe the presentation part. How is the dashboard built? How long is the data preserved in the database?

- [ ] Provide visual examples on how the dashboard looks. Pictures needed.
- [ ] How often is data saved in the database.
- [ ] *Explain your choice of database. <HIGHER GRADE>
- [ ] *Automation/triggers of the data. <HIGHER GRADE>
## Finalizing the design

Show the final results of your project. Give your final thoughts on how you think the project went. What could have been done in an other way, or even better? Pictures are nice!

- [ ] Show final results of the project
- [ ] Pictures
- [ ] *Video presentation <HIGHER GRADE>


