# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.domain.data_object import DataObject
from worldline.connect.sdk.v1.domain.fraud_fields import FraudFields
from worldline.connect.sdk.v1.domain.merchant_risk_assessment import MerchantRiskAssessment
from worldline.connect.sdk.v1.domain.order_risk_assessment import OrderRiskAssessment


class RiskAssessment(DataObject):

    __fraud_fields: Optional[FraudFields] = None
    __merchant: Optional[MerchantRiskAssessment] = None
    __order: Optional[OrderRiskAssessment] = None
    __payment_product_id: Optional[int] = None

    @property
    def fraud_fields(self) -> Optional[FraudFields]:
        """
        | Object containing additional data that will be used to assess the risk of fraud

        Type: :class:`worldline.connect.sdk.v1.domain.fraud_fields.FraudFields`
        """
        return self.__fraud_fields

    @fraud_fields.setter
    def fraud_fields(self, value: Optional[FraudFields]) -> None:
        self.__fraud_fields = value

    @property
    def merchant(self) -> Optional[MerchantRiskAssessment]:
        """
        Type: :class:`worldline.connect.sdk.v1.domain.merchant_risk_assessment.MerchantRiskAssessment`
        """
        return self.__merchant

    @merchant.setter
    def merchant(self, value: Optional[MerchantRiskAssessment]) -> None:
        self.__merchant = value

    @property
    def order(self) -> Optional[OrderRiskAssessment]:
        """
        Type: :class:`worldline.connect.sdk.v1.domain.order_risk_assessment.OrderRiskAssessment`
        """
        return self.__order

    @order.setter
    def order(self, value: Optional[OrderRiskAssessment]) -> None:
        self.__order = value

    @property
    def payment_product_id(self) -> Optional[int]:
        """
        | Payment product identifier
        | Please see payment products <https://apireference.connect.worldline-solutions.com/s2sapi/v1/en_US/python/paymentproducts.html> for a full overview of possible values.

        Type: int
        """
        return self.__payment_product_id

    @payment_product_id.setter
    def payment_product_id(self, value: Optional[int]) -> None:
        self.__payment_product_id = value

    def to_dictionary(self) -> dict:
        dictionary = super(RiskAssessment, self).to_dictionary()
        if self.fraud_fields is not None:
            dictionary['fraudFields'] = self.fraud_fields.to_dictionary()
        if self.merchant is not None:
            dictionary['merchant'] = self.merchant.to_dictionary()
        if self.order is not None:
            dictionary['order'] = self.order.to_dictionary()
        if self.payment_product_id is not None:
            dictionary['paymentProductId'] = self.payment_product_id
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'RiskAssessment':
        super(RiskAssessment, self).from_dictionary(dictionary)
        if 'fraudFields' in dictionary:
            if not isinstance(dictionary['fraudFields'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['fraudFields']))
            value = FraudFields()
            self.fraud_fields = value.from_dictionary(dictionary['fraudFields'])
        if 'merchant' in dictionary:
            if not isinstance(dictionary['merchant'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['merchant']))
            value = MerchantRiskAssessment()
            self.merchant = value.from_dictionary(dictionary['merchant'])
        if 'order' in dictionary:
            if not isinstance(dictionary['order'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['order']))
            value = OrderRiskAssessment()
            self.order = value.from_dictionary(dictionary['order'])
        if 'paymentProductId' in dictionary:
            self.payment_product_id = dictionary['paymentProductId']
        return self
