# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.v1.domain.abstract_payment_method_specific_output import AbstractPaymentMethodSpecificOutput
from worldline.connect.sdk.v1.domain.bank_account_bban import BankAccountBban
from worldline.connect.sdk.v1.domain.bank_account_iban import BankAccountIban
from worldline.connect.sdk.v1.domain.fraud_results import FraudResults
from worldline.connect.sdk.v1.domain.payment_product3201_specific_output import PaymentProduct3201SpecificOutput
from worldline.connect.sdk.v1.domain.payment_product806_specific_output import PaymentProduct806SpecificOutput
from worldline.connect.sdk.v1.domain.payment_product836_specific_output import PaymentProduct836SpecificOutput
from worldline.connect.sdk.v1.domain.payment_product840_specific_output import PaymentProduct840SpecificOutput
from worldline.connect.sdk.v1.domain.payment_product866_specific_output import PaymentProduct866SpecificOutput


class RedirectPaymentMethodSpecificOutput(AbstractPaymentMethodSpecificOutput):

    __bank_account_bban: Optional[BankAccountBban] = None
    __bank_account_iban: Optional[BankAccountIban] = None
    __bic: Optional[str] = None
    __fraud_results: Optional[FraudResults] = None
    __payment_product3201_specific_output: Optional[PaymentProduct3201SpecificOutput] = None
    __payment_product806_specific_output: Optional[PaymentProduct806SpecificOutput] = None
    __payment_product836_specific_output: Optional[PaymentProduct836SpecificOutput] = None
    __payment_product840_specific_output: Optional[PaymentProduct840SpecificOutput] = None
    __payment_product866_specific_output: Optional[PaymentProduct866SpecificOutput] = None
    __token: Optional[str] = None

    @property
    def bank_account_bban(self) -> Optional[BankAccountBban]:
        """
        | Object that holds the Basic Bank Account Number (BBAN) data

        Type: :class:`worldline.connect.sdk.v1.domain.bank_account_bban.BankAccountBban`
        """
        return self.__bank_account_bban

    @bank_account_bban.setter
    def bank_account_bban(self, value: Optional[BankAccountBban]) -> None:
        self.__bank_account_bban = value

    @property
    def bank_account_iban(self) -> Optional[BankAccountIban]:
        """
        | Object containing account holder name and IBAN information

        Type: :class:`worldline.connect.sdk.v1.domain.bank_account_iban.BankAccountIban`
        """
        return self.__bank_account_iban

    @bank_account_iban.setter
    def bank_account_iban(self, value: Optional[BankAccountIban]) -> None:
        self.__bank_account_iban = value

    @property
    def bic(self) -> Optional[str]:
        """
        | The BIC is the Business Identifier Code, also known as SWIFT or Bank Identifier code. It is a code with an internationally agreed format to Identify a specific bank or even branch. The BIC contains 8 or 11 positions: the first 4 contain the bank code, followed by the country code and location code.

        Type: str
        """
        return self.__bic

    @bic.setter
    def bic(self, value: Optional[str]) -> None:
        self.__bic = value

    @property
    def fraud_results(self) -> Optional[FraudResults]:
        """
        | Object containing the results of the fraud screening

        Type: :class:`worldline.connect.sdk.v1.domain.fraud_results.FraudResults`
        """
        return self.__fraud_results

    @fraud_results.setter
    def fraud_results(self, value: Optional[FraudResults]) -> None:
        self.__fraud_results = value

    @property
    def payment_product3201_specific_output(self) -> Optional[PaymentProduct3201SpecificOutput]:
        """
        | PostFinance Card (payment product 3201) specific details

        Type: :class:`worldline.connect.sdk.v1.domain.payment_product3201_specific_output.PaymentProduct3201SpecificOutput`
        """
        return self.__payment_product3201_specific_output

    @payment_product3201_specific_output.setter
    def payment_product3201_specific_output(self, value: Optional[PaymentProduct3201SpecificOutput]) -> None:
        self.__payment_product3201_specific_output = value

    @property
    def payment_product806_specific_output(self) -> Optional[PaymentProduct806SpecificOutput]:
        """
        | Trustly (payment product 806) specific details

        Type: :class:`worldline.connect.sdk.v1.domain.payment_product806_specific_output.PaymentProduct806SpecificOutput`
        """
        return self.__payment_product806_specific_output

    @payment_product806_specific_output.setter
    def payment_product806_specific_output(self, value: Optional[PaymentProduct806SpecificOutput]) -> None:
        self.__payment_product806_specific_output = value

    @property
    def payment_product836_specific_output(self) -> Optional[PaymentProduct836SpecificOutput]:
        """
        | Sofort (payment product 836) specific details

        Type: :class:`worldline.connect.sdk.v1.domain.payment_product836_specific_output.PaymentProduct836SpecificOutput`
        """
        return self.__payment_product836_specific_output

    @payment_product836_specific_output.setter
    def payment_product836_specific_output(self, value: Optional[PaymentProduct836SpecificOutput]) -> None:
        self.__payment_product836_specific_output = value

    @property
    def payment_product840_specific_output(self) -> Optional[PaymentProduct840SpecificOutput]:
        """
        | PayPal (payment product 840) specific details

        Type: :class:`worldline.connect.sdk.v1.domain.payment_product840_specific_output.PaymentProduct840SpecificOutput`
        """
        return self.__payment_product840_specific_output

    @payment_product840_specific_output.setter
    def payment_product840_specific_output(self, value: Optional[PaymentProduct840SpecificOutput]) -> None:
        self.__payment_product840_specific_output = value

    @property
    def payment_product866_specific_output(self) -> Optional[PaymentProduct866SpecificOutput]:
        """
        | Alipay+ (payment product 866) specific details

        Type: :class:`worldline.connect.sdk.v1.domain.payment_product866_specific_output.PaymentProduct866SpecificOutput`
        """
        return self.__payment_product866_specific_output

    @payment_product866_specific_output.setter
    def payment_product866_specific_output(self, value: Optional[PaymentProduct866SpecificOutput]) -> None:
        self.__payment_product866_specific_output = value

    @property
    def token(self) -> Optional[str]:
        """
        | ID of the token. This property is populated when the payment was done with a token or when the payment was tokenized.

        Type: str
        """
        return self.__token

    @token.setter
    def token(self, value: Optional[str]) -> None:
        self.__token = value

    def to_dictionary(self) -> dict:
        dictionary = super(RedirectPaymentMethodSpecificOutput, self).to_dictionary()
        if self.bank_account_bban is not None:
            dictionary['bankAccountBban'] = self.bank_account_bban.to_dictionary()
        if self.bank_account_iban is not None:
            dictionary['bankAccountIban'] = self.bank_account_iban.to_dictionary()
        if self.bic is not None:
            dictionary['bic'] = self.bic
        if self.fraud_results is not None:
            dictionary['fraudResults'] = self.fraud_results.to_dictionary()
        if self.payment_product3201_specific_output is not None:
            dictionary['paymentProduct3201SpecificOutput'] = self.payment_product3201_specific_output.to_dictionary()
        if self.payment_product806_specific_output is not None:
            dictionary['paymentProduct806SpecificOutput'] = self.payment_product806_specific_output.to_dictionary()
        if self.payment_product836_specific_output is not None:
            dictionary['paymentProduct836SpecificOutput'] = self.payment_product836_specific_output.to_dictionary()
        if self.payment_product840_specific_output is not None:
            dictionary['paymentProduct840SpecificOutput'] = self.payment_product840_specific_output.to_dictionary()
        if self.payment_product866_specific_output is not None:
            dictionary['paymentProduct866SpecificOutput'] = self.payment_product866_specific_output.to_dictionary()
        if self.token is not None:
            dictionary['token'] = self.token
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'RedirectPaymentMethodSpecificOutput':
        super(RedirectPaymentMethodSpecificOutput, self).from_dictionary(dictionary)
        if 'bankAccountBban' in dictionary:
            if not isinstance(dictionary['bankAccountBban'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['bankAccountBban']))
            value = BankAccountBban()
            self.bank_account_bban = value.from_dictionary(dictionary['bankAccountBban'])
        if 'bankAccountIban' in dictionary:
            if not isinstance(dictionary['bankAccountIban'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['bankAccountIban']))
            value = BankAccountIban()
            self.bank_account_iban = value.from_dictionary(dictionary['bankAccountIban'])
        if 'bic' in dictionary:
            self.bic = dictionary['bic']
        if 'fraudResults' in dictionary:
            if not isinstance(dictionary['fraudResults'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['fraudResults']))
            value = FraudResults()
            self.fraud_results = value.from_dictionary(dictionary['fraudResults'])
        if 'paymentProduct3201SpecificOutput' in dictionary:
            if not isinstance(dictionary['paymentProduct3201SpecificOutput'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['paymentProduct3201SpecificOutput']))
            value = PaymentProduct3201SpecificOutput()
            self.payment_product3201_specific_output = value.from_dictionary(dictionary['paymentProduct3201SpecificOutput'])
        if 'paymentProduct806SpecificOutput' in dictionary:
            if not isinstance(dictionary['paymentProduct806SpecificOutput'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['paymentProduct806SpecificOutput']))
            value = PaymentProduct806SpecificOutput()
            self.payment_product806_specific_output = value.from_dictionary(dictionary['paymentProduct806SpecificOutput'])
        if 'paymentProduct836SpecificOutput' in dictionary:
            if not isinstance(dictionary['paymentProduct836SpecificOutput'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['paymentProduct836SpecificOutput']))
            value = PaymentProduct836SpecificOutput()
            self.payment_product836_specific_output = value.from_dictionary(dictionary['paymentProduct836SpecificOutput'])
        if 'paymentProduct840SpecificOutput' in dictionary:
            if not isinstance(dictionary['paymentProduct840SpecificOutput'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['paymentProduct840SpecificOutput']))
            value = PaymentProduct840SpecificOutput()
            self.payment_product840_specific_output = value.from_dictionary(dictionary['paymentProduct840SpecificOutput'])
        if 'paymentProduct866SpecificOutput' in dictionary:
            if not isinstance(dictionary['paymentProduct866SpecificOutput'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['paymentProduct866SpecificOutput']))
            value = PaymentProduct866SpecificOutput()
            self.payment_product866_specific_output = value.from_dictionary(dictionary['paymentProduct866SpecificOutput'])
        if 'token' in dictionary:
            self.token = dictionary['token']
        return self
