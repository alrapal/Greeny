""" # boot.py -- run on boot-up
from WIFI import WIFI

# WiFi Connection
try:
    wifi = WIFI()
    ip = wifi.do_connect()
except KeyboardInterrupt:
    print("Keyboard interrupt")

# HTTP request
try:
    wifi.http_get()
except Exception as err:
    print("Exception", err) """