'''
Author: yuweipeng
Date: 2023-01-17 09:58:17
LastEditors: yuweipeng
LastEditTime: 2025-08-12 18:45:00
Description: 数据库工具类（连接字符串通过参数传入，不依赖本地配置）
'''

import csv
import tempfile
import os
from typing import List, Dict, Any, Optional
from contextlib import contextmanager

import pandas as pd
import records
from sqlalchemy import create_engine, text, Engine
from sqlalchemy.orm import sessionmaker, Session


# ================== 工具函数：创建引擎（每次传入 conn_str）==================
def _create_engine(conn_str: str) -> Engine:
    """根据连接字符串创建带优化配置的引擎"""
    return create_engine(
        conn_str,
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=1800,
        pool_pre_ping=True,
        echo=False,
        # 注意：每个 conn_str 创建独立 engine，若频繁调用可考虑缓存
    )


# ================== 上下文管理器：安全获取 Session ==================
@contextmanager
def get_db_session(conn_str: str):
    """
    上下文管理器：自动创建并关闭 session
    :param conn_str: 数据库连接字符串
    """
    engine = _create_engine(conn_str)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
        # 注意：SQLAlchemy 的 dispose 可选，一般不需要频繁调用
        # engine.dispose()  # 若希望立即释放连接池资源可启用


# ================== 查询操作（只读，使用 records + 参数传入 conn_str）==================
def only_query(
    conn_str: str,
    sql: str,
    params: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    执行查询并返回字典列表
    :param conn_str: 数据库连接字符串
    :param sql: SQL 语句（支持 :param 占位符）
    :param params: 参数字典
    :return: 查询结果（list of dict）
    """
    db = records.Database(conn_str, pool_pre_ping=True, pool_size=5)
    try:
        rows = db.query(sql, **(params or {}))
        return rows
    except Exception as e:
        print(f"[ERROR] Query failed: {e}")
        raise
    finally:
        db.close()  # 关闭数据库连接池


# ================== 执行操作（写入：INSERT/UPDATE/DELETE）==================
def exec_sql(
    conn_str: str,
    sql: str,
    params: Optional[Dict[str, Any]] = None
) -> None:
    """
    执行写操作（自动提交或回滚）
    :param conn_str: 数据库连接字符串
    :param sql: SQL 语句
    :param params: 参数字典
    """
    with get_db_session(conn_str) as session:
        compiled_sql = text(sql) if not isinstance(sql, type(text(""))) else sql
        session.execute(compiled_sql, params or {})


# ================== 批量插入（使用临时 CSV 中转）==================
def write_csv_insert_db(
    conn_str: str,
    table_name: str,
    fieldnames: List[str],
    data: List[Dict[str, Any]],
    csv_file: Optional[str] = None,
    batch_size: int = 10000
) -> None:
    """
    将数据写入 CSV 并批量导入数据库
    :param conn_str: 数据库连接字符串
    :param table_name: 目标表名
    :param fieldnames: 字段名列表
    :param data: 数据列表
    :param csv_file: 自定义 CSV 路径（可选）
    :param batch_size: 每批插入行数
    """
    if not data:
        return

    # 使用临时文件避免命名冲突（或使用传入路径）
    temp_file = False
    if not csv_file:
        csv_file = tempfile.mktemp(suffix=".csv")
        temp_file = True

    try:
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)

        engine = _create_engine(conn_str)  # 使用传入的 conn_str 创建 engine

        chunk_iter = pd.read_csv(csv_file, chunksize=batch_size)
        for chunk in chunk_iter:
            chunk.to_sql(
                table_name,
                con=engine,
                if_exists='append',
                index=False,
                method='multi'  # 提高插入效率
            )
    except Exception as e:
        print(f"[ERROR] Failed to insert data: {e}")
        raise
    finally:
        if temp_file and os.path.exists(csv_file):
            os.remove(csv_file)  # 清理临时文件


# ================== 更高效方式：直接使用 Pandas 批量插入（推荐）==================
def bulk_insert_pandas(
    conn_str: str,
    table_name: str,
    data: List[Dict[str, Any]],
    batch_size: int = 10000
) -> None:
    """
    直接将数据转为 DataFrame 插入数据库，无需中间文件
    :param conn_str: 数据库连接字符串
    :param table_name: 表名
    :param data: 数据列表
    :param batch_size: 每批大小
    """
    if not data:
        return

    df = pd.DataFrame(data)
    engine = _create_engine(conn_str)

    try:
        df.to_sql(
            table_name,
            con=engine,
            if_exists='append',
            index=False,
            chunksize=batch_size,
            method='multi'
        )
    except Exception as e:
        print(f"[ERROR] Bulk insert failed: {e}")
        raise


# ================== 使用示例 ==================
if __name__ == '__main__':
    # 示例连接字符串（应由调用方传入，如 API、配置中心、命令行参数等）
    CONN_STR = "mysql+pymysql://root:abc123@11.11.11.11:3306/demo"

    # 1. 查询示例
    sql = "SELECT * FROM ai_workcard_audio WHERE duration > :min_duration LIMIT :limit"
    results = only_query(
        conn_str=CONN_STR,
        sql=sql,
        params={"min_duration": 60, "limit": 5}
    )
    print("Query Results:", results)

    # 2. 写入示例
    sample_data = [
        {"name": "张三", "score": 95},
        {"name": "李四", "score": 87},
    ]
    bulk_insert_pandas(
        conn_str=CONN_STR,
        table_name="test_scores",
        data=sample_data,
        batch_size=5000
    )

    print("✅ 数据插入完成")