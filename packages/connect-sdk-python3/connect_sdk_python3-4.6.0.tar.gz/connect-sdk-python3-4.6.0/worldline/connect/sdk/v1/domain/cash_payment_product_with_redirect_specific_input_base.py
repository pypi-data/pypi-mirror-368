# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.domain.data_object import DataObject


class CashPaymentProductWithRedirectSpecificInputBase(DataObject):

    __return_url: Optional[str] = None

    @property
    def return_url(self) -> Optional[str]:
        """
        Type: str
        """
        return self.__return_url

    @return_url.setter
    def return_url(self, value: Optional[str]) -> None:
        self.__return_url = value

    def to_dictionary(self) -> dict:
        dictionary = super(CashPaymentProductWithRedirectSpecificInputBase, self).to_dictionary()
        if self.return_url is not None:
            dictionary['returnUrl'] = self.return_url
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'CashPaymentProductWithRedirectSpecificInputBase':
        super(CashPaymentProductWithRedirectSpecificInputBase, self).from_dictionary(dictionary)
        if 'returnUrl' in dictionary:
            self.return_url = dictionary['returnUrl']
        return self
