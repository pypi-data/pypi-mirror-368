# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.domain.data_object import DataObject


class MobilePaymentProduct302SpecificInputHostedCheckout(DataObject):

    __business_name: Optional[str] = None

    @property
    def business_name(self) -> Optional[str]:
        """
        | Used as an input for the Apple Pay payment button. Your default business name is configured in the Configuration Center. In case you want to use another business name than the one configured in the Configuration Center, provide your company name in a human readable form.

        Type: str
        """
        return self.__business_name

    @business_name.setter
    def business_name(self, value: Optional[str]) -> None:
        self.__business_name = value

    def to_dictionary(self) -> dict:
        dictionary = super(MobilePaymentProduct302SpecificInputHostedCheckout, self).to_dictionary()
        if self.business_name is not None:
            dictionary['businessName'] = self.business_name
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'MobilePaymentProduct302SpecificInputHostedCheckout':
        super(MobilePaymentProduct302SpecificInputHostedCheckout, self).from_dictionary(dictionary)
        if 'businessName' in dictionary:
            self.business_name = dictionary['businessName']
        return self
