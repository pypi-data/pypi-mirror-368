# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.v1.domain.abstract_payment_method_specific_input import AbstractPaymentMethodSpecificInput


class AbstractRedirectPaymentMethodSpecificInput(AbstractPaymentMethodSpecificInput):

    __expiration_period: Optional[int] = None
    __recurring_payment_sequence_indicator: Optional[str] = None
    __requires_approval: Optional[bool] = None
    __token: Optional[str] = None
    __tokenize: Optional[bool] = None

    @property
    def expiration_period(self) -> Optional[int]:
        """
        Type: int
        """
        return self.__expiration_period

    @expiration_period.setter
    def expiration_period(self, value: Optional[int]) -> None:
        self.__expiration_period = value

    @property
    def recurring_payment_sequence_indicator(self) -> Optional[str]:
        """
        Type: str
        """
        return self.__recurring_payment_sequence_indicator

    @recurring_payment_sequence_indicator.setter
    def recurring_payment_sequence_indicator(self, value: Optional[str]) -> None:
        self.__recurring_payment_sequence_indicator = value

    @property
    def requires_approval(self) -> Optional[bool]:
        """
        Type: bool
        """
        return self.__requires_approval

    @requires_approval.setter
    def requires_approval(self, value: Optional[bool]) -> None:
        self.__requires_approval = value

    @property
    def token(self) -> Optional[str]:
        """
        Type: str
        """
        return self.__token

    @token.setter
    def token(self, value: Optional[str]) -> None:
        self.__token = value

    @property
    def tokenize(self) -> Optional[bool]:
        """
        Type: bool
        """
        return self.__tokenize

    @tokenize.setter
    def tokenize(self, value: Optional[bool]) -> None:
        self.__tokenize = value

    def to_dictionary(self) -> dict:
        dictionary = super(AbstractRedirectPaymentMethodSpecificInput, self).to_dictionary()
        if self.expiration_period is not None:
            dictionary['expirationPeriod'] = self.expiration_period
        if self.recurring_payment_sequence_indicator is not None:
            dictionary['recurringPaymentSequenceIndicator'] = self.recurring_payment_sequence_indicator
        if self.requires_approval is not None:
            dictionary['requiresApproval'] = self.requires_approval
        if self.token is not None:
            dictionary['token'] = self.token
        if self.tokenize is not None:
            dictionary['tokenize'] = self.tokenize
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'AbstractRedirectPaymentMethodSpecificInput':
        super(AbstractRedirectPaymentMethodSpecificInput, self).from_dictionary(dictionary)
        if 'expirationPeriod' in dictionary:
            self.expiration_period = dictionary['expirationPeriod']
        if 'recurringPaymentSequenceIndicator' in dictionary:
            self.recurring_payment_sequence_indicator = dictionary['recurringPaymentSequenceIndicator']
        if 'requiresApproval' in dictionary:
            self.requires_approval = dictionary['requiresApproval']
        if 'token' in dictionary:
            self.token = dictionary['token']
        if 'tokenize' in dictionary:
            self.tokenize = dictionary['tokenize']
        return self
