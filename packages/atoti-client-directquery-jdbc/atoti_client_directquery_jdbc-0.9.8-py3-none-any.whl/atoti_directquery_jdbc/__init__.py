"""Code to use DirectQuery through `JDBC <https://en.wikipedia.org/wiki/Java_Database_Connectivity>`__.

Note:
    For better performance, prefer database-specific connectors when available.
    For instance, to connect to ClickHouse, use :mod:`atoti_directquery_clickhouse`.
"""

from .connection_config import ConnectionConfig as ConnectionConfig
from .table_config import TableConfig as TableConfig
