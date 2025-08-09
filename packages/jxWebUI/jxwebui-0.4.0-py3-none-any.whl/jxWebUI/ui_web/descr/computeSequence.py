#!/usr/bin/python
# -*- coding: UTF-8 -*-

import types
import time
import random
import traceback
from threading import RLock

from enum import Enum

from jxWebUI.ui_web.jxUtils import logger, transValue2Number

class TokenType(Enum):
    var = 'var'
    value = 'value'
    op = 'op'
    leftBracket = '('
    rightBracket = ')'
    @staticmethod
    def from_string(s:str):
        return TokenType[s.lower()]
    @staticmethod
    def to_string(et):
        if et == TokenType.var:
            return 'var'
        if et == TokenType.value:
            return 'value'
        if et == TokenType.op:
            return 'op'
        if et == TokenType.leftBracket:
            return '('
        if et == TokenType.rightBracket:
            return ')'
        return 'unknown'
class Token:
    def __init__(self):
        self.type = None
        self.t = None
        self.v = None
        self.priority = 0

    def toJSON(self):
        return {
            't': self.t,
            'v': self.v,
        }

    def set(self, ty, v):
        self.v = v
        if ty in ['*','/']:
            self.t = 'op'
            self.priority = 1
            self.type = TokenType.op
        elif ty in ['+','-']:
            self.t = 'op'
            self.type = TokenType.op
        elif ty == '(':
            self.priority = -1
            self.type = TokenType.leftBracket
        elif ty == ')':
            self.priority = -1
            self.type = TokenType.rightBracket
        elif ty == 'value':
            self.t = 'value'
            self.type = TokenType.value
        else:
            self.t = 'var'

class computeSequence:
    def __init__(self, type):
        self.type = type
        self.target = None
        self.colName = None
        self.tokens = []

    def transToSuffix(self):
        tl = []
        operators = []
        for t in self.tokens:
            if t.type == TokenType.leftBracket:
                tl.append(t)
            elif t.type == TokenType.rightBracket:
                top = operators.pop()
                while top is not None and top.type != TokenType.leftBracket:
                    tl.append(top)
                    if len(operators) > 0:
                        top = operators.pop()
                    else:
                        top = None
            elif t.type == TokenType.op:
                if len(operators) == 0:
                    operators.append(t)
                else:
                    peek = operators[-1]
                    while len(operators) > 0 and peek.priority >= t.priority:
                        tl.append(operators.pop())
                        if len(operators) > 0:
                            peek = operators[-1]
                        else:
                            break
                    operators.append(t)
            else:
                tl.append(t)
        for t in operators:
            tl.append(t)

        self.tokens = tl

    def toJSON(self):
        tokens = []
        for t in self.tokens:
            tokens.append(t.toJSON())
        cs = {
            'type': self.type,
            'colName': self.colName,
            'target': self.target,
            'tokens': tokens,
        }
        return cs

    def appendToken(self, ty, v):
        t = Token()
        t.set(ty, v)
        self.tokens.append(t)


