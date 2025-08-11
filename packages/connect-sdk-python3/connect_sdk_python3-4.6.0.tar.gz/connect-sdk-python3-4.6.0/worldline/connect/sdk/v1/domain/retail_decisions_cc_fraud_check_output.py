# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.domain.data_object import DataObject


class RetailDecisionsCCFraudCheckOutput(DataObject):

    __fraud_code: Optional[str] = None
    __fraud_neural: Optional[str] = None
    __fraud_rcf: Optional[str] = None

    @property
    def fraud_code(self) -> Optional[str]:
        """
        | Provides additional information about the fraud result

        Type: str
        """
        return self.__fraud_code

    @fraud_code.setter
    def fraud_code(self, value: Optional[str]) -> None:
        self.__fraud_code = value

    @property
    def fraud_neural(self) -> Optional[str]:
        """
        | The raw score returned by the Neural check returned by the evaluation of the transaction

        Type: str
        """
        return self.__fraud_neural

    @fraud_neural.setter
    def fraud_neural(self, value: Optional[str]) -> None:
        self.__fraud_neural = value

    @property
    def fraud_rcf(self) -> Optional[str]:
        """
        | List of RuleCategoryFlags as setup in the Retail Decisions system that lead to the result

        Type: str
        """
        return self.__fraud_rcf

    @fraud_rcf.setter
    def fraud_rcf(self, value: Optional[str]) -> None:
        self.__fraud_rcf = value

    def to_dictionary(self) -> dict:
        dictionary = super(RetailDecisionsCCFraudCheckOutput, self).to_dictionary()
        if self.fraud_code is not None:
            dictionary['fraudCode'] = self.fraud_code
        if self.fraud_neural is not None:
            dictionary['fraudNeural'] = self.fraud_neural
        if self.fraud_rcf is not None:
            dictionary['fraudRCF'] = self.fraud_rcf
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'RetailDecisionsCCFraudCheckOutput':
        super(RetailDecisionsCCFraudCheckOutput, self).from_dictionary(dictionary)
        if 'fraudCode' in dictionary:
            self.fraud_code = dictionary['fraudCode']
        if 'fraudNeural' in dictionary:
            self.fraud_neural = dictionary['fraudNeural']
        if 'fraudRCF' in dictionary:
            self.fraud_rcf = dictionary['fraudRCF']
        return self
