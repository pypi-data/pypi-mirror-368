# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.domain.data_object import DataObject
from worldline.connect.sdk.v1.domain.address_personal import AddressPersonal


class Shipping(DataObject):
    """
    | Object containing information regarding shipping / delivery
    """

    __address: Optional[AddressPersonal] = None
    __address_indicator: Optional[str] = None
    __carrier: Optional[str] = None
    __comments: Optional[str] = None
    __email_address: Optional[str] = None
    __first_usage_date: Optional[str] = None
    __instructions: Optional[str] = None
    __is_first_usage: Optional[bool] = None
    __shipped_from_zip: Optional[str] = None
    __tracking_number: Optional[str] = None
    __type: Optional[str] = None

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
    def address_indicator(self) -> Optional[str]:
        """
        | Indicates shipping method chosen for the transaction. Possible values:
        
        * same-as-billing = the shipping address is the same as the billing address
        * another-verified-address-on-file-with-merchant = the address used for shipping is another verified address of the customer that is on file with you
        * different-than-billing = shipping address is different from the billing address
        * ship-to-store = goods are shipped to a store (shipping address = store address)
        * digital-goods = electronic delivery of digital goods
        * travel-and-event-tickets-not-shipped = travel and/or event tickets that are not shipped
        * other = other means of delivery

        Type: str
        """
        return self.__address_indicator

    @address_indicator.setter
    def address_indicator(self, value: Optional[str]) -> None:
        self.__address_indicator = value

    @property
    def carrier(self) -> Optional[str]:
        """
        | Indicates the carrier that will deliver the products.

        Type: str
        """
        return self.__carrier

    @carrier.setter
    def carrier(self, value: Optional[str]) -> None:
        self.__carrier = value

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
    def email_address(self) -> Optional[str]:
        """
        | Email address linked to the shipping

        Type: str
        """
        return self.__email_address

    @email_address.setter
    def email_address(self, value: Optional[str]) -> None:
        self.__email_address = value

    @property
    def first_usage_date(self) -> Optional[str]:
        """
        | Date (YYYYMMDD) when the shipping details for this transaction were first used.

        Type: str
        """
        return self.__first_usage_date

    @first_usage_date.setter
    def first_usage_date(self, value: Optional[str]) -> None:
        self.__first_usage_date = value

    @property
    def instructions(self) -> Optional[str]:
        """
        | The delivery instructions or preferences for the shipment. The instructions that informed the delivery carrier about handling requirements, delivery methods, and any special considerations to ensure successful delivery. Possible values:
        |  
        * signature-required = A signature is required upon delivery.
        * identification-required = Recipient needs to provide identification.
        * contactless-delivery = Delivery should be contactless.
        * leave-at-door = Leave the package at the recipient's door.
        * leave-at-curb = Leave the package at the curbside.
        * leave-with-neighbor = Leave the package with a neighbor.
        * express = Expedite the delivery process.
        * tracked = The delivery is tracked with real-time updates.
        * untracked = The delivery is untracked, with no real-time updates.

        Type: str
        """
        return self.__instructions

    @instructions.setter
    def instructions(self, value: Optional[str]) -> None:
        self.__instructions = value

    @property
    def is_first_usage(self) -> Optional[bool]:
        """
        | Indicator if this shipping address is used for the first time to ship an order
        
        | true = the shipping details are used for the first time with this transaction
        
        | false = the shipping details have been used for other transactions in the past

        Type: bool
        """
        return self.__is_first_usage

    @is_first_usage.setter
    def is_first_usage(self, value: Optional[bool]) -> None:
        self.__is_first_usage = value

    @property
    def shipped_from_zip(self) -> Optional[str]:
        """
        | The zip/postal code of the location from which the goods were shipped.

        Type: str
        """
        return self.__shipped_from_zip

    @shipped_from_zip.setter
    def shipped_from_zip(self, value: Optional[str]) -> None:
        self.__shipped_from_zip = value

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

    @property
    def type(self) -> Optional[str]:
        """
        | Indicates the merchandise delivery timeframe. Possible values:
        
        * electronic = For electronic delivery (services or digital goods)
        * same-day = For same day deliveries
        * overnight = For overnight deliveries
        * 2-day-or-more = For two day or more delivery time for payments that are processed by the GlobalCollect platform
        * 2-day-or-more = For two day or more delivery time for payments that are processed by the Ogone platform
        * priority = For prioritized deliveries for payments that are processed by the WL Online Payment Acceptance platform
        * ground = For deliveries via ground for payments that are processed by the WL Online Payment Acceptance platform
        * to-store = For deliveries to a store for payments that are processed by the WL Online Payment Acceptance platform

        Type: str
        """
        return self.__type

    @type.setter
    def type(self, value: Optional[str]) -> None:
        self.__type = value

    def to_dictionary(self) -> dict:
        dictionary = super(Shipping, self).to_dictionary()
        if self.address is not None:
            dictionary['address'] = self.address.to_dictionary()
        if self.address_indicator is not None:
            dictionary['addressIndicator'] = self.address_indicator
        if self.carrier is not None:
            dictionary['carrier'] = self.carrier
        if self.comments is not None:
            dictionary['comments'] = self.comments
        if self.email_address is not None:
            dictionary['emailAddress'] = self.email_address
        if self.first_usage_date is not None:
            dictionary['firstUsageDate'] = self.first_usage_date
        if self.instructions is not None:
            dictionary['instructions'] = self.instructions
        if self.is_first_usage is not None:
            dictionary['isFirstUsage'] = self.is_first_usage
        if self.shipped_from_zip is not None:
            dictionary['shippedFromZip'] = self.shipped_from_zip
        if self.tracking_number is not None:
            dictionary['trackingNumber'] = self.tracking_number
        if self.type is not None:
            dictionary['type'] = self.type
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'Shipping':
        super(Shipping, self).from_dictionary(dictionary)
        if 'address' in dictionary:
            if not isinstance(dictionary['address'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['address']))
            value = AddressPersonal()
            self.address = value.from_dictionary(dictionary['address'])
        if 'addressIndicator' in dictionary:
            self.address_indicator = dictionary['addressIndicator']
        if 'carrier' in dictionary:
            self.carrier = dictionary['carrier']
        if 'comments' in dictionary:
            self.comments = dictionary['comments']
        if 'emailAddress' in dictionary:
            self.email_address = dictionary['emailAddress']
        if 'firstUsageDate' in dictionary:
            self.first_usage_date = dictionary['firstUsageDate']
        if 'instructions' in dictionary:
            self.instructions = dictionary['instructions']
        if 'isFirstUsage' in dictionary:
            self.is_first_usage = dictionary['isFirstUsage']
        if 'shippedFromZip' in dictionary:
            self.shipped_from_zip = dictionary['shippedFromZip']
        if 'trackingNumber' in dictionary:
            self.tracking_number = dictionary['trackingNumber']
        if 'type' in dictionary:
            self.type = dictionary['type']
        return self
