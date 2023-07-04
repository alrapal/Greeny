'''
##################################################################################
##################################################################################

Import section

##################################################################################
##################################################################################
'''

import dht                # DHT library provided by micropython
import gc                 # garbage collector for memory management
import custom_exceptions as ce  # custom exceptions for error handling

from ujson import dumps
from boot import blink, mqtt_client, MQTT_CLIENT_ID
from analog_sensor import AnalogSensor      # Analog sensor module which provides an extra abstraction layer and more control over the analog sensors
from machine import Pin, reset, reset_cause      # micropython library for pin access      
from time import sleep            # time functions
from my_secrets import mqtt_feeds    # secret file with credentials
'''
##################################################################################
##################################################################################

Global Variables and Objects

##################################################################################
##################################################################################
'''
# delays
DELAY = 900 # delay in s between each readings -> 15 minutes
BLINK_DELAY_UNKNOWN_ERROR = 500 # in ms define the blink delay for unkown errors
BLINK_DELAY_SENSOR_CONF_ERROR = 100 # blink delay for analog sensor configuration error
BLINK_DELAY_SENSOR_READING_ERROR = 1000
BLINK_DELAY_SENDING_DATA = 50

# pins' GPIO number
PIN_BUTTON = 22
PIN_LIGHT = 26
PIN_DHT = 27
PIN_SOIL = 28

# Mqtt channels to publish
# stored in my_secrets.py to avoid exposing credentials
MQTT_AMBIENT_TEMP_FEED = mqtt_feeds['ambient_temperature']
MQTT_AMBIENT_HUMI_FEED = mqtt_feeds['ambient_humidity']
MQTT_AMBIENT_LIGHT = mqtt_feeds['ambient_light']
MQTT_SOIL_MOISTURE_FEED = mqtt_feeds['soil_moisture']
MQTT_FEED = MQTT_CLIENT_ID
# Boundaries for Analog sensors:
MAX_SOIL = 43500 # Correspond to the reading obtained when sensor in the air and dry
MIN_SOIL = 13000 # Corresponds to the reading obtained when sensor was emegred in water. 

MIN_LIGHT = 300 # Corresponds to the sensor being in the sun
MAX_LIGHT = 2000 # Corresponds to the sensor being under a blanket to mimic dark environment
'''

##################################################################################
##################################################################################

Sensor connection

##################################################################################
##################################################################################
'''

try:
    button = Pin(PIN_BUTTON,Pin.IN)             # Button to control connection on digital pin 20
    light_sensor = AnalogSensor(pin=PIN_LIGHT,name="Ambient Light Sensor") # light sensor connected on pin 26
    # Set the min and max value to be able to retrieve a % of light
    light_sensor.min = MIN_LIGHT
    light_sensor.max = MAX_LIGHT

    soil_sensor = AnalogSensor(pin=PIN_SOIL, name="Soil Moisture Sensor") # Soil moisture sensor connected on pin 28
    # Set the min and max value to be able to retrieve a % of soil humidity
    soil_sensor.min = MIN_SOIL
    soil_sensor.max = MAX_SOIL
    #dht11 sensor for temp and humidity     
    dht11_sensor = dht.DHT11(Pin(PIN_DHT))     # DHT11 Constructor connected to pin analog 27

except ce.InvalidSensorNameException as ne: # exception if invalid sensor name
    print(ne.message)
    blink(BLINK_DELAY_SENSOR_CONF_ERROR)
    reset()
except ce.InvalidPinException as pe: # exception if invalid analog pin for Pico W. 
    print(pe.message)
    blink(BLINK_DELAY_SENSOR_CONF_ERROR)
    reset()
except Exception as e:
    print(str(e))
    blink(BLINK_DELAY_UNKNOWN_ERROR)
    blink(BLINK_DELAY_UNKNOWN_ERROR)
    reset()

while True:
    try: 
        print("Reset cause: {}".format(reset_cause()))

        dht11_sensor.measure()
        current_temperature = dht11_sensor.temperature()
        data = {
            'temperature': current_temperature
        }

        json_data = dumps(data)
        print(json_data)
        mqtt_client.publish(topic=MQTT_AMBIENT_TEMP_FEED,msg=json_data,qos=1)
        blink(BLINK_DELAY_SENDING_DATA)

        current_humidity = dht11_sensor.humidity()
        data = {
            'humidity': current_humidity
        }

        json_data = dumps(data)
        print(json_data)
        mqtt_client.publish(topic=MQTT_AMBIENT_HUMI_FEED,msg=json_data,qos=1)
        blink(BLINK_DELAY_SENDING_DATA)

        percentage_darkness = light_sensor.get_percentage_data()
        # We calculate the complementary percentage because it is more intuitive to think about % of light instead of darkness
        percentage_light = round(100 - percentage_darkness, 0)
        data = {
            'light': percentage_light
        }

        json_data = dumps(data)
        print(json_data)
        mqtt_client.publish(topic=MQTT_AMBIENT_LIGHT,msg=json_data,qos=1)
        blink(BLINK_DELAY_SENDING_DATA)

        percentage_dryness = soil_sensor.get_percentage_data()
        # We calculate the complementary percentage because it is more intuitive to think about % of humidity instead of dryness
        percentage_moist = round(100 - percentage_dryness,0)
        data = {
            'moist': percentage_moist
        }
        json_data = dumps(data)
        print(json_data)
        mqtt_client.publish(topic=MQTT_SOIL_MOISTURE_FEED, msg=json_data,qos=1)
        blink(BLINK_DELAY_SENDING_DATA)
        
        # Print info into the console
        print("###################################")
        print("Available memory: ", gc.mem_free())
        print("###################################")
        print("Light (%): {}".format(percentage_light))
        print("Soil moist (%) {}%".format(percentage_moist))
        print("Temperature is {} degrees Celsius and Humidity is {}%".format(current_temperature, current_humidity))
        print("###################################")

        # Call the garbage collector to clean memory
        gc.collect()
        # wait until next reading
        sleep(DELAY)

    except ce.InvalidMinMaxException as me:
            print(me.message)
            blink(BLINK_DELAY_SENSOR_CONF_ERROR)
            # We do not reset since maybe some data can maybe be sent
    except Exception as e:
            print(str(e)) # print exception messages
            reset() # reset the device if any exception is caught
