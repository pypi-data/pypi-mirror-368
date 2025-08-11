# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.v1.domain.address import Address
from worldline.connect.sdk.v1.domain.address_personal import AddressPersonal
from worldline.connect.sdk.v1.domain.contact_details import ContactDetails
from worldline.connect.sdk.v1.domain.customer_account import CustomerAccount
from worldline.connect.sdk.v1.domain.customer_base import CustomerBase
from worldline.connect.sdk.v1.domain.customer_device import CustomerDevice
from worldline.connect.sdk.v1.domain.personal_information import PersonalInformation


class Customer(CustomerBase):
    """
    | Object containing data related to the customer
    """

    __account: Optional[CustomerAccount] = None
    __account_type: Optional[str] = None
    __billing_address: Optional[Address] = None
    __contact_details: Optional[ContactDetails] = None
    __device: Optional[CustomerDevice] = None
    __fiscal_number: Optional[str] = None
    __is_company: Optional[bool] = None
    __is_previous_customer: Optional[bool] = None
    __locale: Optional[str] = None
    __personal_information: Optional[PersonalInformation] = None
    __shipping_address: Optional[AddressPersonal] = None

    @property
    def account(self) -> Optional[CustomerAccount]:
        """
        | Object containing data related to the account the customer has with you

        Type: :class:`worldline.connect.sdk.v1.domain.customer_account.CustomerAccount`
        """
        return self.__account

    @account.setter
    def account(self, value: Optional[CustomerAccount]) -> None:
        self.__account = value

    @property
    def account_type(self) -> Optional[str]:
        """
        | Type of the customer account that is used to place this order. Can have one of the following values:
        
        * none - The account that was used to place the order with is a guest account or no account was used at all
        * created - The customer account was created during this transaction
        * existing - The customer account was an already existing account prior to this transaction

        Type: str
        """
        return self.__account_type

    @account_type.setter
    def account_type(self, value: Optional[str]) -> None:
        self.__account_type = value

    @property
    def billing_address(self) -> Optional[Address]:
        """
        | Object containing billing address details

        Type: :class:`worldline.connect.sdk.v1.domain.address.Address`
        """
        return self.__billing_address

    @billing_address.setter
    def billing_address(self, value: Optional[Address]) -> None:
        self.__billing_address = value

    @property
    def contact_details(self) -> Optional[ContactDetails]:
        """
        | Object containing contact details like email address and phone number

        Type: :class:`worldline.connect.sdk.v1.domain.contact_details.ContactDetails`
        """
        return self.__contact_details

    @contact_details.setter
    def contact_details(self, value: Optional[ContactDetails]) -> None:
        self.__contact_details = value

    @property
    def device(self) -> Optional[CustomerDevice]:
        """
        | Object containing information on the device and browser of the customer

        Type: :class:`worldline.connect.sdk.v1.domain.customer_device.CustomerDevice`
        """
        return self.__device

    @device.setter
    def device(self, value: Optional[CustomerDevice]) -> None:
        self.__device = value

    @property
    def fiscal_number(self) -> Optional[str]:
        """
        | The fiscal registration number of the customer or the tax registration number of the company in case of a business customer. Please find below specifics per country:
        
        * Argentina - Consumer (DNI) with a length of 7 or 8 digits
        * Argentina - Company (CUIT) with a length of 11 digits
        * Brazil - Consumer (CPF) with a length of 11 digits
        * Brazil - Company (CNPJ) with a length of 14 digits
        * Chile - Consumer (RUT) with a length of 9 digits
        * Colombia - Consumer (NIT) with a length of 8, 9 or 10 digits
        * Denmark - Consumer (CPR-nummer or personnummer) with a length of 10 digits
        * Dominican Republic - Consumer (RNC) with a length of 11 digits
        * Finland - Consumer (Finnish: henkilötunnus (abbreviated as HETU)) with a length of 11 characters
        * India - Consumer (PAN) with a length of 10 characters
        * Mexico - Consumer (RFC) with a length of 13 digits
        * Mexico - Company (RFC) with a length of 12 digits
        * Norway - Consumer (fødselsnummer) with a length of 11 digits
        * Peru - Consumer (RUC) with a length of 11 digits
        * Sweden - Consumer (personnummer) with a length of 10 or 12 digits
        * Uruguay - Consumer (CI) with a length of 8 digits
        * Uruguay - Consumer (NIE) with a length of 9 digits
        * Uruguay - Company (RUT) with a length of 12 digits

        Type: str
        """
        return self.__fiscal_number

    @fiscal_number.setter
    def fiscal_number(self, value: Optional[str]) -> None:
        self.__fiscal_number = value

    @property
    def is_company(self) -> Optional[bool]:
        """
        | Indicates if the payer is a company or an individual
        
        * true =  This is a company
        * false = This is an individual

        Type: bool
        """
        return self.__is_company

    @is_company.setter
    def is_company(self, value: Optional[bool]) -> None:
        self.__is_company = value

    @property
    def is_previous_customer(self) -> Optional[bool]:
        """
        | Specifies if the customer has a history of online shopping with the merchant
        
        * true - The customer is a known returning customer
        * false - The customer is new/unknown customer

        Type: bool
        """
        return self.__is_previous_customer

    @is_previous_customer.setter
    def is_previous_customer(self, value: Optional[bool]) -> None:
        self.__is_previous_customer = value

    @property
    def locale(self) -> Optional[str]:
        """
        | The locale that the customer should be addressed in (for 3rd parties). Note that some 3rd party providers only support the languageCode part of the locale, in those cases we will only use part of the locale provided.

        Type: str
        """
        return self.__locale

    @locale.setter
    def locale(self, value: Optional[str]) -> None:
        self.__locale = value

    @property
    def personal_information(self) -> Optional[PersonalInformation]:
        """
        | Object containing personal information like name, date of birth and gender.

        Type: :class:`worldline.connect.sdk.v1.domain.personal_information.PersonalInformation`
        """
        return self.__personal_information

    @personal_information.setter
    def personal_information(self, value: Optional[PersonalInformation]) -> None:
        self.__personal_information = value

    @property
    def shipping_address(self) -> Optional[AddressPersonal]:
        """
        | Object containing shipping address details

        Type: :class:`worldline.connect.sdk.v1.domain.address_personal.AddressPersonal`

        Deprecated; Use Order.shipping.address instead
        """
        return self.__shipping_address

    @shipping_address.setter
    def shipping_address(self, value: Optional[AddressPersonal]) -> None:
        self.__shipping_address = value

    def to_dictionary(self) -> dict:
        dictionary = super(Customer, self).to_dictionary()
        if self.account is not None:
            dictionary['account'] = self.account.to_dictionary()
        if self.account_type is not None:
            dictionary['accountType'] = self.account_type
        if self.billing_address is not None:
            dictionary['billingAddress'] = self.billing_address.to_dictionary()
        if self.contact_details is not None:
            dictionary['contactDetails'] = self.contact_details.to_dictionary()
        if self.device is not None:
            dictionary['device'] = self.device.to_dictionary()
        if self.fiscal_number is not None:
            dictionary['fiscalNumber'] = self.fiscal_number
        if self.is_company is not None:
            dictionary['isCompany'] = self.is_company
        if self.is_previous_customer is not None:
            dictionary['isPreviousCustomer'] = self.is_previous_customer
        if self.locale is not None:
            dictionary['locale'] = self.locale
        if self.personal_information is not None:
            dictionary['personalInformation'] = self.personal_information.to_dictionary()
        if self.shipping_address is not None:
            dictionary['shippingAddress'] = self.shipping_address.to_dictionary()
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'Customer':
        super(Customer, self).from_dictionary(dictionary)
        if 'account' in dictionary:
            if not isinstance(dictionary['account'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['account']))
            value = CustomerAccount()
            self.account = value.from_dictionary(dictionary['account'])
        if 'accountType' in dictionary:
            self.account_type = dictionary['accountType']
        if 'billingAddress' in dictionary:
            if not isinstance(dictionary['billingAddress'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['billingAddress']))
            value = Address()
            self.billing_address = value.from_dictionary(dictionary['billingAddress'])
        if 'contactDetails' in dictionary:
            if not isinstance(dictionary['contactDetails'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['contactDetails']))
            value = ContactDetails()
            self.contact_details = value.from_dictionary(dictionary['contactDetails'])
        if 'device' in dictionary:
            if not isinstance(dictionary['device'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['device']))
            value = CustomerDevice()
            self.device = value.from_dictionary(dictionary['device'])
        if 'fiscalNumber' in dictionary:
            self.fiscal_number = dictionary['fiscalNumber']
        if 'isCompany' in dictionary:
            self.is_company = dictionary['isCompany']
        if 'isPreviousCustomer' in dictionary:
            self.is_previous_customer = dictionary['isPreviousCustomer']
        if 'locale' in dictionary:
            self.locale = dictionary['locale']
        if 'personalInformation' in dictionary:
            if not isinstance(dictionary['personalInformation'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['personalInformation']))
            value = PersonalInformation()
            self.personal_information = value.from_dictionary(dictionary['personalInformation'])
        if 'shippingAddress' in dictionary:
            if not isinstance(dictionary['shippingAddress'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['shippingAddress']))
            value = AddressPersonal()
            self.shipping_address = value.from_dictionary(dictionary['shippingAddress'])
        return self
