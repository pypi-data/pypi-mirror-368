# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import List, Optional

from worldline.connect.sdk.communication.param_request import ParamRequest
from worldline.connect.sdk.communication.request_param import RequestParam


class DeleteTokenParams(ParamRequest):
    """
    Query parameters for Delete token

    See also https://apireference.connect.worldline-solutions.com/s2sapi/v1/en_US/python/tokens/delete.html
    """

    __mandate_cancel_date: Optional[str] = None

    @property
    def mandate_cancel_date(self) -> Optional[str]:
        """
        | Date of the mandate cancellation
        | Format: YYYYMMDD

        Type: str
        """
        return self.__mandate_cancel_date

    @mandate_cancel_date.setter
    def mandate_cancel_date(self, value: Optional[str]) -> None:
        self.__mandate_cancel_date = value

    def to_request_parameters(self) -> List[RequestParam]:
        """
        :return: list[RequestParam]
        """
        result = []
        if self.mandate_cancel_date is not None:
            result.append(RequestParam("mandateCancelDate", self.mandate_cancel_date))
        return result
