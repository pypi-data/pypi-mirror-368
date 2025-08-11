# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.domain.data_object import DataObject


class PaymentProduct866SpecificOutput(DataObject):
    """
    | Alipay+ (payment product 866) specific details
    """

    __wallet_used: Optional[str] = None

    @property
    def wallet_used(self) -> Optional[str]:
        """
        | The wallet your customer used when completing the payment with Alipay+.

        Type: str
        """
        return self.__wallet_used

    @wallet_used.setter
    def wallet_used(self, value: Optional[str]) -> None:
        self.__wallet_used = value

    def to_dictionary(self) -> dict:
        dictionary = super(PaymentProduct866SpecificOutput, self).to_dictionary()
        if self.wallet_used is not None:
            dictionary['walletUsed'] = self.wallet_used
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'PaymentProduct866SpecificOutput':
        super(PaymentProduct866SpecificOutput, self).from_dictionary(dictionary)
        if 'walletUsed' in dictionary:
            self.wallet_used = dictionary['walletUsed']
        return self
