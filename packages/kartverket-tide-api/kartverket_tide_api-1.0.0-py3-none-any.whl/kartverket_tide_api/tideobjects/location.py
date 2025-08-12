class Location:
    """Represents a location in the api"""
    def __init__(self, name, code, lat, lon):
        self.lat = lat
        self.code = code
        self.name = name
        self.lon = lon
