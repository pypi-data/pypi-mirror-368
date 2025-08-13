"""
MiniSpark - 一个轻量级的Python数据处理库
"""

from .minispark import MiniSpark
from .connectors.csv_connector import CSVConnector
from .connectors.excel_connector import ExcelConnector
from .connectors.json_connector import JSONConnector
from .connectors.sqlite_connector import SQLiteConnector
from .connectors.duckdb_connector import DuckDBConnector
from .connectors.mysql_connector import MySQLConnector
from .connectors.base import BaseConnector

__version__ = "0.1.6"
__author__ = "段福"
__email__ = "duanfu456@163.cm"

__all__ = [
    "MiniSpark",
    "CSVConnector", 
    "ExcelConnector",
    "JSONConnector",
    "SQLiteConnector",
    "DuckDBConnector",
    "MySQLConnector",
    "BaseConnector"
]