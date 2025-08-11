#
# This class was auto-generated from the API references found at
# https://apireference.connect.worldline-solutions.com/
#
from typing import Sequence, Union

from worldline.connect.sdk.communication.request_header import RequestHeader
from worldline.connect.sdk.json.marshaller import Marshaller
from worldline.connect.sdk.v1.domain.webhooks_event import WebhooksEvent
from worldline.connect.sdk.webhooks.api_version_mismatch_exception import ApiVersionMismatchException
from worldline.connect.sdk.webhooks.secret_key_store import SecretKeyStore
from worldline.connect.sdk.webhooks.signature_validator import SignatureValidator


class WebhooksHelper(object):
    """
    Worldline Global Collect platform v1 webhooks helper.
    """

    def __init__(self, marshaller: Marshaller, secret_key_store: SecretKeyStore):
        if marshaller is None:
            raise ValueError("marshaller is required")
        self.__marshaller = marshaller
        self.__signature_validator = SignatureValidator(secret_key_store)

    def unmarshal(self, body: Union[str, bytes], request_headers: Sequence[RequestHeader]) -> WebhooksEvent:
        """
        Unmarshals the given body, while also validating it using the given request headers.

        :raise SignatureValidationException: If the body could not be validated successfully.
        :raise ApiVersionMismatchException: If the resulting event has an API
         version that this version of the SDK does not support.
        :return: The body unmarshalled as a WebhooksEvent.
        """
        self.__signature_validator.validate(body, request_headers)

        event = self.__marshaller.unmarshal(body.decode('utf-8'), WebhooksEvent)
        self.__validate_api_version(event)
        return event

    @staticmethod
    def __validate_api_version(event: WebhooksEvent) -> None:
        if "v1" != event.api_version:
            raise ApiVersionMismatchException(event.api_version, "v1")

    # Used for unit tests
    @property
    def marshaller(self) -> Marshaller:
        return self.__marshaller

    @property
    def secret_key_store(self) -> SecretKeyStore:
        return self.__signature_validator.secret_key_store
