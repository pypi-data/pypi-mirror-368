from .utils.json_map import JsonMap
from .utils.base_model import BaseModel
from .utils.sentinel import SENTINEL


@JsonMap(
    {
        "id_": "id",
        "package_id": "packageId",
        "start_date": "startDate",
        "end_date": "endDate",
        "created_date": "createdDate",
        "start_time": "startTime",
        "end_time": "endTime",
    }
)
class TopUpEsimOkResponsePurchase(BaseModel):
    """TopUpEsimOkResponsePurchase

    :param id_: ID of the purchase, defaults to None
    :type id_: str, optional
    :param package_id: ID of the package, defaults to None
    :type package_id: str, optional
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
    """

    def __init__(
        self,
        id_: str = SENTINEL,
        package_id: str = SENTINEL,
        start_date: str = SENTINEL,
        end_date: str = SENTINEL,
        created_date: str = SENTINEL,
        start_time: float = SENTINEL,
        end_time: float = SENTINEL,
        **kwargs
    ):
        """TopUpEsimOkResponsePurchase

        :param id_: ID of the purchase, defaults to None
        :type id_: str, optional
        :param package_id: ID of the package, defaults to None
        :type package_id: str, optional
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
        """
        self.id_ = self._define_str("id_", id_, nullable=True)
        self.package_id = self._define_str("package_id", package_id, nullable=True)
        self.start_date = self._define_str("start_date", start_date, nullable=True)
        self.end_date = self._define_str("end_date", end_date, nullable=True)
        self.created_date = self._define_str(
            "created_date", created_date, nullable=True
        )
        self.start_time = self._define_number("start_time", start_time, nullable=True)
        self.end_time = self._define_number("end_time", end_time, nullable=True)
        self._kwargs = kwargs


@JsonMap({})
class TopUpEsimOkResponseProfile(BaseModel):
    """TopUpEsimOkResponseProfile

    :param iccid: ID of the eSIM, defaults to None
    :type iccid: str, optional
    """

    def __init__(self, iccid: str = SENTINEL, **kwargs):
        """TopUpEsimOkResponseProfile

        :param iccid: ID of the eSIM, defaults to None
        :type iccid: str, optional
        """
        self.iccid = self._define_str(
            "iccid", iccid, nullable=True, min_length=18, max_length=22
        )
        self._kwargs = kwargs


@JsonMap({})
class TopUpEsimOkResponse(BaseModel):
    """TopUpEsimOkResponse

    :param purchase: purchase, defaults to None
    :type purchase: TopUpEsimOkResponsePurchase, optional
    :param profile: profile, defaults to None
    :type profile: TopUpEsimOkResponseProfile, optional
    """

    def __init__(
        self,
        purchase: TopUpEsimOkResponsePurchase = SENTINEL,
        profile: TopUpEsimOkResponseProfile = SENTINEL,
        **kwargs
    ):
        """TopUpEsimOkResponse

        :param purchase: purchase, defaults to None
        :type purchase: TopUpEsimOkResponsePurchase, optional
        :param profile: profile, defaults to None
        :type profile: TopUpEsimOkResponseProfile, optional
        """
        self.purchase = self._define_object(purchase, TopUpEsimOkResponsePurchase)
        self.profile = self._define_object(profile, TopUpEsimOkResponseProfile)
        self._kwargs = kwargs
