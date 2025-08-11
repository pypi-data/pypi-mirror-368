# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.domain.data_object import DataObject


class DecryptedPaymentData(DataObject):

    __auth_method: Optional[str] = None
    __cardholder_name: Optional[str] = None
    __cryptogram: Optional[str] = None
    __dpan: Optional[str] = None
    __eci: Optional[int] = None
    __expiry_date: Optional[str] = None
    __pan: Optional[str] = None
    __payment_method: Optional[str] = None

    @property
    def auth_method(self) -> Optional[str]:
        """
        | The type of payment credential which the customer used.
        
        * For Google Pay, maps to the paymentMethodDetails.authMethod property in the encrypted payment data.
        
        | .

        Type: str

        Deprecated; Use decryptedPaymentData.paymentMethod instead
        """
        return self.__auth_method

    @auth_method.setter
    def auth_method(self, value: Optional[str]) -> None:
        self.__auth_method = value

    @property
    def cardholder_name(self) -> Optional[str]:
        """
        | The card holder's name on the card. Minimum length of 2, maximum length of 51 characters.
        
        * For Apple Pay, maps to the cardholderName property in the encrypted payment data.
        * For Google Pay this is not available in the encrypted payment data, and can be omitted.

        Type: str
        """
        return self.__cardholder_name

    @cardholder_name.setter
    def cardholder_name(self, value: Optional[str]) -> None:
        self.__cardholder_name = value

    @property
    def cryptogram(self) -> Optional[str]:
        """
        | The 3D secure online payment cryptogram.
        
        * For Apple Pay, maps to the paymentData.onlinePaymentCryptogram property in the encrypted payment data.
        * For Google Pay, maps to the paymentMethodDetails.cryptogram property in the encrypted payment data.
        
        | Not allowed for Google Pay if the authMethod in the response of Google is PAN_ONLY.

        Type: str
        """
        return self.__cryptogram

    @cryptogram.setter
    def cryptogram(self, value: Optional[str]) -> None:
        self.__cryptogram = value

    @property
    def dpan(self) -> Optional[str]:
        """
        | The device specific PAN.
        
        * For Apple Pay, maps to the applicationPrimaryAccountNumber property in the encrypted payment data.
        * For Google Pay, maps to the paymentMethodDetails.dpan property in the encrypted payment data.
        
        | Not allowed for Google Pay if the authMethod in the response of Google is PAN_ONLY.

        Type: str
        """
        return self.__dpan

    @dpan.setter
    def dpan(self, value: Optional[str]) -> None:
        self.__dpan = value

    @property
    def eci(self) -> Optional[int]:
        """
        | The eci is Electronic Commerce Indicator.
        
        * For Apple Pay, maps to the paymentData.eciIndicator property in the encrypted payment data.
        * For Google Pay, maps to the paymentMethodDetails.eciIndicator property in the encrypted payment data.

        Type: int
        """
        return self.__eci

    @eci.setter
    def eci(self, value: Optional[int]) -> None:
        self.__eci = value

    @property
    def expiry_date(self) -> Optional[str]:
        """
        | Expiry date of the card
        | Format: MMYY.
        
        * For Apple Pay, maps to the applicationExpirationDate property in the encrypted payment data. This property is formatted as YYMMDD, so this needs to be converted to get a correctly formatted expiry date.
        * For Google Pay, maps to the paymentMethodDetails.expirationMonth and paymentMethodDetails.expirationYear properties in the encrypted payment data. These need to be combined to get a correctly formatted expiry date.

        Type: str
        """
        return self.__expiry_date

    @expiry_date.setter
    def expiry_date(self, value: Optional[str]) -> None:
        self.__expiry_date = value

    @property
    def pan(self) -> Optional[str]:
        """
        | The non-device specific complete credit/debit card number (also know as the PAN).
        
        * For Apple Pay this is not available in the encrypted payment data, and must be omitted.
        * For Google Pay, maps to the paymentMethodDetails.pan property in the encrypted payment data.
        
        | Not allowed for Google Pay if the authMethod in the response of Google is CRYPTOGRAM_3DS.

        Type: str
        """
        return self.__pan

    @pan.setter
    def pan(self, value: Optional[str]) -> None:
        self.__pan = value

    @property
    def payment_method(self) -> Optional[str]:
        """
        * In case Google provides in the response as authMethod: CRYPTOGRAM_3DS send in as value of this property TOKENIZED_CARD.
        * In case Google provides in the response as authMethod: PAN_ONLY send in as value of this property CARD.
        
        | For Apple Pay this is not available in the encrypted payment data, and must be omitted.

        Type: str
        """
        return self.__payment_method

    @payment_method.setter
    def payment_method(self, value: Optional[str]) -> None:
        self.__payment_method = value

    def to_dictionary(self) -> dict:
        dictionary = super(DecryptedPaymentData, self).to_dictionary()
        if self.auth_method is not None:
            dictionary['authMethod'] = self.auth_method
        if self.cardholder_name is not None:
            dictionary['cardholderName'] = self.cardholder_name
        if self.cryptogram is not None:
            dictionary['cryptogram'] = self.cryptogram
        if self.dpan is not None:
            dictionary['dpan'] = self.dpan
        if self.eci is not None:
            dictionary['eci'] = self.eci
        if self.expiry_date is not None:
            dictionary['expiryDate'] = self.expiry_date
        if self.pan is not None:
            dictionary['pan'] = self.pan
        if self.payment_method is not None:
            dictionary['paymentMethod'] = self.payment_method
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'DecryptedPaymentData':
        super(DecryptedPaymentData, self).from_dictionary(dictionary)
        if 'authMethod' in dictionary:
            self.auth_method = dictionary['authMethod']
        if 'cardholderName' in dictionary:
            self.cardholder_name = dictionary['cardholderName']
        if 'cryptogram' in dictionary:
            self.cryptogram = dictionary['cryptogram']
        if 'dpan' in dictionary:
            self.dpan = dictionary['dpan']
        if 'eci' in dictionary:
            self.eci = dictionary['eci']
        if 'expiryDate' in dictionary:
            self.expiry_date = dictionary['expiryDate']
        if 'pan' in dictionary:
            self.pan = dictionary['pan']
        if 'paymentMethod' in dictionary:
            self.payment_method = dictionary['paymentMethod']
        return self
