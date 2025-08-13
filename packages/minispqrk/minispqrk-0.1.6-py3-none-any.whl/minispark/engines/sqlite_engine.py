import pandas as pd
import os
from typing import Dict
from loguru import logger
from .base import BaseEngine
from sqlalchemy import create_engine


class SQLiteEngine(BaseEngine):
    """SQLite本地处理引擎"""
    
    def __init__(self, database_path: str = ":memory:"):
        super().__init__()
        self.database_path = database_path
        self.connection = None
        logger.info(f"初始化SQLite引擎, 数据库路径: {database_path}")
        
        # 如果是文件数据库，确保目录存在
        if database_path != ":memory:":
            db_dir = os.path.dirname(database_path)
            if db_dir:
                os.makedirs(db_dir, exist_ok=True)
        
        self._get_connection()
    
    def _get_connection(self):
        """获取数据库连接"""
        if self.connection is None:
            logger.info("创建新的SQLite引擎连接")
            if self.database_path == ":memory:":
                self.connection = create_engine(f"sqlite:///{self.database_path}")
            else:
                # 对于文件数据库，使用绝对路径
                self.connection = create_engine(f"sqlite:///{os.path.abspath(self.database_path)}")
        return self.connection
    
    def register_table(self, table_name: str, dataframe: pd.DataFrame):
        """
        注册表到本地引擎
        
        Args:
            table_name: 表名称
            dataframe: DataFrame数据
        """
        logger.info(f"注册表到SQLite引擎: {table_name}, 形状: {dataframe.shape}")
        
        try:
            conn = self._get_connection()
            dataframe.to_sql(table_name, conn, if_exists='replace', index=False)
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
        logger.info(f"SQLite引擎执行查询: {query}")
        
        try:
            conn = self._get_connection()
            result = pd.read_sql(query, conn)
            logger.info(f"查询执行成功, 结果形状: {result.shape}")
            return result
        except Exception as e:
            logger.error(f"SQLite查询执行失败: {e}")
            raise
    
    def close(self):
        """关闭引擎"""
        logger.info("关闭SQLite引擎")
        try:
            if self.connection:
                self.connection.dispose()
                self.connection = None
                logger.info("SQLite引擎已关闭")
        except Exception as e:
            logger.error(f"关闭SQLite引擎时发生错误: {e}")
            raise