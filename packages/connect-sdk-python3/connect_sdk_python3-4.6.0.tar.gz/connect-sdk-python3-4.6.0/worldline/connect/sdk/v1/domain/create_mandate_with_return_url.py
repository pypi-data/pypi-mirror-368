# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.v1.domain.create_mandate_base import CreateMandateBase


class CreateMandateWithReturnUrl(CreateMandateBase):

    __return_url: Optional[str] = None

    @property
    def return_url(self) -> Optional[str]:
        """
        | Return URL to use if the mandate signing requires redirection.
        | Note: The provided URL should be absolute and contain the https:// protocol. IP addresses are not supported, neither localhost. For use on mobile devices a custom protocol can be used in the form of *protocol*://. This protocol must be registered on the device first.
        | URLs without a protocol will be rejected.

        Type: str
        """
        return self.__return_url

    @return_url.setter
    def return_url(self, value: Optional[str]) -> None:
        self.__return_url = value

    def to_dictionary(self) -> dict:
        dictionary = super(CreateMandateWithReturnUrl, self).to_dictionary()
        if self.return_url is not None:
            dictionary['returnUrl'] = self.return_url
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'CreateMandateWithReturnUrl':
        super(CreateMandateWithReturnUrl, self).from_dictionary(dictionary)
        if 'returnUrl' in dictionary:
            self.return_url = dictionary['returnUrl']
        return self
