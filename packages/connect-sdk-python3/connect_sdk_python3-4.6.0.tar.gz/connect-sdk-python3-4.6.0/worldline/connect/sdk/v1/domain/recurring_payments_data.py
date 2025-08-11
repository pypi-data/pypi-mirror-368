# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.domain.data_object import DataObject
from worldline.connect.sdk.v1.domain.frequency import Frequency
from worldline.connect.sdk.v1.domain.trial_information import TrialInformation


class RecurringPaymentsData(DataObject):
    """
    | The object containing reference data for the text that can be displayed on MyCheckout hosted payment page with subscription information.
    
    | Note:
    
    | The data in this object is only meant for displaying recurring payments-related data on your checkout page.
    | You still need to submit all the recurring payment-related data in the corresponding payment product-specific input. (example: cardPaymentMethodSpecificInput.recurring and cardPaymentMethodSpecificInput.isRecurring)
    """

    __recurring_interval: Optional[Frequency] = None
    __trial_information: Optional[TrialInformation] = None

    @property
    def recurring_interval(self) -> Optional[Frequency]:
        """
        | The object containing the frequency and interval between recurring payments.

        Type: :class:`worldline.connect.sdk.v1.domain.frequency.Frequency`
        """
        return self.__recurring_interval

    @recurring_interval.setter
    def recurring_interval(self, value: Optional[Frequency]) -> None:
        self.__recurring_interval = value

    @property
    def trial_information(self) -> Optional[TrialInformation]:
        """
        | The object containing data of the trial period: no-cost or discounted time-constrained trial subscription period. 

        Type: :class:`worldline.connect.sdk.v1.domain.trial_information.TrialInformation`
        """
        return self.__trial_information

    @trial_information.setter
    def trial_information(self, value: Optional[TrialInformation]) -> None:
        self.__trial_information = value

    def to_dictionary(self) -> dict:
        dictionary = super(RecurringPaymentsData, self).to_dictionary()
        if self.recurring_interval is not None:
            dictionary['recurringInterval'] = self.recurring_interval.to_dictionary()
        if self.trial_information is not None:
            dictionary['trialInformation'] = self.trial_information.to_dictionary()
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'RecurringPaymentsData':
        super(RecurringPaymentsData, self).from_dictionary(dictionary)
        if 'recurringInterval' in dictionary:
            if not isinstance(dictionary['recurringInterval'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['recurringInterval']))
            value = Frequency()
            self.recurring_interval = value.from_dictionary(dictionary['recurringInterval'])
        if 'trialInformation' in dictionary:
            if not isinstance(dictionary['trialInformation'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['trialInformation']))
            value = TrialInformation()
            self.trial_information = value.from_dictionary(dictionary['trialInformation'])
        return self
