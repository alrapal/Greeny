# boot.py -- run on boot-up
from WIFI import do_connect, http_get

# WiFi Connection
try:
    ip = do_connect()
except KeyboardInterrupt:
    print("Keyboard interrupt")

# HTTP request
try:
    http_get()
except Exception as err:
    print("Exception", err)