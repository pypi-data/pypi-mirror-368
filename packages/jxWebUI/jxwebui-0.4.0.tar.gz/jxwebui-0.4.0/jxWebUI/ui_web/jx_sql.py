#!/usr/bin/python
# -*- coding: UTF-8 -*-

import random
import json
import traceback

from jxWebUI.ui_web.jxUtils import logger, transValue2String, ValueType, StringIsEmpty, asyncExec

_get_db_connection = None
_db_is_custom = False
def set_func_get_db_connection(func, is_custom=False):
    logger.info(f'set_func_get_db_connection')
    global _get_db_connection, _db_is_custom
    _get_db_connection = func
    _db_is_custom = is_custom

class DB_Interface:
    def type(self):
        # 数据库类型
        pass

    def commit(self):
        # 提交数据库事务
        pass

    def rollback(self):
        # 回滚数据库事务
        pass

    def description(self):
        # 回滚数据库事务
        pass

    def execute(self, sql: str):
        # 执行数据库查询语句
        pass

    def fetchone(self) -> dict:
        # jxWebUI会在execute后调用，获取查询结果的单行数据
        pass

    def fetchall(self) -> list:
        # jxWebUI会在execute后调用，获取查询结果的多行数据
        pass

    def trans2String(self, vt: str, v) -> str:
        # 将数据转换为字符串形式
        # string、datetime类型需要添加引号
        # bool类型转换为1、0[根据自己的数据库设计]
        pass

    def __enter__(self):
        # 进入时打开数据库连接
        pass

    def __exit__(self, type, value, trace):
        # 离开时关闭数据库连接
        pass

class DB(DB_Interface):
    def __init__(self, conn):
        self.conn = conn
        self.cursor = None

    def type(self):
        # 数据库类型
        return 'mysql'

    def commit(self):
        if self.conn is not None:
            self.conn.commit()

    def rollback(self):
        if self.conn is not None:
            self.conn.rollback()

    def execute(self, sql):
        return self.cursor.execute(sql)

    def description(self):
        return self.cursor.description

    def fetchone(self):
        return self.cursor.fetchone()

    def fetchall(self):
        return self.cursor.fetchall()

    def trans2String(self, vt, v):
        return transValue2String(vt, v, withQuote=True, to_db=True)

    def __enter__(self):
        if self.conn is not None:
            self.cursor = self.conn.cursor()
            self.conn.begin()
        return self

    def __exit__(self, type, value, trace):
        if self.conn is not None:
            self.cursor.close()
            self.conn.close()

def get_db():
    if _get_db_connection is None:
        return DB_Interface()
    if _db_is_custom:
        return _get_db_connection()
    conn = _get_db_connection()
    return DB(conn)

class SQL:
    def __init__(self):
        self._select = None
        self._from = None
        self._where = None
        self._where_tmp = None
        self._order_by = ' '
        self._condition_var = {}

    def set_select_body(self, str):
        self._select = str
    def set_from(self, str):
        self._from = str
    def set_where(self, str):
        self._where = str
    def set_order_by(self, str):
        self._order_by = str

    def trans2string(self, db, vt, v, op):
        if op.find('like') >= 0:
            v += '%'
            return f'{op} {db.trans2String(vt, v)}'
        return f'{op} {db.trans2String(vt, v)}'
    def get_where(self, db, ci=None):
        if self._where_tmp is not None:
            return self._where_tmp
        if self._where is not None:
            self._where_tmp = self._where
        if ci is not None:
            for vn, (vt, col_op) in self._condition_var.items():
                v = ci.getInput(vn)
                if not StringIsEmpty(v):
                    dv = self.trans2string(db, vt, v, col_op)
                    if self._where_tmp is None:
                        self._where_tmp = f'WHERE {dv}'
                    else:
                        self._where_tmp = f'{self._where_tmp} AND {dv}'
        if self._where_tmp is None:
            self._where_tmp = ' '
        return self._where_tmp

    def add_condition_var(self, var_name, value_type, col_op):
        vt = ValueType.from_string(value_type)
        self._condition_var[var_name] = (vt, col_op)

    def get_sql(self, limit=15, offset=0):
        return f'SELECT {self._select} {self._from} {self._where_tmp} {self._order_by} LIMIT {limit} OFFSET {offset}'

    def get_sql_count(self):
        return f'SELECT COUNT(1) AS totalCount {self._from} {self._where_tmp}'

    def reset_where(self, db, ci=None):
        self._where_tmp = None
        self.get_where(db, ci)

