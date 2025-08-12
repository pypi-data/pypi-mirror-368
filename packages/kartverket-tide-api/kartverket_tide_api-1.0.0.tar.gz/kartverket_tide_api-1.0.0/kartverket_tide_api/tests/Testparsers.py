import unittest
from kartverket_tide_api.parsers import LocationDataParser
from kartverket_tide_api.tideobjects import WaterLevel
from kartverket_tide_api.exceptions import NoTideDataErrorException
from kartverket_tide_api.exceptions import CannotFindElementException


class TestParsers(unittest.TestCase):
    location_data_valid = """<tide>
<service cominfo="Informasjon relatert til kommune- og regionreformen: Det vil fremover være mulig å søke på både gamle og nye kommunenavn på Se havnivå og Se havnivå i kart. Oppdatert statistikk på Se havnivå i kart vil bli tilgjengelig i løpet av de første tre ukene i 2020. "/>
<locationdata>
<location name="TROMSØ" code="TOS" latitude="70.000000" longitude="20.000000" delay="0" factor="1.07" obsname="TROMSØ" obscode="TOS"/>
<reflevelcode>CD</reflevelcode>
<data type="prediction" unit="cm">
<waterlevel value="281.2" time="2019-12-31T16:40:00+01:00" flag="high"/>
<waterlevel value="95.2" time="2019-12-31T23:02:00+01:00" flag="low"/>
<waterlevel value="253.9" time="2020-01-01T05:10:00+01:00" flag="high"/>
<waterlevel value="114.3" time="2020-01-01T11:08:00+01:00" flag="low"/>
<waterlevel value="269.5" time="2020-01-01T17:21:00+01:00" flag="high"/>
<waterlevel value="105.6" time="2020-01-01T23:46:00+01:00" flag="low"/>
<waterlevel value="244.0" time="2020-01-02T05:56:00+01:00" flag="high"/>
<waterlevel value="125.3" time="2020-01-02T11:53:00+01:00" flag="low"/>
<waterlevel value="258.0" time="2020-01-02T18:06:00+01:00" flag="high"/>
<waterlevel value="114.5" time="2020-01-03T00:34:00+01:00" flag="low"/>
<waterlevel value="236.3" time="2020-01-03T06:49:00+01:00" flag="high"/>
<waterlevel value="134.8" time="2020-01-03T12:46:00+01:00" flag="low"/>
</data>
</locationdata>
</tide>"""

    location_data_no_data = """<tide>
<locationdata>
<nodata info="Sorry. We do not have sea level data for this area."/>
</locationdata>
</tide>"""

    missing_locationdata_tag = """<tide>
    <loca>
    </loca>
    </tide>"""

    missing_data_tag = """<tide>
    <service cominfo="Informasjon relatert til kommune- og regionreformen: Det vil fremover være mulig å søke på både gamle og nye kommunenavn på Se havnivå og Se havnivå i kart. Oppdatert statistikk på Se havnivå i kart vil bli tilgjengelig i løpet av de første tre ukene i 2020. "/>
    <locationdata>
    <location name="TROMSØ" code="TOS" latitude="70.000000" longitude="20.000000" delay="0" factor="1.07" obsname="TROMSØ" obscode="TOS"/>
    <reflevelcode>CD</reflevelcode>
    <da type="prediction" unit="cm">
    <waterlevel value="281.2" time="2019-12-31T16:40:00+01:00" flag="high"/>
    <waterlevel value="95.2" time="2019-12-31T23:02:00+01:00" flag="low"/>
    <waterlevel value="253.9" time="2020-01-01T05:10:00+01:00" flag="high"/>
    <waterlevel value="114.3" time="2020-01-01T11:08:00+01:00" flag="low"/>
    <waterlevel value="269.5" time="2020-01-01T17:21:00+01:00" flag="high"/>
    <waterlevel value="105.6" time="2020-01-01T23:46:00+01:00" flag="low"/>
    <waterlevel value="244.0" time="2020-01-02T05:56:00+01:00" flag="high"/>
    <waterlevel value="125.3" time="2020-01-02T11:53:00+01:00" flag="low"/>
    <waterlevel value="258.0" time="2020-01-02T18:06:00+01:00" flag="high"/>
    <waterlevel value="114.5" time="2020-01-03T00:34:00+01:00" flag="low"/>
    <waterlevel value="236.3" time="2020-01-03T06:49:00+01:00" flag="high"/>
    <waterlevel value="134.8" time="2020-01-03T12:46:00+01:00" flag="low"/>
    </da>
    </locationdata>
    </tide>"""

    def test_location_data_parser_valid(self):
        parser = LocationDataParser(self.location_data_valid)
        result = parser.parse_response()
        water_level_list = result['data']
        assert len(water_level_list) > 0
        for water_level in water_level_list:
            assert type(water_level) is WaterLevel

    def test_local_data_parser_no_data(self):
        parser = LocationDataParser(self.location_data_no_data)
        self.assertRaises(NoTideDataErrorException, parser.parse_response)

    def test_local_data_parser_missing_locationdata_tag(self):
        parser = LocationDataParser(self.missing_locationdata_tag)
        self.assertRaises(CannotFindElementException, parser.parse_response)

    def test_local_data_parser_missing_data_tag(self):
        parser = LocationDataParser(self.missing_data_tag)
        self.assertRaises(CannotFindElementException, parser.parse_response)
    # TODO: station parser


if __name__ == '__main__':
    unittest.main()
