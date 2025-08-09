#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import threading
import types
import time
import random
import datetime
import json
import traceback
from threading import RLock
from decimal import *
from enum import Enum

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
import base64
import pytz

from apscheduler.schedulers.background import BackgroundScheduler

import logging
from logging.handlers import RotatingFileHandler

class ValueType(Enum):
    none = 'none'
    string = 'string'
    int = 'int'
    float = 'float'
    datetime = 'datetime'
    bool = 'bool'
    json = 'json'
    @staticmethod
    def from_string(s:str):
        try:
            return ValueType[s.lower()]
        except:
            return ValueType.none

'''
_func_get_user：
    传入参数：
        user：用户名
        pwd：密码
    返回值：
        用户
用户类要求具有如下的方法：
    #用户名
    def name(self):
        return self.name
    #用户名可能会重复，所以起一个本公司唯一的简称名
    def abbr(self):
        return self.abbr
    #用户所有的角色【包括一级角色，如技术部经理；二级角色，如经理】
    def roles(self):
        return self.roles
'''

class User:
    def __init__(self, name):
        self._name = name
        self._abbr = name
        self._roles = [ ]

    def name(self):
        return self._name
    def abbr(self):
        return self._abbr
    def roles(self):
        return self._roles

_func_get_user = None
def set_func_get_user(func):
    global _func_get_user
    _func_get_user = func
def get_user(user, pwd):
    if _func_get_user is not None:
        return _func_get_user(user, pwd)
    return User(user)


int_Max = 0x7ffffff
tz = pytz.timezone('Asia/Shanghai')

hostID = 1
hostName = 'JingXi'
mask_hostID = (hostID & 0xFFFF) << 48
mask_ts = 0xFFFFFFFF
myID = 0

_LOG_FORMAT = "%(asctime)s [%(filename)s %(lineno)s] - %(levelname)s - %(message)s"
_LOG_maxBytes = 512 * 1024 * 1024
#rolling日志文件的备份数
_LOG_backupCount = 30

private_key_path = '../../secure/privateKey.pem'
_log_name = 'web.log'

_rsa_decryptor = None
def get_rsa_decryptor():
    global _rsa_decryptor
    if _rsa_decryptor is None:
        _rsa_decryptor = RSA_Decryptor(private_key_path)
    return _rsa_decryptor

_allObjCanClear = {}


def _asyncExec(func):
    try:
        func()
    except:
        pr = traceback.format_exc()
        logger.error(pr)
def asyncExec(func):
    threading.Thread(target=_asyncExec, args=[func]).start()

def list_methods(obj):
    return [m for m in dir(obj) if not m.startswith("__")]

def list_methods_cls(cls, mothod_type='instance'):
    import inspect
    all_methods = inspect.getmembers(cls, predicate=inspect.isfunction)
    if mothod_type is None:
        return all_methods
    elif mothod_type == 'instance':
        return {
            name: method
            for name, method in all_methods
            if isinstance(method, types.FunctionType)
            and not name.startswith("__")  # 排除特殊方法
        }
    elif mothod_type == 'classmethod':
        return {
            name: method
            for name, method in all_methods
            if isinstance(method, classmethod)
            and not name.startswith("__")  # 排除特殊方法
        }
    return {
        name: method
        for name, method in all_methods
        if isinstance(method, staticmethod)
        and not name.startswith("__")  # 排除特殊方法
    }


def schedule(func, *args, delay=0, interval=0):
    scheduler = BackgroundScheduler()
    if delay > 0:
        dtnow = datetime.datetime.now()
        dt = dtnow + datetime.timedelta(seconds=delay)
        scheduler.add_job(func, 'date', run_date=dt, args=args, max_instances=2)
    else:
        scheduler.add_job(func, 'interval', seconds=interval, args=args, max_instances=2)
    scheduler.start()
    return scheduler

def stringAdd(str, want, split=','):
    if str is None or len(str) == 0:
        return want
    if want is None or len(want) == 0:
        return str
    return str + split + want

def base64_decode(msg):
    # 将Base64编码的字符串转换为字节形式
    # 将字符串转换为字节格式
    msg_bytes = msg.encode('utf-8')
    encoded_bytes = base64.b64decode(msg_bytes)
    # 将编码的字节形式转换为字符串并返回
    return encoded_bytes.decode('utf-8')

def base64_encode(msg):
    # 将字符串转换为字节格式
    msg_bytes = msg.encode('utf-8')
    # 执行Base64编码
    encoded_bytes = base64.b64encode(msg_bytes)
    # 将编码的字节形式转换为字符串并返回
    return encoded_bytes.decode('utf-8')

