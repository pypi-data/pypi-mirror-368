# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.domain.data_object import DataObject
from worldline.connect.sdk.v1.domain.amount_of_money import AmountOfMoney
from worldline.connect.sdk.v1.domain.sdk_data_input import SdkDataInput
from worldline.connect.sdk.v1.domain.three_d_secure_data import ThreeDSecureData


class AbstractThreeDSecure(DataObject):

    __authentication_amount: Optional[AmountOfMoney] = None
    __authentication_flow: Optional[str] = None
    __challenge_canvas_size: Optional[str] = None
    __challenge_indicator: Optional[str] = None
    __exemption_request: Optional[str] = None
    __prior_three_d_secure_data: Optional[ThreeDSecureData] = None
    __sdk_data: Optional[SdkDataInput] = None
    __skip_authentication: Optional[bool] = None
    __transaction_risk_level: Optional[str] = None

    @property
    def authentication_amount(self) -> Optional[AmountOfMoney]:
        """
        Type: :class:`worldline.connect.sdk.v1.domain.amount_of_money.AmountOfMoney`
        """
        return self.__authentication_amount

    @authentication_amount.setter
    def authentication_amount(self, value: Optional[AmountOfMoney]) -> None:
        self.__authentication_amount = value

    @property
    def authentication_flow(self) -> Optional[str]:
        """
        Type: str
        """
        return self.__authentication_flow

    @authentication_flow.setter
    def authentication_flow(self, value: Optional[str]) -> None:
        self.__authentication_flow = value

    @property
    def challenge_canvas_size(self) -> Optional[str]:
        """
        Type: str
        """
        return self.__challenge_canvas_size

    @challenge_canvas_size.setter
    def challenge_canvas_size(self, value: Optional[str]) -> None:
        self.__challenge_canvas_size = value

    @property
    def challenge_indicator(self) -> Optional[str]:
        """
        Type: str
        """
        return self.__challenge_indicator

    @challenge_indicator.setter
    def challenge_indicator(self, value: Optional[str]) -> None:
        self.__challenge_indicator = value

    @property
    def exemption_request(self) -> Optional[str]:
        """
        Type: str
        """
        return self.__exemption_request

    @exemption_request.setter
    def exemption_request(self, value: Optional[str]) -> None:
        self.__exemption_request = value

    @property
    def prior_three_d_secure_data(self) -> Optional[ThreeDSecureData]:
        """
        Type: :class:`worldline.connect.sdk.v1.domain.three_d_secure_data.ThreeDSecureData`
        """
        return self.__prior_three_d_secure_data

    @prior_three_d_secure_data.setter
    def prior_three_d_secure_data(self, value: Optional[ThreeDSecureData]) -> None:
        self.__prior_three_d_secure_data = value

    @property
    def sdk_data(self) -> Optional[SdkDataInput]:
        """
        Type: :class:`worldline.connect.sdk.v1.domain.sdk_data_input.SdkDataInput`
        """
        return self.__sdk_data

    @sdk_data.setter
    def sdk_data(self, value: Optional[SdkDataInput]) -> None:
        self.__sdk_data = value

    @property
    def skip_authentication(self) -> Optional[bool]:
        """
        Type: bool
        """
        return self.__skip_authentication

    @skip_authentication.setter
    def skip_authentication(self, value: Optional[bool]) -> None:
        self.__skip_authentication = value

    @property
    def transaction_risk_level(self) -> Optional[str]:
        """
        Type: str
        """
        return self.__transaction_risk_level

    @transaction_risk_level.setter
    def transaction_risk_level(self, value: Optional[str]) -> None:
        self.__transaction_risk_level = value

    def to_dictionary(self) -> dict:
        dictionary = super(AbstractThreeDSecure, self).to_dictionary()
        if self.authentication_amount is not None:
            dictionary['authenticationAmount'] = self.authentication_amount.to_dictionary()
        if self.authentication_flow is not None:
            dictionary['authenticationFlow'] = self.authentication_flow
        if self.challenge_canvas_size is not None:
            dictionary['challengeCanvasSize'] = self.challenge_canvas_size
        if self.challenge_indicator is not None:
            dictionary['challengeIndicator'] = self.challenge_indicator
        if self.exemption_request is not None:
            dictionary['exemptionRequest'] = self.exemption_request
        if self.prior_three_d_secure_data is not None:
            dictionary['priorThreeDSecureData'] = self.prior_three_d_secure_data.to_dictionary()
        if self.sdk_data is not None:
            dictionary['sdkData'] = self.sdk_data.to_dictionary()
        if self.skip_authentication is not None:
            dictionary['skipAuthentication'] = self.skip_authentication
        if self.transaction_risk_level is not None:
            dictionary['transactionRiskLevel'] = self.transaction_risk_level
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'AbstractThreeDSecure':
        super(AbstractThreeDSecure, self).from_dictionary(dictionary)
        if 'authenticationAmount' in dictionary:
            if not isinstance(dictionary['authenticationAmount'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['authenticationAmount']))
            value = AmountOfMoney()
            self.authentication_amount = value.from_dictionary(dictionary['authenticationAmount'])
        if 'authenticationFlow' in dictionary:
            self.authentication_flow = dictionary['authenticationFlow']
        if 'challengeCanvasSize' in dictionary:
            self.challenge_canvas_size = dictionary['challengeCanvasSize']
        if 'challengeIndicator' in dictionary:
            self.challenge_indicator = dictionary['challengeIndicator']
        if 'exemptionRequest' in dictionary:
            self.exemption_request = dictionary['exemptionRequest']
        if 'priorThreeDSecureData' in dictionary:
            if not isinstance(dictionary['priorThreeDSecureData'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['priorThreeDSecureData']))
            value = ThreeDSecureData()
            self.prior_three_d_secure_data = value.from_dictionary(dictionary['priorThreeDSecureData'])
        if 'sdkData' in dictionary:
            if not isinstance(dictionary['sdkData'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['sdkData']))
            value = SdkDataInput()
            self.sdk_data = value.from_dictionary(dictionary['sdkData'])
        if 'skipAuthentication' in dictionary:
            self.skip_authentication = dictionary['skipAuthentication']
        if 'transactionRiskLevel' in dictionary:
            self.transaction_risk_level = dictionary['transactionRiskLevel']
        return self
