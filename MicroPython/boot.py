'''
##################################################################################
##################################################################################

Import section

##################################################################################
##################################################################################
'''

import gc

from WIFI import WifiConnector
from mqtt import MQTTClient, MQTTException  # mqtt module and its exceptions
from my_secrets import mqtt_credentials  # secrets is not pushed to avoid having WIFI access on github
from machine import Pin, reset, unique_id
from time import sleep_ms
'''
##################################################################################
##################################################################################

Global Variables and Objects

##################################################################################
##################################################################################
'''
# built in led for user feedback
built_in_led = Pin("LED", Pin.OUT)

# MQTT parameters
MQTT_SERVER = mqtt_credentials['server']
MQTT_PORT = mqtt_credentials['port']
MQTT_USER = mqtt_credentials['username']
MQTT_KEY = mqtt_credentials['key']
MQTT_CLIENT_ID = "Greeny_paralex_pico_w" + str(unique_id())
MQTT_KA = 900
'''
##################################################################################
##################################################################################

Functions section

##################################################################################
##################################################################################
'''

def blink(delay: int): 
    '''
    Function that makes the built in led blink at the given ms interval
    '''
    built_in_led.value(1)
    sleep_ms(delay)
    built_in_led.value(0)
    sleep_ms(delay)

def sub_cb(topic, msg):
    '''
    Callback function when mqtt message received
    '''
    print(topic, msg) # just prints the message. Currently no reactions implemented / needed

'''
##################################################################################
##################################################################################

Functions section

##################################################################################
##################################################################################
'''

try: 
    # Instanciate the objects that will allow wifi and mqtt manipulations
    wifi_connector = WifiConnector()
    mqtt_client = MQTTClient(client_id=MQTT_CLIENT_ID, server=MQTT_SERVER, port=MQTT_PORT, user=MQTT_USER, password=MQTT_KEY, keepalive=MQTT_KA)
    mqtt_client.set_callback(sub_cb) # sets the method to use on message received. We do not subscribe to any channel so this will not be used. 

    # connects to wifi 
    print("Connecting to WiFI network")
    wifi_connector.do_connect()

    # enters an infinity loop until wifi is connected
    # built in led blinks to indicate the connection process
    while not wifi_connector.is_connected():
        blink(100)
        

    # establish connection to MQTT server
    mqtt_client.connect()           # connect to mqtt
    sleep_ms(100)
    mqtt_client.publish(topic="paralex/feeds/last-will", msg="0") # publish a connection status to the adafruit interface
    

except MQTTException as e:
    print("Failed to connect to MQTT. Error message:")
    print(str(e))
    blink(1000) # blink 1 time for 1 second if MQTT error
    reset()
except Exception as e:
    print("Something unexpected happened. Error message:")
    print(str(e))
    blink(500) # blink 2 time for half a second if other error (WIFI or unexpected problem)
    blink(500)
    reset()


gc.collect() # call garbage collector

