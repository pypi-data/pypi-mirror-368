class WaterLevel:
    """Represents waterlevel in the api"""
    def __init__(self, value, time, data_type, tide=None):
        """
        :param value: height of the tide
        :param time: time of this height of the tide
        :param data_type: data type. Myst be prediction, observation, weathereffect or forecast
        :param tide: true if high tide, false if low tide. None by default
        """
        if data_type not in ['prediction', 'observation', 'weathereffect', 'forecast']:
            raise ValueError('type must be prediction, observation, weathereffect or forecast')
        self.tide = tide
        self.type = data_type
        self.time = time
        self.value = value
