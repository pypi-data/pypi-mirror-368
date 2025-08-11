# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.domain.data_object import DataObject


class PaymentProductFieldTooltip(DataObject):

    __image: Optional[str] = None
    __label: Optional[str] = None

    @property
    def image(self) -> Optional[str]:
        """
        | Relative URL that can be used to retrieve an image for the tooltip image. You can use our server-side resize functionality by appending '?size={{width}}x{{height}}' to the full URL, where width and height are specified in pixels. The resized image will always keep its correct aspect ratio.

        Type: str
        """
        return self.__image

    @image.setter
    def image(self, value: Optional[str]) -> None:
        self.__image = value

    @property
    def label(self) -> Optional[str]:
        """
        | A text explaining the field in more detail. This is meant to be used for displaying to the customer.

        Type: str
        """
        return self.__label

    @label.setter
    def label(self, value: Optional[str]) -> None:
        self.__label = value

    def to_dictionary(self) -> dict:
        dictionary = super(PaymentProductFieldTooltip, self).to_dictionary()
        if self.image is not None:
            dictionary['image'] = self.image
        if self.label is not None:
            dictionary['label'] = self.label
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'PaymentProductFieldTooltip':
        super(PaymentProductFieldTooltip, self).from_dictionary(dictionary)
        if 'image' in dictionary:
            self.image = dictionary['image']
        if 'label' in dictionary:
            self.label = dictionary['label']
        return self
