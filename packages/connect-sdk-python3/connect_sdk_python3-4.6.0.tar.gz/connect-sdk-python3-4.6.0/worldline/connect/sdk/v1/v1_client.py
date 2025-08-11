#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Mapping, Optional

from worldline.connect.sdk.api_resource import ApiResource
from worldline.connect.sdk.v1.merchant.merchant_client import MerchantClient


class V1Client(ApiResource):
    """
    V1 client.

    Thread-safe.
    """
    def __init__(self, parent: ApiResource, path_context: Optional[Mapping[str, str]]):
        """
        :param parent:       :class:`worldline.connect.sdk.api_resource.ApiResource`
        :param path_context: Mapping[str, str]
        """
        super(V1Client, self).__init__(parent=parent, path_context=path_context)

    def merchant(self, merchant_id: str) -> MerchantClient:
        """
        Resource /{merchantId}

        :param merchant_id:  str
        :return: :class:`worldline.connect.sdk.v1.merchant.merchant_client.MerchantClient`
        """
        sub_context = {
            "merchantId": merchant_id,
        }
        return MerchantClient(self, sub_context)
