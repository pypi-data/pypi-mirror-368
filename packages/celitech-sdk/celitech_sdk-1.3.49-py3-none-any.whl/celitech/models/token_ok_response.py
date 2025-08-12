from .utils.json_map import JsonMap
from .utils.base_model import BaseModel
from .utils.sentinel import SENTINEL


@JsonMap({})
class TokenOkResponse(BaseModel):
    """TokenOkResponse

    :param token: The generated token, defaults to None
    :type token: str, optional
    """

    def __init__(self, token: str = SENTINEL, **kwargs):
        """TokenOkResponse

        :param token: The generated token, defaults to None
        :type token: str, optional
        """
        self.token = self._define_str("token", token, nullable=True)
        self._kwargs = kwargs
