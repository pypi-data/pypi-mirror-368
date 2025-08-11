# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.domain.data_object import DataObject


class ApproveRefundRequest(DataObject):

    __amount: Optional[int] = None

    @property
    def amount(self) -> Optional[int]:
        """
        | Refund amount to be approved

        Type: int
        """
        return self.__amount

    @amount.setter
    def amount(self, value: Optional[int]) -> None:
        self.__amount = value

    def to_dictionary(self) -> dict:
        dictionary = super(ApproveRefundRequest, self).to_dictionary()
        if self.amount is not None:
            dictionary['amount'] = self.amount
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'ApproveRefundRequest':
        super(ApproveRefundRequest, self).from_dictionary(dictionary)
        if 'amount' in dictionary:
            self.amount = dictionary['amount']
        return self
