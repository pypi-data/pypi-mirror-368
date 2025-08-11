# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.domain.data_object import DataObject
from worldline.connect.sdk.v1.domain.complete_payment_card_payment_method_specific_input import CompletePaymentCardPaymentMethodSpecificInput
from worldline.connect.sdk.v1.domain.merchant import Merchant
from worldline.connect.sdk.v1.domain.order import Order


class CompletePaymentRequest(DataObject):

    __card_payment_method_specific_input: Optional[CompletePaymentCardPaymentMethodSpecificInput] = None
    __merchant: Optional[Merchant] = None
    __order: Optional[Order] = None

    @property
    def card_payment_method_specific_input(self) -> Optional[CompletePaymentCardPaymentMethodSpecificInput]:
        """
        | Object containing the specific input details for card payments

        Type: :class:`worldline.connect.sdk.v1.domain.complete_payment_card_payment_method_specific_input.CompletePaymentCardPaymentMethodSpecificInput`
        """
        return self.__card_payment_method_specific_input

    @card_payment_method_specific_input.setter
    def card_payment_method_specific_input(self, value: Optional[CompletePaymentCardPaymentMethodSpecificInput]) -> None:
        self.__card_payment_method_specific_input = value

    @property
    def merchant(self) -> Optional[Merchant]:
        """
        | Object containing information on you, the merchant

        Type: :class:`worldline.connect.sdk.v1.domain.merchant.Merchant`
        """
        return self.__merchant

    @merchant.setter
    def merchant(self, value: Optional[Merchant]) -> None:
        self.__merchant = value

    @property
    def order(self) -> Optional[Order]:
        """
        | Order object containing order related data

        Type: :class:`worldline.connect.sdk.v1.domain.order.Order`
        """
        return self.__order

    @order.setter
    def order(self, value: Optional[Order]) -> None:
        self.__order = value

    def to_dictionary(self) -> dict:
        dictionary = super(CompletePaymentRequest, self).to_dictionary()
        if self.card_payment_method_specific_input is not None:
            dictionary['cardPaymentMethodSpecificInput'] = self.card_payment_method_specific_input.to_dictionary()
        if self.merchant is not None:
            dictionary['merchant'] = self.merchant.to_dictionary()
        if self.order is not None:
            dictionary['order'] = self.order.to_dictionary()
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'CompletePaymentRequest':
        super(CompletePaymentRequest, self).from_dictionary(dictionary)
        if 'cardPaymentMethodSpecificInput' in dictionary:
            if not isinstance(dictionary['cardPaymentMethodSpecificInput'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['cardPaymentMethodSpecificInput']))
            value = CompletePaymentCardPaymentMethodSpecificInput()
            self.card_payment_method_specific_input = value.from_dictionary(dictionary['cardPaymentMethodSpecificInput'])
        if 'merchant' in dictionary:
            if not isinstance(dictionary['merchant'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['merchant']))
            value = Merchant()
            self.merchant = value.from_dictionary(dictionary['merchant'])
        if 'order' in dictionary:
            if not isinstance(dictionary['order'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['order']))
            value = Order()
            self.order = value.from_dictionary(dictionary['order'])
        return self
