# Greeny

Tutorial on how to assemble and build an IoT device to monitor a plant's soil as well as ambient temperature and lighting conditions. 
This tutorial is part of the Applied IoT course given by Linnaeus University durnig summer 2023.

## Author and credentials
Name: Alexandre Rancati-Palmer
Student credentials: ar224hw

## Description
This projects aims to provide a tool to monitor a plant's soil and environmental conditions. 
The sensors used in this project are the following: 
|Sensor name|Purpose|User guide|
|---|---|---|
|DHT11|Provide data on the ambient temperature and himidity||
|Capacitive soil sensor|Provide data on the humidity in the soil||
|Photo resistor|Provide data on the lighting conditions||

More information about the sensors available [here](#material)
## Estimated time: 
<TODO: ADD ESTIMATED TIME>

# Objective
I am not extaclty the best gardener and I always struggle to water my plants at good time. As a responsible plant owner, I had to be better and IoT can help me reaching my goal. Beside giving me direct indication on when my plants need to be watered, I plan to use the combination of data from the environment and the soil to help me undertsand how my plants react to these different factors. When do they drink the most, in which conditions. This is more of a long term goal but with time, I hope to collect enough data to be able to map a unique hydrolic behaviour for each plant. 

# Material

|Material|Purpose|Price|Purchase|User guide|Specification|
|---|---|---|---|---|---|
|Raspberry pico W| Micro controller with wifi chip|98 kr|[Electrokit](https://www.electrokit.com/produkt/raspberry-pi-pico-w/)|[Raspberry website](https://www.raspberrypi.com/documentation/microcontrollers/raspberry-pi-pico.html)|Wireless (WiFi and Bluetooth), 256kb RAM, ARM architecture, RP2040 CPU, 2Mb flash memory|
|Breadboard|For cleaner wiring|69 kr|[Electrokit](https://www.electrokit.com/produkt/kopplingsdack-840-anslutningar/)| - | - |
|Jumper cables MM|For wiring|29 kr|[Electrokit](https://www.electrokit.com/en/product/jumper-wires-1-pin-male-male-150mm-10-pack/)|-|-|
|Jumper cables MF|For wiring|29 kr|[Electrokit](https://www.electrokit.com/en/product/jumper-wires-1-pin-female-female-150mm-10-pack/)|-|-|
|USB to micro usb cable|Connecting micro controller to computer|19 kr|[Electrokit](https://www.electrokit.com/en/product/usb-cable-a-male-micro-b-male-30cm/)|-|-|
|DHT11|Temperature and humidity sensor|49 kr|[Electrokit](https://www.electrokit.com/en/product/digital-temperature-and-humidity-sensor-dht11/)|[PDF](https://www.electrokit.com/uploads/productfile/41015/41015728_-_Digital_Temperature_Humidity_Sensor.pdf)|Analog, 3.3V to 5.5V, Humidity range 20% to 90% RH with +-5% RH error. Temperature range 0°C to 50°C with +-2° error|
Capacitive Soil Sensor|Soil humidity sensor|67.99 kr|[Amazon](https://www.amazon.se/-/en/dp/B07V6M5C4H?psc=1&ref=ppx_yo2ov_dt_b_product_details)|-|Analog, 3.3V to 5.5V <TODO: Add specs>|
|Light sensor|Resistor reacting to lighting conditions|39 kr|[Electrokit](https://www.electrokit.com/produkt/ljussensor/)|[PDF](https://www.electrokit.com/uploads/productfile/41015/41015727_-_Photoresistor_Module.pdf)|Analog, 3.3V to 5.5V, built-in 10Koms resistor|
|Push button|Button for calibration of sensors|5.50 kr|[Electrokit](https://www.electrokit.com/en/product/push-button-pcb-3mm-black/)|-|-|
|1kohm resistor|Resistance to use with button|1 kr|[Electrokit](https://www.electrokit.com/en/product/resistor-carbon-film-0-25w-1kohm-1k/)|-|1Koms resistance


**Total price: 406.49 kr**

![picture](./Assets/material.jpg)

<TODO: Update with latest picture>

# Computer setup

How is the device programmed. Which IDE are you using. Describe all steps from flashing the firmware, installing plugins in your favorite editor. How flashing is done on MicroPython. The aim is that a beginner should be able to understand.

- [ ] Chosen IDE
- [ ] How the code is uploaded
- [ ] Steps that you needed to do for your computer. Installation of Node.js, extra drivers, etc.

# Putting everything together
The picture below shows how the different sensors should be wired. 

![picture](./Assets/greeny_wiring_bb.jpg)

- The Pico W powers the breadboard via 3v3 pin (pin 37) 
- The Pico connects the breadboard to ground via pin 38
- All sensors are then powered via the breadboard power and ground lines
- The button has a resistor connected to the ground because it is not included in unlike the other sensors. This is to avoide picking up electrical noise when not pressed. 
- Since all sensors are compatible with 5V, it is possible to use pin 40 (VSYS) to power the bredboard instead of the 3v3. This is recommended only if you plan on using the usb connector as power source since the VSYS is directly coming from the usb. It will not work if the usb is not used. This can have the benefit to provide better readings, especially for the soil sensor which, depending on the one you purchased, can provide low quality readings. 
- For data reading, all sensors are analog. This means that we use Pin 34, 32 and 31 to read the analog inputs. In the provided circuit diagram, the sensors are connected as the following: 
   
|Sensor|Pin|Pin Name|
|---|---|---|
|DHT11|`32`|`ADC1`|
|Light sensor|`31`|`ADC0`|
|Soil sensor|`34`|`ADC2`|

- The button can be connected to any GPIO pin since it is used to detect digital signal. In this case, it was connected to `pin 29` / `GP 22`
  
  This setup is not suitable for production since it is using a bread board and the connections are not soldered. Also, it is sensitive to voltage depending on the quality of the sensor, requiring to use the USB for powering the device.  

# Platform

Describe your choice of platform. If you have tried different platforms it can be good to provide a comparison.

Is your platform based on a local installation or a cloud? Do you plan to use a paid subscription or a free? Describe the different alternatives on going forward if you want to scale your idea.

- [ ] Describe platform in terms of functionality
- [ ] *Explain and elaborate what made you choose this platform <HIGHER GRADE>

# The code

Import core functions of your code here, and don’t forget to explain what you have done! Do not put too much code here, focus on the core functionalities. Have you done a specific function that does a calculation, or are you using clever function for sending data on two networks? Or, are you checking if the value is reasonable etc. Explain what you have done, including the setup of the network, wireless, libraries and all that is needed to understand.

# Transmitting the data / connectivity

How is the data transmitted to the internet or local server? Describe the package format. All the different steps that are needed in getting the data to your end-point. Explain both the code and choice of wireless protocols.

- [ ] How often is the data sent?
- [ ] Which wireless protocols did you use (WiFi, LoRa, etc …)?
- [ ] Which transport protocols were used (MQTT, webhook, etc …)
- [ ] *Elaborate on the design choices regarding data transmission and wireless protocols. That is how your choices affect the device range and battery consumption.
# Presenting the data

Describe the presentation part. How is the dashboard built? How long is the data preserved in the database?

- [ ] Provide visual examples on how the dashboard looks. Pictures needed.
- [ ] How often is data saved in the database.
- [ ] *Explain your choice of database. <HIGHER GRADE>
- [ ] *Automation/triggers of the data. <HIGHER GRADE>
# Finalizing the design

Show the final results of your project. Give your final thoughts on how you think the project went. What could have been done in an other way, or even better? Pictures are nice!

- [ ] Show final results of the project
- [ ] Pictures
- [ ] *Video presentation <HIGHER GRADE>


