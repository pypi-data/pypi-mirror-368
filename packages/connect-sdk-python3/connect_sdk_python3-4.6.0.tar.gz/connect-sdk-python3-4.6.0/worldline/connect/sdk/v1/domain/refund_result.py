# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.v1.domain.abstract_order_status import AbstractOrderStatus
from worldline.connect.sdk.v1.domain.order_status_output import OrderStatusOutput
from worldline.connect.sdk.v1.domain.refund_output import RefundOutput


class RefundResult(AbstractOrderStatus):

    __refund_output: Optional[RefundOutput] = None
    __status: Optional[str] = None
    __status_output: Optional[OrderStatusOutput] = None

    @property
    def refund_output(self) -> Optional[RefundOutput]:
        """
        | Object containing refund details

        Type: :class:`worldline.connect.sdk.v1.domain.refund_output.RefundOutput`
        """
        return self.__refund_output

    @refund_output.setter
    def refund_output(self, value: Optional[RefundOutput]) -> None:
        self.__refund_output = value

    @property
    def status(self) -> Optional[str]:
        """
        | Current high-level status of the refund in a human-readable form. Possible values are:
        
        * CREATED - The transaction has been created. This is the initial state once a new refund is created.
        * PENDING_APPROVAL - The transaction is awaiting approval from you to proceed with the processing of the refund
        * REJECTED - The refund has been rejected
        * REFUND_REQUESTED - The transaction is in the queue to be refunded
        * REFUNDED - We have successfully refunded the customer
        * REJECTED_CAPTURE - The refund was rejected by the bank or us during processing
        * CANCELLED - You have cancelled the transaction
        
        
        | Please see Statuses <https://apireference.connect.worldline-solutions.com/s2sapi/v1/en_US/python/statuses.html> for a full overview of possible values.

        Type: str
        """
        return self.__status

    @status.setter
    def status(self, value: Optional[str]) -> None:
        self.__status = value

    @property
    def status_output(self) -> Optional[OrderStatusOutput]:
        """
        | This object has the numeric representation of the current refund status, timestamp of last status change and performable action on the current refund resource.
        | In case of a rejected refund, detailed error information is listed.

        Type: :class:`worldline.connect.sdk.v1.domain.order_status_output.OrderStatusOutput`
        """
        return self.__status_output

    @status_output.setter
    def status_output(self, value: Optional[OrderStatusOutput]) -> None:
        self.__status_output = value

    def to_dictionary(self) -> dict:
        dictionary = super(RefundResult, self).to_dictionary()
        if self.refund_output is not None:
            dictionary['refundOutput'] = self.refund_output.to_dictionary()
        if self.status is not None:
            dictionary['status'] = self.status
        if self.status_output is not None:
            dictionary['statusOutput'] = self.status_output.to_dictionary()
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'RefundResult':
        super(RefundResult, self).from_dictionary(dictionary)
        if 'refundOutput' in dictionary:
            if not isinstance(dictionary['refundOutput'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['refundOutput']))
            value = RefundOutput()
            self.refund_output = value.from_dictionary(dictionary['refundOutput'])
        if 'status' in dictionary:
            self.status = dictionary['status']
        if 'statusOutput' in dictionary:
            if not isinstance(dictionary['statusOutput'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['statusOutput']))
            value = OrderStatusOutput()
            self.status_output = value.from_dictionary(dictionary['statusOutput'])
        return self