def StringIsEmpty(str):
    if str is None:
        return True
    if str == '':
        return True
    if str == 'NaN':
        return True
    return False
def CID():
    global myID
    if myID > int_Max:
        myID = 1
    else:
        myID = myID + 1
    t = time.time()
    ts = int(round(t * 1000))
    return mask_hostID | (((ts >> 10) & mask_ts) << 16) | (myID & 0x0000FFFF)
def Now():
    dt = datetime.datetime.now(tz)
    return dt
def checkAssert(b,msg,*vs):
    if not b:
        if len(vs) == 0:
            raise Exception(msg)
        else:
            raise Exception(msg.format(*vs))
def getLogger(loggerName):
    logger = logging.getLogger(loggerName)
    logger.propagate = False
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(_LOG_FORMAT)
    fh = RotatingFileHandler(f"logs/{loggerName}", maxBytes=_LOG_maxBytes, backupCount=_LOG_backupCount)
    fh.setLevel(logging.INFO)
    fh.setFormatter(formatter)

    logger.addHandler(fh)
    return logger
def periodicityExec(seconds, func, args=None):
    #args是参数列表：
    #delayExec(30,self._startScheduler_timeout,args=[timeOutCheckInterval])
    #_startScheduler_timeout(timeOutCheckInterval)
    scheduler = BackgroundScheduler()
    scheduler.add_job(func, 'interval', seconds=seconds, args=args, misfire_grace_time=10, max_instances=10)
    scheduler.start()
    return scheduler
def waitClear(name, objCanClear):
    logger.info(f'添加可清理对象：{name}')
    co = _allObjCanClear.get(name, None)
    checkAssert(co is None, f'已经添加过可清理对象【{name}')
    _allObjCanClear[name] = objCanClear
def getClearObj(name):
    return _allObjCanClear.get(name, None)
def clearObj(name):
    logger.info(f'清理对象：{name}')
    co = _allObjCanClear.pop(name, None)
    if co is not None:
        co.clear()
def transValue2Number(str):
    try:
        s = str.index('.')
        return float(str)
    except:
        return transValue2Int(str)
def transValue2DateTime(v):
    if isinstance(v, datetime.datetime):
        return v
    sv = str(v)
    try:
        return datetime.datetime.strptime(sv, "%Y-%m-%d %H:%M:%S")
    except:
        try:
            return datetime.datetime.strptime(sv, '%Y-%m-%d')
        except:
            raise Exception(f'数值【{v}】不能转换为日期类型')
def transValue2Int(v):
    if v is None:
        return 0
    try:
        return int(v)
    except:
        return 0
#
#目前只用于sql条件添加，所以送入的值都应该是字符串类型
#
def transValue2String(vt, v, withQuote=False, to_db=False):
    if v is None:
        return None
    if vt == ValueType.bool:
        v = bool(v)
        if to_db:
            if v:
                return '1'
            return '0'
        return '{}'.format(v).lower()
    if vt == ValueType.int:
        v = int(v)
        return '{}'.format(v)
    if vt == ValueType.float:
        v = float(v)
        return '{}'.format(v)
    if vt == ValueType.string or vt == ValueType.datetime:
        v = str(v)
        if withQuote:
            return '\'{}\''.format(v)
        else:
            return v
    return ''


logger = getLogger('jxWebUI.log')

def init_web_log():
    '''
    logger = getLogger(_log_name, level=logging.INFO)
    tornado.log.enable_pretty_logging(logger=logger)
    '''
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler(f"logs/{_log_name}", maxBytes=_LOG_maxBytes, backupCount=_LOG_backupCount)
    gen_log = logging.getLogger("tornado.general")
    gen_log.setLevel(logging.WARNING)
    gen_log.addHandler(file_handler)
    gen_log.propagate = False

    acc_log = logging.getLogger("tornado.access")
    acc_log.setLevel(logging.WARNING)
    acc_log.addHandler(file_handler)
    acc_log.propagate = False

    app_log = logging.getLogger("tornado.application")
    app_log.setLevel(logging.WARNING)
    app_log.addHandler(file_handler)
    app_log.propagate = False

class RSA_Decryptor:
    def __init__(self, private_key_path):
        with open(private_key_path, 'rb') as f:
            self.private_key = RSA.import_key(f.read())
        self.cipher = PKCS1_v1_5.new(self.private_key)

    def decrypt(self, encrypted_str):
        # 处理分段加密
        encrypted_data = base64.b64decode(encrypted_str)
        chunk_size = 128

        decrypted = b''
        for i in range(0, len(encrypted_data), chunk_size):
            chunk = encrypted_data[i:i + chunk_size]
            decrypted += self.cipher.decrypt(chunk, None)

        return decrypted.decode('utf-8')
