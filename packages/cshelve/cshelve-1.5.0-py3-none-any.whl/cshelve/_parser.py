"""
This module is responsible for parsing the configuration file.
It reads the configuration file and returns the provider and its configuration as a dictionary.
It also provides a function to determine if a local shelf should be used based on the file extension.

At this level, the only necessary configuration is the provider name.
Other configurations are loaded into a dictionary and passed to the provider for further configuration.
"""
from logging import Logger
from collections import namedtuple
import configparser
from pathlib import Path

from ._config import from_env


# Default ini section containing the provider and its configuration.
DEFAULT_CONFIG_STORE = "default"
# Key containing the provider name.
PROVIDER_KEY = "provider"
# Key indicating if the usage of pickle is activated (True by default).
USE_PICKLE = "use_pickle"
# Key indicating if the usage of the versionning is activated (True by default).
USE_VERSIONNING = "use_versionning"
# Logging configuration section.
LOGGING_KEY_STORE = "logging"
# Compression configuration section.
COMPRESSION_KEY_STORE = "compression"
# Encryption configuration section.
ENCRYPTION_KEY_STORE = "encryption"
# Provider parameter section.
PROVIDER_PARAMS = "provider_params"

# Tuple containing the provider name and its configuration.
Config = namedtuple(
    "Config",
    [
        "provider",
        "use_pickle",
        "use_versionning",
        "default",
        "logging",
        "compression",
        "encryption",
        "provider_params",
    ],
)


def use_local_shelf(filename: Path) -> bool:
    """
    If the user specify a filename with an extension different of '.ini', a local shelf (the standard library) must be used.
    """
    return not filename.suffix == ".ini"


def load_from_file(logger: Logger, filename: Path) -> Config:
    """
    Load the configuration file and return it as a dictionary.
    """
    logger.debug(f"Loading configuration file: {filename}.")
    config = configparser.ConfigParser()
    config.read(filename)

    return _load_configuration(logger, config)


def load_from_dict(logger: Logger, config: dict) -> Config:
    """
    Load the configuration from a dict and return it.
    """
    logger.debug(f"Loading configuration from a dict.")
    return _load_configuration(logger, config)


def _load_configuration(logger: Logger, config: dict) -> Config:
    c = config[DEFAULT_CONFIG_STORE]
    logging_config = config[LOGGING_KEY_STORE] if LOGGING_KEY_STORE in config else {}
    compression_config = (
        config[COMPRESSION_KEY_STORE] if COMPRESSION_KEY_STORE in config else {}
    )
    encryption_config = (
        config[ENCRYPTION_KEY_STORE] if ENCRYPTION_KEY_STORE in config else {}
    )
    provider_params = config[PROVIDER_PARAMS] if PROVIDER_PARAMS in config else {}

    logger.debug(f"Configuration loaded.")
    return Config(
        provider=c[PROVIDER_KEY],
        default=from_env(dict(c)),
        logging=from_env(dict(logging_config)),
        compression=from_env(dict(compression_config)),
        encryption=from_env(dict(encryption_config)),
        provider_params=from_env(dict(provider_params)),
        # These configurations is checked here to avoid redundant checks.
        use_pickle=c.get(USE_PICKLE, "true").lower() == "true",
        use_versionning=c.get(USE_VERSIONNING, "true").lower() == "true",
    )
