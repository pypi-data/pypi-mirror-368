# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from worldline.connect.sdk.v1.domain.mandate_approval import MandateApproval


class ApproveTokenRequest(MandateApproval):

    def to_dictionary(self) -> dict:
        dictionary = super(ApproveTokenRequest, self).to_dictionary()
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'ApproveTokenRequest':
        super(ApproveTokenRequest, self).from_dictionary(dictionary)
        return self
