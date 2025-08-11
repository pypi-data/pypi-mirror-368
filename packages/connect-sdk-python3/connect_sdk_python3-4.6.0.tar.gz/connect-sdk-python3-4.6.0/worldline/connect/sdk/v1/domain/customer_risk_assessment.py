# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.domain.data_object import DataObject
from worldline.connect.sdk.v1.domain.address import Address
from worldline.connect.sdk.v1.domain.address_personal import AddressPersonal
from worldline.connect.sdk.v1.domain.contact_details_risk_assessment import ContactDetailsRiskAssessment
from worldline.connect.sdk.v1.domain.customer_account_risk_assessment import CustomerAccountRiskAssessment
from worldline.connect.sdk.v1.domain.customer_device_risk_assessment import CustomerDeviceRiskAssessment
from worldline.connect.sdk.v1.domain.personal_information_risk_assessment import PersonalInformationRiskAssessment


class CustomerRiskAssessment(DataObject):
    """
    | Object containing data related to the customer
    """

    __account: Optional[CustomerAccountRiskAssessment] = None
    __account_type: Optional[str] = None
    __billing_address: Optional[Address] = None
    __contact_details: Optional[ContactDetailsRiskAssessment] = None
    __device: Optional[CustomerDeviceRiskAssessment] = None
    __is_previous_customer: Optional[bool] = None
    __locale: Optional[str] = None
    __personal_information: Optional[PersonalInformationRiskAssessment] = None
    __shipping_address: Optional[AddressPersonal] = None

    @property
    def account(self) -> Optional[CustomerAccountRiskAssessment]:
        """
        | Object containing data related to the account the customer has with you

        Type: :class:`worldline.connect.sdk.v1.domain.customer_account_risk_assessment.CustomerAccountRiskAssessment`
        """
        return self.__account

    @account.setter
    def account(self, value: Optional[CustomerAccountRiskAssessment]) -> None:
        self.__account = value

    @property
    def account_type(self) -> Optional[str]:
        """
        | Type of the customer account that is used to place this order. Can have one of the following values:
        
        * none - The account that was used to place the order is a guest account or no account was used at all
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
    def contact_details(self) -> Optional[ContactDetailsRiskAssessment]:
        """
        | Object containing contact details like email address

        Type: :class:`worldline.connect.sdk.v1.domain.contact_details_risk_assessment.ContactDetailsRiskAssessment`
        """
        return self.__contact_details

    @contact_details.setter
    def contact_details(self, value: Optional[ContactDetailsRiskAssessment]) -> None:
        self.__contact_details = value

    @property
    def device(self) -> Optional[CustomerDeviceRiskAssessment]:
        """
        | Object containing information on the device and browser of the customer

        Type: :class:`worldline.connect.sdk.v1.domain.customer_device_risk_assessment.CustomerDeviceRiskAssessment`
        """
        return self.__device

    @device.setter
    def device(self, value: Optional[CustomerDeviceRiskAssessment]) -> None:
        self.__device = value

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
    def personal_information(self) -> Optional[PersonalInformationRiskAssessment]:
        """
        | Object containing personal information like name, date of birth and gender

        Type: :class:`worldline.connect.sdk.v1.domain.personal_information_risk_assessment.PersonalInformationRiskAssessment`
        """
        return self.__personal_information

    @personal_information.setter
    def personal_information(self, value: Optional[PersonalInformationRiskAssessment]) -> None:
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
        dictionary = super(CustomerRiskAssessment, self).to_dictionary()
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
        if self.is_previous_customer is not None:
            dictionary['isPreviousCustomer'] = self.is_previous_customer
        if self.locale is not None:
            dictionary['locale'] = self.locale
        if self.personal_information is not None:
            dictionary['personalInformation'] = self.personal_information.to_dictionary()
        if self.shipping_address is not None:
            dictionary['shippingAddress'] = self.shipping_address.to_dictionary()
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'CustomerRiskAssessment':
        super(CustomerRiskAssessment, self).from_dictionary(dictionary)
        if 'account' in dictionary:
            if not isinstance(dictionary['account'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['account']))
            value = CustomerAccountRiskAssessment()
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
            value = ContactDetailsRiskAssessment()
            self.contact_details = value.from_dictionary(dictionary['contactDetails'])
        if 'device' in dictionary:
            if not isinstance(dictionary['device'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['device']))
            value = CustomerDeviceRiskAssessment()
            self.device = value.from_dictionary(dictionary['device'])
        if 'isPreviousCustomer' in dictionary:
            self.is_previous_customer = dictionary['isPreviousCustomer']
        if 'locale' in dictionary:
            self.locale = dictionary['locale']
        if 'personalInformation' in dictionary:
            if not isinstance(dictionary['personalInformation'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['personalInformation']))
            value = PersonalInformationRiskAssessment()
            self.personal_information = value.from_dictionary(dictionary['personalInformation'])
        if 'shippingAddress' in dictionary:
            if not isinstance(dictionary['shippingAddress'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['shippingAddress']))
            value = AddressPersonal()
            self.shipping_address = value.from_dictionary(dictionary['shippingAddress'])
        return self
