from typing import Union
from .utils.validator import Validator
from .utils.base_service import BaseService
from ..net.transport.serializer import Serializer
from ..net.environment.environment import Environment
from ..models.utils.cast_models import cast_models
from ..models import (
    GetEsim400Response,
    GetEsim401Response,
    GetEsimDevice400Response,
    GetEsimDevice401Response,
    GetEsimDeviceOkResponse,
    GetEsimHistory400Response,
    GetEsimHistory401Response,
    GetEsimHistoryOkResponse,
    GetEsimMac400Response,
    GetEsimMac401Response,
    GetEsimMacOkResponse,
    GetEsimOkResponse,
)


class ESimService(BaseService):

    @cast_models
    def get_esim(self, iccid: str) -> GetEsimOkResponse:
        """Get eSIM Status

        :param iccid: ID of the eSIM
        :type iccid: str
        ...
        :raises RequestError: Raised when a request fails, with optional HTTP status code and details.
        ...
        :return: The parsed response data.
        :rtype: GetEsimOkResponse
        """

        Validator(str).min_length(18).max_length(22).validate(iccid)

        serialized_request = (
            Serializer(
                f"{self.base_url or Environment.DEFAULT.url}/esim",
            )
            .add_query("iccid", iccid)
            .add_error(400, GetEsim400Response)
            .add_error(401, GetEsim401Response)
            .serialize()
            .set_method("GET")
            .set_scopes(set())
        )

        response, status, _ = self.send_request(serialized_request)
        return GetEsimOkResponse._unmap(response)

    @cast_models
    def get_esim_device(self, iccid: str) -> GetEsimDeviceOkResponse:
        """Get eSIM Device

        :param iccid: ID of the eSIM
        :type iccid: str
        ...
        :raises RequestError: Raised when a request fails, with optional HTTP status code and details.
        ...
        :return: The parsed response data.
        :rtype: GetEsimDeviceOkResponse
        """

        Validator(str).min_length(18).max_length(22).validate(iccid)

        serialized_request = (
            Serializer(
                f"{self.base_url or Environment.DEFAULT.url}/esim/{{iccid}}/device",
            )
            .add_path("iccid", iccid)
            .add_error(400, GetEsimDevice400Response)
            .add_error(401, GetEsimDevice401Response)
            .serialize()
            .set_method("GET")
            .set_scopes(set())
        )

        response, status, _ = self.send_request(serialized_request)
        return GetEsimDeviceOkResponse._unmap(response)

    @cast_models
    def get_esim_history(self, iccid: str) -> GetEsimHistoryOkResponse:
        """Get eSIM History

        :param iccid: ID of the eSIM
        :type iccid: str
        ...
        :raises RequestError: Raised when a request fails, with optional HTTP status code and details.
        ...
        :return: The parsed response data.
        :rtype: GetEsimHistoryOkResponse
        """

        Validator(str).min_length(18).max_length(22).validate(iccid)

        serialized_request = (
            Serializer(
                f"{self.base_url or Environment.DEFAULT.url}/esim/{{iccid}}/history",
            )
            .add_path("iccid", iccid)
            .add_error(400, GetEsimHistory400Response)
            .add_error(401, GetEsimHistory401Response)
            .serialize()
            .set_method("GET")
            .set_scopes(set())
        )

        response, status, _ = self.send_request(serialized_request)
        return GetEsimHistoryOkResponse._unmap(response)

    @cast_models
    def get_esim_mac(self, iccid: str) -> GetEsimMacOkResponse:
        """Get eSIM MAC

        :param iccid: ID of the eSIM
        :type iccid: str
        ...
        :raises RequestError: Raised when a request fails, with optional HTTP status code and details.
        ...
        :return: The parsed response data.
        :rtype: GetEsimMacOkResponse
        """

        Validator(str).min_length(18).max_length(22).validate(iccid)

        serialized_request = (
            Serializer(
                f"{self.base_url or Environment.DEFAULT.url}/esim/{{iccid}}/mac",
            )
            .add_path("iccid", iccid)
            .add_error(400, GetEsimMac400Response)
            .add_error(401, GetEsimMac401Response)
            .serialize()
            .set_method("GET")
            .set_scopes(set())
        )

        response, status, _ = self.send_request(serialized_request)
        return GetEsimMacOkResponse._unmap(response)
