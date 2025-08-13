from typing import final

from atoti._pydantic import PYDANTIC_CONFIG as _PYDANTIC_CONFIG
from pydantic.dataclasses import dataclass

from ._config import ClientSideEncryptionConfig


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
class KmsConfig(ClientSideEncryptionConfig):
    """KMS config to use for `client side encryption <https://docs.aws.amazon.com/AmazonS3/latest/dev/UsingClientSideEncryption.html>`__.

    The AWS KMS CMK must have been created in the same AWS region as the destination bucket (Cf. `AWS documentation <https://docs.aws.amazon.com/AmazonS3/latest/dev/replication-config-for-kms-objects.html>`__).

    Example:
        .. doctest::
            :hide:

            >>> session = getfixture("session_with_aws_plugin")

        >>> from atoti_aws import KmsConfig
        >>> client_side_encryption = KmsConfig(
        ...     region="eu-west-3",
        ...     key_id="key_id",
        ... )
    """

    key_id: str
    """The ID to identify the key in KMS."""
