from .utils.json_map import JsonMap
from .utils.base_model import BaseModel
from .utils.sentinel import SENTINEL


@JsonMap({"data_usage_remaining_in_bytes": "dataUsageRemainingInBytes"})
class GetPurchaseConsumptionOkResponse(BaseModel):
    """GetPurchaseConsumptionOkResponse

    :param data_usage_remaining_in_bytes: Remaining balance of the package in bytes, defaults to None
    :type data_usage_remaining_in_bytes: float, optional
    :param status: Status of the connectivity, possible values are 'ACTIVE' or 'NOT_ACTIVE', defaults to None
    :type status: str, optional
    """

    def __init__(
        self,
        data_usage_remaining_in_bytes: float = SENTINEL,
        status: str = SENTINEL,
        **kwargs
    ):
        """GetPurchaseConsumptionOkResponse

        :param data_usage_remaining_in_bytes: Remaining balance of the package in bytes, defaults to None
        :type data_usage_remaining_in_bytes: float, optional
        :param status: Status of the connectivity, possible values are 'ACTIVE' or 'NOT_ACTIVE', defaults to None
        :type status: str, optional
        """
        self.data_usage_remaining_in_bytes = self._define_number(
            "data_usage_remaining_in_bytes",
            data_usage_remaining_in_bytes,
            nullable=True,
        )
        self.status = self._define_str("status", status, nullable=True)
        self._kwargs = kwargs
