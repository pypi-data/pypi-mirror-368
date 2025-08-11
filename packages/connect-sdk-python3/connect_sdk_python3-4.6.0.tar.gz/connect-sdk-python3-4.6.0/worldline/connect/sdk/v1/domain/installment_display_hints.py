# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.domain.data_object import DataObject


class InstallmentDisplayHints(DataObject):
    """
    | Object containing information for the client on how best to display this options
    """

    __display_order: Optional[int] = None
    __label: Optional[str] = None
    __logo: Optional[str] = None

    @property
    def display_order(self) -> Optional[int]:
        """
        | Determines the order in which the installment options should be shown (sorted ascending). In countries like Turkey there are multiple loyalty programs that offer installments

        Type: int
        """
        return self.__display_order

    @display_order.setter
    def display_order(self, value: Optional[int]) -> None:
        self.__display_order = value

    @property
    def label(self) -> Optional[str]:
        """
        | Name of the installment option

        Type: str
        """
        return self.__label

    @label.setter
    def label(self, value: Optional[str]) -> None:
        self.__label = value

    @property
    def logo(self) -> Optional[str]:
        """
        | Partial URL that you can reference for the image of this installment provider. You can use our server-side resize functionality by appending '?size={{width}}x{{height}}' to the full URL, where width and height are specified in pixels. The resized image will always keep its correct aspect ratio.

        Type: str
        """
        return self.__logo

    @logo.setter
    def logo(self, value: Optional[str]) -> None:
        self.__logo = value

    def to_dictionary(self) -> dict:
        dictionary = super(InstallmentDisplayHints, self).to_dictionary()
        if self.display_order is not None:
            dictionary['displayOrder'] = self.display_order
        if self.label is not None:
            dictionary['label'] = self.label
        if self.logo is not None:
            dictionary['logo'] = self.logo
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'InstallmentDisplayHints':
        super(InstallmentDisplayHints, self).from_dictionary(dictionary)
        if 'displayOrder' in dictionary:
            self.display_order = dictionary['displayOrder']
        if 'label' in dictionary:
            self.label = dictionary['label']
        if 'logo' in dictionary:
            self.logo = dictionary['logo']
        return self
