# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.domain.data_object import DataObject


class GetPrivacyPolicyResponse(DataObject):
    """
    | Output of the retrieval of the privacy policy
    """

    __html_content: Optional[str] = None

    @property
    def html_content(self) -> Optional[str]:
        """
        | HTML content to be displayed to the user

        Type: str
        """
        return self.__html_content

    @html_content.setter
    def html_content(self, value: Optional[str]) -> None:
        self.__html_content = value

    def to_dictionary(self) -> dict:
        dictionary = super(GetPrivacyPolicyResponse, self).to_dictionary()
        if self.html_content is not None:
            dictionary['htmlContent'] = self.html_content
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'GetPrivacyPolicyResponse':
        super(GetPrivacyPolicyResponse, self).from_dictionary(dictionary)
        if 'htmlContent' in dictionary:
            self.html_content = dictionary['htmlContent']
        return self
