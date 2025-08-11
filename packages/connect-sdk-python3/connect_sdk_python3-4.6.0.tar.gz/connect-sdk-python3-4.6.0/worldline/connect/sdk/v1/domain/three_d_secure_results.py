# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.domain.data_object import DataObject
from worldline.connect.sdk.v1.domain.amount_of_money import AmountOfMoney
from worldline.connect.sdk.v1.domain.exemption_output import ExemptionOutput
from worldline.connect.sdk.v1.domain.sdk_data_output import SdkDataOutput
from worldline.connect.sdk.v1.domain.three_d_secure_data import ThreeDSecureData


class ThreeDSecureResults(DataObject):
    """
    | Object containing the 3-D Secure specific results
    """

    __acs_transaction_id: Optional[str] = None
    __applied_exemption: Optional[str] = None
    __authentication_amount: Optional[AmountOfMoney] = None
    __cavv: Optional[str] = None
    __directory_server_transaction_id: Optional[str] = None
    __eci: Optional[str] = None
    __exemption_output: Optional[ExemptionOutput] = None
    __scheme_risk_score: Optional[int] = None
    __sdk_data: Optional[SdkDataOutput] = None
    __three_d_secure_data: Optional[ThreeDSecureData] = None
    __three_d_secure_version: Optional[str] = None
    __three_d_server_transaction_id: Optional[str] = None
    __xid: Optional[str] = None

    @property
    def acs_transaction_id(self) -> Optional[str]:
        """
        | Identifier of the authenticated transaction at the ACS/Issuer

        Type: str
        """
        return self.__acs_transaction_id

    @acs_transaction_id.setter
    def acs_transaction_id(self, value: Optional[str]) -> None:
        self.__acs_transaction_id = value

    @property
    def applied_exemption(self) -> Optional[str]:
        """
        | Exemption code from Carte Bancaire (130) (unknown possible values so far -free format)

        Type: str
        """
        return self.__applied_exemption

    @applied_exemption.setter
    def applied_exemption(self, value: Optional[str]) -> None:
        self.__applied_exemption = value

    @property
    def authentication_amount(self) -> Optional[AmountOfMoney]:
        """
        | The amount for which this transaction has been authenticated.

        Type: :class:`worldline.connect.sdk.v1.domain.amount_of_money.AmountOfMoney`
        """
        return self.__authentication_amount

    @authentication_amount.setter
    def authentication_amount(self, value: Optional[AmountOfMoney]) -> None:
        self.__authentication_amount = value

    @property
    def cavv(self) -> Optional[str]:
        """
        | CAVV or AVV result indicating authentication validation value

        Type: str
        """
        return self.__cavv

    @cavv.setter
    def cavv(self, value: Optional[str]) -> None:
        self.__cavv = value

    @property
    def directory_server_transaction_id(self) -> Optional[str]:
        """
        | The 3-D Secure Directory Server transaction ID that is used for the 3D Authentication

        Type: str
        """
        return self.__directory_server_transaction_id

    @directory_server_transaction_id.setter
    def directory_server_transaction_id(self, value: Optional[str]) -> None:
        self.__directory_server_transaction_id = value

    @property
    def eci(self) -> Optional[str]:
        """
        | Indicates Authentication validation results returned after AuthenticationValidation

        Type: str
        """
        return self.__eci

    @eci.setter
    def eci(self, value: Optional[str]) -> None:
        self.__eci = value

    @property
    def exemption_output(self) -> Optional[ExemptionOutput]:
        """
        | Object containing exemption output

        Type: :class:`worldline.connect.sdk.v1.domain.exemption_output.ExemptionOutput`
        """
        return self.__exemption_output

    @exemption_output.setter
    def exemption_output(self, value: Optional[ExemptionOutput]) -> None:
        self.__exemption_output = value

    @property
    def scheme_risk_score(self) -> Optional[int]:
        """
        | Global score calculated by the Carte Bancaire (130) Scoring platform. Possible values from 0 to 99

        Type: int
        """
        return self.__scheme_risk_score

    @scheme_risk_score.setter
    def scheme_risk_score(self, value: Optional[int]) -> None:
        self.__scheme_risk_score = value

    @property
    def sdk_data(self) -> Optional[SdkDataOutput]:
        """
        | Object containing 3-D Secure in-app SDK data

        Type: :class:`worldline.connect.sdk.v1.domain.sdk_data_output.SdkDataOutput`
        """
        return self.__sdk_data

    @sdk_data.setter
    def sdk_data(self, value: Optional[SdkDataOutput]) -> None:
        self.__sdk_data = value

    @property
    def three_d_secure_data(self) -> Optional[ThreeDSecureData]:
        """
        | Object containing data regarding the 3-D Secure authentication

        Type: :class:`worldline.connect.sdk.v1.domain.three_d_secure_data.ThreeDSecureData`
        """
        return self.__three_d_secure_data

    @three_d_secure_data.setter
    def three_d_secure_data(self, value: Optional[ThreeDSecureData]) -> None:
        self.__three_d_secure_data = value

    @property
    def three_d_secure_version(self) -> Optional[str]:
        """
        | The 3-D Secure version used for the authentication.
        
        | This property is used in the communication with the acquirer

        Type: str
        """
        return self.__three_d_secure_version

    @three_d_secure_version.setter
    def three_d_secure_version(self, value: Optional[str]) -> None:
        self.__three_d_secure_version = value

    @property
    def three_d_server_transaction_id(self) -> Optional[str]:
        """
        | The 3-D Secure Server transaction ID that is used for the 3-D Secure version 2 Authentication.

        Type: str
        """
        return self.__three_d_server_transaction_id

    @three_d_server_transaction_id.setter
    def three_d_server_transaction_id(self, value: Optional[str]) -> None:
        self.__three_d_server_transaction_id = value

    @property
    def xid(self) -> Optional[str]:
        """
        | Transaction ID for the Authentication

        Type: str
        """
        return self.__xid

    @xid.setter
    def xid(self, value: Optional[str]) -> None:
        self.__xid = value

    def to_dictionary(self) -> dict:
        dictionary = super(ThreeDSecureResults, self).to_dictionary()
        if self.acs_transaction_id is not None:
            dictionary['acsTransactionId'] = self.acs_transaction_id
        if self.applied_exemption is not None:
            dictionary['appliedExemption'] = self.applied_exemption
        if self.authentication_amount is not None:
            dictionary['authenticationAmount'] = self.authentication_amount.to_dictionary()
        if self.cavv is not None:
            dictionary['cavv'] = self.cavv
        if self.directory_server_transaction_id is not None:
            dictionary['directoryServerTransactionId'] = self.directory_server_transaction_id
        if self.eci is not None:
            dictionary['eci'] = self.eci
        if self.exemption_output is not None:
            dictionary['exemptionOutput'] = self.exemption_output.to_dictionary()
        if self.scheme_risk_score is not None:
            dictionary['schemeRiskScore'] = self.scheme_risk_score
        if self.sdk_data is not None:
            dictionary['sdkData'] = self.sdk_data.to_dictionary()
        if self.three_d_secure_data is not None:
            dictionary['threeDSecureData'] = self.three_d_secure_data.to_dictionary()
        if self.three_d_secure_version is not None:
            dictionary['threeDSecureVersion'] = self.three_d_secure_version
        if self.three_d_server_transaction_id is not None:
            dictionary['threeDServerTransactionId'] = self.three_d_server_transaction_id
        if self.xid is not None:
            dictionary['xid'] = self.xid
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'ThreeDSecureResults':
        super(ThreeDSecureResults, self).from_dictionary(dictionary)
        if 'acsTransactionId' in dictionary:
            self.acs_transaction_id = dictionary['acsTransactionId']
        if 'appliedExemption' in dictionary:
            self.applied_exemption = dictionary['appliedExemption']
        if 'authenticationAmount' in dictionary:
            if not isinstance(dictionary['authenticationAmount'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['authenticationAmount']))
            value = AmountOfMoney()
            self.authentication_amount = value.from_dictionary(dictionary['authenticationAmount'])
        if 'cavv' in dictionary:
            self.cavv = dictionary['cavv']
        if 'directoryServerTransactionId' in dictionary:
            self.directory_server_transaction_id = dictionary['directoryServerTransactionId']
        if 'eci' in dictionary:
            self.eci = dictionary['eci']
        if 'exemptionOutput' in dictionary:
            if not isinstance(dictionary['exemptionOutput'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['exemptionOutput']))
            value = ExemptionOutput()
            self.exemption_output = value.from_dictionary(dictionary['exemptionOutput'])
        if 'schemeRiskScore' in dictionary:
            self.scheme_risk_score = dictionary['schemeRiskScore']
        if 'sdkData' in dictionary:
            if not isinstance(dictionary['sdkData'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['sdkData']))
            value = SdkDataOutput()
            self.sdk_data = value.from_dictionary(dictionary['sdkData'])
        if 'threeDSecureData' in dictionary:
            if not isinstance(dictionary['threeDSecureData'], dict):
                raise TypeError('value \'{}\' is not a dictionary'.format(dictionary['threeDSecureData']))
            value = ThreeDSecureData()
            self.three_d_secure_data = value.from_dictionary(dictionary['threeDSecureData'])
        if 'threeDSecureVersion' in dictionary:
            self.three_d_secure_version = dictionary['threeDSecureVersion']
        if 'threeDServerTransactionId' in dictionary:
            self.three_d_server_transaction_id = dictionary['threeDServerTransactionId']
        if 'xid' in dictionary:
            self.xid = dictionary['xid']
        return self
