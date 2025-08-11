# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import List, Optional

from worldline.connect.sdk.domain.data_object import DataObject
from worldline.connect.sdk.v1.domain.dispute import Dispute


class DisputesResponse(DataObject):

    __disputes: Optional[List[Dispute]] = None

    @property
    def disputes(self) -> Optional[List[Dispute]]:
        """
        | Array containing disputes and their characteristics.

        Type: list[:class:`worldline.connect.sdk.v1.domain.dispute.Dispute`]
        """
        return self.__disputes

    @disputes.setter
    def disputes(self, value: Optional[List[Dispute]]) -> None:
        self.__disputes = value

    def to_dictionary(self) -> dict:
        dictionary = super(DisputesResponse, self).to_dictionary()
        if self.disputes is not None:
            dictionary['disputes'] = []
            for element in self.disputes:
                if element is not None:
                    dictionary['disputes'].append(element.to_dictionary())
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'DisputesResponse':
        super(DisputesResponse, self).from_dictionary(dictionary)
        if 'disputes' in dictionary:
            if not isinstance(dictionary['disputes'], list):
                raise TypeError('value \'{}\' is not a list'.format(dictionary['disputes']))
            self.disputes = []
            for element in dictionary['disputes']:
                value = Dispute()
                self.disputes.append(value.from_dictionary(element))
        return self
