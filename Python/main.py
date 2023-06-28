'''
##################################################################################
##################################################################################

Import section

##################################################################################
##################################################################################
'''

import dht                # DHT library provided by micropython
import gc                 # garbage collector for memory management
import WIFI               # wifi module
import custom_exceptions as ce  # custom exceptions for error handling

from mqtt import MQTTClient, MQTTException  # mqtt module and its exceptions
from ubinascii import hexlify               
from sys import exit                        # method to exit the program
from analog_sensor import AnalogSensor      # Analog sensor module which provides an extra abstraction layer and more control over the analog sensors
from machine import Pin, unique_id          # micropython library for pin access      
from time import sleep, sleep_ms            # time functions
from my_secrets import adafruit_credentials, adafruit_mqtt_feeds    # secret file with credentials
'''
##################################################################################
##################################################################################

Global Variables and Objects

##################################################################################
##################################################################################
'''
# delays
DELAY = 10 # delay in s between each readings
BLINK_DELAY = 500 # in ms define the blink delay 

# pins
PIN_BUTTON = 22
PIN_LIGHT = 26
PIN_DHT = 27
PIN_SOIL = 28

# Adafruit IO (AIO) configuration
AIO_SERVER = "io.adafruit.com"
AIO_PORT = 1883
AIO_USER = adafruit_credentials['username']
AIO_KEY = adafruit_credentials['key']
AIO_CLIENT_ID = hexlify(unique_id())  # Can be anything

# Retrieve credentials from my_secrets.py -> not pushed to avoid exposing credentials
AIO_AMBIENT_TEMP_FEED = adafruit_mqtt_feeds['ambient_temperature']
AIO_BUILTIN_LED_FEED = adafruit_mqtt_feeds['built_in_led']
AIO_AMBIENT_HUMI_FEED = adafruit_mqtt_feeds['ambient_humidity']
AIO_AMBIENT_LIGHT = adafruit_mqtt_feeds['ambient_light']
AIO_SOIL_MOISTURE_FEED = adafruit_mqtt_feeds['soil_moisture']

# Boundaries for Analog sensors:
MAX_SOIL = 43500 # Correspond to the reading obtained when sensor in the air and dry
MIN_SOIL = 13000 # Corresponds to the reading obtained when sensor was emegred in water. 
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
    
    soil_sensor = AnalogSensor(pin=PIN_SOIL, name="Soil Moisture Sensor") # Soil moisture sensor connected on pin 28
    # Set the min and max value to be able to retrieve a % of soil humidity
    soil_sensor.min = MIN_SOIL
    soil_sensor.max = MAX_SOIL
    #dht11 sensor for temp and humidity     
    dht11_sensor = dht.DHT11(Pin(PIN_DHT))     # DHT11 Constructor connected to pin analog 27
    # Built in 
    led = Pin("LED", Pin.OUT)           # Built in LED

    # Connector objects
    # TODO: Move into boot.py
    wifi = WIFI.WIFI(debug=True)
    mqtt_client = MQTTClient(client_id=AIO_CLIENT_ID, server=AIO_SERVER, port=AIO_PORT, user=AIO_USER, password=AIO_KEY)
except ce.InvalidSensorNameException as ne: # exception if invalid sensor name
    print(ne.message)
    exit(1)
except ce.InvalidPinException as pe: # exception if invalid analog pin for Pico W. 
    print(pe.message)
    exit(1)
except Exception as e:
    print(str(e))
    exit(1)




'''
##################################################################################
##################################################################################

Function Definition

##################################################################################
##################################################################################
'''

def blink(delay: int): 
    led.value(1)
    sleep_ms(delay)
    led.value(0)
    sleep_ms(delay)

def sub_cb(topic, msg):
    print(topic, msg)


def connect(debug: bool = False) -> None:
    '''
    Method to connect wifi then to adafruit mqtt
    @param: debug: set to true to print extra information useful for debuging
    '''
    wifi.do_connect()    # connect to wifi
    mqtt_client.set_callback(sub_cb)
    mqtt_client.connect()           # connect to mqtt
    mqtt_client.publish(topic="paralex/feeds/last-will", msg="0") # publish a connection status to the adafruit interface
    if debug:
        print("Connected to %s" % (AIO_SERVER)) #print info if debug is set

def disconnect(debug:bool = False) -> None:
    '''
    Method to disconnect mqtt then wifi
    @param: debug: set to true to print extra information useful for debuging
    '''
    mqtt_client.publish(topic="paralex/feeds/last-will", msg="1") # publish a disconnection message to ada interface
    sleep(DELAY)
    mqtt_client.disconnect()                                       # disconnect first the mqtt client
    wifi.disconnect()                                               # then the wifi
    if debug:
        print("Disconnected from WIFI and MQTT.")                   # debug info
    

