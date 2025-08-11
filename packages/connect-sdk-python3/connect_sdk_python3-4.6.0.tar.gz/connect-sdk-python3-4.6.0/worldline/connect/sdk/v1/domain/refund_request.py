# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.domain.data_object import DataObject
from worldline.connect.sdk.v1.domain.amount_of_money import AmountOfMoney
from worldline.connect.sdk.v1.domain.bank_refund_method_specific_input import BankRefundMethodSpecificInput
from worldline.connect.sdk.v1.domain.refund_customer import RefundCustomer
from worldline.connect.sdk.v1.domain.refund_references import RefundReferences


class RefundRequest(DataObject):

    __amount_of_money: Optional[AmountOfMoney] = None
    __bank_refund_method_specific_input: Optional[BankRefundMethodSpecificInput] = None
    __customer: Optional[RefundCustomer] = None
    __refund_date: Optional[str] = None
    __refund_references: Optional[RefundReferences] = None

    @property
    def amount_of_money(self) -> Optional[AmountOfMoney]:
        """
        | Object containing amount and ISO currency code attributes

        Type: :class:`worldline.connect.sdk.v1.domain.amount_of_money.AmountOfMoney`
        """
        return self.__amount_of_money

    @amount_of_money.setter
    def amount_of_money(self, value: Optional[AmountOfMoney]) -> None:
        self.__amount_of_money = value

    @property
    def bank_refund_method_specific_input(self) -> Optional[BankRefundMethodSpecificInput]:
        """
        | Object containing the specific input details for a bank refund

        Type: :class:`worldline.connect.sdk.v1.domain.bank_refund_method_specific_input.BankRefundMethodSpecificInput`
        """
        return self.__bank_refund_method_specific_input

    @bank_refund_method_specific_input.setter
    def bank_refund_method_specific_input(self, value: Optional[BankRefundMethodSpecificInput]) -> None:
        self.__bank_refund_method_specific_input = value

    @property
    def customer(self) -> Optional[RefundCustomer]:
        """
        | Object containing the details of the customer

        Type: :class:`worldline.connect.sdk.v1.domain.refund_customer.RefundCustomer`
        """
        return self.__customer

    @customer.setter
    def customer(self, value: Optional[RefundCustomer]) -> None:
        self.__customer = value

    @property
    def refund_date(self) -> Optional[str]:
        """
        | Refund date
        | Format: YYYYMMDD

        Type: str
        """
        return self.__refund_date

    @refund_date.setter
    def refund_date(self, value: Optional[str]) -> None:
        self.__refund_date = value

    @property
    def refund_references(self) -> Optional[RefundReferences]:
        """
        | Object that holds all reference properties that are linked to this refund

        Type: :class:`worldline.connect.sdk.v1.domain.refund_references.RefundReferences`
        """
        return self.__refund_references

    @refund_references.setter
    def refund_references(self, value: Optional[RefundReferences]) -> None:
        self.__refund_references = value

    def to_dictionary(self) -> dict:
        dictionary = super(RefundRequest, self).to_dictionary()
        if self.amount_of_money is not None:
            dictionary['amountOfMoney'] = self.amount_of_money.to_dictionary()
        if self.bank_refund_method_specific_input is not None:
            dictionary['bankRefundMethodSpecificInput'] = self.bank_refund_method_specific_input.to_dictionary()
        if self.customer is not None:
            dictionary['customer'] = self.customer.to_dictionary()
        if self.refund_date is not None:
            dictionary['refundDate'] = self.refund_date
        if self.refund_references is not None:
            dictionary['refundReferences'] = self.refund_references.to_dictionary()
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'RefundRequest':
        super(RefundRequest, self).from_dictionary(dictionary)
        if 'amountOfMoney' in dictionary:
            if not isinstance(dictionary['amountOfMoney'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['amountOfMoney']))
            value = AmountOfMoney()
            self.amount_of_money = value.from_dictionary(dictionary['amountOfMoney'])
        if 'bankRefundMethodSpecificInput' in dictionary:
            if not isinstance(dictionary['bankRefundMethodSpecificInput'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['bankRefundMethodSpecificInput']))
            value = BankRefundMethodSpecificInput()
            self.bank_refund_method_specific_input = value.from_dictionary(dictionary['bankRefundMethodSpecificInput'])
        if 'customer' in dictionary:
            if not isinstance(dictionary['customer'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['customer']))
            value = RefundCustomer()
            self.customer = value.from_dictionary(dictionary['customer'])
        if 'refundDate' in dictionary:
            self.refund_date = dictionary['refundDate']
        if 'refundReferences' in dictionary:
            if not isinstance(dictionary['refundReferences'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['refundReferences']))
            value = RefundReferences()
            self.refund_references = value.from_dictionary(dictionary['refundReferences'])
        return self
