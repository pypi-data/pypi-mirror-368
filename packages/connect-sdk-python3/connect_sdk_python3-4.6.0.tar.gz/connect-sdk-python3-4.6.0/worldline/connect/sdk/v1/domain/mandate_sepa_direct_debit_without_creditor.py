# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.domain.data_object import DataObject
from worldline.connect.sdk.v1.domain.bank_account_iban import BankAccountIban
from worldline.connect.sdk.v1.domain.debtor import Debtor
from worldline.connect.sdk.v1.domain.mandate_approval import MandateApproval


class MandateSepaDirectDebitWithoutCreditor(DataObject):

    __bank_account_iban: Optional[BankAccountIban] = None
    __customer_contract_identifier: Optional[str] = None
    __debtor: Optional[Debtor] = None
    __is_recurring: Optional[bool] = None
    __mandate_approval: Optional[MandateApproval] = None
    __pre_notification: Optional[str] = None

    @property
    def bank_account_iban(self) -> Optional[BankAccountIban]:
        """
        | Object containing Account holder and IBAN information

        Type: :class:`worldline.connect.sdk.v1.domain.bank_account_iban.BankAccountIban`
        """
        return self.__bank_account_iban

    @bank_account_iban.setter
    def bank_account_iban(self, value: Optional[BankAccountIban]) -> None:
        self.__bank_account_iban = value

    @property
    def customer_contract_identifier(self) -> Optional[str]:
        """
        | Identifies the contract between customer and merchant

        Type: str
        """
        return self.__customer_contract_identifier

    @customer_contract_identifier.setter
    def customer_contract_identifier(self, value: Optional[str]) -> None:
        self.__customer_contract_identifier = value

    @property
    def debtor(self) -> Optional[Debtor]:
        """
        | Object containing information on the debtor

        Type: :class:`worldline.connect.sdk.v1.domain.debtor.Debtor`
        """
        return self.__debtor

    @debtor.setter
    def debtor(self, value: Optional[Debtor]) -> None:
        self.__debtor = value

    @property
    def is_recurring(self) -> Optional[bool]:
        """
        * true
        * false

        Type: bool
        """
        return self.__is_recurring

    @is_recurring.setter
    def is_recurring(self, value: Optional[bool]) -> None:
        self.__is_recurring = value

    @property
    def mandate_approval(self) -> Optional[MandateApproval]:
        """
        | Object containing the details of the mandate approval

        Type: :class:`worldline.connect.sdk.v1.domain.mandate_approval.MandateApproval`
        """
        return self.__mandate_approval

    @mandate_approval.setter
    def mandate_approval(self, value: Optional[MandateApproval]) -> None:
        self.__mandate_approval = value

    @property
    def pre_notification(self) -> Optional[str]:
        """
        | Indicates whether a pre-notification should be sent to the customer.
        
        * do-not-send - Do not send a pre-notification
        * send-on-first-collection - Send a pre-notification

        Type: str
        """
        return self.__pre_notification

    @pre_notification.setter
    def pre_notification(self, value: Optional[str]) -> None:
        self.__pre_notification = value

    def to_dictionary(self) -> dict:
        dictionary = super(MandateSepaDirectDebitWithoutCreditor, self).to_dictionary()
        if self.bank_account_iban is not None:
            dictionary['bankAccountIban'] = self.bank_account_iban.to_dictionary()
        if self.customer_contract_identifier is not None:
            dictionary['customerContractIdentifier'] = self.customer_contract_identifier
        if self.debtor is not None:
            dictionary['debtor'] = self.debtor.to_dictionary()
        if self.is_recurring is not None:
            dictionary['isRecurring'] = self.is_recurring
        if self.mandate_approval is not None:
            dictionary['mandateApproval'] = self.mandate_approval.to_dictionary()
        if self.pre_notification is not None:
            dictionary['preNotification'] = self.pre_notification
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'MandateSepaDirectDebitWithoutCreditor':
        super(MandateSepaDirectDebitWithoutCreditor, self).from_dictionary(dictionary)
        if 'bankAccountIban' in dictionary:
            if not isinstance(dictionary['bankAccountIban'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['bankAccountIban']))
            value = BankAccountIban()
            self.bank_account_iban = value.from_dictionary(dictionary['bankAccountIban'])
        if 'customerContractIdentifier' in dictionary:
            self.customer_contract_identifier = dictionary['customerContractIdentifier']
        if 'debtor' in dictionary:
            if not isinstance(dictionary['debtor'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['debtor']))
            value = Debtor()
            self.debtor = value.from_dictionary(dictionary['debtor'])
        if 'isRecurring' in dictionary:
            self.is_recurring = dictionary['isRecurring']
        if 'mandateApproval' in dictionary:
            if not isinstance(dictionary['mandateApproval'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['mandateApproval']))
            value = MandateApproval()
            self.mandate_approval = value.from_dictionary(dictionary['mandateApproval'])
        if 'preNotification' in dictionary:
            self.pre_notification = dictionary['preNotification']
        return self
