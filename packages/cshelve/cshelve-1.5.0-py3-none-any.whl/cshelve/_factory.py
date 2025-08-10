"""
Factory module to return the correct module to be used.
"""
from logging import Logger
from .provider_interface import ProviderInterface
from .exceptions import UnknownProviderError


def factory(logger: Logger, provider: str) -> ProviderInterface:
    """
    Return the correct module to be used.
    """
    logger.debug(f"Creating the provider '{provider}'...")
    res = _factory(logger, provider)
    logger.debug("Provider created.")
    return res


def _factory(logger: Logger, provider: str):
    logger.info(f"Loading provider {provider}")

    if provider == "azure-blob":
        from ._azure_blob_storage import AzureBlobStorage

        return AzureBlobStorage(logger)
    if provider == "aws-s3":
        from ._aws_s3 import AwsS3

        return AwsS3(logger)
    elif provider == "in-memory":
        from ._in_memory import InMemory

        return InMemory(logger)
    elif provider == "sftp":
        from ._sftp import SFTP

        return SFTP(logger)

    logger.critical("Provider not found.")
    raise UnknownProviderError(f"Provider Interface '{provider}' is not supported.")
