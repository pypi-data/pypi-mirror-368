from typing import List
from typing import Union
from .utils.json_map import JsonMap
from .utils.base_model import BaseModel
from .utils.sentinel import SENTINEL


@JsonMap(
    {
        "id_": "id",
        "data_limit_in_bytes": "dataLimitInBytes",
        "destination_name": "destinationName",
        "price_in_cents": "priceInCents",
    }
)
class Package(BaseModel):
    """Package

    :param id_: ID of the package, defaults to None
    :type id_: str, optional
    :param data_limit_in_bytes: Size of the package in Bytes, defaults to None
    :type data_limit_in_bytes: float, optional
    :param destination: ISO representation of the package's destination., defaults to None
    :type destination: str, optional
    :param destination_name: Name of the package's destination, defaults to None
    :type destination_name: str, optional
    :param price_in_cents: Price of the package in cents, defaults to None
    :type price_in_cents: float, optional
    """

    def __init__(
        self,
        id_: str = SENTINEL,
        data_limit_in_bytes: float = SENTINEL,
        destination: str = SENTINEL,
        destination_name: str = SENTINEL,
        price_in_cents: float = SENTINEL,
        **kwargs
    ):
        """Package

        :param id_: ID of the package, defaults to None
        :type id_: str, optional
        :param data_limit_in_bytes: Size of the package in Bytes, defaults to None
        :type data_limit_in_bytes: float, optional
        :param destination: ISO representation of the package's destination., defaults to None
        :type destination: str, optional
        :param destination_name: Name of the package's destination, defaults to None
        :type destination_name: str, optional
        :param price_in_cents: Price of the package in cents, defaults to None
        :type price_in_cents: float, optional
        """
        self.id_ = self._define_str("id_", id_, nullable=True)
        self.data_limit_in_bytes = self._define_number(
            "data_limit_in_bytes", data_limit_in_bytes, nullable=True
        )
        self.destination = self._define_str("destination", destination, nullable=True)
        self.destination_name = self._define_str(
            "destination_name", destination_name, nullable=True
        )
        self.price_in_cents = self._define_number(
            "price_in_cents", price_in_cents, nullable=True
        )
        self._kwargs = kwargs


@JsonMap({})
class PurchasesEsim(BaseModel):
    """PurchasesEsim

    :param iccid: ID of the eSIM, defaults to None
    :type iccid: str, optional
    """

    def __init__(self, iccid: str = SENTINEL, **kwargs):
        """PurchasesEsim

        :param iccid: ID of the eSIM, defaults to None
        :type iccid: str, optional
        """
        self.iccid = self._define_str(
            "iccid", iccid, nullable=True, min_length=18, max_length=22
        )
        self._kwargs = kwargs


