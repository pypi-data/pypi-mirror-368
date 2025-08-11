# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.domain.data_object import DataObject


class ExemptionOutput(DataObject):
    """
    | Object containing exemption output
    """

    __exemption_raised: Optional[str] = None
    __exemption_rejection_reason: Optional[str] = None
    __exemption_request: Optional[str] = None

    @property
    def exemption_raised(self) -> Optional[str]:
        """
        | Type of strong customer authentication (SCA) exemption that was raised towards the acquirer for this transaction.

        Type: str
        """
        return self.__exemption_raised

    @exemption_raised.setter
    def exemption_raised(self, value: Optional[str]) -> None:
        self.__exemption_raised = value

    @property
    def exemption_rejection_reason(self) -> Optional[str]:
        """
        | The request exemption could not be granted. The reason why is returned in this property.

        Type: str
        """
        return self.__exemption_rejection_reason

    @exemption_rejection_reason.setter
    def exemption_rejection_reason(self, value: Optional[str]) -> None:
        self.__exemption_rejection_reason = value

    @property
    def exemption_request(self) -> Optional[str]:
        """
        | Type of strong customer authentication (SCA) exemption requested by you for this transaction.

        Type: str
        """
        return self.__exemption_request

    @exemption_request.setter
    def exemption_request(self, value: Optional[str]) -> None:
        self.__exemption_request = value

    def to_dictionary(self) -> dict:
        dictionary = super(ExemptionOutput, self).to_dictionary()
        if self.exemption_raised is not None:
            dictionary['exemptionRaised'] = self.exemption_raised
        if self.exemption_rejection_reason is not None:
            dictionary['exemptionRejectionReason'] = self.exemption_rejection_reason
        if self.exemption_request is not None:
            dictionary['exemptionRequest'] = self.exemption_request
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'ExemptionOutput':
        super(ExemptionOutput, self).from_dictionary(dictionary)
        if 'exemptionRaised' in dictionary:
            self.exemption_raised = dictionary['exemptionRaised']
        if 'exemptionRejectionReason' in dictionary:
            self.exemption_rejection_reason = dictionary['exemptionRejectionReason']
        if 'exemptionRequest' in dictionary:
            self.exemption_request = dictionary['exemptionRequest']
        return self
