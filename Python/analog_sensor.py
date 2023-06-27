from machine import ADC, Pin
from custom_exceptions import InvalidPinException, InvalidMinMaxException, InvalidSensorNameException
from time import sleep_ms

valid_pico_w_analog_pins = (26,27,28) # list of the valid pico w analog pins

class AnalogSensor():
    def __init__(self, pin, name):
        if not name.strip():
            raise InvalidSensorNameException(message="The name of the sensor should not be empty or contain only white spaces")
        if pin not in valid_pico_w_analog_pins:
            raise InvalidPinException(message="Invalid Pin provided. The valid analog pins for pico W are 26, 27 or 28")
       
        
        self._pin:int = pin
        self._max:int = None
        self._min:int = None
        self._name:int = name
        # The ADC sensor 
        self._sensor = ADC(Pin(self._pin)) 

    '''
    Getters and setters
    '''
    @property #allows to access the value using this form: object.pin instead object.pin()
    def pin(self) -> int:
        pass

    @pin.setter #allows to set the value using object.pin instead of object.pin()
    def pin(self, value: int):
        # Check if the pin is a valid analog pin for a 
        if value != 26 or value != 27 or value != 28:
            raise InvalidPinException(message="Invalid Pin provided. The valid analog pins for pico W are 26, 27 or 28")
        self._pin = value

    @property 
    def sensor(self) -> int:
        return self._sensor

    @property
    def max(self) -> int:
        return self._max

    @max.setter
    def max(self, value: int):
        if self._min == None:
            raise InvalidMinMaxException(message="Please set the minimum for " + self._name + " first.")
        if value < 0 or value < self._min:
            raise InvalidMinMaxException(message="The maximum boundary for " + self._name + " should be >= 0. and >= to the minimum boundary.")
        self._max = value
    @property
    def min(self) -> int:
        pass

    @min.setter
    def min(self, value: int):
        if value < 0 or value > self._max:
            raise InvalidMinMaxException(message="The minimum boundary for " + self._name + " should be >= 0. and <= to the maximum boundary.")
        self._max = value

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        if not value.strip():
            raise InvalidSensorNameException(message="The name of the sensor should not be empty or contain only white spaces")
        self._name = value

    '''
    Methods
    '''

    def get_raw_data(self) -> int:
        '''
        Return the raw value read from the sensor
        '''
        return self.sensor.read_u16()

    def calculate_percentage_data(self, value) -> float:
        '''
        Return the value in percentage based on the _min and the _max for the provided value
        If out of bound, returns max or min. 
        '''
        if self._max == None or self._min == None:
            raise InvalidMinMaxException(message="Minimum and / or maximum boundaries are not define for sensor " + self._name)
        
        # clamp the value between _min and _max to ensure it falls within the range
        value_clamped = max(self._min, min(self._max, value))
        return ((value_clamped - self._min) / (self._max - self._min)) * 100

    def get_percentage_data(self) -> float:
        '''
        Reads the sensor value and returns the value in percentage based on the _min and the _max
        If out of bound, returns closest max or min. 
        '''

        if self._max == None or self._min == None:
            raise InvalidMinMaxException(message="Minimum and / or maximum boundaries are not define for sensor " + self._name)
        
        # clamp the value between _min and _max to ensure it falls within the range
        value_clamped = max(self._min, min(self._max, self.get_raw_data()))
        return ((value_clamped - self._min) / (self._max - self._min)) * 100
    
    def calibrate_min(self):
        '''
        Allows to set _min using a mean of 10 readings with 100 ms interval. The min should reflect the minimum value expected to be returned.
        Place the sensor in the conditions triggering the minimum output and call the method.
        Should be called before calibrate_max if no _max value has been set.
        '''
        ms_interval = 100
        iterations = 10
        total = 0
        for _ in range(iterations):
            total += self.get_raw_data()
            sleep_ms(ms_interval)
        self.min = int(total/iterations) # we use the setter to check for the exceptions
    
    def calibrate_max(self):
        '''
        Allows to set _max using a mean of 10 readings with 100 ms. The max should reflect the maximum value expected to be returned.
        Place the sensor in the conditions triggering the maximum output and call the method.
        '''
        ms_interval = 100
        iterations = 10
        total = 0
        for _ in range(iterations):
            total += self.get_raw_data()
            sleep_ms(ms_interval)
        self.max = int(total/iterations) # we use the setter to check for the exceptions

    def to_string(self):
        '''
        Returns a string about the sensor with key attributes' values
        '''
        return "Sensor {}, connected to pin {}, with min = {} and max = {}".format(self.name, self.pin, self.min, self.max)