# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import List, Optional

from worldline.connect.sdk.domain.data_object import DataObject
from worldline.connect.sdk.v1.domain.refund_result import RefundResult


class FindRefundsResponse(DataObject):

    __limit: Optional[int] = None
    __offset: Optional[int] = None
    __refunds: Optional[List[RefundResult]] = None
    __total_count: Optional[int] = None

    @property
    def limit(self) -> Optional[int]:
        """
        | The limit you used in the request.

        Type: int
        """
        return self.__limit

    @limit.setter
    def limit(self, value: Optional[int]) -> None:
        self.__limit = value

    @property
    def offset(self) -> Optional[int]:
        """
        | The offset you used in the request.

        Type: int
        """
        return self.__offset

    @offset.setter
    def offset(self, value: Optional[int]) -> None:
        self.__offset = value

    @property
    def refunds(self) -> Optional[List[RefundResult]]:
        """
        | A list of refunds that matched your filter, starting at the given offset and limited to the given limit.

        Type: list[:class:`worldline.connect.sdk.v1.domain.refund_result.RefundResult`]
        """
        return self.__refunds

    @refunds.setter
    def refunds(self, value: Optional[List[RefundResult]]) -> None:
        self.__refunds = value

    @property
    def total_count(self) -> Optional[int]:
        """
        | The total number of refunds that matched your filter.

        Type: int
        """
        return self.__total_count

    @total_count.setter
    def total_count(self, value: Optional[int]) -> None:
        self.__total_count = value

    def to_dictionary(self) -> dict:
        dictionary = super(FindRefundsResponse, self).to_dictionary()
        if self.limit is not None:
            dictionary['limit'] = self.limit
        if self.offset is not None:
            dictionary['offset'] = self.offset
        if self.refunds is not None:
            dictionary['refunds'] = []
            for element in self.refunds:
                if element is not None:
                    dictionary['refunds'].append(element.to_dictionary())
        if self.total_count is not None:
            dictionary['totalCount'] = self.total_count
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'FindRefundsResponse':
        super(FindRefundsResponse, self).from_dictionary(dictionary)
        if 'limit' in dictionary:
            self.limit = dictionary['limit']
        if 'offset' in dictionary:
            self.offset = dictionary['offset']
        if 'refunds' in dictionary:
            if not isinstance(dictionary['refunds'], list):
                raise TypeError('value \'{}\' is not a list'.format(dictionary['refunds']))
            self.refunds = []
            for element in dictionary['refunds']:
                value = RefundResult()
                self.refunds.append(value.from_dictionary(element))
        if 'totalCount' in dictionary:
            self.total_count = dictionary['totalCount']
        return self
