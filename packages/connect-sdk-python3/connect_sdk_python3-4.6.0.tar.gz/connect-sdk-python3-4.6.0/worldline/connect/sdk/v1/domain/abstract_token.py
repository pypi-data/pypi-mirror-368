# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.domain.data_object import DataObject


class AbstractToken(DataObject):

    __alias: Optional[str] = None

    @property
    def alias(self) -> Optional[str]:
        """
        | An alias for the token. This can be used to visually represent the token.
        | If no alias is given in Create token calls, a payment product specific default is used, e.g. the obfuscated card number for card payment products.
        | Do not include any unobfuscated sensitive data in the alias.

        Type: str
        """
        return self.__alias

    @alias.setter
    def alias(self, value: Optional[str]) -> None:
        self.__alias = value

    def to_dictionary(self) -> dict:
        dictionary = super(AbstractToken, self).to_dictionary()
        if self.alias is not None:
            dictionary['alias'] = self.alias
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'AbstractToken':
        super(AbstractToken, self).from_dictionary(dictionary)
        if 'alias' in dictionary:
            self.alias = dictionary['alias']
        return self
