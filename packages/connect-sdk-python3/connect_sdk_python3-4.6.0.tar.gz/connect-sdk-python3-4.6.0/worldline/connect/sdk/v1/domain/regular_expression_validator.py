# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.domain.data_object import DataObject


class RegularExpressionValidator(DataObject):

    __regular_expression: Optional[str] = None

    @property
    def regular_expression(self) -> Optional[str]:
        """
        | Contains the regular expression that the value of the field needs to be validated against

        Type: str
        """
        return self.__regular_expression

    @regular_expression.setter
    def regular_expression(self, value: Optional[str]) -> None:
        self.__regular_expression = value

    def to_dictionary(self) -> dict:
        dictionary = super(RegularExpressionValidator, self).to_dictionary()
        if self.regular_expression is not None:
            dictionary['regularExpression'] = self.regular_expression
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'RegularExpressionValidator':
        super(RegularExpressionValidator, self).from_dictionary(dictionary)
        if 'regularExpression' in dictionary:
            self.regular_expression = dictionary['regularExpression']
        return self
