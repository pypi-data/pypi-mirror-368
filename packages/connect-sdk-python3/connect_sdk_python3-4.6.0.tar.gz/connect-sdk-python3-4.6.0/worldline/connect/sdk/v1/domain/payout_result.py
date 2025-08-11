# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.v1.domain.abstract_order_status import AbstractOrderStatus
from worldline.connect.sdk.v1.domain.order_output import OrderOutput
from worldline.connect.sdk.v1.domain.order_status_output import OrderStatusOutput


class PayoutResult(AbstractOrderStatus):

    __payout_output: Optional[OrderOutput] = None
    __status: Optional[str] = None
    __status_output: Optional[OrderStatusOutput] = None

    @property
    def payout_output(self) -> Optional[OrderOutput]:
        """
        | Object containing payout details

        Type: :class:`worldline.connect.sdk.v1.domain.order_output.OrderOutput`
        """
        return self.__payout_output

    @payout_output.setter
    def payout_output(self, value: Optional[OrderOutput]) -> None:
        self.__payout_output = value

    @property
    def status(self) -> Optional[str]:
        """
        | Current high-level status of the payouts in a human-readable form. Possible values are :
        
        * CREATED - The transaction has been created. This is the initial state once a new payout is created.
        * PENDING_APPROVAL - The transaction is awaiting approval from you to proceed with the paying out of the funds
        * REJECTED - The transaction has been rejected
        * PAYOUT_REQUESTED - The transaction is in the queue to be payed out to the customer
        * ACCOUNT_CREDITED - We have successfully credited the customer
        * REJECTED_CREDIT - The credit to the account of the customer was rejected by the bank
        * CANCELLED - You have cancelled the transaction
        * REVERSED - The payout has been reversed and the money is returned to your balance
        
        
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
        | This object has the numeric representation of the current payout status, timestamp of last status change and performable action on the current payout resource.
        | In case of a rejected payout, detailed error information is listed.

        Type: :class:`worldline.connect.sdk.v1.domain.order_status_output.OrderStatusOutput`
        """
        return self.__status_output

    @status_output.setter
    def status_output(self, value: Optional[OrderStatusOutput]) -> None:
        self.__status_output = value

    def to_dictionary(self) -> dict:
        dictionary = super(PayoutResult, self).to_dictionary()
        if self.payout_output is not None:
            dictionary['payoutOutput'] = self.payout_output.to_dictionary()
        if self.status is not None:
            dictionary['status'] = self.status
        if self.status_output is not None:
            dictionary['statusOutput'] = self.status_output.to_dictionary()
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'PayoutResult':
        super(PayoutResult, self).from_dictionary(dictionary)
        if 'payoutOutput' in dictionary:
            if not isinstance(dictionary['payoutOutput'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['payoutOutput']))
            value = OrderOutput()
            self.payout_output = value.from_dictionary(dictionary['payoutOutput'])
        if 'status' in dictionary:
            self.status = dictionary['status']
        if 'statusOutput' in dictionary:
            if not isinstance(dictionary['statusOutput'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['statusOutput']))
            value = OrderStatusOutput()
            self.status_output = value.from_dictionary(dictionary['statusOutput'])
        return self
