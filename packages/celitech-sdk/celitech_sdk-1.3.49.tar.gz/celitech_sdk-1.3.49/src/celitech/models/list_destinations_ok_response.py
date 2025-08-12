from typing import List
from .utils.json_map import JsonMap
from .utils.base_model import BaseModel
from .utils.sentinel import SENTINEL


@JsonMap({"supported_countries": "supportedCountries"})
class Destinations(BaseModel):
    """Destinations

    :param name: Name of the destination, defaults to None
    :type name: str, optional
    :param destination: ISO representation of the destination, defaults to None
    :type destination: str, optional
    :param supported_countries: This array indicates the geographical area covered by a specific destination. If the destination represents a single country, the array will include that country. However, if the destination represents a broader regional scope, the array will be populated with the names of the countries belonging to that region., defaults to None
    :type supported_countries: List[str], optional
    """

    def __init__(
        self,
        name: str = SENTINEL,
        destination: str = SENTINEL,
        supported_countries: List[str] = SENTINEL,
        **kwargs
    ):
        """Destinations

        :param name: Name of the destination, defaults to None
        :type name: str, optional
        :param destination: ISO representation of the destination, defaults to None
        :type destination: str, optional
        :param supported_countries: This array indicates the geographical area covered by a specific destination. If the destination represents a single country, the array will include that country. However, if the destination represents a broader regional scope, the array will be populated with the names of the countries belonging to that region., defaults to None
        :type supported_countries: List[str], optional
        """
        self.name = self._define_str("name", name, nullable=True)
        self.destination = self._define_str("destination", destination, nullable=True)
        self.supported_countries = supported_countries
        self._kwargs = kwargs


@JsonMap({})
class ListDestinationsOkResponse(BaseModel):
    """ListDestinationsOkResponse

    :param destinations: destinations, defaults to None
    :type destinations: List[Destinations], optional
    """

    def __init__(self, destinations: List[Destinations] = SENTINEL, **kwargs):
        """ListDestinationsOkResponse

        :param destinations: destinations, defaults to None
        :type destinations: List[Destinations], optional
        """
        self.destinations = self._define_list(destinations, Destinations)
        self._kwargs = kwargs
