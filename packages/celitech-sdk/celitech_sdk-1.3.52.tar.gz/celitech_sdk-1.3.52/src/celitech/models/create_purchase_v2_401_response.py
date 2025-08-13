from .utils.json_map import JsonMap
from ..net.transport.api_error import ApiError
from .utils.sentinel import SENTINEL


@JsonMap({})
class CreatePurchaseV2_401Response(ApiError):
    """CreatePurchaseV2_401Response

    :param message: Message of the error, defaults to None
    :type message: str, optional
    """

    def __init__(self, message: str = SENTINEL, **kwargs):
        """CreatePurchaseV2_401Response

        :param message: Message of the error, defaults to None
        :type message: str, optional
        """
        self.message = self._define_str("message", message, nullable=True)
        self._kwargs = kwargs
