from typing import final

from atoti._pydantic import PYDANTIC_CONFIG as _PYDANTIC_CONFIG
from atoti.directquery._external_table_config import (
    ArrayConversionConfig,
    ExternalTableConfig,
)
from pydantic.dataclasses import dataclass

from .connection_config import ConnectionConfig


@final
@dataclass(config=_PYDANTIC_CONFIG, frozen=True, kw_only=True)
class TableConfig(ExternalTableConfig[ConnectionConfig], ArrayConversionConfig):
    """Config passed to :meth:`~atoti.Session.add_external_table`."""
