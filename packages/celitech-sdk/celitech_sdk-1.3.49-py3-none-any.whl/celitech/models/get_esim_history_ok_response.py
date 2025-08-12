from typing import List
from .utils.json_map import JsonMap
from .utils.base_model import BaseModel
from .utils.sentinel import SENTINEL


@JsonMap({"status_date": "statusDate", "date_": "date"})
class History(BaseModel):
    """History

    :param status: The status of the eSIM at a given time, possible values are 'RELEASED', 'DOWNLOADED', 'INSTALLED', 'ENABLED', 'DELETED', or 'ERROR', defaults to None
    :type status: str, optional
    :param status_date: The date when the eSIM status changed in the format 'yyyy-MM-ddThh:mm:ssZZ', defaults to None
    :type status_date: str, optional
    :param date_: Epoch value representing the date when the eSIM status changed, defaults to None
    :type date_: float, optional
    """

    def __init__(
        self,
        status: str = SENTINEL,
        status_date: str = SENTINEL,
        date_: float = SENTINEL,
        **kwargs
    ):
        """History

        :param status: The status of the eSIM at a given time, possible values are 'RELEASED', 'DOWNLOADED', 'INSTALLED', 'ENABLED', 'DELETED', or 'ERROR', defaults to None
        :type status: str, optional
        :param status_date: The date when the eSIM status changed in the format 'yyyy-MM-ddThh:mm:ssZZ', defaults to None
        :type status_date: str, optional
        :param date_: Epoch value representing the date when the eSIM status changed, defaults to None
        :type date_: float, optional
        """
        self.status = self._define_str("status", status, nullable=True)
        self.status_date = self._define_str("status_date", status_date, nullable=True)
        self.date_ = self._define_number("date_", date_, nullable=True)
        self._kwargs = kwargs


@JsonMap({})
class GetEsimHistoryOkResponseEsim(BaseModel):
    """GetEsimHistoryOkResponseEsim

    :param iccid: ID of the eSIM, defaults to None
    :type iccid: str, optional
    :param history: history, defaults to None
    :type history: List[History], optional
    """

    def __init__(
        self, iccid: str = SENTINEL, history: List[History] = SENTINEL, **kwargs
    ):
        """GetEsimHistoryOkResponseEsim

        :param iccid: ID of the eSIM, defaults to None
        :type iccid: str, optional
        :param history: history, defaults to None
        :type history: List[History], optional
        """
        self.iccid = self._define_str(
            "iccid", iccid, nullable=True, min_length=18, max_length=22
        )
        self.history = self._define_list(history, History)
        self._kwargs = kwargs


@JsonMap({})
class GetEsimHistoryOkResponse(BaseModel):
    """GetEsimHistoryOkResponse

    :param esim: esim, defaults to None
    :type esim: GetEsimHistoryOkResponseEsim, optional
    """

    def __init__(self, esim: GetEsimHistoryOkResponseEsim = SENTINEL, **kwargs):
        """GetEsimHistoryOkResponse

        :param esim: esim, defaults to None
        :type esim: GetEsimHistoryOkResponseEsim, optional
        """
        self.esim = self._define_object(esim, GetEsimHistoryOkResponseEsim)
        self._kwargs = kwargs
