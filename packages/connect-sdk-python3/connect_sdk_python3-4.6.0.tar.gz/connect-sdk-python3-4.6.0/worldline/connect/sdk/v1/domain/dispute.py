# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.domain.data_object import DataObject
from worldline.connect.sdk.v1.domain.dispute_output import DisputeOutput
from worldline.connect.sdk.v1.domain.dispute_status_output import DisputeStatusOutput


class Dispute(DataObject):

    __dispute_output: Optional[DisputeOutput] = None
    __id: Optional[str] = None
    __payment_id: Optional[str] = None
    __status: Optional[str] = None
    __status_output: Optional[DisputeStatusOutput] = None

    @property
    def dispute_output(self) -> Optional[DisputeOutput]:
        """
        | This property contains the creationDetails and default information regarding a dispute.

        Type: :class:`worldline.connect.sdk.v1.domain.dispute_output.DisputeOutput`
        """
        return self.__dispute_output

    @dispute_output.setter
    def dispute_output(self, value: Optional[DisputeOutput]) -> None:
        self.__dispute_output = value

    @property
    def id(self) -> Optional[str]:
        """
        | Dispute ID for a given merchant.

        Type: str
        """
        return self.__id

    @id.setter
    def id(self, value: Optional[str]) -> None:
        self.__id = value

    @property
    def payment_id(self) -> Optional[str]:
        """
        | The ID of the payment that is being disputed.

        Type: str
        """
        return self.__payment_id

    @payment_id.setter
    def payment_id(self, value: Optional[str]) -> None:
        self.__payment_id = value

    @property
    def status(self) -> Optional[str]:
        """
        | Current dispute status.

        Type: str
        """
        return self.__status

    @status.setter
    def status(self, value: Optional[str]) -> None:
        self.__status = value

    @property
    def status_output(self) -> Optional[DisputeStatusOutput]:
        """
        | This property contains the output for a dispute regarding the status of the dispute.

        Type: :class:`worldline.connect.sdk.v1.domain.dispute_status_output.DisputeStatusOutput`
        """
        return self.__status_output

    @status_output.setter
    def status_output(self, value: Optional[DisputeStatusOutput]) -> None:
        self.__status_output = value

    def to_dictionary(self) -> dict:
        dictionary = super(Dispute, self).to_dictionary()
        if self.dispute_output is not None:
            dictionary['disputeOutput'] = self.dispute_output.to_dictionary()
        if self.id is not None:
            dictionary['id'] = self.id
        if self.payment_id is not None:
            dictionary['paymentId'] = self.payment_id
        if self.status is not None:
            dictionary['status'] = self.status
        if self.status_output is not None:
            dictionary['statusOutput'] = self.status_output.to_dictionary()
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'Dispute':
        super(Dispute, self).from_dictionary(dictionary)
        if 'disputeOutput' in dictionary:
            if not isinstance(dictionary['disputeOutput'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['disputeOutput']))
            value = DisputeOutput()
            self.dispute_output = value.from_dictionary(dictionary['disputeOutput'])
        if 'id' in dictionary:
            self.id = dictionary['id']
        if 'paymentId' in dictionary:
            self.payment_id = dictionary['paymentId']
        if 'status' in dictionary:
            self.status = dictionary['status']
        if 'statusOutput' in dictionary:
            if not isinstance(dictionary['statusOutput'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['statusOutput']))
            value = DisputeStatusOutput()
            self.status_output = value.from_dictionary(dictionary['statusOutput'])
        return self
