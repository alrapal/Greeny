# main.py -- put your code here!

import dht                 # import the builtin library
from machine import ADC, Pin, PWM    # library for pin access      
import time      
from LoRaWAN import lora
from secrets import lorawan_credentials
import WIFI
DEBUG = False

'''
Wifi connection
'''
wifi = WIFI.WIFI()

'''
LoRaWAN Connection
'''
lora = lora(debug=DEBUG) # Declare and assign lora object. Change DEBUG on line 9 for activating

# Credentials for LoRaWAN -> in secrets.py that is not pushed to avoid exposing credentials
DEV_EUI = lorawan_credentials['DEV_EUI']
APP_EUI = lorawan_credentials['APP_EUI']
APP_KEY = lorawan_credentials['APP_KEY']

'''
Sensor section
'''
# Digital
passivePiezzo = PWM(Pin(20))             # Passive Piezzo is connected on digital pin 20 in out mode to produce sound
collision_sensor = Pin(21, Pin.IN)  # Vibration sensor connected to digital pin 21

# Analog
ldr_sensor = ADC(Pin(26))           # LDR sensor connected to analog pin 26 for light detection
tempSensor = dht.DHT11(Pin(27))     # DHT11 Constructor connected to pin analog 27

# Built in
led = Pin("LED", Pin.OUT)           # Built in LED

# definition of the notes for the buzzer:
tone = 500 # this will be the frequency on the frequency scale defined for the piezo 

# Avoid while true. This can be later changed with a button for instance. 
is_active = True

def play_alarm():
        passivePiezzo.duty_u16(1000)  # Setup the max frequency to 1000 
        passivePiezzo.freq(tone)


def stop_alarm():
    passivePiezzo.duty_u16(0) # Setup the max frequency to 0 to turn it off 


def connect_LoRaWAN():
    '''
    Attemps to connect to LoRaWAN network
    '''
    # Limit of while loop before continuing if connection unsuccessful 
    ATTEMPT_LIMIT = 1
    LORA_ATTEMPT = 0
    # LoRaWAN connection
    try:
        # config using credentials
        lora.configure(DEV_EUI, APP_EUI, APP_KEY)

        lora.startJoin()
        print("Start Join LoRaWAN network.....")
        # Tries to connect until limit of attempt is reached
        while not lora.checkJoinStatus() and (LORA_ATTEMPT < ATTEMPT_LIMIT):
            print("Joining LoRaWAN network....")
            LORA_ATTEMPT = LORA_ATTEMPT + 1
        time.sleep(1)
        # Prints appropriate message, based on the reason the previsou loops has been exited
        if lora.checkJoinStatus():
            print("Join success!") 
        else: 
            print("Could not connect to LoRaWAN network.")        # library for making delays between reading
    except Exception as e:
        print(str(e))

'''
Try the different connections. First tries to connect to LoRaWAN network and if unsuccessful, tries the WIFI
'''
try:
    connect_LoRaWAN()
    if not lora.checkJoinStatus():
        ip = wifi.do_connect()
        wifi.http_get()
except KeyboardInterrupt:
    print("Keyboard interrupt")
except Exception as e:
    print(str(e))

'''
Actual sensor measurement section
'''
while is_active:
    try:
        # DHT11 measurement and reaction
        tempSensor.measure()
        temperature = tempSensor.temperature()
        humidity = tempSensor.humidity()
        print("Temperature is {} degrees Celsius and Humidity is {}%".format(temperature, humidity))
        
        # LDR sensor measurement and reaction
        ldr_reading = ldr_sensor.read_u16()
        darkness = round(ldr_reading / 65535 * 100, 2)
        print("ldr_reading: {}".format(ldr_reading))

        # vibration sensor measurement
        collision_reading = collision_sensor.value()
        print("collision detected: {}".format(not bool(collision_reading)))

        # Produce sound if vibration detected
        if not collision_reading:
            led.value(1)
            play_alarm()
        else: 
            led.value(0)
            stop_alarm()


        print("###################################")

    except Exception as e:
        # Print all exception messages
        print(str(e))
    time.sleep_ms(10)
