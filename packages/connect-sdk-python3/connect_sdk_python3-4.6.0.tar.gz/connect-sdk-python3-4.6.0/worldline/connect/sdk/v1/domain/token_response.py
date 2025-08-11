# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.domain.data_object import DataObject
from worldline.connect.sdk.v1.domain.token_card import TokenCard
from worldline.connect.sdk.v1.domain.token_e_wallet import TokenEWallet
from worldline.connect.sdk.v1.domain.token_non_sepa_direct_debit import TokenNonSepaDirectDebit
from worldline.connect.sdk.v1.domain.token_sepa_direct_debit import TokenSepaDirectDebit


class TokenResponse(DataObject):

    __card: Optional[TokenCard] = None
    __e_wallet: Optional[TokenEWallet] = None
    __id: Optional[str] = None
    __non_sepa_direct_debit: Optional[TokenNonSepaDirectDebit] = None
    __original_payment_id: Optional[str] = None
    __payment_product_id: Optional[int] = None
    __sepa_direct_debit: Optional[TokenSepaDirectDebit] = None

    @property
    def card(self) -> Optional[TokenCard]:
        """
        | Object containing card details

        Type: :class:`worldline.connect.sdk.v1.domain.token_card.TokenCard`
        """
        return self.__card

    @card.setter
    def card(self, value: Optional[TokenCard]) -> None:
        self.__card = value

    @property
    def e_wallet(self) -> Optional[TokenEWallet]:
        """
        | Object containing eWallet details

        Type: :class:`worldline.connect.sdk.v1.domain.token_e_wallet.TokenEWallet`
        """
        return self.__e_wallet

    @e_wallet.setter
    def e_wallet(self, value: Optional[TokenEWallet]) -> None:
        self.__e_wallet = value

    @property
    def id(self) -> Optional[str]:
        """
        | ID of the token

        Type: str
        """
        return self.__id

    @id.setter
    def id(self, value: Optional[str]) -> None:
        self.__id = value

    @property
    def non_sepa_direct_debit(self) -> Optional[TokenNonSepaDirectDebit]:
        """
        | Object containing the non SEPA Direct Debit details

        Type: :class:`worldline.connect.sdk.v1.domain.token_non_sepa_direct_debit.TokenNonSepaDirectDebit`
        """
        return self.__non_sepa_direct_debit

    @non_sepa_direct_debit.setter
    def non_sepa_direct_debit(self, value: Optional[TokenNonSepaDirectDebit]) -> None:
        self.__non_sepa_direct_debit = value

    @property
    def original_payment_id(self) -> Optional[str]:
        """
        | The initial Payment ID of the transaction from which the token has been created

        Type: str
        """
        return self.__original_payment_id

    @original_payment_id.setter
    def original_payment_id(self, value: Optional[str]) -> None:
        self.__original_payment_id = value

    @property
    def payment_product_id(self) -> Optional[int]:
        """
        | Payment product identifier
        | Please see payment products <https://apireference.connect.worldline-solutions.com/s2sapi/v1/en_US/python/paymentproducts.html> for a full overview of possible values.

        Type: int
        """
        return self.__payment_product_id

    @payment_product_id.setter
    def payment_product_id(self, value: Optional[int]) -> None:
        self.__payment_product_id = value

    @property
    def sepa_direct_debit(self) -> Optional[TokenSepaDirectDebit]:
        """
        | Object containing the SEPA Direct Debit details

        Type: :class:`worldline.connect.sdk.v1.domain.token_sepa_direct_debit.TokenSepaDirectDebit`
        """
        return self.__sepa_direct_debit

    @sepa_direct_debit.setter
    def sepa_direct_debit(self, value: Optional[TokenSepaDirectDebit]) -> None:
        self.__sepa_direct_debit = value

    def to_dictionary(self) -> dict:
        dictionary = super(TokenResponse, self).to_dictionary()
        if self.card is not None:
            dictionary['card'] = self.card.to_dictionary()
        if self.e_wallet is not None:
            dictionary['eWallet'] = self.e_wallet.to_dictionary()
        if self.id is not None:
            dictionary['id'] = self.id
        if self.non_sepa_direct_debit is not None:
            dictionary['nonSepaDirectDebit'] = self.non_sepa_direct_debit.to_dictionary()
        if self.original_payment_id is not None:
            dictionary['originalPaymentId'] = self.original_payment_id
        if self.payment_product_id is not None:
            dictionary['paymentProductId'] = self.payment_product_id
        if self.sepa_direct_debit is not None:
            dictionary['sepaDirectDebit'] = self.sepa_direct_debit.to_dictionary()
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'TokenResponse':
        super(TokenResponse, self).from_dictionary(dictionary)
        if 'card' in dictionary:
            if not isinstance(dictionary['card'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['card']))
            value = TokenCard()
            self.card = value.from_dictionary(dictionary['card'])
        if 'eWallet' in dictionary:
            if not isinstance(dictionary['eWallet'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['eWallet']))
            value = TokenEWallet()
            self.e_wallet = value.from_dictionary(dictionary['eWallet'])
        if 'id' in dictionary:
            self.id = dictionary['id']
        if 'nonSepaDirectDebit' in dictionary:
            if not isinstance(dictionary['nonSepaDirectDebit'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['nonSepaDirectDebit']))
            value = TokenNonSepaDirectDebit()
            self.non_sepa_direct_debit = value.from_dictionary(dictionary['nonSepaDirectDebit'])
        if 'originalPaymentId' in dictionary:
            self.original_payment_id = dictionary['originalPaymentId']
        if 'paymentProductId' in dictionary:
            self.payment_product_id = dictionary['paymentProductId']
        if 'sepaDirectDebit' in dictionary:
            if not isinstance(dictionary['sepaDirectDebit'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['sepaDirectDebit']))
            value = TokenSepaDirectDebit()
            self.sepa_direct_debit = value.from_dictionary(dictionary['sepaDirectDebit'])
        return self
