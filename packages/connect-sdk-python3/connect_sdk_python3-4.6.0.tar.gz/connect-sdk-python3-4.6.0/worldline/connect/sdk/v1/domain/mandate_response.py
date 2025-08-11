# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.domain.data_object import DataObject
from worldline.connect.sdk.v1.domain.mandate_customer import MandateCustomer


class MandateResponse(DataObject):

    __alias: Optional[str] = None
    __customer: Optional[MandateCustomer] = None
    __customer_reference: Optional[str] = None
    __recurrence_type: Optional[str] = None
    __status: Optional[str] = None
    __unique_mandate_reference: Optional[str] = None

    @property
    def alias(self) -> Optional[str]:
        """
        | An alias for the mandate. This can be used to visually represent the mandate.
        | Do not include any unobfuscated sensitive data in the alias.
        | Default value if not provided is the obfuscated IBAN of the customer.

        Type: str
        """
        return self.__alias

    @alias.setter
    def alias(self, value: Optional[str]) -> None:
        self.__alias = value

    @property
    def customer(self) -> Optional[MandateCustomer]:
        """
        | Customer object containing customer specific inputs

        Type: :class:`worldline.connect.sdk.v1.domain.mandate_customer.MandateCustomer`
        """
        return self.__customer

    @customer.setter
    def customer(self, value: Optional[MandateCustomer]) -> None:
        self.__customer = value

    @property
    def customer_reference(self) -> Optional[str]:
        """
        | The unique identifier of the customer to which this mandate is applicable

        Type: str
        """
        return self.__customer_reference

    @customer_reference.setter
    def customer_reference(self, value: Optional[str]) -> None:
        self.__customer_reference = value

    @property
    def recurrence_type(self) -> Optional[str]:
        """
        | Specifieds whether the mandate is for one-off or recurring payments.

        Type: str
        """
        return self.__recurrence_type

    @recurrence_type.setter
    def recurrence_type(self, value: Optional[str]) -> None:
        self.__recurrence_type = value

    @property
    def status(self) -> Optional[str]:
        """
        | The status of the mandate. Possible values are:
        
        * ACTIVE
        * EXPIRED
        * CREATED
        * REVOKED
        * WAITING_FOR_REFERENCE
        * BLOCKED
        * USED

        Type: str
        """
        return self.__status

    @status.setter
    def status(self, value: Optional[str]) -> None:
        self.__status = value

    @property
    def unique_mandate_reference(self) -> Optional[str]:
        """
        | The unique identifier of the mandate

        Type: str
        """
        return self.__unique_mandate_reference

    @unique_mandate_reference.setter
    def unique_mandate_reference(self, value: Optional[str]) -> None:
        self.__unique_mandate_reference = value

    def to_dictionary(self) -> dict:
        dictionary = super(MandateResponse, self).to_dictionary()
        if self.alias is not None:
            dictionary['alias'] = self.alias
        if self.customer is not None:
            dictionary['customer'] = self.customer.to_dictionary()
        if self.customer_reference is not None:
            dictionary['customerReference'] = self.customer_reference
        if self.recurrence_type is not None:
            dictionary['recurrenceType'] = self.recurrence_type
        if self.status is not None:
            dictionary['status'] = self.status
        if self.unique_mandate_reference is not None:
            dictionary['uniqueMandateReference'] = self.unique_mandate_reference
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'MandateResponse':
        super(MandateResponse, self).from_dictionary(dictionary)
        if 'alias' in dictionary:
            self.alias = dictionary['alias']
        if 'customer' in dictionary:
            if not isinstance(dictionary['customer'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['customer']))
            value = MandateCustomer()
            self.customer = value.from_dictionary(dictionary['customer'])
        if 'customerReference' in dictionary:
            self.customer_reference = dictionary['customerReference']
        if 'recurrenceType' in dictionary:
            self.recurrence_type = dictionary['recurrenceType']
        if 'status' in dictionary:
            self.status = dictionary['status']
        if 'uniqueMandateReference' in dictionary:
            self.unique_mandate_reference = dictionary['uniqueMandateReference']
        return self
