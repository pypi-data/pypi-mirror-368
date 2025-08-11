# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.v1.domain.card import Card
from worldline.connect.sdk.v1.domain.risk_assessment import RiskAssessment


class RiskAssessmentCard(RiskAssessment):

    __card: Optional[Card] = None

    @property
    def card(self) -> Optional[Card]:
        """
        | Object containing Card object

        Type: :class:`worldline.connect.sdk.v1.domain.card.Card`
        """
        return self.__card

    @card.setter
    def card(self, value: Optional[Card]) -> None:
        self.__card = value

    def to_dictionary(self) -> dict:
        dictionary = super(RiskAssessmentCard, self).to_dictionary()
        if self.card is not None:
            dictionary['card'] = self.card.to_dictionary()
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'RiskAssessmentCard':
        super(RiskAssessmentCard, self).from_dictionary(dictionary)
        if 'card' in dictionary:
            if not isinstance(dictionary['card'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['card']))
            value = Card()
            self.card = value.from_dictionary(dictionary['card'])
        return self
