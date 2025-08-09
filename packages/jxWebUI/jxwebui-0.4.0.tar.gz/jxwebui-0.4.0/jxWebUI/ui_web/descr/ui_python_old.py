#!/usr/bin/python
# -*- coding: UTF-8 -*-

import types
import time
import random
import traceback
from threading import RLock
from multiprocessing import Process

from antlr4 import *
from antlr4.InputStream import InputStream
from antlr4.error.ErrorListener import ErrorListener

import nicegui as np
from nicegui import ui
from contextlib import contextmanager

from jx.jxUtils import jxUtils
from jx.jxGo import jxGo

from ui_web.ui_pythonVisitor import ui_pythonVisitor
from ui_web.ui_pythonLexer import ui_pythonLexer
from ui_web.ui_pythonParser import ui_pythonParser
from ui_web.ui_pythonListener import ui_pythonListener

def register_web_ui(ui_name, ui_def_func):
    _web_ui_list[ui_name] = ui_def_func

def _start(port):
    from nicegui import ui
    ui.run(reload=False, native=False, port=port)

def _start2(port):
    from fastapi import FastAPI
    from nicegui import ui
    import uvicorn
    app = FastAPI()
    # 挂载 NiceGUI 到 FastAPI
    ui.run_with(app)
    # 使用 uvicorn 直接启动
    uvicorn.run(app, host='0.0.0.0', port=port)

def _rendering(ui_name, port):
    jxGo.log('info', f'web_config_gui init page:{ui_name}')
    f = _web_ui_list.get(ui_name, None)
    jxUtils.checkAssert(f is not None, f'ui_name not register:{ui_name}')
    f()
    _start2(port)

def rendering(ui_name, port=8080):
    Process(target=_rendering, args=(ui_name,port,)).start()
    jxGo.log('info', f'ui_python rendering:{ui_name}')



def set_func(control, fn, func):
    control.__dict__[fn] = types.MethodType(func, control)

def get_parent_class(obj):
    return obj.__class__.__bases__[0]


#动态容器：对应一个表、一个div这样的一个容器
class WebContainer:
    def __init__(self, name):
        self.name = name
        #本容器所有的控件
        self.items = {}
        #本容器所有的实时数据
        self.data = {}
        #本容器用ui_func声明的函数
        #self.funcs = {}

    def publish(self, str):
        jxGo.log('info', f'ui_python publish:{str}')
        visitor = UIPython.New(str)
        register_web_ui(self.name, lambda :visitor.rendering(self))

    def control(self, name):
        #jxGo.log('info', f'ui_python control[{name}]')
        d = self.items.get(name, None)
        jxUtils.checkAssert(d is not None, f'control[{name}] not register')
        return d

    def update(self, name, item, value):
        #jxGo.log('info', f'ui_python update[{name}.{item}]:{value}')
        d = self.data.get(name, None)
        jxUtils.checkAssert(d is not None, f'data[{name}] not register')
        d.update({
            item: value
        })

    def call(self, fn, *args, **kwargs):
        #jxGo.log('info', f'ui_python call[{fn}]:{args},{kwargs}')
        #用继承的方式来做
        #f = self.funcs.get(fn)
        f = getattr(self, fn, None)
        jxUtils.checkAssert(f is not None, f'func[{fn}] not register')
        f(*args, **kwargs)

    #注册控件函数
    #dc = DynamicContainer()
    #@dc.ui_func
    #def my_label_change(self, text: str) -> None:
    #    print(text)
    #    get_parent_class(self)._handle_text_change(self, text)
    #    if text == 'ok':
    #        self.classes(replace='text-positive')
    #    else:
    #        self.classes(replace='text-negative')
    #
    #然后定义
    #   label 测试 bind=model, bind_name=status, bind_value=error, func=_handle_text_change, func_name=my_label_change
    #
    #def ui_func(self, func):
    #    fn = func.__name__
    #    self.funcs[fn] = func

class jx_button(ui.button):
    pass
class jx_input(ui.input):
    pass
class jx_label(ui.label):
    pass

@contextmanager
def web_button(dynamicContainer, name, attrs):
    text = attrs.get('text', None)
    jxUtils.checkAssert(text is not None, f'button[{name}] must set text')
    func_name = attrs.get('on_click', None)
    jxUtils.checkAssert(func_name is not None, f'button[{name}] must set on_click')
    func = getattr(dynamicContainer, func_name, None)
    jxUtils.checkAssert(func is not None, f'button[{name}] set on_click[{func_name}] not def func')
    conf = {
        'text': text,
    }
    icon = attrs.get('icon', None)
    if icon is not None:
        conf['icon'] = icon
    on_click = lambda e: func(e)
    delay = attrs.get('delay', 0)
    if delay > 0:
        def delay_func(e):
            button.disable()
            func(e)
            time.sleep(delay)
            button.enable()
        on_click = delay_func
    else:
        once = attrs.get('once', None)
        if once is not None:
            def once_func(e):
                button.disable()
                func(e)
            on_click = once_func
    conf['on_click'] = on_click
    button = jx_button(**conf)
    dynamicContainer.items[name] = button

