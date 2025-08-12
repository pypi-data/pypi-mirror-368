from kartverket_tide_api.parsers import AbstractResponseParser
from kartverket_tide_api.exceptions import CannotFindElementException, NoTideDataErrorException
from kartverket_tide_api.tideobjects import WaterLevel


class LocationDataParser(AbstractResponseParser):
    def _parsing_logic(self) -> {}:
        """Parse the response of a station list request. Returns a dictionary containing a list of stations

        :exception CannotFindElementException: cannot find some expected element in the xml
        :exception NoTideDataErrorException: the xml has no tide data

        :return dict containing a list of WaterLevel objects
        """
        location_data = self.root.find('locationdata')
        if location_data is None:
            raise CannotFindElementException('Cannot find location_data element')
        nodata = location_data.find('nodata')

        if nodata is not None:
            raise NoTideDataErrorException('This location has no tide data')
        data = location_data.find('data')

        if data is None:
            raise CannotFindElementException('Cannot find data element')

        data_type = data.attrib['type']
        water_levels = []
        for water_level in data.iter('waterlevel'):
            attribs = water_level.attrib
            if attribs['flag'] == 'high' or attribs['flag'] == 'low':
                water_levels.append(WaterLevel(attribs['value'],
                                               attribs['time'],
                                               data_type,
                                               attribs['flag'] == 'high'))
            else:
                water_levels.append(WaterLevel(attribs['value'],
                                               attribs['time'],
                                               data_type))

        return {'data': water_levels}
