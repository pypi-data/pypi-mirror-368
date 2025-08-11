# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import List, Optional

from worldline.connect.sdk.domain.data_object import DataObject


class CybersourceDecisionManager(DataObject):
    """
    | This object contains the results of the Cybersource Decision Manager assessment. Cybersource is a fraud detection tool leveraging data networks, configurable rules, intelligence, and device fingerprinting to identify risky transactions.
    """

    __clause_name: Optional[str] = None
    __fraud_score: Optional[int] = None
    __policy_applied: Optional[str] = None
    __reason_codes: Optional[List[str]] = None

    @property
    def clause_name(self) -> Optional[str]:
        """
        | Name of the clause within the applied policy that was triggered during the evaluation of this transaction.

        Type: str
        """
        return self.__clause_name

    @clause_name.setter
    def clause_name(self, value: Optional[str]) -> None:
        self.__clause_name = value

    @property
    def fraud_score(self) -> Optional[int]:
        """
        | Result of the Cybersource Decision Manager check. This contains the normalized fraud score from a scale of 0 to 100. A higher score indicates an increased risk of fraud.

        Type: int
        """
        return self.__fraud_score

    @fraud_score.setter
    def fraud_score(self, value: Optional[int]) -> None:
        self.__fraud_score = value

    @property
    def policy_applied(self) -> Optional[str]:
        """
        | Name of the policy that was applied during the evaluation of this transaction.

        Type: str
        """
        return self.__policy_applied

    @policy_applied.setter
    def policy_applied(self, value: Optional[str]) -> None:
        self.__policy_applied = value

    @property
    def reason_codes(self) -> Optional[List[str]]:
        """
        | List of one or more reason codes.

        Type: list[str]
        """
        return self.__reason_codes

    @reason_codes.setter
    def reason_codes(self, value: Optional[List[str]]) -> None:
        self.__reason_codes = value

    def to_dictionary(self) -> dict:
        dictionary = super(CybersourceDecisionManager, self).to_dictionary()
        if self.clause_name is not None:
            dictionary['clauseName'] = self.clause_name
        if self.fraud_score is not None:
            dictionary['fraudScore'] = self.fraud_score
        if self.policy_applied is not None:
            dictionary['policyApplied'] = self.policy_applied
        if self.reason_codes is not None:
            dictionary['reasonCodes'] = []
            for element in self.reason_codes:
                if element is not None:
                    dictionary['reasonCodes'].append(element)
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'CybersourceDecisionManager':
        super(CybersourceDecisionManager, self).from_dictionary(dictionary)
        if 'clauseName' in dictionary:
            self.clause_name = dictionary['clauseName']
        if 'fraudScore' in dictionary:
            self.fraud_score = dictionary['fraudScore']
        if 'policyApplied' in dictionary:
            self.policy_applied = dictionary['policyApplied']
        if 'reasonCodes' in dictionary:
            if not isinstance(dictionary['reasonCodes'], list):
                raise TypeError('value \'{}\' is not a list'.format(dictionary['reasonCodes']))
            self.reason_codes = []
            for element in dictionary['reasonCodes']:
                self.reason_codes.append(element)
        return self
