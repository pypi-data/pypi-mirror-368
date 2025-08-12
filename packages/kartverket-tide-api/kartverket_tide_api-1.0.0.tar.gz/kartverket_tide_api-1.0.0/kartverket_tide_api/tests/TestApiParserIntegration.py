import unittest

from kartverket_tide_api.exceptions import NoTideDataErrorException
from kartverket_tide_api.tide_api import TideApi
from kartverket_tide_api.parsers import LocationDataParser
import vcr

from kartverket_tide_api.tideobjects import WaterLevel


class TestApiParserIntegration(unittest.TestCase):
    def setUp(self) -> None:
        self.api = TideApi()
        self.valid_lat = 70
        self.invalid_lat = 68
        self.valid_lon = 20
        self.invalid_lon = 20
        self.from_time = '2019-12-31T15:52:01+01'
        self.to_time = '2020-01-03T15:52:01+01'

    @vcr.use_cassette('vcr_cassete/locationdata_valid.yaml')
    def test_get_location_data_valid(self):
        result = self.api.get_location_data(self.valid_lon, self.valid_lat, self.from_time, self.to_time, 'TAB')
        parser = LocationDataParser(result)
        water_level_list = parser.parse_response()['data']
        assert len(water_level_list) > 0
        for water_level in water_level_list:
            assert type(water_level) is WaterLevel

    @vcr.use_cassette('vcr_cassete/locationdata_nodata.yaml')
    def test_get_location_data_invalid_location(self):
        result = self.api.get_location_data(self.invalid_lon, self.invalid_lat,
                                            self.from_time, self.to_time, 'TAB')
        parser = LocationDataParser(result)
        self.assertRaises(NoTideDataErrorException, parser.parse_response)

    # TODO test station


if __name__ == '__main__':
    unittest.main()
