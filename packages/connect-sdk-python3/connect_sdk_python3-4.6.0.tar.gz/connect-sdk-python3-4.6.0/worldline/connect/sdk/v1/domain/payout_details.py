# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.domain.data_object import DataObject
from worldline.connect.sdk.v1.domain.amount_of_money import AmountOfMoney
from worldline.connect.sdk.v1.domain.payout_customer import PayoutCustomer
from worldline.connect.sdk.v1.domain.payout_references import PayoutReferences


class PayoutDetails(DataObject):

    __amount_of_money: Optional[AmountOfMoney] = None
    __customer: Optional[PayoutCustomer] = None
    __references: Optional[PayoutReferences] = None

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
    def customer(self) -> Optional[PayoutCustomer]:
        """
        | Object containing the details of the customer.

        Type: :class:`worldline.connect.sdk.v1.domain.payout_customer.PayoutCustomer`
        """
        return self.__customer

    @customer.setter
    def customer(self, value: Optional[PayoutCustomer]) -> None:
        self.__customer = value

    @property
    def references(self) -> Optional[PayoutReferences]:
        """
        | Object that holds all reference properties that are linked to this transaction

        Type: :class:`worldline.connect.sdk.v1.domain.payout_references.PayoutReferences`
        """
        return self.__references

    @references.setter
    def references(self, value: Optional[PayoutReferences]) -> None:
        self.__references = value

    def to_dictionary(self) -> dict:
        dictionary = super(PayoutDetails, self).to_dictionary()
        if self.amount_of_money is not None:
            dictionary['amountOfMoney'] = self.amount_of_money.to_dictionary()
        if self.customer is not None:
            dictionary['customer'] = self.customer.to_dictionary()
        if self.references is not None:
            dictionary['references'] = self.references.to_dictionary()
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'PayoutDetails':
        super(PayoutDetails, self).from_dictionary(dictionary)
        if 'amountOfMoney' in dictionary:
            if not isinstance(dictionary['amountOfMoney'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['amountOfMoney']))
            value = AmountOfMoney()
            self.amount_of_money = value.from_dictionary(dictionary['amountOfMoney'])
        if 'customer' in dictionary:
            if not isinstance(dictionary['customer'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['customer']))
            value = PayoutCustomer()
            self.customer = value.from_dictionary(dictionary['customer'])
        if 'references' in dictionary:
            if not isinstance(dictionary['references'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['references']))
            value = PayoutReferences()
            self.references = value.from_dictionary(dictionary['references'])
        return self
