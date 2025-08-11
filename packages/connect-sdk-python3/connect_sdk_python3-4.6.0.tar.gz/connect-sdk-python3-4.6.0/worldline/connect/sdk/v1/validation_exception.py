#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import List, Optional

from .api_exception import ApiException
from worldline.connect.sdk.v1.domain.api_error import APIError


class ValidationException(ApiException):
    """
    Represents an error response from the Worldline Global Collect platform when validation of requests failed.
    """

    def __init__(self, status_code: int, response_body: str, error_id: Optional[str], errors: Optional[List[APIError]],
                 message: str = "the Worldline Global Collect platform returned an incorrect request error response"):
        super(ValidationException, self).__init__(status_code, response_body, error_id, errors, message)
