import unittest
from kartverket_tide_api.tide_api import TideApi
import vcr
import xml.etree.ElementTree as ElementTree


class TestTideApi(unittest.TestCase):
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
        ElementTree.fromstring(result)

    @vcr.use_cassette('vcr_cassete/locationdata_nodata.yaml')
    def test_get_location_data_invalid_location(self):
        result = self.api.get_location_data(self.invalid_lon, self.invalid_lat,
                                            self.from_time, self.to_time, 'TAB')
        ElementTree.fromstring(result)

    def test_get_location_data_invalid_type(self):
        self.assertRaises(ValueError, self.api.get_location_data, self.invalid_lon, self.invalid_lat,
                          self.from_time, self.to_time, 'TA')

    # TODO test getstation


if __name__ == '__main__':
    unittest.main()
