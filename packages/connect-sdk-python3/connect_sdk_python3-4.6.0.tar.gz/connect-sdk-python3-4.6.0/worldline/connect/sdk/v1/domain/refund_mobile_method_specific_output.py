# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.v1.domain.refund_method_specific_output import RefundMethodSpecificOutput


class RefundMobileMethodSpecificOutput(RefundMethodSpecificOutput):

    __network: Optional[str] = None

    @property
    def network(self) -> Optional[str]:
        """
        | The network that was used for the refund. The string that represents the network is identical to the strings that the payment product vendors use in their documentation.For instance: "Visa" for Google Pay <https://developer.apple.com/reference/passkit/pkpaymentnetwork>.

        Type: str
        """
        return self.__network

    @network.setter
    def network(self, value: Optional[str]) -> None:
        self.__network = value

    def to_dictionary(self) -> dict:
        dictionary = super(RefundMobileMethodSpecificOutput, self).to_dictionary()
        if self.network is not None:
            dictionary['network'] = self.network
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'RefundMobileMethodSpecificOutput':
        super(RefundMobileMethodSpecificOutput, self).from_dictionary(dictionary)
        if 'network' in dictionary:
            self.network = dictionary['network']
        return self
