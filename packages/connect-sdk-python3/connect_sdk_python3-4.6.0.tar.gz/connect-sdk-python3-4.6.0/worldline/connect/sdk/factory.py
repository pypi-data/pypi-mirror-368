from configparser import ConfigParser
from typing import Optional, Union

from .client import Client
from .communicator import Communicator
from .communicator_configuration import CommunicatorConfiguration

from worldline.connect.sdk.authentication.authorization_type import AuthorizationType
from worldline.connect.sdk.authentication.authenticator import Authenticator
from worldline.connect.sdk.authentication.v1hmac_authenticator import V1HMACAuthenticator
from worldline.connect.sdk.communication.connection import Connection
from worldline.connect.sdk.communication.default_connection import DefaultConnection
from worldline.connect.sdk.communication.metadata_provider import MetadataProvider
from worldline.connect.sdk.json.default_marshaller import DefaultMarshaller
from worldline.connect.sdk.json.marshaller import Marshaller


class Factory(object):
    """
    Worldline Global Collect platform factory for several SDK components.
    """

    @staticmethod
    def create_configuration(configuration_file_name: Union[str, bytes], authorization_id: str, authorization_secret: str) -> CommunicatorConfiguration:
        """
        Creates a CommunicatorConfiguration based on the configuration values in configuration_file_name, authorization_id and authorization_secret.
        """
        try:
            parser = ConfigParser()
            with open(configuration_file_name) as f:
                parser.read_file(f)
            return CommunicatorConfiguration(properties=parser,
                                             authorization_id=authorization_id,
                                             authorization_secret=authorization_secret)
        except IOError as e:
            raise RuntimeError("Unable to read configuration located at {}".format(e.filename), e) from e

    @staticmethod
    def create_communicator_from_configuration(communicator_configuration: CommunicatorConfiguration,
                                               metadata_provider: Optional[MetadataProvider] = None,
                                               connection: Optional[Connection] = None,
                                               authenticator: Optional[Authenticator] = None,
                                               marshaller: Optional[Marshaller] = None) -> Communicator:
        """
        Creates a Communicator based on the configuration stored in the CommunicatorConfiguration argument
        """
        if metadata_provider is None:
            metadata_provider = MetadataProvider(integrator=communicator_configuration.integrator,
                                                 shopping_cart_extension=communicator_configuration.shopping_cart_extension)
        if connection is None:
            connection = DefaultConnection(communicator_configuration.connect_timeout,
                                           communicator_configuration.socket_timeout,
                                           communicator_configuration.max_connections,
                                           communicator_configuration.proxy_configuration)
        if authenticator is None:
            authenticator = Factory.__get_authenticator(communicator_configuration)
        if marshaller is None:
            marshaller = DefaultMarshaller.instance()
        return Communicator(api_endpoint=communicator_configuration.api_endpoint,
                            metadata_provider=metadata_provider,
                            connection=connection,
                            authenticator=authenticator,
                            marshaller=marshaller)

    @staticmethod
    def __get_authenticator(communicator_configuration: CommunicatorConfiguration) -> Authenticator:
        if communicator_configuration.authorization_type == AuthorizationType.V1HMAC:
            return V1HMACAuthenticator(communicator_configuration.api_key_id, communicator_configuration.secret_api_key)
        raise RuntimeError("Unknown authorizationType " + communicator_configuration.authorization_type)

    @staticmethod
    def create_communicator_from_file(configuration_file_name: Union[str, bytes], authorization_id: str, authorization_secret: str,
                                      metadata_provider: Optional[MetadataProvider] = None,
                                      connection: Optional[Connection] = None,
                                      authenticator: Optional[Authenticator] = None,
                                      marshaller: Optional[Marshaller] = None) -> Communicator:
        """
        Creates a Communicator based on the configuration values in configuration_file_name, api_id_key and authorization_secret.
        """
        configuration = Factory.create_configuration(configuration_file_name, authorization_id, authorization_secret)
        return Factory.create_communicator_from_configuration(configuration,
                                                              metadata_provider=metadata_provider,
                                                              connection=connection,
                                                              authenticator=authenticator,
                                                              marshaller=marshaller)

    @staticmethod
    def create_client_from_configuration(communicator_configuration: CommunicatorConfiguration,
                                         metadata_provider: Optional[MetadataProvider] = None,
                                         connection: Optional[Connection] = None,
                                         authenticator: Optional[Authenticator] = None,
                                         marshaller: Optional[Marshaller] = None) -> Client:
        """
        Create a Client based on the configuration stored in the CommunicatorConfiguration argument
        """
        communicator = Factory.create_communicator_from_configuration(communicator_configuration,
                                                                      metadata_provider=metadata_provider,
                                                                      connection=connection,
                                                                      authenticator=authenticator,
                                                                      marshaller=marshaller)
        return Client(communicator)

    @staticmethod
    def create_client_from_communicator(communicator: Communicator) -> Client:
        """
        Create a Client based on the settings stored in the Communicator argument
        """
        return Client(communicator)

    @staticmethod
    def create_client_from_file(configuration_file_name: Union[str, bytes], authorization_id: str, authorization_secret: str,
                                metadata_provider: Optional[MetadataProvider] = None,
                                connection: Optional[Connection] = None,
                                authenticator: Optional[Authenticator] = None,
                                marshaller: Optional[Marshaller] = None) -> Client:
        """
        Creates a Client based on the configuration values in configuration_file_name, authorization_id and authorization_secret.
        """
        communicator = Factory.create_communicator_from_file(configuration_file_name, authorization_id, authorization_secret,
                                                             metadata_provider=metadata_provider,
                                                             connection=connection,
                                                             authenticator=authenticator,
                                                             marshaller=marshaller)
        return Client(communicator)
