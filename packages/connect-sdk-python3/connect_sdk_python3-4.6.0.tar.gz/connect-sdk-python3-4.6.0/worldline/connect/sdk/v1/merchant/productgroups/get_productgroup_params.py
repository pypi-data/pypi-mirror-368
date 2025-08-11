# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import List, Optional

from worldline.connect.sdk.communication.param_request import ParamRequest
from worldline.connect.sdk.communication.request_param import RequestParam


class GetProductgroupParams(ParamRequest):
    """
    Query parameters for Get payment product group

    See also https://apireference.connect.worldline-solutions.com/s2sapi/v1/en_US/python/productgroups/get.html
    """

    __country_code: Optional[str] = None
    __currency_code: Optional[str] = None
    __locale: Optional[str] = None
    __amount: Optional[int] = None
    __is_recurring: Optional[bool] = None
    __is_installments: Optional[bool] = None
    __hide: Optional[List[str]] = None

    @property
    def country_code(self) -> Optional[str]:
        """
        | ISO 3166-1 alpha-2 country code of the transaction

        Type: str
        """
        return self.__country_code

    @country_code.setter
    def country_code(self, value: Optional[str]) -> None:
        self.__country_code = value

    @property
    def currency_code(self) -> Optional[str]:
        """
        | Three-letter ISO currency code representing the currency for the amount

        Type: str
        """
        return self.__currency_code

    @currency_code.setter
    def currency_code(self, value: Optional[str]) -> None:
        self.__currency_code = value

    @property
    def locale(self) -> Optional[str]:
        """
        | Locale used in the GUI towards the consumer. Please make sure that a language pack is configured for the locale you are submitting. If you submit a locale that is not setup on your account we will use the default language pack for your account. You can easily upload additional language packs and set the default language pack in the Configuration Center.

        Type: str
        """
        return self.__locale

    @locale.setter
    def locale(self, value: Optional[str]) -> None:
        self.__locale = value

    @property
    def amount(self) -> Optional[int]:
        """
        | Amount  of the transaction in cents and always having 2 decimals.

        Type: int
        """
        return self.__amount

    @amount.setter
    def amount(self, value: Optional[int]) -> None:
        self.__amount = value

    @property
    def is_recurring(self) -> Optional[bool]:
        """
        | Toggles filtering on support for recurring payments. Default value is false.
        
        * true - filter out groups that do not support recurring payments, where a group supports recurring payments if it has at least one payment product that supports recurring.
        * false - do not filter

        Type: bool
        """
        return self.__is_recurring

    @is_recurring.setter
    def is_recurring(self, value: Optional[bool]) -> None:
        self.__is_recurring = value

    @property
    def is_installments(self) -> Optional[bool]:
        """
        | This allows you to filter payment products based on their support for installments or not
        
        * true
        * false
        
        | If this is omitted all payment products are returned.

        Type: bool
        """
        return self.__is_installments

    @is_installments.setter
    def is_installments(self, value: Optional[bool]) -> None:
        self.__is_installments = value

    @property
    def hide(self) -> Optional[List[str]]:
        """
        | Allows you to hide elements from the response, reducing the amount of data that needs to be returned to your client. Possible options are:
        
        * fields - Don't return any data on fields of the payment product
        * accountsOnFile - Don't return any accounts on file data
        * translations - Don't return any label texts associated with the payment products

        Type: list[str]
        """
        return self.__hide

    @hide.setter
    def hide(self, value: Optional[List[str]]) -> None:
        self.__hide = value

    def add_hide(self, value: str) -> None:
        """
        :param value: str
        """
        if self.hide is None:
            self.hide = []
        self.hide.append(value)

    def to_request_parameters(self) -> List[RequestParam]:
        """
        :return: list[RequestParam]
        """
        result = []
        if self.country_code is not None:
            result.append(RequestParam("countryCode", self.country_code))
        if self.currency_code is not None:
            result.append(RequestParam("currencyCode", self.currency_code))
        if self.locale is not None:
            result.append(RequestParam("locale", self.locale))
        if self.amount is not None:
            result.append(RequestParam("amount", str(self.amount)))
        if self.is_recurring is not None:
            result.append(RequestParam("isRecurring", str(self.is_recurring)))
        if self.is_installments is not None:
            result.append(RequestParam("isInstallments", str(self.is_installments)))
        if self.hide is not None:
            for hide_element in self.hide:
                if hide_element is not None:
                    result.append(RequestParam("hide", hide_element))
        return result
