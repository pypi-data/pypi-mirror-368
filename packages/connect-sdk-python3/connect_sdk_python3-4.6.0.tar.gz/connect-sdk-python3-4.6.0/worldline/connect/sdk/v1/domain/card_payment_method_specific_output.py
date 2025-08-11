# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.v1.domain.abstract_payment_method_specific_output import AbstractPaymentMethodSpecificOutput
from worldline.connect.sdk.v1.domain.card_essentials import CardEssentials
from worldline.connect.sdk.v1.domain.card_fraud_results import CardFraudResults
from worldline.connect.sdk.v1.domain.network_token_data import NetworkTokenData
from worldline.connect.sdk.v1.domain.three_d_secure_results import ThreeDSecureResults


class CardPaymentMethodSpecificOutput(AbstractPaymentMethodSpecificOutput):
    """
    | Card payment specific response data
    """

    __authorisation_code: Optional[str] = None
    __card: Optional[CardEssentials] = None
    __fraud_results: Optional[CardFraudResults] = None
    __initial_scheme_transaction_id: Optional[str] = None
    __network_token_data: Optional[NetworkTokenData] = None
    __network_token_used: Optional[bool] = None
    __payment_account_reference: Optional[str] = None
    __scheme_transaction_id: Optional[str] = None
    __three_d_secure_results: Optional[ThreeDSecureResults] = None
    __token: Optional[str] = None

    @property
    def authorisation_code(self) -> Optional[str]:
        """
        | Card Authorization code as returned by the acquirer

        Type: str
        """
        return self.__authorisation_code

    @authorisation_code.setter
    def authorisation_code(self, value: Optional[str]) -> None:
        self.__authorisation_code = value

    @property
    def card(self) -> Optional[CardEssentials]:
        """
        | Object containing card details

        Type: :class:`worldline.connect.sdk.v1.domain.card_essentials.CardEssentials`
        """
        return self.__card

    @card.setter
    def card(self, value: Optional[CardEssentials]) -> None:
        self.__card = value

    @property
    def fraud_results(self) -> Optional[CardFraudResults]:
        """
        | Fraud results contained in the CardFraudResults object

        Type: :class:`worldline.connect.sdk.v1.domain.card_fraud_results.CardFraudResults`
        """
        return self.__fraud_results

    @fraud_results.setter
    def fraud_results(self, value: Optional[CardFraudResults]) -> None:
        self.__fraud_results = value

    @property
    def initial_scheme_transaction_id(self) -> Optional[str]:
        """
        | The unique scheme transactionId of the initial transaction that was performed with SCA.
        | Should be stored by the merchant to allow it to be submitted in future transactions.

        Type: str
        """
        return self.__initial_scheme_transaction_id

    @initial_scheme_transaction_id.setter
    def initial_scheme_transaction_id(self, value: Optional[str]) -> None:
        self.__initial_scheme_transaction_id = value

    @property
    def network_token_data(self) -> Optional[NetworkTokenData]:
        """
        | Object holding data that describes a network token.

        Type: :class:`worldline.connect.sdk.v1.domain.network_token_data.NetworkTokenData`
        """
        return self.__network_token_data

    @network_token_data.setter
    def network_token_data(self, value: Optional[NetworkTokenData]) -> None:
        self.__network_token_data = value

    @property
    def network_token_used(self) -> Optional[bool]:
        """
        | Indicates if a network token was used during the payment.

        Type: bool
        """
        return self.__network_token_used

    @network_token_used.setter
    def network_token_used(self, value: Optional[bool]) -> None:
        self.__network_token_used = value

    @property
    def payment_account_reference(self) -> Optional[str]:
        """
        | A unique reference to the primary account number. Payment Account Reference provides a consolidated view of transactions associated with a PAN and its affiliated tokens, making it easier to identify customers and their associated transactions across payment channels.

        Type: str
        """
        return self.__payment_account_reference

    @payment_account_reference.setter
    def payment_account_reference(self, value: Optional[str]) -> None:
        self.__payment_account_reference = value

    @property
    def scheme_transaction_id(self) -> Optional[str]:
        """
        | The unique scheme transactionId of this transaction.
        | Should be stored by the merchant to allow it to be submitted in future transactions. Use this value in case the initialSchemeTransactionId property is empty.

        Type: str
        """
        return self.__scheme_transaction_id

    @scheme_transaction_id.setter
    def scheme_transaction_id(self, value: Optional[str]) -> None:
        self.__scheme_transaction_id = value

    @property
    def three_d_secure_results(self) -> Optional[ThreeDSecureResults]:
        """
        | 3D Secure results object

        Type: :class:`worldline.connect.sdk.v1.domain.three_d_secure_results.ThreeDSecureResults`
        """
        return self.__three_d_secure_results

    @three_d_secure_results.setter
    def three_d_secure_results(self, value: Optional[ThreeDSecureResults]) -> None:
        self.__three_d_secure_results = value

    @property
    def token(self) -> Optional[str]:
        """
        | If a token was used for or created during the payment, then the ID of that token.

        Type: str
        """
        return self.__token

    @token.setter
    def token(self, value: Optional[str]) -> None:
        self.__token = value

    def to_dictionary(self) -> dict:
        dictionary = super(CardPaymentMethodSpecificOutput, self).to_dictionary()
        if self.authorisation_code is not None:
            dictionary['authorisationCode'] = self.authorisation_code
        if self.card is not None:
            dictionary['card'] = self.card.to_dictionary()
        if self.fraud_results is not None:
            dictionary['fraudResults'] = self.fraud_results.to_dictionary()
        if self.initial_scheme_transaction_id is not None:
            dictionary['initialSchemeTransactionId'] = self.initial_scheme_transaction_id
        if self.network_token_data is not None:
            dictionary['networkTokenData'] = self.network_token_data.to_dictionary()
        if self.network_token_used is not None:
            dictionary['networkTokenUsed'] = self.network_token_used
        if self.payment_account_reference is not None:
            dictionary['paymentAccountReference'] = self.payment_account_reference
        if self.scheme_transaction_id is not None:
            dictionary['schemeTransactionId'] = self.scheme_transaction_id
        if self.three_d_secure_results is not None:
            dictionary['threeDSecureResults'] = self.three_d_secure_results.to_dictionary()
        if self.token is not None:
            dictionary['token'] = self.token
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'CardPaymentMethodSpecificOutput':
        super(CardPaymentMethodSpecificOutput, self).from_dictionary(dictionary)
        if 'authorisationCode' in dictionary:
            self.authorisation_code = dictionary['authorisationCode']
        if 'card' in dictionary:
            if not isinstance(dictionary['card'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['card']))
            value = CardEssentials()
            self.card = value.from_dictionary(dictionary['card'])
        if 'fraudResults' in dictionary:
            if not isinstance(dictionary['fraudResults'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['fraudResults']))
            value = CardFraudResults()
            self.fraud_results = value.from_dictionary(dictionary['fraudResults'])
        if 'initialSchemeTransactionId' in dictionary:
            self.initial_scheme_transaction_id = dictionary['initialSchemeTransactionId']
        if 'networkTokenData' in dictionary:
            if not isinstance(dictionary['networkTokenData'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['networkTokenData']))
            value = NetworkTokenData()
            self.network_token_data = value.from_dictionary(dictionary['networkTokenData'])
        if 'networkTokenUsed' in dictionary:
            self.network_token_used = dictionary['networkTokenUsed']
        if 'paymentAccountReference' in dictionary:
            self.payment_account_reference = dictionary['paymentAccountReference']
        if 'schemeTransactionId' in dictionary:
            self.scheme_transaction_id = dictionary['schemeTransactionId']
        if 'threeDSecureResults' in dictionary:
            if not isinstance(dictionary['threeDSecureResults'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['threeDSecureResults']))
            value = ThreeDSecureResults()
            self.three_d_secure_results = value.from_dictionary(dictionary['threeDSecureResults'])
        if 'token' in dictionary:
            self.token = dictionary['token']
        return self
