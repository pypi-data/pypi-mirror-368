#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import List, Optional

from .api_exception import ApiException
from worldline.connect.sdk.v1.domain.api_error import APIError


class ReferenceException(ApiException):
    """
    Represents an error response from the Worldline Global Collect platform when a non-existing or removed object is trying to be accessed.
    """

    def __init__(self, status_code: int, response_body: str, error_id: Optional[str], errors: Optional[List[APIError]],
                 message: str = "the Worldline Global Collect platform returned a reference error response"):
        super(ReferenceException, self).__init__(status_code, response_body, error_id, errors, message)
