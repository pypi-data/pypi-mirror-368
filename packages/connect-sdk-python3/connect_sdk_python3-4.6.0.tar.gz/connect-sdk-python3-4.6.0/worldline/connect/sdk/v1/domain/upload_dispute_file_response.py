# -*- coding: utf-8 -*-
#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Optional

from worldline.connect.sdk.domain.data_object import DataObject


class UploadDisputeFileResponse(DataObject):
    """
    | Response of a file upload request
    """

    __dispute_id: Optional[str] = None
    __file_id: Optional[str] = None

    @property
    def dispute_id(self) -> Optional[str]:
        """
        | Dispute ID that is associated with the created dispute.

        Type: str
        """
        return self.__dispute_id

    @dispute_id.setter
    def dispute_id(self, value: Optional[str]) -> None:
        self.__dispute_id = value

    @property
    def file_id(self) -> Optional[str]:
        """
        | The file ID that is associated with the uploaded file. This ID can be used for further communication regarding the file and retrieval of aforementioned property.

        Type: str
        """
        return self.__file_id

    @file_id.setter
    def file_id(self, value: Optional[str]) -> None:
        self.__file_id = value

    def to_dictionary(self) -> dict:
        dictionary = super(UploadDisputeFileResponse, self).to_dictionary()
        if self.dispute_id is not None:
            dictionary['disputeId'] = self.dispute_id
        if self.file_id is not None:
            dictionary['fileId'] = self.file_id
        return dictionary

    def from_dictionary(self, dictionary: dict) -> 'UploadDisputeFileResponse':
        super(UploadDisputeFileResponse, self).from_dictionary(dictionary)
        if 'disputeId' in dictionary:
            self.dispute_id = dictionary['disputeId']
        if 'fileId' in dictionary:
            self.file_id = dictionary['fileId']
        return self
