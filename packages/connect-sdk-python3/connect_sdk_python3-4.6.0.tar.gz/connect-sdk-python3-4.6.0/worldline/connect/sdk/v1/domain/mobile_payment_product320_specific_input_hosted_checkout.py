# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.domain.data_object import DataObject
from worldline.connect.sdk.v1.domain.g_pay_three_d_secure import GPayThreeDSecure


class MobilePaymentProduct320SpecificInputHostedCheckout(DataObject):

    __merchant_name: Optional[str] = None
    __merchant_origin: Optional[str] = None
    __three_d_secure: Optional[GPayThreeDSecure] = None

    @property
    def merchant_name(self) -> Optional[str]:
        """
        | Used as an input for the Google Pay payment sheet. Provide your company name in a human readable form.

        Type: str
        """
        return self.__merchant_name

    @merchant_name.setter
    def merchant_name(self, value: Optional[str]) -> None:
        self.__merchant_name = value

    @property
    def merchant_origin(self) -> Optional[str]:
        """
        | Used as an input for the Google Pay payment sheet. Provide the url of your webshop. For international (non-ASCII) domains, please use Punycode <https://en.wikipedia.org/wiki/Punycode>.

        Type: str
        """
        return self.__merchant_origin

    @merchant_origin.setter
    def merchant_origin(self, value: Optional[str]) -> None:
        self.__merchant_origin = value

    @property
    def three_d_secure(self) -> Optional[GPayThreeDSecure]:
        """
        | Object containing specific data regarding 3-D Secure

        Type: :class:`worldline.connect.sdk.v1.domain.g_pay_three_d_secure.GPayThreeDSecure`
        """
        return self.__three_d_secure

    @three_d_secure.setter
    def three_d_secure(self, value: Optional[GPayThreeDSecure]) -> None:
        self.__three_d_secure = value

    def to_dictionary(self) -> dict:
        dictionary = super(MobilePaymentProduct320SpecificInputHostedCheckout, self).to_dictionary()
        if self.merchant_name is not None:
            dictionary['merchantName'] = self.merchant_name
        if self.merchant_origin is not None:
            dictionary['merchantOrigin'] = self.merchant_origin
        if self.three_d_secure is not None:
            dictionary['threeDSecure'] = self.three_d_secure.to_dictionary()
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'MobilePaymentProduct320SpecificInputHostedCheckout':
        super(MobilePaymentProduct320SpecificInputHostedCheckout, self).from_dictionary(dictionary)
        if 'merchantName' in dictionary:
            self.merchant_name = dictionary['merchantName']
        if 'merchantOrigin' in dictionary:
            self.merchant_origin = dictionary['merchantOrigin']
        if 'threeDSecure' in dictionary:
            if not isinstance(dictionary['threeDSecure'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['threeDSecure']))
            value = GPayThreeDSecure()
            self.three_d_secure = value.from_dictionary(dictionary['threeDSecure'])
        return self
