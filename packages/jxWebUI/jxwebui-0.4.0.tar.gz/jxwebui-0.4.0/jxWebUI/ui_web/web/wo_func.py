#!/usr/bin/python
# -*- coding: UTF-8 -*-

import types
import json
import time
import random
import traceback
from threading import RLock

from jxWebUI.ui_web.jxUtils import logger, checkAssert, Now, ValueType, list_methods, stringAdd

WebCtlAttrs = {
    'width':{
        'type': ValueType.int,
        'default': 0,
    },
    'title': {
        'type': ValueType.string,
        'default': None,
    },
    'password':{
        'type': ValueType.bool,
        'default': False,
    },
    'placeholder': {
        'type': ValueType.string,
        'default': None,
    },
    'alone':{
        'type': ValueType.bool,
        'default': False,
    },
    'bind': {
        'type': ValueType.string,
        'default': None,
    },
    'header': {
        'type': ValueType.bool,
        'default': True,
    },
    'pagination':{
        'type': ValueType.bool,
        'default': False,
    },
    'newRow': {
        'type': ValueType.bool,
        'default': False,
    },
    'text': {
        'type': ValueType.string,
        'default': None,
    },
    'capaname': {
        'type': ValueType.string,
        'default': None,
    },
    'motion': {
        'type': ValueType.string,
        'default': None,
    },
    'demand': {
        'type': ValueType.string,
        'default': None,
    },
    'color': {
        'type': ValueType.string,
        'default': 'primary',
    },
    'icon': {
        'type': ValueType.string,
        'default': None,
    },
    'iconSize':{
        'type': ValueType.int,
        'default': 2,
    },
    'confirm': {
        'type': ValueType.string,
        'default': None,
    },
    'prompt':{
        'type': ValueType.string,
        'default': None,
    },
    'ignoreCapaid': {
        'type': ValueType.bool,
        'default': False,
    },
    'primary': {
        'type': ValueType.bool,
        'default': False,
    },
    'dispInDialog': {
        'type': ValueType.bool,
        'default': False,
    },
    'params': {
        'type': ValueType.json,
        'default': None,
    },
    'require': {
        'type': ValueType.json,
        'default': None,
    },
    'hide': {
        'type': ValueType.bool,
        'default': False,
    },
    'date': {
        'type': ValueType.bool,
        'default': True,
    },
    'time': {
        'type': ValueType.bool,
        'default': True,
    },
    'minuteStep': {
        'type': ValueType.int,
        'default': 30,
    },
    'initDisp': {
        'type': ValueType.bool,
        'default': True,
    },
    'useText': {
        'type': ValueType.bool,
        'default': False,
    },
    'values':{
        'type': ValueType.json,
        'default': None,
    },
    'value':{
        'type': ValueType.string,
        'default': None,
    },
    'defaultValue':{
        'type': ValueType.string,
        'default': None,
    },
    'group':{
        'type': ValueType.string,
        'default': 'mygroup',
    },
    'chartType':{
        'type': ValueType.string,
        'default': None,
    },
    'labels':{
        'type': ValueType.json,
        'default': None,
    },
    'capa':{
        'type': ValueType.int,
        'default': 10,
    },
    'height':{
        'type': ValueType.int,
        'default': 600,
    },
    'base64Code': {
        'type': ValueType.bool,
        'default': True,
    },
    'showLineNumber': {
        'type': ValueType.bool,
        'default': True,
    },
    'okBtn':{
        'type': ValueType.string,
        'default': None,
    },
}

_id = 0
def get_id():
    global _id
    _id += 1
    return _id

class Values:
    def __init__(self):
        self._values = []

    def append(self, value, text=None):
        if text is None:
            text = value
        self._values.append({
            'value':value,
            'text':text,
        })
        return self

    def to_json(self):
        return self._values

class WebCtl:
    cls_types = {}

    @classmethod
    def register(cls, plugin_cls):
        td = {}
        td['cls'] = plugin_cls
        cls.cls_types[plugin_cls.__name__] = td
        return plugin_cls

    @classmethod
    def is_container(cls, plugin_cls):
        td = cls.cls_types.get(plugin_cls.__name__, None)
        checkAssert(td is not None, f'未注册的类型：{plugin_cls.__name__}')
        td['is_container'] = True
        return plugin_cls

    @classmethod
    def end_with_semicolon(cls, plugin_cls):
        td = cls.cls_types.get(plugin_cls.__name__, None)
        checkAssert(td is not None, f'未注册的类型：{plugin_cls.__name__}')
        td['end_with_semicolon'] = True
        return plugin_cls

    @classmethod
    def Not_include_oneself(cls, plugin_cls):
        td = cls.cls_types.get(plugin_cls.__name__, None)
        checkAssert(td is not None, f'未注册的类型：{plugin_cls.__name__}')
        td['Not_include_oneself'] = True
        return plugin_cls

    @classmethod
    def Not_include_colon(cls, plugin_cls):
        td = cls.cls_types.get(plugin_cls.__name__, None)
        checkAssert(td is not None, f'未注册的类型：{plugin_cls.__name__}')
        td['Not_include_colon'] = True
        return plugin_cls

    @classmethod
    def check_is_web_ctl(cls, name):
        if name not in ['page', 'col']:
            td = cls.cls_types.get(name, None)
            return td is not None
        return False

    @classmethod
    def check_is_container(cls, name):
        td = cls.cls_types.get(name, None)
        if td is not None:
            return td.get('is_container', False)
        return False

    @classmethod
    def check_end_with_semicolon(cls, name):
        td = cls.cls_types.get(name, None)
        if td is not None:
            return td.get('end_with_semicolon', False)
        return False

    @classmethod
    def check_Not_include_colon(cls, name):
        td = cls.cls_types.get(name, None)
        if td is not None:
            return td.get('Not_include_colon', False)
        return False

    @classmethod
    def check_Not_include_oneself(cls, name):
        td = cls.cls_types.get(name, None)
        if td is not None:
            return td.get('Not_include_oneself', False)
        return False

    @classmethod
    def get_cls(cls, name):
        td = cls.cls_types.get(name, None)
        if td is not None:
            return td.get('cls')
        return None

