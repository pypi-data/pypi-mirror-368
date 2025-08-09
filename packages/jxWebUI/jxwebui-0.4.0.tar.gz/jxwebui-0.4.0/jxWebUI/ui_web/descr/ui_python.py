#!/usr/bin/python
# -*- coding: UTF-8 -*-

import types
import time
import random
import traceback
from threading import RLock
from multiprocessing import Process

from antlr4 import *
from antlr4.error.ErrorListener import ErrorListener

from jxWebUI.ui_web.jxUtils import logger, transValue2Number

from jxWebUI.ui_web.descr.ui_pythonVisitor import ui_pythonVisitor
from jxWebUI.ui_web.descr.ui_pythonLexer import ui_pythonLexer
from jxWebUI.ui_web.descr.ui_pythonParser import ui_pythonParser
from jxWebUI.ui_web.descr.ui_pythonListener import ui_pythonListener

from antlr4.error.ErrorStrategy import ErrorStrategy, DefaultErrorStrategy

_out_text = None
def get_out():
    global _out_text
    rs =  _out_text
    _out_text = None
    return rs
def set_out(text):
    global _out_text
    if _out_text is None:
        _out_text = text
    else:
        _out_text += '\n' + text

class CustomErrorStrategy(DefaultErrorStrategy):
    def recover(self, recognizer, e):
        # 自定义恢复逻辑
        recognizer.consume()

class jxErrorListener(ErrorListener):
    def __init__(self, str):
        super().__init__()
        self._str = str

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        msg = f'[{self._str}] syntaxError: line:{line}/column:{column}/msg: {msg}'
        raise Exception(msg)

    def reportAmbiguity(self, recognizer, dfa, startIndex, stopIndex, exact, ambigAlts, configs):
        msg = f'[{self._str}] reportAmbiguity: startIndex:{startIndex} stopIndex:{stopIndex}'
        set_out(msg)

    def reportAttemptingFullContext(self, recognizer, dfa, startIndex, stopIndex, conflictingAlts, configs):
        msg = f'[{self._str}] reportAttemptingFullContext: startIndex:{startIndex} stopIndex:{stopIndex}'
        set_out(msg)

    def reportContextSensitivity(self, recognizer, dfa, startIndex, stopIndex, prediction, configs):
        msg = f'[{self._str}] reportContextSensitivity: startIndex:{startIndex} stopIndex:{stopIndex}'
        set_out(msg)

