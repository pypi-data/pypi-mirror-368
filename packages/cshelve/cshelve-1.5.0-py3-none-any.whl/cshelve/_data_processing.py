"""
This module provides the DataProcessing class, which handles pre-processing and post-processing of data.

Examples:
    >>> dp = DataProcessing(logger=None, signed=False)
    >>> dp.add(lambda x: x + b'1', lambda x: x[:-1], 'a')
    >>> dp.add(lambda x: x + b'2', lambda x: x[:-1], 'b')
    >>> assert b'42' == dp.apply_post_processing(dp.apply_pre_processing(b'42'))
"""
from abc import abstractmethod
from collections import namedtuple
import struct
from typing import Callable, List, Optional

from .exceptions import DataProcessingSignatureError

_DataProcessing = namedtuple("DataProcessing", ["signature", "data"])
_DataProcessingMetadata = namedtuple(
    "DataProcessingMetadata", ["len_signature", "len_data", "data_processing"]
)

# Algorithm signatures to be applied to the data.
SIGNATURES = {"COMPRESSION": b"c", "ENCRYPTION": b"e"}
# Default signature, when no processing is applied.
EMPTY_SIGNATURE = b""


class DataProcessing:
    """
    A class to handle pre-processing and post-processing of data.
    A signature option is available to ensure the data processing is applied in the correct order.
    Adding a signature is optional and adds metadata to the data.
    """

    def __new__(cls, logger, signed: bool):
        if signed:
            return super(DataProcessing, cls).__new__(_SignedDataProcessing)
        return super(DataProcessing, cls).__new__(_UnSignedDataProcessing)

    def __init__(self, logger, signed: bool):
        """
        Initializes the DataProcessing class.
        """
        self.logger = logger
        self.pre_processing: List[Callable[[bytes], bytes]] = []
        self.post_processing: List[Callable[[bytes], bytes]] = []

    def add(
        self,
        pre_processing: Callable[[bytes], bytes],
        post_processing: Callable[[bytes], bytes],
        signature: Optional[bytes] = None,
    ):
        """
        Adds functions for processing.
        The signature is used to generate the signature of the data.
        """
        self.pre_processing.append(pre_processing)
        # Add to the beginning of the list to ensure the order is correct.
        self.post_processing.insert(0, post_processing)

    def apply_pre_processing(self, data: bytes) -> bytes:
        """
        Applies all pre-processing functions to the data.
        """
        for fct in self.pre_processing:
            data = fct(data)
        return data

    @abstractmethod
    def apply_post_processing(self, data: bytes) -> bytes:
        """
        Applies all post-processing functions to the data.
        """
        ...


class _UnSignedDataProcessing(DataProcessing):
    def apply_post_processing(self, data: bytes) -> bytes:
        """
        Apply a series of post-processing functions to the given data.

        Args:
            data (bytes): The input data to be processed.

        Returns:
            bytes: The processed data after applying all post-processing functions.
        """
        for fct in self.post_processing:
            data = fct(data)
        return data


class _SignedDataProcessing(DataProcessing):
    def __init__(self, logger, *args, **kwargs):
        super().__init__(logger, *args, **kwargs)
        # The signature of the data processing.
        # It is used to ensure the data processing is applied in the correct order.
        self.signature = EMPTY_SIGNATURE

    def add(
        self,
        pre_processing: Callable[[bytes], bytes],
        post_processing: Callable[[bytes], bytes],
        signature: bytes,
    ):
        super().add(pre_processing, post_processing, signature)
        # Add the signature to the beginning of the list to ensure the order is correct.
        self.signature = signature + self.signature

    def apply_pre_processing(self, data: bytes) -> bytes:
        """
        Apply pre-processing to the given data.

        This method first calls the superclass's apply_pre_processing method
        to perform any necessary pre-processing steps. It then encapsulates
        the processed data with a signature.

        Args:
            data (bytes): The data to be pre-processed.

        Returns:
            bytes: The pre-processed and encapsulated data.
        """
        data = super().apply_pre_processing(data)
        return self.encapsulate(data, self.signature)

    def apply_post_processing(self, data: bytes) -> bytes:
        """
        Apply post-processing transformations to the given data based on the metadata and signature.

        Args:
            data (bytes): The input data to be processed.

        Returns:
            bytes: The processed data after applying the necessary transformations.

        Raises:
            DataProcessingSignatureError: If the data processing signature is incompatible with the expected signature.
        """
        metadata = _DataProcessingMetadata._make(
            struct.unpack(f"<BQ{len(data) - 1 - 8}s", data)
        )
        data_processing = _DataProcessing._make(
            struct.unpack(
                f"<{metadata.len_signature}s{metadata.len_data}s",
                metadata.data_processing,
            )
        )

        result = data_processing.data
        signature = data_processing.signature

        # Apply all signatures known from the current signature if possible.
        for idx, s in enumerate(self.signature):
            if signature == EMPTY_SIGNATURE:
                # The signature of the object can be shorter then the signature of the incoming object.
                break
            if signature[0] == s:
                # The transformation must be applied.
                result = self.post_processing[idx](result)
                signature = signature[1:]
        else:
            # If the signature is not empty, it means at least one transformation of the incoming object
            # is unknowned of the current process and so the incoming object can't be retrieved.
            if signature != EMPTY_SIGNATURE:
                self.logger.error(
                    "Data processing signature: %s is incompatible with: %s",
                    data_processing.signature,
                    self.signature,
                )
                raise DataProcessingSignatureError(
                    f"Following transformation can't be applied: {signature}."
                )

        return result

    @classmethod
    def encapsulate(cls, data: bytes, signature: bytes = EMPTY_SIGNATURE) -> bytes:
        """
        Wraps the data with the processing metadata.
        """
        len_data = len(data)
        len_data_proc_signature = len(signature)

        data_processing = struct.pack(
            f"<{len_data_proc_signature}s{len_data}s",
            signature,
            data,
        )
        # We are using unsigned long long due to the potential size of the data.
        metadata = struct.pack(
            f"<BQ{len_data_proc_signature + len_data}s",
            len_data_proc_signature,
            len_data,
            data_processing,
        )

        return metadata
