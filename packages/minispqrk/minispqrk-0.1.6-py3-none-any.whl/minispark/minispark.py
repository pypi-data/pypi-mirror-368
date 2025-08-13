import pandas as pd
import toml
import os
import tempfile
from typing import Dict, Any, List
from loguru import logger
from .connectors.base import BaseConnector
from .engines.base import BaseEngine
from .processors.data_processor import DataProcessor
import time
import atexit
import shutil


class MiniSpark:
    """MiniSpark主类"""
    
    def __init__(self, config_path: str = "config.toml"):
        """
        初始化MiniSpark
        
        Args:
            config_path: 配置文件路径
        """
        # 配置日志
        logger.info("初始化MiniSpark")
        
        self.config = self._load_config(config_path)
        self.connectors: Dict[str, BaseConnector] = {}
        # 用于跟踪临时数据库文件，以便在程序结束时清理
        self.temp_database_path = None
        self.engine: BaseEngine = self._init_engine()
        self.processor = DataProcessor()
        # 设置DataProcessor对MiniSpark的引用
        self.processor.set_minispark(self)
        self.tables: Dict[str, pd.DataFrame] = {}
        
        # 注册退出处理函数
        atexit.register(self._cleanup_temp_database)
        
        logger.info("MiniSpark初始化完成")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        logger.info(f"加载配置文件: {config_path}")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = toml.load(f)
            logger.info("配置文件加载成功")
            return config
        except FileNotFoundError:
            logger.warning(f"配置文件 {config_path} 不存在，使用默认配置")
            # 如果配置文件不存在，返回默认配置
            return {
                "engine": {
                    "type": "sqlite",
                    "database_path": ":memory:"
                },
                "storage": {
                    "format": "parquet"
                }
            }
    
    def _init_engine(self) -> BaseEngine:
        """初始化本地处理引擎"""
        engine_type = self.config.get("engine", {}).get("type", "sqlite")
        database_path = self.config.get("engine", {}).get("database_path", ":memory:")
        
        # 处理临时文件数据库路径
        final_database_path = database_path
        if database_path != ":memory:" and not os.path.isabs(database_path):
            # 如果不是内存数据库且不是绝对路径，则在临时目录中创建
            temp_dir = tempfile.gettempdir()
            final_database_path = os.path.join(temp_dir, database_path)
            self.temp_database_path = final_database_path
            # 确保临时文件所在的目录存在
            os.makedirs(os.path.dirname(final_database_path) if os.path.dirname(final_database_path) else temp_dir, exist_ok=True)
            logger.info(f"使用临时数据库文件: {final_database_path}")
        elif database_path != ":memory:" and os.path.isabs(database_path):
            # 如果是绝对路径，也记录下来以便清理
            self.temp_database_path = database_path
        
        logger.info(f"初始化本地处理引擎: {engine_type}, 数据库路径: {final_database_path}")
        
        if engine_type == "duckdb":
            try:
                from .engines.duckdb_engine import DuckDBEngine
                # 添加超时机制测试DuckDB引擎
                engine = None
                start_time = time.time()
                timeout = 10  # 10秒超时
                
                logger.info("尝试初始化DuckDB引擎")
                engine = DuckDBEngine(final_database_path)
                
                # 简单测试引擎是否工作正常
                test_result = engine.execute_query("SELECT 'test' as result")
                logger.info("DuckDB引擎测试查询成功")
                
                logger.info("DuckDB引擎初始化成功")
                return engine
            except Exception as e:
                logger.warning(f"DuckDB引擎初始化失败: {e}，回退到SQLite引擎")
                from .engines.sqlite_engine import SQLiteEngine
                return SQLiteEngine(final_database_path)
        elif engine_type == "sqlite":
            from .engines.sqlite_engine import SQLiteEngine
            return SQLiteEngine(final_database_path)
        else:
            logger.error(f"不支持的引擎类型: {engine_type}")
            raise ValueError(f"不支持的引擎类型: {engine_type}")
    
    def _cleanup_temp_database(self):
        """清理临时数据库文件"""
        if self.temp_database_path and os.path.exists(self.temp_database_path):
            try:
                # 先关闭引擎以释放文件锁
                if hasattr(self, 'engine') and self.engine:
                    self.engine.close()
                
                # 删除临时数据库文件
                os.remove(self.temp_database_path)
                logger.info(f"已清理临时数据库文件: {self.temp_database_path}")
            except Exception as e:
                logger.warning(f"清理临时数据库文件失败: {e}")
    
    def add_connector(self, name: str, connector: BaseConnector):
        """
        添加数据库连接器
        
        Args:
            name: 连接器名称
            connector: 连接器实例
        """
        logger.info(f"添加连接器: {name}, 类型: {type(connector).__name__}")
        self.connectors[name] = connector
    
    def load_data(self, connector_name: str, query: str, table_name: str, register: bool = True, **kwargs):
        """
        从指定连接器加载数据
        
        Args:
            connector_name: 连接器名称
            query: SQL查询语句或文件路径
            table_name: 表名称
            register: 是否注册到本地引擎
            **kwargs: 传递给连接器的额外参数
        """
        logger.info(f"从连接器 {connector_name} 加载数据, 表名: {table_name}")
        
        if connector_name not in self.connectors:
            logger.error(f"连接器 {connector_name} 不存在")
            raise ValueError(f"连接器 {connector_name} 不存在")
        
        connector = self.connectors[connector_name]
        # 检查连接器的sql方法是否支持额外参数
        import inspect
        sig = inspect.signature(connector.sql)
        if 'kwargs' in sig.parameters or any(p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values()):
            df = connector.sql(query, table_name, register, **kwargs)
        else:
            df = connector.sql(query, table_name, register)
        
        # 保存到本地表缓存
        self.tables[table_name] = df
        
        # 如果需要注册到本地引擎
        if register:
            logger.info(f"注册表 {table_name} 到本地引擎")
            self.engine.register_table(table_name, df)
        
        logger.info(f"数据加载完成，表名: {table_name}")
        return df
    
    def execute_query(self, query: str, table_name: str = None, register: bool = True):
        """
        在本地引擎中执行SQL查询
        
        Args:
            query: SQL查询语句
            table_name: 表名称，如果提供则将结果注册为表
            register: 是否注册到本地引擎（仅在table_name提供时有效）
        """
        logger.info(f"执行SQL查询: {query}")
        result = self.engine.execute_query(query)
        logger.info("查询执行完成")
        
        # 如果提供了表名，则将结果注册到本地引擎
        if table_name is not None and register:
            logger.info(f"将查询结果注册为表: {table_name}")
            self.engine.register_table(table_name, result)
            # 同时保存到本地表缓存
            self.tables[table_name] = result
        
        return result
    
    def list_tables(self):
        """
        列出所有已注册的表及其基本信息
        
        Returns:
            dict: 包含表信息的字典
        """
        if not self.tables:
            print("没有已注册的表")
            return {}
        
        print("已注册的表:")
        print("=" * 60)
        table_info = {}
        for table_name, df in self.tables.items():
            info = {
                'shape': df.shape,
                'columns': list(df.columns),
                'memory_usage': df.memory_usage(deep=True).sum()
            }
            table_info[table_name] = info
            
            print(f"表名: {table_name}")
            print(f"  形状: {df.shape}")
            print(f"  列名: {list(df.columns)}")
            print(f"  内存占用: {info['memory_usage']} bytes")
            print()
            
        return table_info
    
    def close(self):
        """关闭所有连接和引擎"""
        logger.info("关闭所有连接和引擎")
        
        # 关闭所有连接器
        for name, connector in self.connectors.items():
            logger.info(f"关闭连接器: {name}")
            connector.close()
        
        # 关闭本地引擎
        logger.info("关闭本地引擎")
        self.engine.close()
        
        # 清理临时数据库文件
        self._cleanup_temp_database()
        
        logger.info("所有连接和引擎已关闭")