'''
用来函数式定义web组件
'''
class WO_Func:
    '''
    {
        attr:{
            'type': 'type1',
        }
    }
    '''
    pre_define_attrs = []
    def __init__(self, type, name):
        self.type = type
        if isinstance(name, int):
            name = f'{type}__{name}__'
        self.name = name
        self.attrs = {}
        self.children = []

        self._current_attr = None

    def before_attr(self):
        return ''

    def after_attr(self):
        return ''

    def add_sub(self, *args):
        if len(args) == 0:
            wo_name = get_id()
        else:
            wo_name = args[0]
        sc = WebCtl.get_cls(self._current_attr)
        so = sc(wo_name)
        self.children.append(so)
        return so

    def __str__(self):
        ms = f' {self.type} {self.name}'
        sa = ''
        for k, v in self.attrs.items():
            sa = stringAdd(sa, f'{k}={v}', ',')
        if WebCtl.check_Not_include_oneself(self.type):
            rs = f'{self.before_attr()} {sa} {self.after_attr()}'
        else:
            rs = f'{ms} {self.before_attr()} {sa} {self.after_attr()}'
        if len(self.children) > 0:
            t = rs.strip()
            if len(t) > 0:
                if not WebCtl.check_Not_include_colon(self.type):
                    rs += ':'
            for c in self.children:
                rs += str(c)
        if WebCtl.check_end_with_semicolon(self.type):
            rs += ';'
        else:
            rs += ' '
        return rs

    def set_attr_value(self, value):
        ad = WebCtlAttrs.get(self._current_attr, None)
        at = ad.get('type')
        if at == ValueType.string or at == ValueType.datetime:
            self.attrs[self._current_attr] = f'"{str(value)}"'
        elif at == ValueType.int:
            self.attrs[self._current_attr] = int(value)
        elif at == ValueType.float:
            self.attrs[self._current_attr] = float(value)
        elif at == ValueType.bool:
            if isinstance(value, bool):
                if value:
                    self.attrs[self._current_attr] = 'true'
                else:
                    self.attrs[self._current_attr] = 'false'
            else:
                self.attrs[self._current_attr] = str(value)
        elif at == ValueType.json:
            if self._current_attr == 'require':
                l = []
                for v in value:
                    d = {'paramName':v}
                    l.append(d)
                value = l
            self.attrs[self._current_attr] = json.dumps(value)
        else:
            raise Exception(f'不支持的类型：{at}')
        return self

    def __getattr__(self, name):
        if name in self.__class__.pre_define_attrs:
            self._current_attr = name
            return self.set_attr_value
        else:
            if WebCtl.check_is_web_ctl(name):
                checkAssert(WebCtl.check_is_container(self.type), f'web控件[{self.name}]的类型[{self.type}]不是组容器，无法添加：{name}')
                checkAssert(WebCtl.check_is_web_ctl(name), f'web控件[{self.name}]的类型[{self.type}]add 子控件识别：{name}不是web控件')
                self._current_attr = name
                return self.add_sub
            raise Exception(f'web控件[{self.name}]的类型[{self.type}]没有属性：{name}')

#不可见，只供用来创建页面
@WebCtl.Not_include_colon
@WebCtl.Not_include_oneself
@WebCtl.is_container
@WebCtl.register
class page(WO_Func):
    pre_define_attrs = []
    def __init__(self):
        super().__init__('page', '')
        self._okBtn = None
        self.a = None
        self._compute = ''

    def okBtn(self):
        okBtn = get_id()
        self.a = a(okBtn).hide(True)
        self._okBtn = self.a.name
        return self.a

    def before_attr(self):
        if self._okBtn is not None:
            return f'okBtn="{self._okBtn}"'
        return ''

    def __str__(self):
        rs = super().__str__()
        if self.a is not None:
            sa = str(self.a)
            rs += f' web:{sa};'
        if self._compute != '':
            rs += f'compute {self._compute};'
        return rs

    def compute(self, value):
        self._compute += ' ' + value

