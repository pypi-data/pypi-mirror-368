# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import List, Optional

from worldline.connect.sdk.communication.param_request import ParamRequest
from worldline.connect.sdk.communication.request_param import RequestParam


class ConvertAmountParams(ParamRequest):
    """
    Query parameters for Convert amount

    See also https://apireference.connect.worldline-solutions.com/s2sapi/v1/en_US/python/services/convertAmount.html
    """

    __source: Optional[str] = None
    __target: Optional[str] = None
    __amount: Optional[int] = None

    @property
    def source(self) -> Optional[str]:
        """
        | Three-letter ISO currency code representing the source currency

        Type: str
        """
        return self.__source

    @source.setter
    def source(self, value: Optional[str]) -> None:
        self.__source = value

    @property
    def target(self) -> Optional[str]:
        """
        | Three-letter ISO currency code representing the target currency

        Type: str
        """
        return self.__target

    @target.setter
    def target(self, value: Optional[str]) -> None:
        self.__target = value

    @property
    def amount(self) -> Optional[int]:
        """
        | Amount to be converted in cents and always having 2 decimals

        Type: int
        """
        return self.__amount

    @amount.setter
    def amount(self, value: Optional[int]) -> None:
        self.__amount = value

    def to_request_parameters(self) -> List[RequestParam]:
        """
        :return: list[RequestParam]
        """
        result = []
        if self.source is not None:
            result.append(RequestParam("source", self.source))
        if self.target is not None:
            result.append(RequestParam("target", self.target))
        if self.amount is not None:
            result.append(RequestParam("amount", str(self.amount)))
        return result
