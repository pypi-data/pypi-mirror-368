# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import List, Optional

from worldline.connect.sdk.communication.param_request import ParamRequest
from worldline.connect.sdk.communication.request_param import RequestParam


class FindPayoutsParams(ParamRequest):
    """
    Query parameters for Find payouts

    See also https://apireference.connect.worldline-solutions.com/s2sapi/v1/en_US/python/payouts/find.html
    """

    __merchant_reference: Optional[str] = None
    __merchant_order_id: Optional[int] = None
    __offset: Optional[int] = None
    __limit: Optional[int] = None

    @property
    def merchant_reference(self) -> Optional[str]:
        """
        | Your unique transaction reference to filter on.

        Type: str
        """
        return self.__merchant_reference

    @merchant_reference.setter
    def merchant_reference(self, value: Optional[str]) -> None:
        self.__merchant_reference = value

    @property
    def merchant_order_id(self) -> Optional[int]:
        """
        | Your order identifier to filter on.

        Type: int
        """
        return self.__merchant_order_id

    @merchant_order_id.setter
    def merchant_order_id(self, value: Optional[int]) -> None:
        self.__merchant_order_id = value

    @property
    def offset(self) -> Optional[int]:
        """
        | The zero-based index of the first payout in the result. If omitted, the offset will be 0.

        Type: int
        """
        return self.__offset

    @offset.setter
    def offset(self, value: Optional[int]) -> None:
        self.__offset = value

    @property
    def limit(self) -> Optional[int]:
        """
        | The maximum number of payouts to return, with a maximum of 100. If omitted, the limit will be 10.

        Type: int
        """
        return self.__limit

    @limit.setter
    def limit(self, value: Optional[int]) -> None:
        self.__limit = value

    def to_request_parameters(self) -> List[RequestParam]:
        """
        :return: list[RequestParam]
        """
        result = []
        if self.merchant_reference is not None:
            result.append(RequestParam("merchantReference", self.merchant_reference))
        if self.merchant_order_id is not None:
            result.append(RequestParam("merchantOrderId", str(self.merchant_order_id)))
        if self.offset is not None:
            result.append(RequestParam("offset", str(self.offset)))
        if self.limit is not None:
            result.append(RequestParam("limit", str(self.limit)))
        return result
