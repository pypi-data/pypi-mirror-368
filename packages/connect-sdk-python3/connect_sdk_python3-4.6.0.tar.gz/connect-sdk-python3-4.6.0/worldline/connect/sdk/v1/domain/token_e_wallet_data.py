# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.domain.data_object import DataObject


class TokenEWalletData(DataObject):

    __billing_agreement_id: Optional[str] = None

    @property
    def billing_agreement_id(self) -> Optional[str]:
        """
        | Identification of the PayPal recurring billing agreement

        Type: str
        """
        return self.__billing_agreement_id

    @billing_agreement_id.setter
    def billing_agreement_id(self, value: Optional[str]) -> None:
        self.__billing_agreement_id = value

    def to_dictionary(self) -> dict:
        dictionary = super(TokenEWalletData, self).to_dictionary()
        if self.billing_agreement_id is not None:
            dictionary['billingAgreementId'] = self.billing_agreement_id
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'TokenEWalletData':
        super(TokenEWalletData, self).from_dictionary(dictionary)
        if 'billingAgreementId' in dictionary:
            self.billing_agreement_id = dictionary['billingAgreementId']
        return self
