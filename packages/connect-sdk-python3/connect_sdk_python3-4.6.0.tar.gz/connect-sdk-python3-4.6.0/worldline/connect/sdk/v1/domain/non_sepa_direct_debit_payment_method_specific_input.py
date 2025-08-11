# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.v1.domain.abstract_payment_method_specific_input import AbstractPaymentMethodSpecificInput
from worldline.connect.sdk.v1.domain.non_sepa_direct_debit_payment_product705_specific_input import NonSepaDirectDebitPaymentProduct705SpecificInput
from worldline.connect.sdk.v1.domain.non_sepa_direct_debit_payment_product730_specific_input import NonSepaDirectDebitPaymentProduct730SpecificInput


class NonSepaDirectDebitPaymentMethodSpecificInput(AbstractPaymentMethodSpecificInput):

    __date_collect: Optional[str] = None
    __direct_debit_text: Optional[str] = None
    __is_recurring: Optional[bool] = None
    __payment_product705_specific_input: Optional[NonSepaDirectDebitPaymentProduct705SpecificInput] = None
    __payment_product730_specific_input: Optional[NonSepaDirectDebitPaymentProduct730SpecificInput] = None
    __recurring_payment_sequence_indicator: Optional[str] = None
    __requires_approval: Optional[bool] = None
    __token: Optional[str] = None
    __tokenize: Optional[bool] = None

    @property
    def date_collect(self) -> Optional[str]:
        """
        | Direct Debit payment collection date
        | Format: YYYYMMDD

        Type: str
        """
        return self.__date_collect

    @date_collect.setter
    def date_collect(self, value: Optional[str]) -> None:
        self.__date_collect = value

    @property
    def direct_debit_text(self) -> Optional[str]:
        """
        | Descriptor intended to identify the transaction on the customer's bank statement

        Type: str
        """
        return self.__direct_debit_text

    @direct_debit_text.setter
    def direct_debit_text(self, value: Optional[str]) -> None:
        self.__direct_debit_text = value

    @property
    def is_recurring(self) -> Optional[bool]:
        """
        | Indicates if this transaction is of a one-off or a recurring type
        
        * true - This is recurring
        * false - This is one-off

        Type: bool
        """
        return self.__is_recurring

    @is_recurring.setter
    def is_recurring(self, value: Optional[bool]) -> None:
        self.__is_recurring = value

    @property
    def payment_product705_specific_input(self) -> Optional[NonSepaDirectDebitPaymentProduct705SpecificInput]:
        """
        | Object containing UK Direct Debit specific details

        Type: :class:`worldline.connect.sdk.v1.domain.non_sepa_direct_debit_payment_product705_specific_input.NonSepaDirectDebitPaymentProduct705SpecificInput`
        """
        return self.__payment_product705_specific_input

    @payment_product705_specific_input.setter
    def payment_product705_specific_input(self, value: Optional[NonSepaDirectDebitPaymentProduct705SpecificInput]) -> None:
        self.__payment_product705_specific_input = value

    @property
    def payment_product730_specific_input(self) -> Optional[NonSepaDirectDebitPaymentProduct730SpecificInput]:
        """
        | Object containing ACH specific details

        Type: :class:`worldline.connect.sdk.v1.domain.non_sepa_direct_debit_payment_product730_specific_input.NonSepaDirectDebitPaymentProduct730SpecificInput`
        """
        return self.__payment_product730_specific_input

    @payment_product730_specific_input.setter
    def payment_product730_specific_input(self, value: Optional[NonSepaDirectDebitPaymentProduct730SpecificInput]) -> None:
        self.__payment_product730_specific_input = value

    @property
    def recurring_payment_sequence_indicator(self) -> Optional[str]:
        """
        * first = This transaction is the first of a series of recurring transactions
        * recurring = This transaction is a subsequent transaction in a series of recurring transactions
        * last = This transaction is the last transaction of a series of recurring transactions

        Type: str
        """
        return self.__recurring_payment_sequence_indicator

    @recurring_payment_sequence_indicator.setter
    def recurring_payment_sequence_indicator(self, value: Optional[str]) -> None:
        self.__recurring_payment_sequence_indicator = value

    @property
    def requires_approval(self) -> Optional[bool]:
        """
        * true - The payment requires approval before the funds will be captured using the Approve payment or Capture payment API.
        * false - The payment does not require approval, and the funds will be captured automatically.

        Type: bool
        """
        return self.__requires_approval

    @requires_approval.setter
    def requires_approval(self, value: Optional[bool]) -> None:
        self.__requires_approval = value

    @property
    def token(self) -> Optional[str]:
        """
        | ID of the stored token that contains the bank account details to be debited

        Type: str
        """
        return self.__token

    @token.setter
    def token(self, value: Optional[str]) -> None:
        self.__token = value

    @property
    def tokenize(self) -> Optional[bool]:
        """
        | Indicates if this transaction should be tokenized
        
        * true - Tokenize the transaction
        * false - Do not tokenize the transaction, unless it would be tokenized by other means such as auto-tokenization of recurring payments.

        Type: bool
        """
        return self.__tokenize

    @tokenize.setter
    def tokenize(self, value: Optional[bool]) -> None:
        self.__tokenize = value

    def to_dictionary(self) -> dict:
        dictionary = super(NonSepaDirectDebitPaymentMethodSpecificInput, self).to_dictionary()
        if self.date_collect is not None:
            dictionary['dateCollect'] = self.date_collect
        if self.direct_debit_text is not None:
            dictionary['directDebitText'] = self.direct_debit_text
        if self.is_recurring is not None:
            dictionary['isRecurring'] = self.is_recurring
        if self.payment_product705_specific_input is not None:
            dictionary['paymentProduct705SpecificInput'] = self.payment_product705_specific_input.to_dictionary()
        if self.payment_product730_specific_input is not None:
            dictionary['paymentProduct730SpecificInput'] = self.payment_product730_specific_input.to_dictionary()
        if self.recurring_payment_sequence_indicator is not None:
            dictionary['recurringPaymentSequenceIndicator'] = self.recurring_payment_sequence_indicator
        if self.requires_approval is not None:
            dictionary['requiresApproval'] = self.requires_approval
        if self.token is not None:
            dictionary['token'] = self.token
        if self.tokenize is not None:
            dictionary['tokenize'] = self.tokenize
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'NonSepaDirectDebitPaymentMethodSpecificInput':
        super(NonSepaDirectDebitPaymentMethodSpecificInput, self).from_dictionary(dictionary)
        if 'dateCollect' in dictionary:
            self.date_collect = dictionary['dateCollect']
        if 'directDebitText' in dictionary:
            self.direct_debit_text = dictionary['directDebitText']
        if 'isRecurring' in dictionary:
            self.is_recurring = dictionary['isRecurring']
        if 'paymentProduct705SpecificInput' in dictionary:
            if not isinstance(dictionary['paymentProduct705SpecificInput'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['paymentProduct705SpecificInput']))
            value = NonSepaDirectDebitPaymentProduct705SpecificInput()
            self.payment_product705_specific_input = value.from_dictionary(dictionary['paymentProduct705SpecificInput'])
        if 'paymentProduct730SpecificInput' in dictionary:
            if not isinstance(dictionary['paymentProduct730SpecificInput'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['paymentProduct730SpecificInput']))
            value = NonSepaDirectDebitPaymentProduct730SpecificInput()
            self.payment_product730_specific_input = value.from_dictionary(dictionary['paymentProduct730SpecificInput'])
        if 'recurringPaymentSequenceIndicator' in dictionary:
            self.recurring_payment_sequence_indicator = dictionary['recurringPaymentSequenceIndicator']
        if 'requiresApproval' in dictionary:
            self.requires_approval = dictionary['requiresApproval']
        if 'token' in dictionary:
            self.token = dictionary['token']
        if 'tokenize' in dictionary:
            self.tokenize = dictionary['tokenize']
        return self
