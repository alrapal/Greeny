# main.py -- put your code here!

import dht                 # import the builtin library
from machine import Pin    # library for pin access      
import time                # library for making delays between reading

tempSensor = dht.DHT11(Pin(27))     # DHT11 Constructor connected to pin 27

is_active = True

while is_active:
    try:
        tempSensor.measure()
        temperature = tempSensor.temperature()
        humidity = tempSensor.humidity()
        print("Temperature is {} degrees Celsius and Humidity is {}%".format(temperature, humidity))
    except Exception as e:
        # Print all exception messages
        print(str(e))
    time.sleep(2)