class UIPython(ui_pythonVisitor):
    def __init__(self, tree):
        self.capaInstance = None
        self.sql = None
        self.cs = None
        self._tree = tree

    # Visit a parse tree produced by ui_pythonParser#kv.
    def visitKv(self, ctx:ui_pythonParser.KvContext):
        k = None
        if ctx.VARIABLE() is not None:
            k = ctx.VARIABLE().getText()
        else:
            k = self.visitStringValue(ctx.STRING())
        v = self.parserValue(ctx.value())
        set_out(f'visitKv:[{k}] = {v}')
        return k, v

    def visitJsonObj(self, ctx:ui_pythonParser.JsonObjContext):
        rs = {}
        for kv in ctx.kv():
            k, v = self.visitKv(kv)
            rs[k] = v
        set_out(f'visitJsonObj:{rs}')
        return rs

    def visitJsonArr(self, ctx:ui_pythonParser.JsonArrContext):
        rs = []
        for v in ctx.value():
            rs.append(self.parserValue(v))
        set_out(f'visitJsonArr:{rs}')
        return rs

    def visitJson(self, ctx:ui_pythonParser.JsonContext):
        return self.visitChildren(ctx)

    def visitNumberValue(self, ctx: ui_pythonParser.NumberValueContext):
        ct = ctx.getText()
        return transValue2Number(ct)

    # Visit a parse tree produced by ui_pythonParser#stringValue.
    def visitStringValue(self, ctx: ui_pythonParser.StringValueContext):
        s =  ctx.getText()
        return s[1:-1]

    # Visit a parse tree produced by ui_pythonParser#booleanValue.
    def visitBooleanValue(self, ctx: ui_pythonParser.BooleanValueContext):
        s =  ctx.getText()
        ls = s.lower()
        return ls == 'true'

    # Visit a parse tree produced by ui_pythonParser#variableValue.
    def visitVariableValue(self, ctx: ui_pythonParser.VariableValueContext):
        return ctx.getText()

    def parserValue(self, ctx: ui_pythonParser.ValueContext):
        if isinstance(ctx, ui_pythonParser.NumberValueContext):
            return self.visitNumberValue(ctx)
        if isinstance(ctx, ui_pythonParser.StringValueContext):
            return self.visitStringValue(ctx)
        if isinstance(ctx, ui_pythonParser.BooleanValueContext):
            return self.visitBooleanValue(ctx)
        if isinstance(ctx, ui_pythonParser.VariableValueContext):
            return self.visitVariableValue(ctx)
        if isinstance(ctx, ui_pythonParser.JsonValueContext):
            return self.visitJson(ctx)
        return ''

    def visitComputeOP(self, ctx:ui_pythonParser.ComputeOPContext):
        op = ctx.getText()
        self.cs.appendToken(op, op)

    def visitComputeCol(self, ctx:ui_pythonParser.ComputeColContext):
        ex = ctx.VARIABLE()
        if ex is not None:
            v = ex.getText()
            self.cs.appendToken('var', v)
        else:
            v = ctx.getText()
            self.cs.appendToken('value', v)

    # Visit a parse tree produced by ui_pythonParser#colSingleOP.
    def visitColSingleOP(self, ctx:ui_pythonParser.ColSingleOPContext):
        el = ctx.computeCol()
        l = len(el)
        self.visitComputeCol(el[0])
        for i in range(1, l):
            self.visitComputeOP(ctx.computeOP(i-1))
            self.visitComputeCol(el[i])

    def visitColOPBrackets(self, ctx:ui_pythonParser.ColOPBracketsContext):
        self.cs.appendToken('(', '(')
        el = ctx.computeCol()
        l = len(el)
        self.computeCol(el[0])
        for i in range(1, l):
            self.visitComputeOP(ctx.computeOP(i-1))
            self.computeCol(el[i])
        self.cs.appendToken(')', ')')

    def visitComputeMultiCol(self, ctx:ui_pythonParser.ComputeMultiColContext):
        ex = ctx.colSingleOP()
        if ex is not None:
            self.visitColSingleOP(ex)
        else:
            self.visitColOPBrackets(ctx.colOPBrackets())

    def visitComputeEquality(self, ctx:ui_pythonParser.ComputeEqualityContext):
        el = ctx.computeMultiCol()
        l = len(el)
        self.visitComputeMultiCol(el[0])
        for i in range(1, l):
            self.visitComputeOP(ctx.computeOP())
            self.visitComputeMultiCol(el[i])

    def visitRowCompute(self, ctx:ui_pythonParser.RowComputeContext):
        from jxWebUI.ui_web.descr.computeSequence import computeSequence
        if ctx.ROW() is not None:
            self.cs = computeSequence('preRow')
        else:
            self.cs = computeSequence('alias')
        self.cs.target = ctx.VARIABLE().getText()
        self.visitComputeEquality(ctx.computeEquality())
        self.cs.transToSuffix()
        return self.cs

    def visitColCompute(self, ctx:ui_pythonParser.ColComputeContext):
        from jxWebUI.ui_web.descr.computeSequence import computeSequence
        self.cs = computeSequence('colSum')
        self.cs.target = ctx.VARIABLE().getText()
        self.cs.colName = ctx.sqlAliasCol().getText()
        return self.cs

    def visitComputeStatement(self, ctx:ui_pythonParser.ComputeStatementContext):
        cl = []
        for cx in ctx.computeStyle():
            x = cx.rowCompute()
            if x is not None:
                cs = self.visitRowCompute(x)
                cl.append(cs.toJSON())
            else:
                x = cx.colCompute()
                cs = self.visitColCompute(x)
                cl.append(cs.toJSON())
        set_out(f'visitComputeStatement:{cl}')
        return cl

    def visitAttrStatement(self, ctx: ui_pythonParser.AttrStatementContext):
        vx = ctx.VARIABLE()
        vn = vx.getText()
        v = self.parserValue(ctx.value())
        set_out(f'visitAttrStatement:{vn} = {v}')
        return vn, v

    # Visit a parse tree produced by ui_pythonParser#webStatement.
    def visitWebStatement(self, ctx: ui_pythonParser.WebStatementContext):
        wt = ctx.VARIABLE(0).getText()
        wn = ctx.VARIABLE(1).getText()
        al = {}
        for a in ctx.attrStatement():
            vn, v = self.visitAttrStatement(a)
            al[vn] = v
        from jxWebUI.ui_web.web.wo import WO
        wo = WO(wt, wn, al)
        set_out(f'visitWebStatement:{wt}/{wn}/{al}:{wo}')
        return wo

    # Visit a parse tree produced by ui_pythonParser#tableRowStatement.
    def visitTableRowStatement_my(self, ctx: ui_pythonParser.TableRowStatementContext, table, rowid):
        col = 0
        for a in ctx.webStatement():
            wo = self.visitWebStatement(a)
            self.capaInstance.add_wo(wo)
            table.add_children(wo)
            wo.attrs['rowid'] = rowid
            wo.attrs['col'] = f'c{col}'
            col += 1

    # Visit a parse tree produced by ui_pythonParser#tableStatement.
    def visitTableStatement(self, ctx: ui_pythonParser.TableStatementContext):
        tn = ctx.VARIABLE().getText()
        al = {}
        for a in ctx.attrStatement():
            vn, v = self.visitAttrStatement(a)
            al[vn] = v
        from jxWebUI.ui_web.web.wo import WO
        wo = WO('table', tn, al)
        rowid = 0
        for r in ctx.tableRowStatement():
            self.visitTableRowStatement_my(r, wo, rowid)
            rowid += 1
        return wo

    def visitTableColStatement_my(self, ctx:ui_pythonParser.TableColStatementContext, table):
        cn = ctx.VARIABLE(0).getText()
        head = ctx.VARIABLE(1).getText()
        ct = 'text'
        if ctx.VARIABLE(2) is not None:
            ct = ctx.VARIABLE(2).getText()
        al = {}
        al['head'] = head
        for a in ctx.attrStatement():
            vn, v = self.visitAttrStatement(a)
            al[vn] = v
        from jxWebUI.ui_web.web.wo import WO
        wo = WO(ct, cn, al)
        #
        #数据表的列暂不添加
        #
        #self.capaInstance.add_wo(wo)
        table.add_children(wo)

    def visitDataTableStatement(self, ctx:ui_pythonParser.DataTableStatementContext):
        tn = ctx.VARIABLE().getText()
        al = {}
        for a in ctx.attrStatement():
            vn, v = self.visitAttrStatement(a)
            al[vn] = v
        from jxWebUI.ui_web.web.wo import DataTable
        al['query'] = 'search'
        al['queryParam'] = {'listTable': tn}
        wo = DataTable(tn, al)
        wo.children_is_col = True
        for r in ctx.tableColStatement():
            self.visitTableColStatement_my(r, wo)
        cx = ctx.computeStatement()
        if cx is not None:
            cl = self.visitComputeStatement(cx)
            wo.compSeq = cl
        return wo

    # Visit a parse tree produced by ui_pythonParser#uiPageStatement.
    def visitUiStatement(self, ctx:ui_pythonParser.UiStatementContext):
        tx = ctx.tableStatement()
        if tx is not None:
            return self.visitTableStatement(tx)

        tx = ctx.dataTableStatement()
        if tx is not None:
            return self.visitDataTableStatement(tx)

        return self.visitWebStatement(ctx.webStatement())

    # Visit a parse tree produced by ui_pythonParser#uiPageStatement.
    def visitUiPageStatement(self, ctx:ui_pythonParser.UiPageStatementContext):
        al = {}
        for a in ctx.attrStatement():
            vn, v = self.visitAttrStatement(a)
            al[vn] = v
        rs = []
        for ux in ctx.uiStatement():
            wo = self.visitUiStatement(ux)
            self.capaInstance.add_wo(wo)
            set_out(f'visitUiPageStatement:{ux}:{wo}')
            rs.append(wo)
        cl = None
        cx = ctx.computeStatement()
        if cx is not None:
            cl = self.visitComputeStatement(cx)
        return rs, al, cl

    def getUIPage(self, ci):
        self.capaInstance = ci
        return self.visit(self._tree)

    #
    #sql语句解析
    #
    def visitSqlAliasCol(self, ctx:ui_pythonParser.SqlAliasColContext):
        return ctx.getText()
    def visitSelectCol(self, ctx:ui_pythonParser.SelectColContext):
        return ctx.getText()
    def visitSelectColDef(self, ctx:ui_pythonParser.SelectColDefContext):
        c = self.visitSelectCol(ctx.selectCol())
        v = ctx.VARIABLE()
        if v is not None:
            return f'{c} AS {v}'
        return c

    # Visit a parse tree produced by ui_pythonParser#selectStatementBody.
    def visitSelectStatementBody(self, ctx:ui_pythonParser.SelectStatementBodyContext):
        bs = None
        for sx in ctx.selectColDef():
            c = self.visitSelectColDef(sx)
            if bs is None:
                bs = c
            else:
                bs = f'{bs}, {c}'
        self.sql.set_select_body(bs)

    def visitFromTableDef(self, ctx:ui_pythonParser.FromTableDefContext):
        vl = ctx.VARIABLE()
        if len(vl) == 2:
            return f'{ctx.VARIABLE(0).getText()} AS {ctx.VARIABLE(1).getText()}'
        else:
            return ctx.VARIABLE(0).getText()

    def visitFromStatement(self, ctx:ui_pythonParser.FromStatementContext):
        fs = None
        for sx in ctx.fromTableDef():
            c = self.visitFromTableDef(sx)
            if fs is None:
                fs = f'FROM {c}'
            else:
                fs = f'{fs}, {c}'
        self.sql.set_from(fs)

    def visitConditionStatement(self, ctx:ui_pythonParser.ConditionStatementContext):
        if isinstance(ctx, ui_pythonParser.JxSqlCompareContext):
            c = self.visitSqlAliasCol(ctx.sqlAliasCol())
            vn = ctx.VARIABLE().getText()
            vt = ctx.DATATYPE().getText()
            self.sql.add_condition_var(vn, vt, f'{c} {ctx.op.text}')
            return None
        return ctx.getText()

    # Visit a parse tree produced by ui_pythonParser#sqlWhere.
    def visitWhereStatement(self, ctx:ui_pythonParser.WhereStatementContext):
        ws = None
        for sx in ctx.conditionStatement():
            c = self.visitConditionStatement(sx)
            if c is not None:
                if ws is None:
                    ws = f'WHERE {c}'
                else:
                    ws = f'{ws} AND {c}'
        if ws is not None:
            self.sql.set_where(ws)

    # Visit a parse tree produced by ui_pythonParser#orderByStatement.
    def visitOrderByStatement(self, ctx:ui_pythonParser.OrderByStatementContext):
        cn = self.visitSqlAliasCol(ctx.sqlAliasCol())
        bs = f'ORDER BY {cn}'
        if ctx.sqlDesc() is not None:
            bs = f'{bs} {ctx.sqlDesc().getText()}'
        self.sql.set_order_by(bs)

    def getSQL(self):
        from jxWebUI.ui_web.jx_sql import SQL
        self.sql = SQL()
        self.visit(self._tree)
        return self.sql

    @classmethod
    def SQL(cls, str):
        input_stream = InputStream(str)
        lexer = ui_pythonLexer(input_stream)
        lexer.removeErrorListeners()
        lexer._listeners = [ jxErrorListener(str) ]

        token_stream = CommonTokenStream(lexer)
        parser = ui_pythonParser(token_stream)
        parser.removeErrorListeners()
        parser.addErrorListener(jxErrorListener(str))

        tree = parser.sqlStatement()

        logger.info( f'UIPython 【{str}】：{tree.toStringTree(recog=parser)}')

        return UIPython(tree)

    @classmethod
    def UiPage(cls, str):
        input_stream = InputStream(str)
        lexer = ui_pythonLexer(input_stream)
        lexer.removeErrorListeners()
        lexer._listeners = [ jxErrorListener(str) ]

        token_stream = CommonTokenStream(lexer)
        parser = ui_pythonParser(token_stream)
        parser.removeErrorListeners()
        parser.addErrorListener(jxErrorListener(str))

        tree = parser.uiPageStatement()

        logger.info( f'UIPython 【{str}】：{tree.toStringTree(recog=parser)}')

        return UIPython(tree)
