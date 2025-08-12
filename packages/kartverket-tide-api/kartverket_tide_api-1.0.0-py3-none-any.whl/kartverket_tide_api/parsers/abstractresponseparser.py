import xml.etree.ElementTree as ElementTree
from kartverket_tide_api.exceptions import InvalidStationTypeErrorException, UnknownApiErrorException
from abc import ABC, abstractmethod


class AbstractResponseParser(ABC):
    """An abstract class for parsing a response from the api

    This class is abstract. A sub class should be created for each response that is to be parsed.
    The sub class should implement the parsing logic in _parsing_logic.
    parse_response should be called to parse the response

    Attributes
    ----------
    root: Element
        the root element of the response XML tree
    """

    def __init__(self, response: str):
        """
        Parameters
        ----------
        response
            a string of the XMl response
        """
        self.root = ElementTree.XML(response)
        super().__init__()

    def error_check(self):
        """Checks if the response being parsed is an error response, and raises an appropriate exception in case of
        an error

        Raises
        ------
        InvalidStationTypeErrorException
            response contains an error for invalid station type

        UnknownApiErrorException
            response contains some unknown error
        """
        error = self.root.find('error')
        if error is not None:
            if error.attrib == 'Invalid station type':
                raise InvalidStationTypeErrorException('Invalid station type')
            else:
                raise UnknownApiErrorException(error.attrib)

    @abstractmethod
    def _parsing_logic(self) -> {}:
        """Abstract method that performs the parsing of the response. This method should be implemented to parse a
        specific response

        Return
        ------
        dict
        """
        pass

    def parse_response(self):
        """Start parsing the response by checking for errors and using the _parsing_logic implementation

        Raises
        ------
        ApiErrorException
        Exceptions documented in the error_check method

        Return
        ------
        dict containing
        """
        self.error_check()
        return self._parsing_logic()
