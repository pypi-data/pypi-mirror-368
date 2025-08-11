# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.domain.data_object import DataObject
from worldline.connect.sdk.v1.domain.company_information import CompanyInformation


class CustomerBase(DataObject):
    """
    | Basic information of a customer
    """

    __company_information: Optional[CompanyInformation] = None
    __merchant_customer_id: Optional[str] = None
    __vat_number: Optional[str] = None

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
    def vat_number(self) -> Optional[str]:
        """
        | Local VAT number of the company

        Type: str

        Deprecated; Use companyInformation.vatNumber instead
        """
        return self.__vat_number

    @vat_number.setter
    def vat_number(self, value: Optional[str]) -> None:
        self.__vat_number = value

    def to_dictionary(self) -> dict:
        dictionary = super(CustomerBase, self).to_dictionary()
        if self.company_information is not None:
            dictionary['companyInformation'] = self.company_information.to_dictionary()
        if self.merchant_customer_id is not None:
            dictionary['merchantCustomerId'] = self.merchant_customer_id
        if self.vat_number is not None:
            dictionary['vatNumber'] = self.vat_number
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'CustomerBase':
        super(CustomerBase, self).from_dictionary(dictionary)
        if 'companyInformation' in dictionary:
            if not isinstance(dictionary['companyInformation'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['companyInformation']))
            value = CompanyInformation()
            self.company_information = value.from_dictionary(dictionary['companyInformation'])
        if 'merchantCustomerId' in dictionary:
            self.merchant_customer_id = dictionary['merchantCustomerId']
        if 'vatNumber' in dictionary:
            self.vat_number = dictionary['vatNumber']
        return self
