# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.domain.data_object import DataObject
from worldline.connect.sdk.v1.domain.card_without_cvv import CardWithoutCvv


class CompletePaymentCardPaymentMethodSpecificInput(DataObject):

    __card: Optional[CardWithoutCvv] = None

    @property
    def card(self) -> Optional[CardWithoutCvv]:
        """
        | Object containing card details

        Type: :class:`worldline.connect.sdk.v1.domain.card_without_cvv.CardWithoutCvv`
        """
        return self.__card

    @card.setter
    def card(self, value: Optional[CardWithoutCvv]) -> None:
        self.__card = value

    def to_dictionary(self) -> dict:
        dictionary = super(CompletePaymentCardPaymentMethodSpecificInput, self).to_dictionary()
        if self.card is not None:
            dictionary['card'] = self.card.to_dictionary()
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'CompletePaymentCardPaymentMethodSpecificInput':
        super(CompletePaymentCardPaymentMethodSpecificInput, self).from_dictionary(dictionary)
        if 'card' in dictionary:
            if not isinstance(dictionary['card'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['card']))
            value = CardWithoutCvv()
            self.card = value.from_dictionary(dictionary['card'])
        return self
