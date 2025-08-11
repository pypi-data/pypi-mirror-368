# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from worldline.connect.sdk.v1.domain.dispute import Dispute


class DisputeResponse(Dispute):

    def to_dictionary(self) -> dict:
        dictionary = super(DisputeResponse, self).to_dictionary()
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'DisputeResponse':
        super(DisputeResponse, self).from_dictionary(dictionary)
        return self
