# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.domain.data_object import DataObject


class Frequency(DataObject):
    """
    | The object containing the frequency and interval between recurring payments.
    """

    __interval: Optional[str] = None
    __interval_frequency: Optional[int] = None

    @property
    def interval(self) -> Optional[str]:
        """
        | The interval between recurring payments specified as days, weeks, quarters, or years.

        Type: str
        """
        return self.__interval

    @interval.setter
    def interval(self, value: Optional[str]) -> None:
        self.__interval = value

    @property
    def interval_frequency(self) -> Optional[int]:
        """
        | The number of days, weeks, months, quarters, or years between recurring payments.

        Type: int
        """
        return self.__interval_frequency

    @interval_frequency.setter
    def interval_frequency(self, value: Optional[int]) -> None:
        self.__interval_frequency = value

    def to_dictionary(self) -> dict:
        dictionary = super(Frequency, self).to_dictionary()
        if self.interval is not None:
            dictionary['interval'] = self.interval
        if self.interval_frequency is not None:
            dictionary['intervalFrequency'] = self.interval_frequency
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'Frequency':
        super(Frequency, self).from_dictionary(dictionary)
        if 'interval' in dictionary:
            self.interval = dictionary['interval']
        if 'intervalFrequency' in dictionary:
            self.interval_frequency = dictionary['intervalFrequency']
        return self
