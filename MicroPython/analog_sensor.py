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
        return self._pin

    @pin.setter #allows to set the value using object.pin instead of object.pin()
    def pin(self, value: int):
        # Check if the pin is a valid analog pin for a 
        if value not in valid_pico_w_analog_pins:
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
        '''
        Should be used only if min has been set
        '''
        if self._min is None:
            raise InvalidMinMaxException(message="Please set the minimum for " + self._name + " first.")
        if value < 0 or value < self._min:
            raise InvalidMinMaxException(message="The maximum boundary for " + self._name + " should be >= 0. and >= to the minimum boundary.")
        self._max = value
    @property
    def min(self) -> int:
        return self._min

    @min.setter
    def min(self, value: int):
        # check if the value is <= to 0 -> negatives are not allowed
        if value < 0:
            raise InvalidMinMaxException(message="The minimum boundary for " + self._name + " should be >= 0")
        # Check if the max has been defined and in that case if the value is superior or equal to the max -> there should be a gap between min and max with min < max
        if self._max is not None and value >= self._max:
            raise InvalidMinMaxException(message="The minimum boundary for " + self._name + " should be < to the maximum boundary")
        self._min = value
        

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
        If out of bound, returns closest max or min. 
        '''
        if self._max is None or self._min is None:
            raise InvalidMinMaxException(message="Minimum and/or maximum boundaries are not defined for sensor " + self._name)

        if value <= self.min:
            return 0.0
        if value >= self.max:
            return 100.0
        
        adjusted_max = self.max - self.min
        adjusted_value = value - self.min
        percentage = adjusted_value / adjusted_max * 100
        
        return percentage

    def get_percentage_data(self) -> float:
        '''
        Reads the sensor value and returns the value in percentage based on the _min and the _max
        If out of bound, returns closest max or min. 
        '''
        # clamp the value between _min and _max to ensure it falls within the range
        result = self.calculate_percentage_data(value=self.get_raw_data())
        return result
    
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
        self.min = int(round(total/iterations)) # we use the setter to check for the exceptions
    
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
        self.max = int(round(total/iterations)) # we use the setter to check for the exceptions

    def __str__(self):
        '''
        Returns a string about the sensor with key attributes' values
        '''
        return "Sensor {}, connected to pin {}, with min = {} and max = {}".format(self.name, self.pin, self.min, self.max)