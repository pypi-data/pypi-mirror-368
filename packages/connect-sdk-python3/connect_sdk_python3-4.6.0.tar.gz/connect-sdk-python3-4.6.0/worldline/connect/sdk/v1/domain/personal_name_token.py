# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from worldline.connect.sdk.v1.domain.personal_name_base import PersonalNameBase


class PersonalNameToken(PersonalNameBase):

    def to_dictionary(self) -> dict:
        dictionary = super(PersonalNameToken, self).to_dictionary()
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'PersonalNameToken':
        super(PersonalNameToken, self).from_dictionary(dictionary)
        return self
