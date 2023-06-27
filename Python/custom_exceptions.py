class InvalidPinException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class InvalidMinMaxException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class InvalidSensorNameException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)