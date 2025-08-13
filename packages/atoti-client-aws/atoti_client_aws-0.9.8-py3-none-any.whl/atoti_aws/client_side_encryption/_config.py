from abc import ABC

import atoti as tt
from atoti._pydantic import PYDANTIC_CONFIG as _PYDANTIC_CONFIG
from pydantic.dataclasses import dataclass


@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
class ClientSideEncryptionConfig(tt.ClientSideEncryptionConfig, ABC):
    region: str
    """The AWS region to interact with."""
