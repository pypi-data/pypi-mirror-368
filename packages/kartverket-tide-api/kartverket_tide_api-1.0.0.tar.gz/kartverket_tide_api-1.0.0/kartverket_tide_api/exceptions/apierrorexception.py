class ApiErrorException(Exception):
    """An API Error Exception"""

    def __init__(self, status):
        self.status = status

    def __str__(self):
        return "APIError: status={}".format(self.status)


class InvalidStationTypeErrorException(ApiErrorException):
    """Invalid station type error exception"""

    def __init__(self, status):
        self.status = status

    def __str__(self):
        return "InvalidStationTypeError: status={}".format(self.status)


class NoTideDataErrorException(ApiErrorException):
    """No tide data error exception"""

    def __init__(self, status):
        self.status = status

    def __str__(self):
        return "NoTideDataErrorException: status={}".format(self.status)


class UnknownApiErrorException(ApiErrorException):
    """Unknown exception due to an error returned by the api"""

    def __init__(self, status):
        self.status = status

    def __str__(self):
        return "UnknownApiErrorException: status={}".format(self.status)