def read_sensors(debug: bool = False) -> int:
    '''
    Method to read the current sensor values
    @param: debug: set to true to print extra information useful for debuging
    @return: humidity, temperature and ligh readings from sensors as int values
    '''
    # DHT11 measurements
    dht11_sensor.measure()
    current_temperature = dht11_sensor.temperature()
    current_humidity = dht11_sensor.humidity()
    
    # LDR sensor measurement
    try:
        current_ldr_reading = light_sensor.get_raw_data()
        current_soil_reading = soil_sensor.get_percentage_data()
        # _per_current_ldr_reading = light_sensor.calculate_percentage_data(current_ldr_reading)
        if debug:
            print("Amount of light: {}".format(current_ldr_reading))
            print("Soil dryness {}%".format(current_soil_reading))
            # print("Amount of light %: {}%".format(_per_current_ldr_reading))
            print("Temperature is {} degrees Celsius and Humidity is {}%".format(current_temperature, current_humidity))
            print("###################################")
    except ce.InvalidMinMaxException as me:
        print(me.message)
    # Print the values if DEBUG set to TRUE

    return current_humidity, current_temperature, current_ldr_reading, current_soil_reading


def are_equal_readings(previous: int, current: int) -> bool:
    '''
    compare two sensore readings 
    @params: two sensor readings as int
    @return: True if equal, False if non equal
    '''
    return previous == current


'''
Main function.
Check button status and connection status and connect disconnect accordingly. 
Reads the sensors values and send the, via mqtt if connection
'''

def main(debug:bool = False):
    debug = debug
    is_connected = False # When booting, the connection has not happened yet
    previous_temp = 0
    previous_humi = 0
    previous_ldr = 0
    previous_soil = 0
    previous_button_status = 0 # initiliase the button status since it is a switch, we need to keep in memory the previous status for comparison
    while True:
        try:
            # Check if the button is pressed
            button_is_pressed = button.value() # returns 1 when pressed
            
            if previous_button_status != button_is_pressed: # update the button status if it is different than the previous one
                print("Button status set to: ", bool(button_is_pressed))
                previous_button_status = button_is_pressed


            # Connects if the connection status is false and the button has been pressed
            if not is_connected and previous_button_status:
                connect(debug=True)
                is_connected = True
                led.value(1)
            # Disconnects if the 
            elif is_connected and previous_button_status:
                disconnect(debug=True)
                is_connected = False
                previous_temp = 0
                previous_humi = 0
                previous_ldr = 0
                previous_soil = 0
                led.value(0)
            # elif connecte and button pressed: 
                # disconnect
            elif is_connected:   # if connection is active 
                # read values and publish them if they are different than the previous one. 
                current_humidity, current_temperature, current_ldr_reading, current_soil_reading = read_sensors(debug=True)
                
                if not are_equal_readings(previous_soil, current_soil_reading):
                    previous_soil = current_soil_reading
                    mqtt_client.publish(topic=AIO_SOIL_MOISTURE_FEED, msg=str(previous_soil))
                if not are_equal_readings(previous_humi, current_humidity):
                    previous_humi = current_humidity

                    mqtt_client.publish(topic=AIO_AMBIENT_HUMI_FEED,msg=str(previous_humi))
                if not are_equal_readings(previous_temp, current_temperature):
                    previous_temp = current_temperature
                    mqtt_client.publish(topic=AIO_AMBIENT_TEMP_FEED,msg=str(previous_temp))
                if not are_equal_readings(previous_ldr, current_ldr_reading):
                    previous_ldr = current_ldr_reading
                    mqtt_client.publish(topic=AIO_AMBIENT_LIGHT,msg=str(previous_ldr))
                    # TODO: add publication when feed created
            else:
                print("Press the button to initialise connection")
                # add a small delay to smoothen the loop
            gc.collect() # call garbage collector to free memory after each iteration and avoid memory leak.
            if debug:
                print("Available memory: ", gc.mem_free())
            sleep(DELAY)   
        except MQTTException:
                print("Not connected to MQTT. Something went wrong") # print exception messages
                exit(1)
        except Exception as e:
                print(str(e)) # print exception messages
                exit(1)
       
'''     
##################################################################################
##################################################################################

Main

##################################################################################
##################################################################################
'''

main(debug=False)

if __name__ == "__main__":
    main()