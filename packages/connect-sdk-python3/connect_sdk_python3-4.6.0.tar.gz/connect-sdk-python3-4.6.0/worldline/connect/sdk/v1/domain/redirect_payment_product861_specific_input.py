# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.domain.data_object import DataObject


class RedirectPaymentProduct861SpecificInput(DataObject):

    __mobile_device: Optional[bool] = None

    @property
    def mobile_device(self) -> Optional[bool]:
        """
        | This indicates that a customer is on a mobile device and it is used to distinguish whether a customer should be redirected to AliPay Desktop or Mobile. Alternatively, if you cannot determine whether a customer is on a mobile device or not, a customer can be redirected to AliPay Mobile if the property CreatePaymentRequest.order.customer.device.userAgent is supplied.

        Type: bool
        """
        return self.__mobile_device

    @mobile_device.setter
    def mobile_device(self, value: Optional[bool]) -> None:
        self.__mobile_device = value

    def to_dictionary(self) -> dict:
        dictionary = super(RedirectPaymentProduct861SpecificInput, self).to_dictionary()
        if self.mobile_device is not None:
            dictionary['mobileDevice'] = self.mobile_device
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'RedirectPaymentProduct861SpecificInput':
        super(RedirectPaymentProduct861SpecificInput, self).from_dictionary(dictionary)
        if 'mobileDevice' in dictionary:
            self.mobile_device = dictionary['mobileDevice']
        return self
