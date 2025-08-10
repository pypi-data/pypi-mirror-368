"""
This module contains the exceptions raised by the cshelve package.
`dbm` exceptions are based on the sub implementations and are not following a standard.
Consequently, we are creating custom exceptions to handle the errors.
"""
from typing import Type


class DataProcessingSignatureError(RuntimeError):
    """
    Raised when the signature of the data processing is incorrect.
    """

    pass


class UnknownProviderError(RuntimeError):
    """
    Raised when an unknown cloud provider is specified in the configuration.
    """

    pass


class UnknownCompressionAlgorithmError(RuntimeError):
    """
    Raised when the compression algorithm provided is incorrect.
    """

    pass


class UnknownEncryptionAlgorithmError(RuntimeError):
    """
    Raised when the encryption algorithm provided is incorrect.
    """

    pass


class MissingEncryptionKeyError(RuntimeError):
    """
    Raised when there is no encryption key provided.
    """

    pass


class EncryptedDataCorruptionError(RuntimeError):
    """
    Raised when a data is not accessible due to a corruption.
    """

    pass


class KeyNotFoundError(KeyError):
    """
    Raised when a resource is not found.
    """

    pass


class ReadOnlyError(Exception):
    """
    Raised when an attempt is made to write to a read-only DB.
    """

    pass


class DBDoesNotExistsError(Exception):
    """
    Raised when an the DB does not exist and the flag does not allow creating it.
    """

    pass


class CanNotCreateDBError(Exception):
    """
    Raised when an attempt is made to create a DB and it fails.
    """

    pass


class AuthError(Exception):
    """
    Based class for Auth exception.
    """

    pass


class AuthTypeError(AuthError):
    """
    Raised when the auth type is unknown.
    """

    pass


class AuthArgumentError(AuthError):
    """
    Raised when the auth type is unknown.
    """

    pass


class ConfigurationError(RuntimeError):
    """
    Raised when the configuration provided for a provider is incorrect.
    """

    pass


def key_access(exception: Type[Exception]):
    """
    Create a KeyNotFoundError exception if the key is not found.
    """

    def wrapper(func):
        def inner(self, key, *args, **kwargs):
            try:
                return func(self, key, *args, **kwargs)
            except exception as e:
                raise KeyNotFoundError(f"Key not found: {key}") from e

        return inner

    return wrapper
