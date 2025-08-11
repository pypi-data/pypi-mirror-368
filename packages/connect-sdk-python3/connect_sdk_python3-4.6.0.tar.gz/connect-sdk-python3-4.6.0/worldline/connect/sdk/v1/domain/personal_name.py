# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.v1.domain.personal_name_base import PersonalNameBase


class PersonalName(PersonalNameBase):

    __title: Optional[str] = None

    @property
    def title(self) -> Optional[str]:
        """
        | Title of customer

        Type: str
        """
        return self.__title

    @title.setter
    def title(self, value: Optional[str]) -> None:
        self.__title = value

    def to_dictionary(self) -> dict:
        dictionary = super(PersonalName, self).to_dictionary()
        if self.title is not None:
            dictionary['title'] = self.title
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'PersonalName':
        super(PersonalName, self).from_dictionary(dictionary)
        if 'title' in dictionary:
            self.title = dictionary['title']
        return self
