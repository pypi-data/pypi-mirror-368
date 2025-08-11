# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from worldline.connect.sdk.v1.domain.abstract_three_d_secure import AbstractThreeDSecure


class ThreeDSecureBase(AbstractThreeDSecure):
    """
    | Object containing specific data regarding 3-D Secure
    """

    def to_dictionary(self) -> dict:
        dictionary = super(ThreeDSecureBase, self).to_dictionary()
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'ThreeDSecureBase':
        super(ThreeDSecureBase, self).from_dictionary(dictionary)
        return self
