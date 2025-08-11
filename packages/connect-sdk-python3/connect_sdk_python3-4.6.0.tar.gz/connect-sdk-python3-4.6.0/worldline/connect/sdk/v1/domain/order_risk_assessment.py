# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.domain.data_object import DataObject
from worldline.connect.sdk.v1.domain.additional_order_input_airline_data import AdditionalOrderInputAirlineData
from worldline.connect.sdk.v1.domain.amount_of_money import AmountOfMoney
from worldline.connect.sdk.v1.domain.customer_risk_assessment import CustomerRiskAssessment
from worldline.connect.sdk.v1.domain.shipping_risk_assessment import ShippingRiskAssessment


class OrderRiskAssessment(DataObject):

    __additional_input: Optional[AdditionalOrderInputAirlineData] = None
    __amount_of_money: Optional[AmountOfMoney] = None
    __customer: Optional[CustomerRiskAssessment] = None
    __shipping: Optional[ShippingRiskAssessment] = None

    @property
    def additional_input(self) -> Optional[AdditionalOrderInputAirlineData]:
        """
        | Object containing additional input on the order

        Type: :class:`worldline.connect.sdk.v1.domain.additional_order_input_airline_data.AdditionalOrderInputAirlineData`
        """
        return self.__additional_input

    @additional_input.setter
    def additional_input(self, value: Optional[AdditionalOrderInputAirlineData]) -> None:
        self.__additional_input = value

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
    def customer(self) -> Optional[CustomerRiskAssessment]:
        """
        | Object containing the details of the customer

        Type: :class:`worldline.connect.sdk.v1.domain.customer_risk_assessment.CustomerRiskAssessment`
        """
        return self.__customer

    @customer.setter
    def customer(self, value: Optional[CustomerRiskAssessment]) -> None:
        self.__customer = value

    @property
    def shipping(self) -> Optional[ShippingRiskAssessment]:
        """
        | Object containing information regarding shipping / delivery

        Type: :class:`worldline.connect.sdk.v1.domain.shipping_risk_assessment.ShippingRiskAssessment`
        """
        return self.__shipping

    @shipping.setter
    def shipping(self, value: Optional[ShippingRiskAssessment]) -> None:
        self.__shipping = value

    def to_dictionary(self) -> dict:
        dictionary = super(OrderRiskAssessment, self).to_dictionary()
        if self.additional_input is not None:
            dictionary['additionalInput'] = self.additional_input.to_dictionary()
        if self.amount_of_money is not None:
            dictionary['amountOfMoney'] = self.amount_of_money.to_dictionary()
        if self.customer is not None:
            dictionary['customer'] = self.customer.to_dictionary()
        if self.shipping is not None:
            dictionary['shipping'] = self.shipping.to_dictionary()
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'OrderRiskAssessment':
        super(OrderRiskAssessment, self).from_dictionary(dictionary)
        if 'additionalInput' in dictionary:
            if not isinstance(dictionary['additionalInput'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['additionalInput']))
            value = AdditionalOrderInputAirlineData()
            self.additional_input = value.from_dictionary(dictionary['additionalInput'])
        if 'amountOfMoney' in dictionary:
            if not isinstance(dictionary['amountOfMoney'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['amountOfMoney']))
            value = AmountOfMoney()
            self.amount_of_money = value.from_dictionary(dictionary['amountOfMoney'])
        if 'customer' in dictionary:
            if not isinstance(dictionary['customer'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['customer']))
            value = CustomerRiskAssessment()
            self.customer = value.from_dictionary(dictionary['customer'])
        if 'shipping' in dictionary:
            if not isinstance(dictionary['shipping'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['shipping']))
            value = ShippingRiskAssessment()
            self.shipping = value.from_dictionary(dictionary['shipping'])
        return self
