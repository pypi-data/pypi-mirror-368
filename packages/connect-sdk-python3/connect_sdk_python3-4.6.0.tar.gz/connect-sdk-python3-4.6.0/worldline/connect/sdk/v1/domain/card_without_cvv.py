# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.v1.domain.card_essentials import CardEssentials


class CardWithoutCvv(CardEssentials):

    __issue_number: Optional[str] = None

    @property
    def issue_number(self) -> Optional[str]:
        """
        | Issue number on the card (if applicable)

        Type: str
        """
        return self.__issue_number

    @issue_number.setter
    def issue_number(self, value: Optional[str]) -> None:
        self.__issue_number = value

    def to_dictionary(self) -> dict:
        dictionary = super(CardWithoutCvv, self).to_dictionary()
        if self.issue_number is not None:
            dictionary['issueNumber'] = self.issue_number
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'CardWithoutCvv':
        super(CardWithoutCvv, self).from_dictionary(dictionary)
        if 'issueNumber' in dictionary:
            self.issue_number = dictionary['issueNumber']
        return self
