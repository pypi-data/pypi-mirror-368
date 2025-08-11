# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import List, Optional

from worldline.connect.sdk.domain.data_object import DataObject
from worldline.connect.sdk.v1.domain.lodging_charge import LodgingCharge
from worldline.connect.sdk.v1.domain.lodging_room import LodgingRoom


class LodgingData(DataObject):
    """
    | Object that holds lodging specific data
    """

    __charges: Optional[List[LodgingCharge]] = None
    __check_in_date: Optional[str] = None
    __check_out_date: Optional[str] = None
    __folio_number: Optional[str] = None
    __is_confirmed_reservation: Optional[bool] = None
    __is_facility_fire_safety_conform: Optional[bool] = None
    __is_no_show: Optional[bool] = None
    __is_preference_smoking_room: Optional[bool] = None
    __number_of_adults: Optional[int] = None
    __number_of_nights: Optional[int] = None
    __number_of_rooms: Optional[int] = None
    __program_code: Optional[str] = None
    __property_customer_service_phone_number: Optional[str] = None
    __property_phone_number: Optional[str] = None
    __renter_name: Optional[str] = None
    __rooms: Optional[List[LodgingRoom]] = None

    @property
    def charges(self) -> Optional[List[LodgingCharge]]:
        """
        | Object that holds lodging related charges

        Type: list[:class:`worldline.connect.sdk.v1.domain.lodging_charge.LodgingCharge`]
        """
        return self.__charges

    @charges.setter
    def charges(self, value: Optional[List[LodgingCharge]]) -> None:
        self.__charges = value

    @property
    def check_in_date(self) -> Optional[str]:
        """
        | The date the guest checks into (or plans to check in to) the facility. 
        | Format: YYYYMMDD

        Type: str
        """
        return self.__check_in_date

    @check_in_date.setter
    def check_in_date(self, value: Optional[str]) -> None:
        self.__check_in_date = value

    @property
    def check_out_date(self) -> Optional[str]:
        """
        | The date the guest checks out of (or plans to check out of) the facility. 
        | Format: YYYYMMDD

        Type: str
        """
        return self.__check_out_date

    @check_out_date.setter
    def check_out_date(self, value: Optional[str]) -> None:
        self.__check_out_date = value

    @property
    def folio_number(self) -> Optional[str]:
        """
        | The Lodging Folio Number assigned to the itemized statement of charges and credits associated with this lodging stay, which can be any combination of characters and numerals defined by the Merchant or authorized Third Party Processor.

        Type: str
        """
        return self.__folio_number

    @folio_number.setter
    def folio_number(self, value: Optional[str]) -> None:
        self.__folio_number = value

    @property
    def is_confirmed_reservation(self) -> Optional[bool]:
        """
        | Indicates whether the room reservation is confirmed.
        
        * true - The room reservation is confirmed
        * false - The room reservation is not confirmed

        Type: bool
        """
        return self.__is_confirmed_reservation

    @is_confirmed_reservation.setter
    def is_confirmed_reservation(self, value: Optional[bool]) -> None:
        self.__is_confirmed_reservation = value

    @property
    def is_facility_fire_safety_conform(self) -> Optional[bool]:
        """
        | Defines whether or not the facility conforms to the requirements of the Hotel and Motel Fire Safety Act of 1990, or similar legislation.
        
        * true - The facility conform to the requirements
        * false - The facility doesn't conform to the requirements

        Type: bool
        """
        return self.__is_facility_fire_safety_conform

    @is_facility_fire_safety_conform.setter
    def is_facility_fire_safety_conform(self, value: Optional[bool]) -> None:
        self.__is_facility_fire_safety_conform = value

    @property
    def is_no_show(self) -> Optional[bool]:
        """
        | Indicate if this the customer is a no show case. In such case, the lodging property can charge a no show fee.
        
        * true - The customer is a no show
        * false - Not applicable

        Type: bool
        """
        return self.__is_no_show

    @is_no_show.setter
    def is_no_show(self, value: Optional[bool]) -> None:
        self.__is_no_show = value

    @property
    def is_preference_smoking_room(self) -> Optional[bool]:
        """
        | Indicated the preference of the customer for a smoking or non-smoking room.
        
        * true - A smoking room is preferred
        * false - A non-smoking room is preferred

        Type: bool
        """
        return self.__is_preference_smoking_room

    @is_preference_smoking_room.setter
    def is_preference_smoking_room(self, value: Optional[bool]) -> None:
        self.__is_preference_smoking_room = value

    @property
    def number_of_adults(self) -> Optional[int]:
        """
        | The total number of adult guests staying (or planning to stay) at the facility (i.e., all booked rooms)

        Type: int
        """
        return self.__number_of_adults

    @number_of_adults.setter
    def number_of_adults(self, value: Optional[int]) -> None:
        self.__number_of_adults = value

    @property
    def number_of_nights(self) -> Optional[int]:
        """
        | The number of nights for the lodging stay

        Type: int
        """
        return self.__number_of_nights

    @number_of_nights.setter
    def number_of_nights(self, value: Optional[int]) -> None:
        self.__number_of_nights = value

    @property
    def number_of_rooms(self) -> Optional[int]:
        """
        | The number of rooms rented for the lodging stay

        Type: int
        """
        return self.__number_of_rooms

    @number_of_rooms.setter
    def number_of_rooms(self, value: Optional[int]) -> None:
        self.__number_of_rooms = value

    @property
    def program_code(self) -> Optional[str]:
        """
        | Code that corresponds to the category of lodging charges detailed in this message.Allowed values:
        
        * lodging - (Default) Submitted charges are for lodging
        * noShow - Submitted charges are for the failure of the guest(s) to check in for reserved a room
        * advancedDeposit - Submitted charges are for an Advanced Deposit to reserve one or more rooms
        
        | If no value is submitted the default value lodging is used.

        Type: str
        """
        return self.__program_code

    @program_code.setter
    def program_code(self, value: Optional[str]) -> None:
        self.__program_code = value

    @property
    def property_customer_service_phone_number(self) -> Optional[str]:
        """
        | The international customer service phone number of the facility

        Type: str
        """
        return self.__property_customer_service_phone_number

    @property_customer_service_phone_number.setter
    def property_customer_service_phone_number(self, value: Optional[str]) -> None:
        self.__property_customer_service_phone_number = value

    @property
    def property_phone_number(self) -> Optional[str]:
        """
        | The local phone number of the facility in an international phone number format

        Type: str
        """
        return self.__property_phone_number

    @property_phone_number.setter
    def property_phone_number(self, value: Optional[str]) -> None:
        self.__property_phone_number = value

    @property
    def renter_name(self) -> Optional[str]:
        """
        | Name of the person or business entity charged for the reservation and/or lodging stay

        Type: str
        """
        return self.__renter_name

    @renter_name.setter
    def renter_name(self, value: Optional[str]) -> None:
        self.__renter_name = value

    @property
    def rooms(self) -> Optional[List[LodgingRoom]]:
        """
        | Object that holds lodging related room data

        Type: list[:class:`worldline.connect.sdk.v1.domain.lodging_room.LodgingRoom`]
        """
        return self.__rooms

    @rooms.setter
    def rooms(self, value: Optional[List[LodgingRoom]]) -> None:
        self.__rooms = value

    def to_dictionary(self) -> dict:
        dictionary = super(LodgingData, self).to_dictionary()
        if self.charges is not None:
            dictionary['charges'] = []
            for element in self.charges:
                if element is not None:
                    dictionary['charges'].append(element.to_dictionary())
        if self.check_in_date is not None:
            dictionary['checkInDate'] = self.check_in_date
        if self.check_out_date is not None:
            dictionary['checkOutDate'] = self.check_out_date
        if self.folio_number is not None:
            dictionary['folioNumber'] = self.folio_number
        if self.is_confirmed_reservation is not None:
            dictionary['isConfirmedReservation'] = self.is_confirmed_reservation
        if self.is_facility_fire_safety_conform is not None:
            dictionary['isFacilityFireSafetyConform'] = self.is_facility_fire_safety_conform
        if self.is_no_show is not None:
            dictionary['isNoShow'] = self.is_no_show
        if self.is_preference_smoking_room is not None:
            dictionary['isPreferenceSmokingRoom'] = self.is_preference_smoking_room
        if self.number_of_adults is not None:
            dictionary['numberOfAdults'] = self.number_of_adults
        if self.number_of_nights is not None:
            dictionary['numberOfNights'] = self.number_of_nights
        if self.number_of_rooms is not None:
            dictionary['numberOfRooms'] = self.number_of_rooms
        if self.program_code is not None:
            dictionary['programCode'] = self.program_code
        if self.property_customer_service_phone_number is not None:
            dictionary['propertyCustomerServicePhoneNumber'] = self.property_customer_service_phone_number
        if self.property_phone_number is not None:
            dictionary['propertyPhoneNumber'] = self.property_phone_number
        if self.renter_name is not None:
            dictionary['renterName'] = self.renter_name
        if self.rooms is not None:
            dictionary['rooms'] = []
            for element in self.rooms:
                if element is not None:
                    dictionary['rooms'].append(element.to_dictionary())
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'LodgingData':
        super(LodgingData, self).from_dictionary(dictionary)
        if 'charges' in dictionary:
            if not isinstance(dictionary['charges'], list):
                raise TypeError('value \'{}\' is not a list'.format(dictionary['charges']))
            self.charges = []
            for element in dictionary['charges']:
                value = LodgingCharge()
                self.charges.append(value.from_dictionary(element))
        if 'checkInDate' in dictionary:
            self.check_in_date = dictionary['checkInDate']
        if 'checkOutDate' in dictionary:
            self.check_out_date = dictionary['checkOutDate']
        if 'folioNumber' in dictionary:
            self.folio_number = dictionary['folioNumber']
        if 'isConfirmedReservation' in dictionary:
            self.is_confirmed_reservation = dictionary['isConfirmedReservation']
        if 'isFacilityFireSafetyConform' in dictionary:
            self.is_facility_fire_safety_conform = dictionary['isFacilityFireSafetyConform']
        if 'isNoShow' in dictionary:
            self.is_no_show = dictionary['isNoShow']
        if 'isPreferenceSmokingRoom' in dictionary:
            self.is_preference_smoking_room = dictionary['isPreferenceSmokingRoom']
        if 'numberOfAdults' in dictionary:
            self.number_of_adults = dictionary['numberOfAdults']
        if 'numberOfNights' in dictionary:
            self.number_of_nights = dictionary['numberOfNights']
        if 'numberOfRooms' in dictionary:
            self.number_of_rooms = dictionary['numberOfRooms']
        if 'programCode' in dictionary:
            self.program_code = dictionary['programCode']
        if 'propertyCustomerServicePhoneNumber' in dictionary:
            self.property_customer_service_phone_number = dictionary['propertyCustomerServicePhoneNumber']
        if 'propertyPhoneNumber' in dictionary:
            self.property_phone_number = dictionary['propertyPhoneNumber']
        if 'renterName' in dictionary:
            self.renter_name = dictionary['renterName']
        if 'rooms' in dictionary:
            if not isinstance(dictionary['rooms'], list):
                raise TypeError('value \'{}\' is not a list'.format(dictionary['rooms']))
            self.rooms = []
            for element in dictionary['rooms']:
                value = LodgingRoom()
                self.rooms.append(value.from_dictionary(element))
        return self
