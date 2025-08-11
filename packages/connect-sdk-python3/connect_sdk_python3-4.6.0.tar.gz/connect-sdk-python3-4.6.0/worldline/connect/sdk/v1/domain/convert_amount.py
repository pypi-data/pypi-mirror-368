# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.domain.data_object import DataObject


class ConvertAmount(DataObject):

    __converted_amount: Optional[int] = None

    @property
    def converted_amount(self) -> Optional[int]:
        """
        | Converted amount in cents and having 2 decimal

        Type: int
        """
        return self.__converted_amount

    @converted_amount.setter
    def converted_amount(self, value: Optional[int]) -> None:
        self.__converted_amount = value

    def to_dictionary(self) -> dict:
        dictionary = super(ConvertAmount, self).to_dictionary()
        if self.converted_amount is not None:
            dictionary['convertedAmount'] = self.converted_amount
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'ConvertAmount':
        super(ConvertAmount, self).from_dictionary(dictionary)
        if 'convertedAmount' in dictionary:
            self.converted_amount = dictionary['convertedAmount']
        return self
