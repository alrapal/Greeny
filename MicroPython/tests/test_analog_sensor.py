from unittest.mock import MagicMock
import unittest
import sys
from ..custom_exceptions import *
# Create a mock machine module since it is MicroPython dependent
mock_machine = MagicMock()
sys.modules['machine'] = mock_machine

# Create a mock time module since it is MicroPython dependent (sleep_ms)
mock_time = MagicMock()
sys.modules['time'] = mock_time

# Mock sleep_ms
def mock_sleep_ms(ms):
    pass

mock_time.sleep_ms = mock_sleep_ms

class MockADC:
    def read_u16(self):
        return 123456

class MockPin:
    def init(self, mode):
        pass


# Assign mock classes to ADC and Pin attributes of mock_machine
mock_machine.ADC.return_value = MockADC()
mock_machine.Pin.return_value = MockPin()

from MicroPython.analog_sensor import AnalogSensor

class TestAnalogSensor(unittest.TestCase):
    def test_get_raw_data(self):
        sensor = AnalogSensor(26, "TestSensor")  # This will use your MockADC and MockPin
        self.assertEqual(sensor.get_raw_data(), 123456)  # the mock value we set in MockADC.read_u16

    def test_calculate_percentage_data_comprised_value(self):
        sensor = AnalogSensor(26, "TestSensor")
        # set min and max as light sensor
        sensor.min = 300
        sensor.max = 2000

        result = sensor.calculate_percentage_data(value=1150)
        self.assertTrue(result == 50,msg="Should be 50% - is {}".format(result))

    def test_calculate_percentage_data_negative_value(self):
        sensor = AnalogSensor(26, "TestSensor")
        # set min and max as light sensor
        sensor.min = 300
        sensor.max = 2000

        result = sensor.calculate_percentage_data(value=-100)
        self.assertTrue(result == 0,msg="Should be 0% - is {}".format(result))

    def test_calculate_percentage_data_above_max(self):
        sensor = AnalogSensor(26, "TestSensor")
        # set min and max as light sensor
        sensor.min = 300
        sensor.max = 2000

        result = sensor.calculate_percentage_data(value=50000)
        self.assertTrue(result == 100,msg="Should be 0% - is {}".format(result))
    

    def test_set_max_first_should_throw_exception(self):
        sensor = AnalogSensor(26, "TestSensor")

        with self.assertRaises(InvalidMinMaxException):
            # Call the method or code that should raise the exception
            sensor.max = 2000
