# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.domain.data_object import DataObject
from worldline.connect.sdk.v1.domain.approve_payment_card_payment_method_specific_output import ApprovePaymentCardPaymentMethodSpecificOutput
from worldline.connect.sdk.v1.domain.approve_payment_mobile_payment_method_specific_output import ApprovePaymentMobilePaymentMethodSpecificOutput
from worldline.connect.sdk.v1.domain.payment import Payment


class PaymentApprovalResponse(DataObject):

    __card_payment_method_specific_output: Optional[ApprovePaymentCardPaymentMethodSpecificOutput] = None
    __mobile_payment_method_specific_output: Optional[ApprovePaymentMobilePaymentMethodSpecificOutput] = None
    __payment: Optional[Payment] = None
    __payment_method_specific_output: Optional[ApprovePaymentCardPaymentMethodSpecificOutput] = None

    @property
    def card_payment_method_specific_output(self) -> Optional[ApprovePaymentCardPaymentMethodSpecificOutput]:
        """
        | Object containing additional card payment method specific details

        Type: :class:`worldline.connect.sdk.v1.domain.approve_payment_card_payment_method_specific_output.ApprovePaymentCardPaymentMethodSpecificOutput`
        """
        return self.__card_payment_method_specific_output

    @card_payment_method_specific_output.setter
    def card_payment_method_specific_output(self, value: Optional[ApprovePaymentCardPaymentMethodSpecificOutput]) -> None:
        self.__card_payment_method_specific_output = value

    @property
    def mobile_payment_method_specific_output(self) -> Optional[ApprovePaymentMobilePaymentMethodSpecificOutput]:
        """
        | Object containing additional mobile payment method specific details

        Type: :class:`worldline.connect.sdk.v1.domain.approve_payment_mobile_payment_method_specific_output.ApprovePaymentMobilePaymentMethodSpecificOutput`
        """
        return self.__mobile_payment_method_specific_output

    @mobile_payment_method_specific_output.setter
    def mobile_payment_method_specific_output(self, value: Optional[ApprovePaymentMobilePaymentMethodSpecificOutput]) -> None:
        self.__mobile_payment_method_specific_output = value

    @property
    def payment(self) -> Optional[Payment]:
        """
        | Object that holds the payment data

        Type: :class:`worldline.connect.sdk.v1.domain.payment.Payment`
        """
        return self.__payment

    @payment.setter
    def payment(self, value: Optional[Payment]) -> None:
        self.__payment = value

    @property
    def payment_method_specific_output(self) -> Optional[ApprovePaymentCardPaymentMethodSpecificOutput]:
        """
        | Object containing additional payment method specific details
        | Deprecated: this property does not support different outputs for payment methods other than cards. Please use cardPaymentMethodSpecificOutput instead.

        Type: :class:`worldline.connect.sdk.v1.domain.approve_payment_card_payment_method_specific_output.ApprovePaymentCardPaymentMethodSpecificOutput`

        Deprecated; Use cardPaymentMethodSpecificOutput instead
        """
        return self.__payment_method_specific_output

    @payment_method_specific_output.setter
    def payment_method_specific_output(self, value: Optional[ApprovePaymentCardPaymentMethodSpecificOutput]) -> None:
        self.__payment_method_specific_output = value

    def to_dictionary(self) -> dict:
        dictionary = super(PaymentApprovalResponse, self).to_dictionary()
        if self.card_payment_method_specific_output is not None:
            dictionary['cardPaymentMethodSpecificOutput'] = self.card_payment_method_specific_output.to_dictionary()
        if self.mobile_payment_method_specific_output is not None:
            dictionary['mobilePaymentMethodSpecificOutput'] = self.mobile_payment_method_specific_output.to_dictionary()
        if self.payment is not None:
            dictionary['payment'] = self.payment.to_dictionary()
        if self.payment_method_specific_output is not None:
            dictionary['paymentMethodSpecificOutput'] = self.payment_method_specific_output.to_dictionary()
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'PaymentApprovalResponse':
        super(PaymentApprovalResponse, self).from_dictionary(dictionary)
        if 'cardPaymentMethodSpecificOutput' in dictionary:
            if not isinstance(dictionary['cardPaymentMethodSpecificOutput'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['cardPaymentMethodSpecificOutput']))
            value = ApprovePaymentCardPaymentMethodSpecificOutput()
            self.card_payment_method_specific_output = value.from_dictionary(dictionary['cardPaymentMethodSpecificOutput'])
        if 'mobilePaymentMethodSpecificOutput' in dictionary:
            if not isinstance(dictionary['mobilePaymentMethodSpecificOutput'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['mobilePaymentMethodSpecificOutput']))
            value = ApprovePaymentMobilePaymentMethodSpecificOutput()
            self.mobile_payment_method_specific_output = value.from_dictionary(dictionary['mobilePaymentMethodSpecificOutput'])
        if 'payment' in dictionary:
            if not isinstance(dictionary['payment'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['payment']))
            value = Payment()
            self.payment = value.from_dictionary(dictionary['payment'])
        if 'paymentMethodSpecificOutput' in dictionary:
            if not isinstance(dictionary['paymentMethodSpecificOutput'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['paymentMethodSpecificOutput']))
            value = ApprovePaymentCardPaymentMethodSpecificOutput()
            self.payment_method_specific_output = value.from_dictionary(dictionary['paymentMethodSpecificOutput'])
        return self
