# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import List, Optional

from worldline.connect.sdk.domain.data_object import DataObject
from worldline.connect.sdk.v1.domain.api_error import APIError
from worldline.connect.sdk.v1.domain.key_value_pair import KeyValuePair


class OrderStatusOutput(DataObject):

    __errors: Optional[List[APIError]] = None
    __is_cancellable: Optional[bool] = None
    __is_retriable: Optional[bool] = None
    __provider_raw_output: Optional[List[KeyValuePair]] = None
    __status_category: Optional[str] = None
    __status_code: Optional[int] = None
    __status_code_change_date_time: Optional[str] = None

    @property
    def errors(self) -> Optional[List[APIError]]:
        """
        | Custom object contains the set of errors

        Type: list[:class:`worldline.connect.sdk.v1.domain.api_error.APIError`]
        """
        return self.__errors

    @errors.setter
    def errors(self, value: Optional[List[APIError]]) -> None:
        self.__errors = value

    @property
    def is_cancellable(self) -> Optional[bool]:
        """
        | Flag indicating if the payment can be cancelled
        
        * true
        * false

        Type: bool
        """
        return self.__is_cancellable

    @is_cancellable.setter
    def is_cancellable(self, value: Optional[bool]) -> None:
        self.__is_cancellable = value

    @property
    def is_retriable(self) -> Optional[bool]:
        """
        | Flag indicating whether a rejected payment may be retried by the merchant without incurring a fee 
        
        * true
        * false

        Type: bool
        """
        return self.__is_retriable

    @is_retriable.setter
    def is_retriable(self, value: Optional[bool]) -> None:
        self.__is_retriable = value

    @property
    def provider_raw_output(self) -> Optional[List[KeyValuePair]]:
        """
        | This is the raw response returned by the acquirer. This property contains unprocessed data directly returned by the acquirer. It's recommended for data analysis only due to its dynamic nature, which may undergo future changes.

        Type: list[:class:`worldline.connect.sdk.v1.domain.key_value_pair.KeyValuePair`]
        """
        return self.__provider_raw_output

    @provider_raw_output.setter
    def provider_raw_output(self, value: Optional[List[KeyValuePair]]) -> None:
        self.__provider_raw_output = value

    @property
    def status_category(self) -> Optional[str]:
        """
        | Highlevel status of the payment, payout or refund with the following possible values:
        
        * CREATED - The transaction has been created. This is the initial state once a new payment, payout or refund is created. This category groups the following statuses:
        
        * CREATED
        
        
        * PENDING_PAYMENT: The payment is waiting on customer action. This category groups the following statuses:
        
        * PENDING_PAYMENT
        * REDIRECTED
        
        
        * ACCOUNT_VERIFIED: The account has been verified. This category groups the following statuses:
        
        * ACCOUNT_VERIFIED
        
        
        * PENDING_MERCHANT: The transaction is awaiting approval to proceed with the payment, payout or refund. This category groups the following statuses:
        
        * PENDING_APPROVAL
        * PENDING_COMPLETION
        * PENDING_CAPTURE
        * PENDING_FRAUD_APPROVAL
        
        
        * PENDING_CONNECT_OR_3RD_PARTY: The transaction is in the queue to be processed. This category groups the following statuses:
        
        * AUTHORIZATION_REQUESTED
        * CAPTURE_REQUESTED
        * PAYOUT_REQUESTED
        * REFUND_REQUESTED
        
        
        * COMPLETED: The transaction has completed. This category groups the following statuses:
        
        * CAPTURED
        * PAID
        * ACCOUNT_CREDITED
        * CHARGEBACK_NOTIFICATION
        
        
        * REVERSED: The transaction has been reversed. This category groups the following statuses:
        
        * CHARGEBACKED
        * REVERSED
        
        
        * REFUNDED: The transaction has been refunded. This category groups the following statuses:
        
        * REFUNDED
        
        
        * UNSUCCESSFUL: The transaction has been rejected or is in such a state that it will never become successful. This category groups the following statuses:
        
        * CANCELLED
        * REJECTED
        * REJECTED_CAPTURE
        * REJECTED_CREDIT
        
        
        
        
        | Please see Statuses <https://apireference.connect.worldline-solutions.com/s2sapi/v1/en_US/python/statuses.html> for a full overview of possible values.

        Type: str
        """
        return self.__status_category

    @status_category.setter
    def status_category(self, value: Optional[str]) -> None:
        self.__status_category = value

    @property
    def status_code(self) -> Optional[int]:
        """
        | Numeric status code of the legacy API. It is returned to ease the migration from the legacy APIs to Worldline Connect. You should not write new business logic based on this property as it will be deprecated in a future version of the API. The value can also be found in the GlobalCollect Payment Console, in the Ogone BackOffice and in report files.

        Type: int
        """
        return self.__status_code

    @status_code.setter
    def status_code(self, value: Optional[int]) -> None:
        self.__status_code = value

    @property
    def status_code_change_date_time(self) -> Optional[str]:
        """
        | Date and time of payment
        | Format: YYYYMMDDHH24MISS

        Type: str
        """
        return self.__status_code_change_date_time

    @status_code_change_date_time.setter
    def status_code_change_date_time(self, value: Optional[str]) -> None:
        self.__status_code_change_date_time = value

    def to_dictionary(self) -> dict:
        dictionary = super(OrderStatusOutput, self).to_dictionary()
        if self.errors is not None:
            dictionary['errors'] = []
            for element in self.errors:
                if element is not None:
                    dictionary['errors'].append(element.to_dictionary())
        if self.is_cancellable is not None:
            dictionary['isCancellable'] = self.is_cancellable
        if self.is_retriable is not None:
            dictionary['isRetriable'] = self.is_retriable
        if self.provider_raw_output is not None:
            dictionary['providerRawOutput'] = []
            for element in self.provider_raw_output:
                if element is not None:
                    dictionary['providerRawOutput'].append(element.to_dictionary())
        if self.status_category is not None:
            dictionary['statusCategory'] = self.status_category
        if self.status_code is not None:
            dictionary['statusCode'] = self.status_code
        if self.status_code_change_date_time is not None:
            dictionary['statusCodeChangeDateTime'] = self.status_code_change_date_time
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'OrderStatusOutput':
        super(OrderStatusOutput, self).from_dictionary(dictionary)
        if 'errors' in dictionary:
            if not isinstance(dictionary['errors'], list):
                raise TypeError('value \'{}\' is not a list'.format(dictionary['errors']))
            self.errors = []
            for element in dictionary['errors']:
                value = APIError()
                self.errors.append(value.from_dictionary(element))
        if 'isCancellable' in dictionary:
            self.is_cancellable = dictionary['isCancellable']
        if 'isRetriable' in dictionary:
            self.is_retriable = dictionary['isRetriable']
        if 'providerRawOutput' in dictionary:
            if not isinstance(dictionary['providerRawOutput'], list):
                raise TypeError('value \'{}\' is not a list'.format(dictionary['providerRawOutput']))
            self.provider_raw_output = []
            for element in dictionary['providerRawOutput']:
                value = KeyValuePair()
                self.provider_raw_output.append(value.from_dictionary(element))
        if 'statusCategory' in dictionary:
            self.status_category = dictionary['statusCategory']
        if 'statusCode' in dictionary:
            self.status_code = dictionary['statusCode']
        if 'statusCodeChangeDateTime' in dictionary:
            self.status_code_change_date_time = dictionary['statusCodeChangeDateTime']
        return self
