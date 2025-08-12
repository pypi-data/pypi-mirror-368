from .utils.json_map import JsonMap
from .utils.base_model import BaseModel
from .utils.sentinel import SENTINEL


@JsonMap({"id_": "id", "package_id": "packageId", "created_date": "createdDate"})
class CreatePurchaseV2OkResponsePurchase(BaseModel):
    """CreatePurchaseV2OkResponsePurchase

    :param id_: ID of the purchase, defaults to None
    :type id_: str, optional
    :param package_id: ID of the package, defaults to None
    :type package_id: str, optional
    :param created_date: Creation date of the purchase in the format 'yyyy-MM-ddThh:mm:ssZZ', defaults to None
    :type created_date: str, optional
    """

    def __init__(
        self,
        id_: str = SENTINEL,
        package_id: str = SENTINEL,
        created_date: str = SENTINEL,
        **kwargs
    ):
        """CreatePurchaseV2OkResponsePurchase

        :param id_: ID of the purchase, defaults to None
        :type id_: str, optional
        :param package_id: ID of the package, defaults to None
        :type package_id: str, optional
        :param created_date: Creation date of the purchase in the format 'yyyy-MM-ddThh:mm:ssZZ', defaults to None
        :type created_date: str, optional
        """
        self.id_ = self._define_str("id_", id_, nullable=True)
        self.package_id = self._define_str("package_id", package_id, nullable=True)
        self.created_date = self._define_str(
            "created_date", created_date, nullable=True
        )
        self._kwargs = kwargs


@JsonMap(
    {
        "activation_code": "activationCode",
        "manual_activation_code": "manualActivationCode",
    }
)
class CreatePurchaseV2OkResponseProfile(BaseModel):
    """CreatePurchaseV2OkResponseProfile

    :param iccid: ID of the eSIM, defaults to None
    :type iccid: str, optional
    :param activation_code: QR Code of the eSIM as base64, defaults to None
    :type activation_code: str, optional
    :param manual_activation_code: Manual Activation Code of the eSIM, defaults to None
    :type manual_activation_code: str, optional
    """

    def __init__(
        self,
        iccid: str = SENTINEL,
        activation_code: str = SENTINEL,
        manual_activation_code: str = SENTINEL,
        **kwargs
    ):
        """CreatePurchaseV2OkResponseProfile

        :param iccid: ID of the eSIM, defaults to None
        :type iccid: str, optional
        :param activation_code: QR Code of the eSIM as base64, defaults to None
        :type activation_code: str, optional
        :param manual_activation_code: Manual Activation Code of the eSIM, defaults to None
        :type manual_activation_code: str, optional
        """
        self.iccid = self._define_str(
            "iccid", iccid, nullable=True, min_length=18, max_length=22
        )
        self.activation_code = self._define_str(
            "activation_code",
            activation_code,
            nullable=True,
            min_length=1000,
            max_length=8000,
        )
        self.manual_activation_code = self._define_str(
            "manual_activation_code", manual_activation_code, nullable=True
        )
        self._kwargs = kwargs


@JsonMap({})
class CreatePurchaseV2OkResponse(BaseModel):
    """CreatePurchaseV2OkResponse

    :param purchase: purchase, defaults to None
    :type purchase: CreatePurchaseV2OkResponsePurchase, optional
    :param profile: profile, defaults to None
    :type profile: CreatePurchaseV2OkResponseProfile, optional
    """

    def __init__(
        self,
        purchase: CreatePurchaseV2OkResponsePurchase = SENTINEL,
        profile: CreatePurchaseV2OkResponseProfile = SENTINEL,
        **kwargs
    ):
        """CreatePurchaseV2OkResponse

        :param purchase: purchase, defaults to None
        :type purchase: CreatePurchaseV2OkResponsePurchase, optional
        :param profile: profile, defaults to None
        :type profile: CreatePurchaseV2OkResponseProfile, optional
        """
        self.purchase = self._define_object(
            purchase, CreatePurchaseV2OkResponsePurchase
        )
        self.profile = self._define_object(profile, CreatePurchaseV2OkResponseProfile)
        self._kwargs = kwargs
