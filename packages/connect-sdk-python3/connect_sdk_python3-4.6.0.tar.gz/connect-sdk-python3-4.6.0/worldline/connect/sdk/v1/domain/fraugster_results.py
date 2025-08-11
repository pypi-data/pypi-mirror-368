# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.domain.data_object import DataObject


class FraugsterResults(DataObject):

    __fraud_investigation_points: Optional[str] = None
    __fraud_score: Optional[int] = None

    @property
    def fraud_investigation_points(self) -> Optional[str]:
        """
        | Result of the Fraugster check
        | Contains the investigation points used during the evaluation

        Type: str
        """
        return self.__fraud_investigation_points

    @fraud_investigation_points.setter
    def fraud_investigation_points(self, value: Optional[str]) -> None:
        self.__fraud_investigation_points = value

    @property
    def fraud_score(self) -> Optional[int]:
        """
        | Result of the Fraugster check
        | Contains the overall Fraud score which is an integer between 0 and 99

        Type: int
        """
        return self.__fraud_score

    @fraud_score.setter
    def fraud_score(self, value: Optional[int]) -> None:
        self.__fraud_score = value

    def to_dictionary(self) -> dict:
        dictionary = super(FraugsterResults, self).to_dictionary()
        if self.fraud_investigation_points is not None:
            dictionary['fraudInvestigationPoints'] = self.fraud_investigation_points
        if self.fraud_score is not None:
            dictionary['fraudScore'] = self.fraud_score
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'FraugsterResults':
        super(FraugsterResults, self).from_dictionary(dictionary)
        if 'fraudInvestigationPoints' in dictionary:
            self.fraud_investigation_points = dictionary['fraudInvestigationPoints']
        if 'fraudScore' in dictionary:
            self.fraud_score = dictionary['fraudScore']
        return self
