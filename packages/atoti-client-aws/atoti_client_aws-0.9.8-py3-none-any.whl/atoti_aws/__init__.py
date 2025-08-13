"""Code to load CSV and Parquet files from AWS S3 into Atoti tables.

Authentication is handled by the underlying AWS SDK for Java library.
Refer to their `documentation <https://docs.aws.amazon.com/sdk-for-java/v2/developer-guide/credentials.html>`__  for the available options.

Example:
    .. doctest::
        :hide:

        >>> session = getfixture("session_with_aws_plugin")

    >>> table = session.read_csv(
    ...     "s3://test.public.atoti.io/city.csv",
    ...     keys={"city"},
    ...     table_name="City",
    ... )
    >>> table.head().sort_index()
            value
    city
    London  200.0
    Paris   100.0

"""

from .client_side_encryption import *
from .s3_ping_discovery_protocol import (
    S3PingDiscoveryProtocol as S3PingDiscoveryProtocol,
)
