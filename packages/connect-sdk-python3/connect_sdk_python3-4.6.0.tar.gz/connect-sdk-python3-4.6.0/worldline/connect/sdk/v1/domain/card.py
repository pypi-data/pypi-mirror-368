# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.v1.domain.card_without_cvv import CardWithoutCvv


class Card(CardWithoutCvv):

    __cvv: Optional[str] = None
    __partial_pin: Optional[str] = None

    @property
    def cvv(self) -> Optional[str]:
        """
        | Card Verification Value, a 3 or 4 digit code used as an additional security feature for card not present transactions.

        Type: str
        """
        return self.__cvv

    @cvv.setter
    def cvv(self, value: Optional[str]) -> None:
        self.__cvv = value

    @property
    def partial_pin(self) -> Optional[str]:
        """
        | The first 2 digits of the card's PIN code. May be optionally submitted for the following payment products:
        
        * BC Card (paymentProductId 180)
        * Hana Card (paymentProductId 181)
        * Hyundai Card (paymentProductId 182)
        * KB Card (paymentProductId 183)
        * Lotte Card (paymentProductId 184)
        * NH Card (paymentProductId 185)
        * Samsung Card (paymentProductId 186)
        * Shinhan Card (paymentProductId 187)
        
        | Submitting this property may improve your authorization rate.

        Type: str
        """
        return self.__partial_pin

    @partial_pin.setter
    def partial_pin(self, value: Optional[str]) -> None:
        self.__partial_pin = value

    def to_dictionary(self) -> dict:
        dictionary = super(Card, self).to_dictionary()
        if self.cvv is not None:
            dictionary['cvv'] = self.cvv
        if self.partial_pin is not None:
            dictionary['partialPin'] = self.partial_pin
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'Card':
        super(Card, self).from_dictionary(dictionary)
        if 'cvv' in dictionary:
            self.cvv = dictionary['cvv']
        if 'partialPin' in dictionary:
            self.partial_pin = dictionary['partialPin']
        return self
