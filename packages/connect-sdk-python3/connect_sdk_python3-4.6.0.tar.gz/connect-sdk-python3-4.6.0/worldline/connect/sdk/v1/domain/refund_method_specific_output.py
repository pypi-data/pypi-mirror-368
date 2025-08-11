# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.domain.data_object import DataObject


class RefundMethodSpecificOutput(DataObject):

    __refund_product_id: Optional[int] = None
    __total_amount_paid: Optional[int] = None
    __total_amount_refunded: Optional[int] = None

    @property
    def refund_product_id(self) -> Optional[int]:
        """
        | Refund product identifier
        | Please see refund products <https://apireference.connect.worldline-solutions.com/s2sapi/v1/en_US/python/refundproducts.html> for a full overview of possible values.

        Type: int
        """
        return self.__refund_product_id

    @refund_product_id.setter
    def refund_product_id(self, value: Optional[int]) -> None:
        self.__refund_product_id = value

    @property
    def total_amount_paid(self) -> Optional[int]:
        """
        | Total paid amount (in cents and always with 2 decimals)

        Type: int
        """
        return self.__total_amount_paid

    @total_amount_paid.setter
    def total_amount_paid(self, value: Optional[int]) -> None:
        self.__total_amount_paid = value

    @property
    def total_amount_refunded(self) -> Optional[int]:
        """
        Type: int
        """
        return self.__total_amount_refunded

    @total_amount_refunded.setter
    def total_amount_refunded(self, value: Optional[int]) -> None:
        self.__total_amount_refunded = value

    def to_dictionary(self) -> dict:
        dictionary = super(RefundMethodSpecificOutput, self).to_dictionary()
        if self.refund_product_id is not None:
            dictionary['refundProductId'] = self.refund_product_id
        if self.total_amount_paid is not None:
            dictionary['totalAmountPaid'] = self.total_amount_paid
        if self.total_amount_refunded is not None:
            dictionary['totalAmountRefunded'] = self.total_amount_refunded
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'RefundMethodSpecificOutput':
        super(RefundMethodSpecificOutput, self).from_dictionary(dictionary)
        if 'refundProductId' in dictionary:
            self.refund_product_id = dictionary['refundProductId']
        if 'totalAmountPaid' in dictionary:
            self.total_amount_paid = dictionary['totalAmountPaid']
        if 'totalAmountRefunded' in dictionary:
            self.total_amount_refunded = dictionary['totalAmountRefunded']
        return self