@contextmanager
def web_input(dynamicContainer, name, attrs):
    text = attrs.get('text', None)
    jxUtils.checkAssert(text is not None, f'input[{name}] must set text')
    conf = {
        'label': text,
    }
    placeholder = attrs.get('placeholder', None)
    if placeholder is not None:
        conf['placeholder'] = placeholder
    validation = attrs.get('validation', None)
    if validation is not None:
        func_name = attrs.get('validation_func', None)
        jxUtils.checkAssert(func_name is not None, f'input[{name}] set validation[{validation}] but not set validation_func')
        func = getattr(dynamicContainer, func_name, None)
        jxUtils.checkAssert(func is not None, f'input[{name}] set validation[{validation}] with {func_name} but not register func')
        conf['validation'] = lambda value: func(value)
    func_name = attrs.get('on_change', None)
    if func_name is not None:
        func = getattr(dynamicContainer, func_name, None)
        jxUtils.checkAssert(func is not None, f'input[{name}] set on_change with {func_name} but not register func')
        conf['on_change'] = lambda e: func(e.value)

    dynamicContainer.items[name] = jx_input(**conf)

@contextmanager
def web_label(dynamicContainer, name, attrs):
    text = attrs.get('text', None)
    if text is not None:
        label = jx_label(text)
    else:
        label = jx_label()
    dynamicContainer.items[name] = label
    bind = attrs.get('bind', None)
    if bind is not None:
        bind_name = attrs.get('bind_name', None)
        jxUtils.checkAssert(bind_name is not None, f'label[{name}] set bind[{bind}] but not set bind_name')
        bind_value = attrs.get('bind_value', None)
        jxUtils.checkAssert(bind_value is not None, f'label[{name}] set bind[{bind}] but not set bind_value')
        bd = dynamicContainer.data.get(bind, None)
        if bd is None:
            bd = {}
            bd[bind_name] = bind_value
            dynamicContainer.data[bind] = bd
        label.bind_text_from(dynamicContainer.data[bind], bind_name)
    func_attr = attrs.get('func', None)
    if func_attr is not None:
        func_name = attrs.get('func_name', None)
        jxUtils.checkAssert(func_name is not None, f'label[{name}] set func[{func_attr}] but not set func_name')
        func = getattr(dynamicContainer, func_name, None)
        jxUtils.checkAssert(func is not None, f'label[{name}] set func[{func_attr}] with {func_name} but not register func')
        set_func(label, func_attr, func)

class jxErrorListener(ErrorListener):
    def __init__(self, str):
        super().__init__()
        self._str = str

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        msg = f'[{self._str}] syntaxError: line:{line}/column:{column}/msg: {msg}'
        raise Exception(msg)

    def reportAmbiguity(self, recognizer, dfa, startIndex, stopIndex, exact, ambigAlts, configs):
        raise Exception('reportAmbiguity')

    def reportAttemptingFullContext(self, recognizer, dfa, startIndex, stopIndex, conflictingAlts, configs):
        raise Exception('reportAttemptingFullContext')

    def reportContextSensitivity(self, recognizer, dfa, startIndex, stopIndex, prediction, configs):
        raise Exception('reportContextSensitivity')

class UIPython(ui_pythonVisitor):
    def __init__(self, tree):
        self._tree = tree

    def visitNumberValue(self, ctx: ui_pythonParser.NumberValueContext):
        ct = ctx.getText()
        return jxUtils.transValue2Number(ct)

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
        return ''

    # Visit a parse tree produced by ui_pythonParser#attrStatement.
    def visitAttrStatement(self, ctx: ui_pythonParser.AttrStatementContext):
        vx = ctx.VARIABLE()
        vn = vx.getText()
        v = self.parserValue(ctx.value())
        return vn, v

    # Visit a parse tree produced by ui_pythonParser#webStatement.
    def visitWebStatement(self, ctx: ui_pythonParser.WebStatementContext):
        wt = ctx.VARIABLE(0).getText()
        wn = ctx.VARIABLE(1).getText()
        al = {}
        for a in ctx.attrStatement():
            vn, v = self.visitAttrStatement(a)
            al[vn] = v
        if wt == 'label':
            web_label(self.dynamicContainer, wn, al)
        if wt == 'input':
            web_input(self.dynamicContainer, wn, al)
        if wt == 'button':
            web_button(self.dynamicContainer, wn, al)


    # Visit a parse tree produced by ui_pythonParser#tableRowStatement.
    def visitTableRowStatement(self, ctx: ui_pythonParser.TableRowStatementContext):
        with ui.row():
            for a in ctx.webStatement():
                self.visitWebStatement(a)

    # Visit a parse tree produced by ui_pythonParser#tableStatement.
    def visitTableStatement(self, ctx: ui_pythonParser.TableStatementContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by ui_pythonParser#ui_table.
    def visitUi_table(self, ctx: ui_pythonParser.Ui_tableContext):
        #
        #visitTableStatement
        #
        for r in ctx.tableRowStatement():
            self.visitTableRowStatement(r)

    def rendering(self, dynamicContainer):
        self.dynamicContainer = dynamicContainer
        self.visit(self._tree)

    @classmethod
    def New(cls, str):
        input_stream = InputStream(str)
        lexer = ui_pythonLexer(input_stream)
        lexer.removeErrorListeners()
        lexer._listeners = [ jxErrorListener(str) ]

        token_stream = CommonTokenStream(lexer)
        parser = ui_pythonParser(token_stream)
        parser.removeErrorListeners()
        parser.addErrorListener(jxErrorListener(str))

        tree = parser.uiStatement()

        jxGo.log('info', f'UIPython 【{str}】：{tree.toStringTree(recog=parser)}')

        return UIPython(tree)
