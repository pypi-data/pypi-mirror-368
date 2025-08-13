from typing import final

import atoti as tt
from atoti._pydantic import PYDANTIC_CONFIG as _PYDANTIC_CONFIG
from pydantic.dataclasses import dataclass

from ._config import ClientSideEncryptionConfig


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True)
class KeyPair(ClientSideEncryptionConfig, tt.KeyPair):
    """Key pair to use for `client side encryption <https://docs.aws.amazon.com/AmazonS3/latest/dev/UsingClientSideEncryption.html>`__.

    Example:
        .. doctest::
            :hide:

            >>> session = getfixture("session_with_aws_plugin")

        >>> from atoti_aws import KeyPair
        >>> client_side_encryption = KeyPair(
        ...     "public_key",
        ...     "private_key",
        ...     region="eu-west-3",
        ... )
    """
