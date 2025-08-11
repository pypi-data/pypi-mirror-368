# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.v1.domain.address import Address
from worldline.connect.sdk.v1.domain.customer_base import CustomerBase
from worldline.connect.sdk.v1.domain.personal_information_token import PersonalInformationToken


class CustomerToken(CustomerBase):

    __billing_address: Optional[Address] = None
    __personal_information: Optional[PersonalInformationToken] = None

    @property
    def billing_address(self) -> Optional[Address]:
        """
        | Object containing the billing address details

        Type: :class:`worldline.connect.sdk.v1.domain.address.Address`
        """
        return self.__billing_address

    @billing_address.setter
    def billing_address(self, value: Optional[Address]) -> None:
        self.__billing_address = value

    @property
    def personal_information(self) -> Optional[PersonalInformationToken]:
        """
        | Object containing personal information of the customer

        Type: :class:`worldline.connect.sdk.v1.domain.personal_information_token.PersonalInformationToken`
        """
        return self.__personal_information

    @personal_information.setter
    def personal_information(self, value: Optional[PersonalInformationToken]) -> None:
        self.__personal_information = value

    def to_dictionary(self) -> dict:
        dictionary = super(CustomerToken, self).to_dictionary()
        if self.billing_address is not None:
            dictionary['billingAddress'] = self.billing_address.to_dictionary()
        if self.personal_information is not None:
            dictionary['personalInformation'] = self.personal_information.to_dictionary()
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'CustomerToken':
        super(CustomerToken, self).from_dictionary(dictionary)
        if 'billingAddress' in dictionary:
            if not isinstance(dictionary['billingAddress'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['billingAddress']))
            value = Address()
            self.billing_address = value.from_dictionary(dictionary['billingAddress'])
        if 'personalInformation' in dictionary:
            if not isinstance(dictionary['personalInformation'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['personalInformation']))
            value = PersonalInformationToken()
            self.personal_information = value.from_dictionary(dictionary['personalInformation'])
        return self