@JsonMap(
    {
        "id_": "id",
        "start_date": "startDate",
        "end_date": "endDate",
        "created_date": "createdDate",
        "start_time": "startTime",
        "end_time": "endTime",
        "created_at": "createdAt",
        "purchase_type": "purchaseType",
        "reference_id": "referenceId",
    }
)
class Purchases(BaseModel):
    """Purchases

    :param id_: ID of the purchase, defaults to None
    :type id_: str, optional
    :param start_date: Start date of the package's validity in the format 'yyyy-MM-ddThh:mm:ssZZ', defaults to None
    :type start_date: str, optional
    :param end_date: End date of the package's validity in the format 'yyyy-MM-ddThh:mm:ssZZ', defaults to None
    :type end_date: str, optional
    :param created_date: Creation date of the purchase in the format 'yyyy-MM-ddThh:mm:ssZZ', defaults to None
    :type created_date: str, optional
    :param start_time: Epoch value representing the start time of the package's validity, defaults to None
    :type start_time: float, optional
    :param end_time: Epoch value representing the end time of the package's validity, defaults to None
    :type end_time: float, optional
    :param created_at: Epoch value representing the date of creation of the purchase, defaults to None
    :type created_at: float, optional
    :param package: package, defaults to None
    :type package: Package, optional
    :param esim: esim, defaults to None
    :type esim: PurchasesEsim, optional
    :param source: The `source` indicates whether the purchase was made from the API, dashboard, landing-page, promo-page or iframe. For purchases made before September 8, 2023, the value will be displayed as 'Not available'., defaults to None
    :type source: str, optional
    :param purchase_type: The `purchaseType` indicates whether this is the initial purchase that creates the eSIM (First Purchase) or a subsequent top-up on an existing eSIM (Top-up Purchase)., defaults to None
    :type purchase_type: str, optional
    :param reference_id: The `referenceId` that was provided by the partner during the purchase or top-up flow. This identifier can be used for analytics and debugging purposes., defaults to None
    :type reference_id: str, optional
    """

    def __init__(
        self,
        id_: str = SENTINEL,
        start_date: str = SENTINEL,
        end_date: str = SENTINEL,
        created_date: str = SENTINEL,
        start_time: float = SENTINEL,
        end_time: float = SENTINEL,
        created_at: float = SENTINEL,
        package: Package = SENTINEL,
        esim: PurchasesEsim = SENTINEL,
        source: str = SENTINEL,
        purchase_type: str = SENTINEL,
        reference_id: str = SENTINEL,
        **kwargs
    ):
        """Purchases

        :param id_: ID of the purchase, defaults to None
        :type id_: str, optional
        :param start_date: Start date of the package's validity in the format 'yyyy-MM-ddThh:mm:ssZZ', defaults to None
        :type start_date: str, optional
        :param end_date: End date of the package's validity in the format 'yyyy-MM-ddThh:mm:ssZZ', defaults to None
        :type end_date: str, optional
        :param created_date: Creation date of the purchase in the format 'yyyy-MM-ddThh:mm:ssZZ', defaults to None
        :type created_date: str, optional
        :param start_time: Epoch value representing the start time of the package's validity, defaults to None
        :type start_time: float, optional
        :param end_time: Epoch value representing the end time of the package's validity, defaults to None
        :type end_time: float, optional
        :param created_at: Epoch value representing the date of creation of the purchase, defaults to None
        :type created_at: float, optional
        :param package: package, defaults to None
        :type package: Package, optional
        :param esim: esim, defaults to None
        :type esim: PurchasesEsim, optional
        :param source: The `source` indicates whether the purchase was made from the API, dashboard, landing-page, promo-page or iframe. For purchases made before September 8, 2023, the value will be displayed as 'Not available'., defaults to None
        :type source: str, optional
        :param purchase_type: The `purchaseType` indicates whether this is the initial purchase that creates the eSIM (First Purchase) or a subsequent top-up on an existing eSIM (Top-up Purchase)., defaults to None
        :type purchase_type: str, optional
        :param reference_id: The `referenceId` that was provided by the partner during the purchase or top-up flow. This identifier can be used for analytics and debugging purposes., defaults to None
        :type reference_id: str, optional
        """
        self.id_ = self._define_str("id_", id_, nullable=True)
        self.start_date = self._define_str("start_date", start_date, nullable=True)
        self.end_date = self._define_str("end_date", end_date, nullable=True)
        self.created_date = self._define_str(
            "created_date", created_date, nullable=True
        )
        self.start_time = self._define_number("start_time", start_time, nullable=True)
        self.end_time = self._define_number("end_time", end_time, nullable=True)
        self.created_at = self._define_number("created_at", created_at, nullable=True)
        self.package = self._define_object(package, Package)
        self.esim = self._define_object(esim, PurchasesEsim)
        self.source = self._define_str("source", source, nullable=True)
        self.purchase_type = self._define_str(
            "purchase_type", purchase_type, nullable=True
        )
        self.reference_id = self._define_str(
            "reference_id", reference_id, nullable=True
        )
        self._kwargs = kwargs


@JsonMap({"after_cursor": "afterCursor"})
class ListPurchasesOkResponse(BaseModel):
    """ListPurchasesOkResponse

    :param purchases: purchases, defaults to None
    :type purchases: List[Purchases], optional
    :param after_cursor: The cursor value representing the end of the current page of results. Use this cursor value as the "afterCursor" parameter in your next request to retrieve the subsequent page of results. It ensures that you continue fetching data from where you left off, facilitating smooth pagination., defaults to None
    :type after_cursor: str, optional
    """

    def __init__(
        self,
        purchases: List[Purchases] = SENTINEL,
        after_cursor: Union[str, None] = SENTINEL,
        **kwargs
    ):
        """ListPurchasesOkResponse

        :param purchases: purchases, defaults to None
        :type purchases: List[Purchases], optional
        :param after_cursor: The cursor value representing the end of the current page of results. Use this cursor value as the "afterCursor" parameter in your next request to retrieve the subsequent page of results. It ensures that you continue fetching data from where you left off, facilitating smooth pagination., defaults to None
        :type after_cursor: str, optional
        """
        self.purchases = self._define_list(purchases, Purchases)
        self.after_cursor = self._define_str(
            "after_cursor", after_cursor, nullable=True
        )
        self._kwargs = kwargs
