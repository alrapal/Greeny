'''
##################################################################################
##################################################################################

Import section

##################################################################################
##################################################################################
'''

import dht                 # import the builtin library
from machine import ADC, Pin, unique_id    # library for pin access      
from time import sleep, sleep_ms
from my_secrets import adafruit_credentials, adafruit_mqtt_feeds
import WIFI
from mqtt import MQTTClient, MQTTException
from ubinascii import hexlify
from sys import exit
import gc
'''
##################################################################################
##################################################################################

Global Variables and Objects

##################################################################################
##################################################################################
'''

DELAY = 10 # delay in s

BLINK_DELAY = 500 # in ms
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

'''
Sensor section
'''
# Digital
button = Pin(22,Pin.IN)             # Button to control connection on digital pin 20
# Analog
ldr_sensor = ADC(Pin(26))           # LDR sensor connected to analog pin 26 for light detection
dht11_sensor = dht.DHT11(Pin(27))     # DHT11 Constructor connected to pin analog 27

# Built in
led = Pin("LED", Pin.OUT)           # Built in LED

def blink(delay: int): 
    led.value(1)
    sleep_ms(delay)
    led.value(0)
    sleep_ms(delay)
    
blink(delay=BLINK_DELAY)

# Connector objects
wifi = WIFI.WIFI(debug=True)
mqtt_client = MQTTClient(client_id=AIO_CLIENT_ID, server=AIO_SERVER, port=AIO_PORT, user=AIO_USER, password=AIO_KEY)

blink(delay=BLINK_DELAY)
'''
##################################################################################
##################################################################################

Function Definition

##################################################################################
##################################################################################
'''
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
    current_ldr_reading = ldr_sensor.read_u16()
    
    # Print the values if DEBUG set to TRUE
    if debug:
        print("Amount of light: {}".format(current_ldr_reading))
        print("Temperature is {} degrees Celsius and Humidity is {}%".format(current_temperature, current_humidity))
        print("###################################")
    return current_humidity, current_temperature, current_ldr_reading


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
                led.value(0)
            # elif connecte and button pressed: 
                # disconnect
            elif is_connected:   # if connection is active 
                # read values and publish them if they are different than the previous one. 
                current_humidity, current_temperature, current_ldr_reading = read_sensors(debug=True)

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
        except MQTTException as me:
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