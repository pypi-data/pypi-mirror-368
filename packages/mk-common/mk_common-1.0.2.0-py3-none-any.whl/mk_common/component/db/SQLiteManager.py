# 文件名: sqlite_manager.py
import sqlite3
import pandas as pd
from typing import List, Optional, Dict, Union, Tuple
from loguru import logger
from pathlib import Path
import os


class SQLiteManager:
    def __init__(self, db_name: str = 'example.db', target_dir: str = r"D:\sqlit_db"):

        # 2. 确保目标文件夹存在（如果不存在则创建）
        Path(target_dir).mkdir(parents=True, exist_ok=True)

        # 2. 确保目标文件夹存在（如果不存在则创建）
        Path(target_dir).mkdir(parents=True, exist_ok=True)
        # 3. 创建数据库文件完整路径
        db_path = os.path.join(target_dir, db_name)

        """
        初始化数据库连接

        :param db_name: 数据库文件名
        """
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

    def create_table(self, table_name: str, columns_def: Union[Dict[str, str], str]):
        """
        创建表（支持传入字典列定义或完整SQL语句）

        :param table_name: 表名
        :param columns_def: 列定义字典或完整的CREATE TABLE SQL语句
        """
        if isinstance(columns_def, dict):
            # 如果是字典，构建CREATE TABLE语句
            columns_sql = ", ".join([f"{col} {dtype}" for col, dtype in columns_def.items()])
            create_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_sql})"
        elif isinstance(columns_def, str):
            # 如果是字符串，直接使用
            create_sql = columns_def
            # 验证表名是否匹配
            if table_name.lower() not in create_sql.lower():
                raise ValueError(f"SQL语句中未包含指定的表名 '{table_name}'")
        else:
            raise TypeError("columns_def 必须是字典或字符串")

        try:
            self.cursor.execute(create_sql)
            self.conn.commit()
            logger.info(f"表 '{table_name}' 创建成功")
            return True
        except sqlite3.Error as e:
            logger.error(f"创建表失败: {e}")
            raise

    def drop_table(self, table_name: str, if_exists: bool = True):
        """
        删除表

        :param table_name: 要删除的表名
        :param if_exists: 是否添加IF EXISTS子句
        :return: 操作是否成功
        """
        if_exists_clause = "IF EXISTS " if if_exists else ""
        drop_sql = f"DROP TABLE {if_exists_clause}{table_name}"

        try:
            self.cursor.execute(drop_sql)
            self.conn.commit()
            logger.info(f"表 '{table_name}' 已成功删除")
            return True
        except sqlite3.Error as e:
            logger.error(f"删除表失败: {e}")
            return False

    def table_exists(self, table_name: str) -> bool:
        """
        检查表是否存在

        :param table_name: 表名
        :return: 表是否存在
        """
        check_sql = f"SELECT name FROM sqlite_master WHERE type='table' AND name=?"
        self.cursor.execute(check_sql, (table_name,))
        return self.cursor.fetchone() is not None

    def create_index(self, table_name: str, columns: Union[str, List[str]],
                     index_name: Optional[str] = None, unique: bool = False,
                     if_not_exists: bool = True):
        """
        创建索引

        :param table_name: 表名
        :param columns: 索引列名（单个或多个）
        :param index_name: 索引名称（可选，自动生成）
        :param unique: 是否创建唯一索引
        :param if_not_exists: 是否添加IF NOT EXISTS子句
        :return: 操作是否成功
        """
        # 处理列名
        if isinstance(columns, str):
            columns = [columns]

        # 生成索引名称（如果未提供）
        if not index_name:
            col_str = '_'.join(columns)
            index_name = f"idx_{table_name}_{col_str}"

        # 构建索引列字符串
        columns_str = ', '.join(columns)

        # 构建CREATE INDEX语句
        unique_str = "UNIQUE" if unique else ""
        if_exists = "IF NOT EXISTS" if if_not_exists else ""
        create_index_sql = (
            f"CREATE {unique_str} INDEX {if_exists} {index_name} "
            f"ON {table_name} ({columns_str})"
        )

        try:
            self.cursor.execute(create_index_sql)
            self.conn.commit()
            logger.info(f"成功创建索引 '{index_name}' 在表 '{table_name}' 的列 {columns}")
            return True
        except sqlite3.OperationalError as e:
            logger.error(f"创建索引失败: {e}")
            return False

    def drop_index(self, index_name: str):
        """
        删除索引

        :param index_name: 索引名称
        :return: 操作是否成功
        """
        drop_sql = f"DROP INDEX IF EXISTS {index_name}"
        try:
            self.cursor.execute(drop_sql)
            self.conn.commit()
            logger.info(f"索引 '{index_name}' 已删除")
            return True
        except sqlite3.Error as e:
            logger.error(f"删除索引失败: {e}")
            return False

    def get_table_info(self, table_name: str) -> pd.DataFrame:
        """
        获取表的列信息

        :param table_name: 表名
        :return: 包含列信息的DataFrame
        """
        return self.query_to_dataframe(f"PRAGMA table_info({table_name})")

    def get_indexes(self, table_name: str) -> pd.DataFrame:
        """
        获取表的索引信息

        :param table_name: 表名
        :return: 包含索引信息的DataFrame
        """
        return self.query_to_dataframe(f"PRAGMA index_list({table_name})")

    def get_index_info(self, index_name: str) -> pd.DataFrame:
        """
        获取索引的详细信息

        :param index_name: 索引名称
        :return: 包含索引详细信息的DataFrame
        """
        return self.query_to_dataframe(f"PRAGMA index_info({index_name})")

    def insert_dataframe(self, df: pd.DataFrame, table_name: str,
                         if_exists: str = 'append', index: bool = False) -> bool:
        """
        将整个DataFrame插入到数据库表中

        :param df: 要插入的DataFrame
        :param table_name: 目标表名
        :param if_exists: {'fail', 'replace', 'append'} 表存在时的处理方式
        :param index: 是否将DataFrame索引作为一列插入
        :return: 操作是否成功
        """
        try:
            # 将DataFrame写入SQLite
            df.to_sql(table_name, self.conn, if_exists=if_exists, index=index)
            logger.info(f"成功插入 {len(df)} 行数据到表 '{table_name}' (模式: {if_exists})")
            return True
        except ValueError as e:
            logger.error(f"插入DataFrame失败: {e}")
            return False

    def insert_record(self, table_name: str, data: dict) -> Optional[int]:
        """
        插入单条记录

        :param table_name: 表名
        :param data: 列名和值的字典
        :return: 新插入行的ID（失败时返回None）
        """
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?'] * len(data))
        insert_sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

        try:
            self.cursor.execute(insert_sql, tuple(data.values()))
            self.conn.commit()
            logger.info(f"插入数据到 {table_name}: {data}")
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            logger.error(f"插入记录失败: {e}")
            return None

    def update_data(self, table_name: str, set_values: dict, condition: str = "") -> int:
        """
        更新数据

        :param table_name: 表名
        :param set_values: 要更新的列和值
        :param condition: WHERE条件语句
        :return: 受影响的行数
        """
        set_clause = ', '.join([f"{k} = ?" for k in set_values.keys()])
        update_sql = f"UPDATE {table_name} SET {set_clause}"

        if condition:
            update_sql += f" WHERE {condition}"

        params = tuple(set_values.values())
        try:
            self.cursor.execute(update_sql, params)
            self.conn.commit()
            affected_rows = self.cursor.rowcount
            logger.info(f"更新表 '{table_name}' {affected_rows} 行记录")
            return affected_rows
        except sqlite3.Error as e:
            logger.error(f"更新数据失败: {e}")
            return 0

    def delete_data(self, table_name: str, condition: str = "") -> int:
        """
        删除数据

        :param table_name: 表名
        :param condition: WHERE条件语句
        :return: 受影响的行数
        """
        delete_sql = f"DELETE FROM {table_name}"
        if condition:
            delete_sql += f" WHERE {condition}"

        try:
            self.cursor.execute(delete_sql)
            self.conn.commit()
            affected_rows = self.cursor.rowcount
            logger.info(f"从表 '{table_name}' 删除 {affected_rows} 行记录")
            return affected_rows
        except sqlite3.Error as e:
            logger.error(f"删除数据失败: {e}")
            return 0

    def query_to_dataframe(self, query: str, params: Tuple = ()) -> pd.DataFrame:
        """
        执行查询并返回DataFrame

        :param query: SQL查询语句
        :param params: 查询参数元组
        :return: 包含查询结果的DataFrame
        """
        try:
            return pd.read_sql_query(query, self.conn, params=params)
        except sqlite3.Error as e:
            logger.error(f"查询失败: {e}")
            return pd.DataFrame()

    def table_to_dataframe(self, table_name: str) -> pd.DataFrame:
        """
        将整个表转换为DataFrame

        :param table_name: 表名
        :return: 包含表数据的DataFrame
        """
        return self.query_to_dataframe(f"SELECT * FROM {table_name}")

    def execute_sql(self, sql: str, params: Tuple = ()) -> int:
        """
        执行任意SQL语句

        :param sql: 要执行的SQL语句
        :param params: 参数元组
        :return: 受影响的行数
        """
        try:
            self.cursor.execute(sql, params)
            self.conn.commit()
            logger.info(f"执行SQL: {sql}")
            return self.cursor.rowcount
        except sqlite3.Error as e:
            logger.error(f"执行SQL失败: {e}")
            return 0

    def close_connection(self):
        """关闭数据库连接"""
        try:
            self.conn.close()
        except sqlite3.Error as e:
            logger.error(f"关闭连接失败: {e}")

    def __enter__(self):
        """支持上下文管理器"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文时自动关闭连接"""
        self.close_connection()
