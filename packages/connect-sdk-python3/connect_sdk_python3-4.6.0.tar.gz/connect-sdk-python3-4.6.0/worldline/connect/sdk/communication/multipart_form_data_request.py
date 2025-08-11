from abc import ABC, abstractmethod

from .multipart_form_data_object import MultipartFormDataObject


class MultipartFormDataRequest(ABC):
    """
    A representation of a multipart/form-data request.
    """

    @abstractmethod
    def to_multipart_form_data_object(self) -> MultipartFormDataObject:
        """
        :return: :class:`worldline.connect.sdk.communication.MultipartFormDataObject`
        """
        raise NotImplementedError
