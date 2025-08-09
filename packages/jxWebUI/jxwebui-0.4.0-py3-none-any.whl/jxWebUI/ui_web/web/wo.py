#!/usr/bin/python
# -*- coding: UTF-8 -*-

import types
import time
import random
import traceback
from threading import RLock

from jxWebUI.ui_web.jxUtils import logger

'''
一个web组件
'''
class WO:
    class Instance:
        def __init__(self, wo, parent_wo, capa_instance):
            self.wo = wo
            self.capa_instance = capa_instance
            if parent_wo is not None and parent_wo.children_is_col:
                self.name = wo.name
            else:
                self.name = f'{capa_instance.id}_{wo.name}'
            self.attrs = wo.attrs.copy()
            self.bind = self.attrs.get('bind',None)
            self.children = {}

        def attr(self, attr, value):
            v = {}
            v['capaid'] = self.capa_instance.id
            v['woID'] = self.name
            v['attr'] = attr
            v['data'] = value
            return v

        def ui(self):
            wo = {}
            wo['capaid'] = self.capa_instance.id
            wo['type'] = self.wo.type
            wo['name'] = self.name
            wo['originalName'] = self.wo.name
            for k, v in self.wo.attrs.items():
                wo[k] = v
            if len(self.wo.children) > 0:
                cn = 'ctls'
                if self.wo.children_is_cs:
                    cn = 'cs'
                sl = []
                wo[cn] = sl
                for v in self.children.values():
                    sl.append(v.ui())
            if self.wo.compSeq is not None:
                wo['compSeq'] = self.wo.compSeq
            return wo

    def __init__(self, type, name, attrs):
        self.type = type
        self.name = name
        self.attrs = attrs
        self.children = {}
        self.children_is_cs = False
        self.children_is_col = False

        self.compSeq = None

        from jxWebUI.ui_web.web.ui import register_wo
        register_wo(self)

    def add_children(self, wo):
        self.children[wo.name] = wo

    def New(self, capa_instance, parent_wo, wo_instance, bind_data, all_wo_instance, all_bind_data):
        wi = WO.Instance(self, parent_wo, capa_instance)
        wo_instance[self.name] = wi
        all_wo_instance[wi.name] = wi
        if 'bind' in self.attrs:
            bind_data[self.attrs['bind']] = wi
            all_bind_data[wi.name] = wi
        for swo in self.children.values():
            si = swo.New(capa_instance, self, wo_instance, bind_data, all_wo_instance, all_bind_data)
            wi.children[swo.name] = si

        capa_instance.wo_instance_wo_name[wi.name] = self
        return wi

class DataTable(WO):
    def __init__(self, name, attrs):
        super().__init__('table', name, attrs)
        self.children_is_cs = True
        self.children_is_col = True

class Div(WO):
    def __init__(self, name, attrs):
        super().__init__('div', name, attrs)
        self.children_is_cs = True


class ShortCutTree:
    class Node:
        def __init__(self, ty, label, **attrs):
            self.type = ty
            self.text = label
            self.attrs = attrs
            self.nodes = {}

    def __init__(self):
        self.nodes = {}

    def toJson(self):
        rs = {}
        ra = []
        rs['out'] = ra
        wo = {}
        ra.append(wo)
        wo['woID'] = 'shortCutTree'
        wo['attr'] = 'treeData'
        ro = {}
        wo['data'] = ro
        nodes = []
        ro['nodes'] = nodes
        for f in self.nodes.values():
            fo = {}
            nodes.append(fo)
            fo['type'] = f.type
            fo['text'] = f.text
            ns = []
            fo['nodes'] = ns
            for n in f.nodes.values():
                no = {}
                ns.append(no)
                no['type'] = n.type
                no['text'] = n.text
                for k, v in n.attrs.items():
                    no[k] = v
        return rs

    def add_item(self, folder, label, **attrs):
        n = self.nodes.get(folder, None)
        if n is None:
            n = ShortCutTree.Node('folder', folder)
            self.nodes[folder] = n
        sn = ShortCutTree.Node('item', label, **attrs)
        n.nodes[label] = sn

    def add_folder(self, label):
        n = ShortCutTree.Node('folder',label)
        self.nodes[label] = n


