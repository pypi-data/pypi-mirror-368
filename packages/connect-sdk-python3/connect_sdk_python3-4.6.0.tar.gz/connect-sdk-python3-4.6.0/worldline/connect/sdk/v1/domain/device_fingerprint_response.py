# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.domain.data_object import DataObject


class DeviceFingerprintResponse(DataObject):

    __device_fingerprint_transaction_id: Optional[str] = None
    __html: Optional[str] = None

    @property
    def device_fingerprint_transaction_id(self) -> Optional[str]:
        """
        | Contains the unique id which is used by the device fingerprint collector script. This must be used to set the property fraudFields.deviceFingerprintTransactionId in either in the CreatePayment.order.customer.device.deviceFingerprintTransactionId, the CreateRiskAssessmentCards.order.customer.device.deviceFingerprintTransactionId or the CreateRiskAssessmentBankaccounts.order.customer.device.deviceFingerprintTransactionId.

        Type: str
        """
        return self.__device_fingerprint_transaction_id

    @device_fingerprint_transaction_id.setter
    def device_fingerprint_transaction_id(self, value: Optional[str]) -> None:
        self.__device_fingerprint_transaction_id = value

    @property
    def html(self) -> Optional[str]:
        """
        | Contains the ready-to-use device fingerprint collector script. You have to inject it into your page and call it when the customer presses the final payment submit button. For Cybersource, the script must be added to the body of the page.
        | You should only call it once per payment request.

        Type: str
        """
        return self.__html

    @html.setter
    def html(self, value: Optional[str]) -> None:
        self.__html = value

    def to_dictionary(self) -> dict:
        dictionary = super(DeviceFingerprintResponse, self).to_dictionary()
        if self.device_fingerprint_transaction_id is not None:
            dictionary['deviceFingerprintTransactionId'] = self.device_fingerprint_transaction_id
        if self.html is not None:
            dictionary['html'] = self.html
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'DeviceFingerprintResponse':
        super(DeviceFingerprintResponse, self).from_dictionary(dictionary)
        if 'deviceFingerprintTransactionId' in dictionary:
            self.device_fingerprint_transaction_id = dictionary['deviceFingerprintTransactionId']
        if 'html' in dictionary:
            self.html = dictionary['html']
        return self
