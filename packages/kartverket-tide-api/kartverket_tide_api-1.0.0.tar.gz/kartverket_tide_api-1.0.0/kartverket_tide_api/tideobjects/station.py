class Station:
    """Used to represent a station

    Attributes
    ----------
    name
        name of the station

    code
        code of the station

    lat
        latitude of the station

    lon
        longitude of the station

    station_type
        the station type for the station. Can be PERM, CURRENT, ACTIVE or SECOND
    """
    def __init__(self, name, code, lat, long, station_type=""):
        """
        :param name:
        :param code:
        :param lat:
        :param long:
        :param station_type:

        :raises ValueError: invalid station type
        """
        if station_type != 'PERM' and station_type != 'CURRENT' and station_type != 'ACTIVE' and station_type != 'SECOND' and station_type != "":
            raise ValueError('station_type must be PERM, CURRENT, TEMP or PUBLIC')
        self.name = name
        self.code = code
        self.lat = lat
        self.long = long
        self.station_type = station_type
