import pandas as pd
import os
from typing import Dict
from loguru import logger
from .base import BaseEngine


class DuckDBEngine(BaseEngine):
    """DuckDB本地处理引擎"""
    
    def __init__(self, database_path: str = ":memory:"):
        super().__init__()
        self.database_path = database_path
        self.connection = None
        logger.info(f"初始化DuckDB引擎, 数据库路径: {database_path}")
        
        # 如果是文件数据库，确保目录存在
        if database_path != ":memory:":
            db_dir = os.path.dirname(database_path)
            if db_dir:
                os.makedirs(db_dir, exist_ok=True)
        
        self._get_connection()
    
    def _get_connection(self):
        """获取数据库连接"""
        try:
            logger.info("尝试导入duckdb库")
            import duckdb
            logger.info("duckdb库导入成功")
            
            if self.connection is None:
                logger.info("创建新的DuckDB引擎连接")
                # 修复：移除不兼容的timeout参数
                self.connection = duckdb.connect(self.database_path)
                logger.info("DuckDB引擎连接创建成功")
            return self.connection
        except ImportError as e:
            logger.error(f"使用DuckDB引擎需要安装duckdb库: {e}")
            raise ImportError("使用DuckDB引擎需要安装duckdb库")
        except Exception as e:
            logger.error(f"创建DuckDB引擎连接失败: {e}")
            raise
    
    def register_table(self, table_name: str, dataframe: pd.DataFrame):
        """
        注册表到本地引擎
        
        Args:
            table_name: 表名称
            dataframe: DataFrame数据
        """
        logger.info(f"注册表到DuckDB引擎: {table_name}, 形状: {dataframe.shape}")
        
        try:
            conn = self._get_connection()
            conn.register(table_name, dataframe)
            self.tables[table_name] = dataframe
            logger.info(f"表 {table_name} 注册成功")
        except Exception as e:
            logger.error(f"表 {table_name} 注册失败: {e}")
            raise
    
    def execute_query(self, query: str):
        """
        执行SQL查询
        
        Args:
            query: SQL查询语句
        """
        logger.info(f"DuckDB引擎执行查询: {query}")
        
        try:
            conn = self._get_connection()
            result = conn.execute(query).fetchdf()
            logger.info(f"查询执行成功, 结果形状: {result.shape}")
            return result
        except Exception as e:
            logger.error(f"DuckDB查询执行失败: {e}")
            raise
    
    def close(self):
        """关闭引擎"""
        logger.info("关闭DuckDB引擎")
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.info("DuckDB引擎已关闭")