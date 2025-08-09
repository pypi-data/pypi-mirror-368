#!/usr/bin/python
# -*- coding: UTF-8 -*-

import re
import base64
import types
import time
import datetime
import random
import traceback
from threading import RLock

from jxWebUI.ui_web.jxUtils import logger, checkAssert, Now, ValueType, base64_encode

'''
手册
'''
class ManualAttr:
    def __init__(self, attr, attr_type, default_value=None):
        self.attr = attr
        self.attr_type = attr_type
        self.default_value = default_value

class ManualDoc:
    def __init__(self, manual_name, doc_txt, name=None, target=None, attrs=None):
        self.manual_name = manual_name
        self.doc_txt = doc_txt
        self.name = name
        self.target = target
        self.attrs = attrs

    def list_attr(self):
        rs = []
        for a in self.attrs:
            rs.append({'attr':a.attr, 'attr_type':a.attr_type, 'default_value':a.default_value})
        return rs

class Manual:
    def __init__(self, name):
        self.name = name
        self.capaname = f'{name}.manual'
        from jxWebUI.ui_web.web.capa import Capa
        self.capa = Capa(self.capaname)
        self.capa.cmd_list['pre_disp_manual'] = self.pre_disp_manual
        self.manuals = {}

        self.current_manual_md_txt = None

        ms = f'table table_markdown header=false,width=1200:\n    row\n        markdown markdown_manual width=900\n;'
        self.capa.add_page('disp_manual', ms, self.disp_manual)

    def disp_manual(self, ci, db, ctx):
        if self.current_manual_md_txt is not None:
            ci.setOutput('markdown_manual', self.current_manual_md_txt)

    def pre_disp_manual(self, ci, db, ctx):
        manual_name = ci.getInput('manual_name')
        mt = self.manuals.get(manual_name)
        checkAssert(mt is not None, f'找不到手册：{manual_name}')
        if mt.doc_txt is not None:
            self.current_manual_md_txt = base64_encode(mt.doc_txt)
        else:
            self.current_manual_md_txt = None

    def add_manual_md(self, folder, name, manual_md_txt, dual_manual_attr=None):
        mn = f'{folder}.{name}'
        self.capa.shortCutTree_add_item(folder, name, 'disp_manual', manual_name=mn)
        target = None
        attrs = None
        if dual_manual_attr is not None:
            target, attrs = dual_manual_attr(manual_md_txt)
            if target is None:
                attrs = None
        self.manuals[mn] = ManualDoc(mn, manual_md_txt, name, target, attrs)

    def shortCutTree_add_item(self, folder, label, demand, authority='common', **attrs):
        self.capa.shortCutTree_add_item(folder, label, demand, authority=authority, **attrs)
