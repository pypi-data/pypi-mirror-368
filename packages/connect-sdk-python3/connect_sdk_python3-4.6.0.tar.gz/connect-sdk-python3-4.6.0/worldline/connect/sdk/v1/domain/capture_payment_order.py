# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.domain.data_object import DataObject
from worldline.connect.sdk.v1.domain.capture_payment_order_additional_input import CapturePaymentOrderAdditionalInput
from worldline.connect.sdk.v1.domain.capture_payment_order_references import CapturePaymentOrderReferences


class CapturePaymentOrder(DataObject):

    __additional_input: Optional[CapturePaymentOrderAdditionalInput] = None
    __references: Optional[CapturePaymentOrderReferences] = None

    @property
    def additional_input(self) -> Optional[CapturePaymentOrderAdditionalInput]:
        """
        | Object containing additional input on the order

        Type: :class:`worldline.connect.sdk.v1.domain.capture_payment_order_additional_input.CapturePaymentOrderAdditionalInput`
        """
        return self.__additional_input

    @additional_input.setter
    def additional_input(self, value: Optional[CapturePaymentOrderAdditionalInput]) -> None:
        self.__additional_input = value

    @property
    def references(self) -> Optional[CapturePaymentOrderReferences]:
        """
        | Object that holds all reference properties that are linked to this transaction

        Type: :class:`worldline.connect.sdk.v1.domain.capture_payment_order_references.CapturePaymentOrderReferences`
        """
        return self.__references

    @references.setter
    def references(self, value: Optional[CapturePaymentOrderReferences]) -> None:
        self.__references = value

    def to_dictionary(self) -> dict:
        dictionary = super(CapturePaymentOrder, self).to_dictionary()
        if self.additional_input is not None:
            dictionary['additionalInput'] = self.additional_input.to_dictionary()
        if self.references is not None:
            dictionary['references'] = self.references.to_dictionary()
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'CapturePaymentOrder':
        super(CapturePaymentOrder, self).from_dictionary(dictionary)
        if 'additionalInput' in dictionary:
            if not isinstance(dictionary['additionalInput'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['additionalInput']))
            value = CapturePaymentOrderAdditionalInput()
            self.additional_input = value.from_dictionary(dictionary['additionalInput'])
        if 'references' in dictionary:
            if not isinstance(dictionary['references'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['references']))
            value = CapturePaymentOrderReferences()
            self.references = value.from_dictionary(dictionary['references'])
        return self
