# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.domain.data_object import DataObject
from worldline.connect.sdk.v1.domain.address_personal import AddressPersonal


class ShippingRiskAssessment(DataObject):
    """
    | Object containing information regarding shipping / delivery
    """

    __address: Optional[AddressPersonal] = None
    __comments: Optional[str] = None
    __tracking_number: Optional[str] = None

    @property
    def address(self) -> Optional[AddressPersonal]:
        """
        | Object containing address information

        Type: :class:`worldline.connect.sdk.v1.domain.address_personal.AddressPersonal`
        """
        return self.__address

    @address.setter
    def address(self, value: Optional[AddressPersonal]) -> None:
        self.__address = value

    @property
    def comments(self) -> Optional[str]:
        """
        | Comments included during shipping

        Type: str
        """
        return self.__comments

    @comments.setter
    def comments(self, value: Optional[str]) -> None:
        self.__comments = value

    @property
    def tracking_number(self) -> Optional[str]:
        """
        | Shipment tracking number

        Type: str
        """
        return self.__tracking_number

    @tracking_number.setter
    def tracking_number(self, value: Optional[str]) -> None:
        self.__tracking_number = value

    def to_dictionary(self) -> dict:
        dictionary = super(ShippingRiskAssessment, self).to_dictionary()
        if self.address is not None:
            dictionary['address'] = self.address.to_dictionary()
        if self.comments is not None:
            dictionary['comments'] = self.comments
        if self.tracking_number is not None:
            dictionary['trackingNumber'] = self.tracking_number
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'ShippingRiskAssessment':
        super(ShippingRiskAssessment, self).from_dictionary(dictionary)
        if 'address' in dictionary:
            if not isinstance(dictionary['address'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['address']))
            value = AddressPersonal()
            self.address = value.from_dictionary(dictionary['address'])
        if 'comments' in dictionary:
            self.comments = dictionary['comments']
        if 'trackingNumber' in dictionary:
            self.tracking_number = dictionary['trackingNumber']
        return self