@WebCtl.is_container
@WebCtl.register
class web(WO_Func):
    pre_define_attrs = [ ]
    def __init__(self):
        super().__init__('web', '')

@WebCtl.Not_include_colon
@WebCtl.register
class col(WO_Func):
    pre_define_attrs = ['text', 'capaname', 'motion', 'width', 'demand', 'hide', 'ignoreCapaid', 'confirm', 'prompt', 'primary', 'dispInDialog', 'params', 'require',]
    def __init__(self, name):
        super().__init__('col', name)
        self.head_str = ''
        self.type_a = ''

    def a(self):
        self.type_a = ' type a'
        return self

    def before_attr(self):
        return f'head {self.head_str}{self.type_a}'

    def head(self, value):
        self.head_str = value
        return self

@WebCtl.end_with_semicolon
@WebCtl.register
class dataTable(WO_Func):
    pre_define_attrs = ['bind', 'title', 'header', 'width', 'pagination', 'newRow',]
    def __init__(self, name):
        super().__init__('dataTable', name)
        self._compute = ''

    def col(self, value):
        c = col(value)
        self.children.append(c)
        return c

    def after_attr(self):
        if self._compute != '':
            return f'compute {self._compute}'
        return ''

    def compute(self, value):
        self._compute = 'pre row ' + value
        return self

@WebCtl.Not_include_colon
@WebCtl.is_container
@WebCtl.register
class row(WO_Func):
    pre_define_attrs = []
    def __init__(self):
        super().__init__('row', '')

@WebCtl.end_with_semicolon
@WebCtl.is_container
@WebCtl.register
class table(WO_Func):
    pre_define_attrs = ['alone', 'title', 'header', 'width',]
    def __init__(self, name):
        super().__init__('table', name)

    def row(self):
        r = row()
        self.children.append(r)
        return r

@WebCtl.register
class text(WO_Func):
    pre_define_attrs = ['text', 'bind', 'width',]
    def __init__(self, name):
        super().__init__('text', name)

@WebCtl.register
class input(WO_Func):
    pre_define_attrs = ['placeholder', 'bind', 'width','password',]
    def __init__(self, name):
        super().__init__('input', name)

@WebCtl.register
class combobox(WO_Func):
    pre_define_attrs = ['values', 'bind', 'width','value','useText',]
    def __init__(self, name):
        super().__init__('combobox', name)
        self.vs = Values()

    def append(self, value, text=None):
        self.vs.append(value, text)
        return self

    def after_attr(self):
        if len(self.vs._values) > 0:
            return f',values={self.vs.to_json()}'
        return ''

@WebCtl.register
class button(WO_Func):
    pre_define_attrs = ['text', 'capaname', 'motion', 'width', 'demand', 'color', 'icon', 'iconSize', 'ignoreCapaid', 'confirm', 'prompt', 'primary', 'dispInDialog', 'params', 'require',]
    def __init__(self, name):
        super().__init__('button', name)

@WebCtl.register
class a(WO_Func):
    pre_define_attrs = ['text', 'capaname', 'motion', 'width', 'demand', 'hide', 'ignoreCapaid', 'confirm', 'prompt', 'primary', 'dispInDialog', 'params', 'require',]
    def __init__(self, name):
        super().__init__('a', name)

@WebCtl.register
class checkbox(WO_Func):
    pre_define_attrs = ['bind', 'width',]
    def __init__(self, name):
        super().__init__('checkbox', name)

@WebCtl.register
class dtpicker(WO_Func):
    pre_define_attrs = ['bind', 'width', 'date', 'time', 'minuteStep', 'initDisp', ]
    def __init__(self, name):
        super().__init__('dtpicker', name)

@WebCtl.register
class radio(WO_Func):
    pre_define_attrs = ['bind', 'width', 'group', 'values', 'defaultValue', ]
    def __init__(self, name):
        super().__init__('radio', name)

@WebCtl.register
class checkboxGroup(WO_Func):
    pre_define_attrs = ['bind', 'width', 'group', 'values', ]
    def __init__(self, name):
        super().__init__('checkboxGroup', name)

@WebCtl.register
class markdown(WO_Func):
    pre_define_attrs = ['bind', 'width', ]
    def __init__(self, name):
        super().__init__('markdown', name)

@WebCtl.register
class chart(WO_Func):
    pre_define_attrs = ['bind', 'width', 'chartType', 'labels', 'color', 'capa', 'height', ]
    def __init__(self, name):
        super().__init__('chart', name)


@WebCtl.register
class textarea(WO_Func):
    pre_define_attrs = ['bind', 'width', 'text', 'base64Code', ]
    def __init__(self, name):
        super().__init__('textarea', name)


@WebCtl.register
class codeEditor(WO_Func):
    pre_define_attrs = ['bind', 'width', 'height', 'showLineNumber', ]
    def __init__(self, name):
        super().__init__('codeEditor', name)




