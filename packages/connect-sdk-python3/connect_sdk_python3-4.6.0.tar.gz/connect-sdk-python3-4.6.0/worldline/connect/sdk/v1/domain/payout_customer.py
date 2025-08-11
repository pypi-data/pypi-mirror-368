# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.domain.data_object import DataObject
from worldline.connect.sdk.v1.domain.address import Address
from worldline.connect.sdk.v1.domain.company_information import CompanyInformation
from worldline.connect.sdk.v1.domain.contact_details_base import ContactDetailsBase
from worldline.connect.sdk.v1.domain.personal_name import PersonalName


class PayoutCustomer(DataObject):

    __address: Optional[Address] = None
    __company_information: Optional[CompanyInformation] = None
    __contact_details: Optional[ContactDetailsBase] = None
    __merchant_customer_id: Optional[str] = None
    __name: Optional[PersonalName] = None

    @property
    def address(self) -> Optional[Address]:
        """
        | Object containing address details

        Type: :class:`worldline.connect.sdk.v1.domain.address.Address`
        """
        return self.__address

    @address.setter
    def address(self, value: Optional[Address]) -> None:
        self.__address = value

    @property
    def company_information(self) -> Optional[CompanyInformation]:
        """
        | Object containing company information

        Type: :class:`worldline.connect.sdk.v1.domain.company_information.CompanyInformation`
        """
        return self.__company_information

    @company_information.setter
    def company_information(self, value: Optional[CompanyInformation]) -> None:
        self.__company_information = value

    @property
    def contact_details(self) -> Optional[ContactDetailsBase]:
        """
        | Object containing contact details like email address and phone number

        Type: :class:`worldline.connect.sdk.v1.domain.contact_details_base.ContactDetailsBase`
        """
        return self.__contact_details

    @contact_details.setter
    def contact_details(self, value: Optional[ContactDetailsBase]) -> None:
        self.__contact_details = value

    @property
    def merchant_customer_id(self) -> Optional[str]:
        """
        | Your identifier for the customer. It can be used as a search criteria in the GlobalCollect Payment Console and is also included in the GlobalCollect report files. It is used in the fraud-screening process for payments on the Ogone Payment Platform.

        Type: str
        """
        return self.__merchant_customer_id

    @merchant_customer_id.setter
    def merchant_customer_id(self, value: Optional[str]) -> None:
        self.__merchant_customer_id = value

    @property
    def name(self) -> Optional[PersonalName]:
        """
        | Object containing PersonalName object

        Type: :class:`worldline.connect.sdk.v1.domain.personal_name.PersonalName`
        """
        return self.__name

    @name.setter
    def name(self, value: Optional[PersonalName]) -> None:
        self.__name = value

    def to_dictionary(self) -> dict:
        dictionary = super(PayoutCustomer, self).to_dictionary()
        if self.address is not None:
            dictionary['address'] = self.address.to_dictionary()
        if self.company_information is not None:
            dictionary['companyInformation'] = self.company_information.to_dictionary()
        if self.contact_details is not None:
            dictionary['contactDetails'] = self.contact_details.to_dictionary()
        if self.merchant_customer_id is not None:
            dictionary['merchantCustomerId'] = self.merchant_customer_id
        if self.name is not None:
            dictionary['name'] = self.name.to_dictionary()
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'PayoutCustomer':
        super(PayoutCustomer, self).from_dictionary(dictionary)
        if 'address' in dictionary:
            if not isinstance(dictionary['address'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['address']))
            value = Address()
            self.address = value.from_dictionary(dictionary['address'])
        if 'companyInformation' in dictionary:
            if not isinstance(dictionary['companyInformation'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['companyInformation']))
            value = CompanyInformation()
            self.company_information = value.from_dictionary(dictionary['companyInformation'])
        if 'contactDetails' in dictionary:
            if not isinstance(dictionary['contactDetails'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['contactDetails']))
            value = ContactDetailsBase()
            self.contact_details = value.from_dictionary(dictionary['contactDetails'])
        if 'merchantCustomerId' in dictionary:
            self.merchant_customer_id = dictionary['merchantCustomerId']
        if 'name' in dictionary:
            if not isinstance(dictionary['name'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['name']))
            value = PersonalName()
            self.name = value.from_dictionary(dictionary['name'])
        return self
