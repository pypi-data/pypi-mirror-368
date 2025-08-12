from typing import List
from typing import Union
from .utils.json_map import JsonMap
from .utils.base_model import BaseModel
from .utils.sentinel import SENTINEL


@JsonMap(
    {
        "id_": "id",
        "data_limit_in_bytes": "dataLimitInBytes",
        "min_days": "minDays",
        "max_days": "maxDays",
        "price_in_cents": "priceInCents",
    }
)
class Packages(BaseModel):
    """Packages

    :param id_: ID of the package, defaults to None
    :type id_: str, optional
    :param destination: ISO representation of the package's destination., defaults to None
    :type destination: str, optional
    :param data_limit_in_bytes: Size of the package in Bytes, defaults to None
    :type data_limit_in_bytes: float, optional
    :param min_days: Min number of days for the package, defaults to None
    :type min_days: float, optional
    :param max_days: Max number of days for the package, defaults to None
    :type max_days: float, optional
    :param price_in_cents: Price of the package in cents, defaults to None
    :type price_in_cents: float, optional
    """

    def __init__(
        self,
        id_: str = SENTINEL,
        destination: str = SENTINEL,
        data_limit_in_bytes: float = SENTINEL,
        min_days: float = SENTINEL,
        max_days: float = SENTINEL,
        price_in_cents: float = SENTINEL,
        **kwargs
    ):
        """Packages

        :param id_: ID of the package, defaults to None
        :type id_: str, optional
        :param destination: ISO representation of the package's destination., defaults to None
        :type destination: str, optional
        :param data_limit_in_bytes: Size of the package in Bytes, defaults to None
        :type data_limit_in_bytes: float, optional
        :param min_days: Min number of days for the package, defaults to None
        :type min_days: float, optional
        :param max_days: Max number of days for the package, defaults to None
        :type max_days: float, optional
        :param price_in_cents: Price of the package in cents, defaults to None
        :type price_in_cents: float, optional
        """
        self.id_ = self._define_str("id_", id_, nullable=True)
        self.destination = self._define_str("destination", destination, nullable=True)
        self.data_limit_in_bytes = self._define_number(
            "data_limit_in_bytes", data_limit_in_bytes, nullable=True
        )
        self.min_days = self._define_number("min_days", min_days, nullable=True)
        self.max_days = self._define_number("max_days", max_days, nullable=True)
        self.price_in_cents = self._define_number(
            "price_in_cents", price_in_cents, nullable=True
        )
        self._kwargs = kwargs


@JsonMap({"after_cursor": "afterCursor"})
class ListPackagesOkResponse(BaseModel):
    """ListPackagesOkResponse

    :param packages: packages, defaults to None
    :type packages: List[Packages], optional
    :param after_cursor: The cursor value representing the end of the current page of results. Use this cursor value as the "afterCursor" parameter in your next request to retrieve the subsequent page of results. It ensures that you continue fetching data from where you left off, facilitating smooth pagination, defaults to None
    :type after_cursor: str, optional
    """

    def __init__(
        self,
        packages: List[Packages] = SENTINEL,
        after_cursor: Union[str, None] = SENTINEL,
        **kwargs
    ):
        """ListPackagesOkResponse

        :param packages: packages, defaults to None
        :type packages: List[Packages], optional
        :param after_cursor: The cursor value representing the end of the current page of results. Use this cursor value as the "afterCursor" parameter in your next request to retrieve the subsequent page of results. It ensures that you continue fetching data from where you left off, facilitating smooth pagination, defaults to None
        :type after_cursor: str, optional
        """
        self.packages = self._define_list(packages, Packages)
        self.after_cursor = self._define_str(
            "after_cursor", after_cursor, nullable=True
        )
        self._kwargs = kwargs
