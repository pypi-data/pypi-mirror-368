import requests


class TideApi:
    """Used to send api requests to kartverket tide api"""
    api_endpoint = 'https://vannstand.kartverket.no/tideapi.php'

    def get_station_list(self, station_type='PERM'):
        """Send a stationlist request to the tide api.
        Parameters
        ----------
        station_type
            the type of station that is being requested. Valid station types are:
            PERM
            CURRENT
            TEMP
            PUBLIC

        Raises
        ------
        ValueError
            invalid station type

        HTTPError
            status code of response wasn't 200

        Return
        ------
        string containing xml
        """
        if station_type != 'PERM' and station_type != 'CURRENT' and station_type != 'TEMP' and station_type != 'PUBLIC':
            raise ValueError('station_type must be PERM, CURRENT, TEMP or PUBLIC')
        payload = {'tide_request': 'stationlist',
                   'station_type': station_type}
        response = self.send_request(payload)

        return response

    def get_location_data(self, lon, lat, fromtime, totime, data_type='PRE'):
        """send locationdata request to tide api

        Parameters
        ----------
        lon: get tide data from this longitude
        lat: get tide data from this latitude
        fromtime: get tide data from this time
        totime: get tide data to this time
        data_type: type of tide data. Valid types are ALL, TAB, PRE and OBS

        Raises
        ------
        ValueError
            invalid parameter input

        HTTPError
            status code of response wasn't 200

        Timeout
            request timed out


        :return string containing xml
        """
        if data_type not in ['ALL', 'TAB', 'PRE', 'OBS']:
            raise ValueError('data_type must be ALL, TAB, OBS or PRE')
        tide_request = 'locationdata'
        dst = '1'
        refcode = 'CD'
        lang = 'en'

        payload = {'tide_request': tide_request,
                   'fromtime': fromtime,
                   'totime': totime,
                   'data_type': data_type,
                   'dst': dst,
                   'refcode': refcode,
                   'lang': lang,
                   'lon': lon,
                   'lat': lat,
                   'datatype': data_type}
        response = self.send_request(payload)
        return response

    def send_request(self, payload: {}):
        """Send a http request to the tide api endpoint

        Parameters
        ----------
        payload
            dictionary containing http parameters

        Raises
        ------
        HTTPError
            status code of response wasn't 200

        Timeout
            request timed out

        TooManyRedirects

        RequestException

        Return
        ------
        string containing the body of the http response
        """
        try:
            response = requests.get(self.api_endpoint, params=payload)
            # Check for failure in response code and raise exception if error is found
            response.raise_for_status()
            return response.content.decode()
        except requests.exceptions.Timeout as e:
            raise e
        except requests.exceptions.TooManyRedirects:
            # TODO: Handle this exception
            pass
        except requests.exceptions.RequestException as e:
            raise e
