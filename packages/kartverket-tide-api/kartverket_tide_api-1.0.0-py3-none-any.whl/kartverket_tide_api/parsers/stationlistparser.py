from kartverket_tide_api.parsers import AbstractResponseParser
from kartverket_tide_api.tideobjects import Station
from kartverket_tide_api.exceptions import CannotFindElementException


class StationListParser(AbstractResponseParser):
    def _parsing_logic(self) -> {}:
        """Parse the response of a station list request. Returns a dictionary containing a list of stations

        Excaptions
        ----------
        CannotFindElementException
            the xml input doesn't contain some element

        InvalidStationTypeException
            the xml input contains a invalid station type error

        :return dict containing a list of Station objects
        """
        station_info = self.root.find('stationinfo')
        if station_info is None:
            raise CannotFindElementException('Cannot find station_info element')
        stations = []
        for station in station_info.iter('location'):
            attribs = station.attrib
            stations.append(Station(attribs['name'],
                                    attribs['code'],
                                    attribs['latitude'],
                                    attribs['longitude'],
                                    attribs['type']))
        return {'stationinfo': stations}
