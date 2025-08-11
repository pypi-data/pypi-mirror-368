#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import List, Optional

from .api_exception import ApiException
from worldline.connect.sdk.v1.domain.api_error import APIError


class IdempotenceException(ApiException):
    """
    Represents an error response from the Worldline Global Collect platform when an idempotent request failed because the first request has not finished yet.
    """

    def __init__(self, idempotence_key: str, idempotence_request_timestamp: int,
                 status_code: int, response_body: str, error_id: Optional[str], errors: Optional[List[APIError]],
                 message: str = "the Worldline Global Collect platform returned a duplicate request error response"):
        super(IdempotenceException, self).__init__(status_code, response_body, error_id, errors, message)
        self.__idempotence_key = idempotence_key
        self.__idempotence_request_timestamp = idempotence_request_timestamp

    @property
    def idempotence_key(self) -> str:
        """
        :return: The key that was used for the idempotent request.
        """
        return self.__idempotence_key

    @property
    def idempotence_request_timestamp(self) -> int:
        """
        :return: The request timestamp of the first idempotent request with the same key.
        """
        return self.__idempotence_request_timestamp
