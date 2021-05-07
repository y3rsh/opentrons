class SerialException(Exception):
    pass


class NoResponse(SerialException):
    pass


class AlarmResponse(SerialException):
    pass


class ErrorResponse(SerialException):
    pass
