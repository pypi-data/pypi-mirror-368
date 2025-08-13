from typing import final

from atoti._pydantic import PYDANTIC_CONFIG as _PYDANTIC_CONFIG
from atoti.distribution_protocols import DiscoveryProtocol
from pydantic.dataclasses import dataclass
from typing_extensions import override


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
class S3PingDiscoveryProtocol(DiscoveryProtocol):
    region_name: str
    bucket_name: str
    bucket_prefix: str = ""
    check_if_bucket_exists: bool = True
    acl_grant_bucket_owner_full_control: bool = False
    path_style_access_enabled: bool = False

    @property
    @override
    def _name(self) -> str:
        return "aws.S3_PING"
