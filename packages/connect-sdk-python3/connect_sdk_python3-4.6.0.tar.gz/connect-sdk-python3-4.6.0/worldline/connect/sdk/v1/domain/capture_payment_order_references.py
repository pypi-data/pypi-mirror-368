# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.domain.data_object import DataObject


class CapturePaymentOrderReferences(DataObject):

    __merchant_capture_reference: Optional[str] = None

    @property
    def merchant_capture_reference(self) -> Optional[str]:
        """
        | Your (unique) reference for the capture that you can use to reconcile our report files

        Type: str
        """
        return self.__merchant_capture_reference

    @merchant_capture_reference.setter
    def merchant_capture_reference(self, value: Optional[str]) -> None:
        self.__merchant_capture_reference = value

    def to_dictionary(self) -> dict:
        dictionary = super(CapturePaymentOrderReferences, self).to_dictionary()
        if self.merchant_capture_reference is not None:
            dictionary['merchantCaptureReference'] = self.merchant_capture_reference
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'CapturePaymentOrderReferences':
        super(CapturePaymentOrderReferences, self).from_dictionary(dictionary)
        if 'merchantCaptureReference' in dictionary:
            self.merchant_capture_reference = dictionary['merchantCaptureReference']
        return self
