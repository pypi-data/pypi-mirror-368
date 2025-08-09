#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import re

from jxWebUI.ui_web.jxUtils import logger, checkAssert, Now, ValueType, StringIsEmpty, transValue2String

def start_manual_server(port=10068, web_def=False):
    from jxWebUI import docsRoot
    from jxWebUI.ui_web.demo.manual import Manual
    from jxWebUI.ui_web.jxUtils import set_func_get_user

    manual = Manual('jxWebUI')

    class WebControlDef:
        def __init__(self):
            self.capaname = f'WebControlDef'
            from jxWebUI.ui_web.web.capa import Capa
            self.target = None
            self.attrs = None

            self.manual = None
            self.ms = None
            self.appended_attr_num = 0

            self.capa = Capa(self.capaname)
            self.capa.cmd_list['pre_disp_control_def'] = self.pre_disp_control_def
            self.capa.cmd_list['control_def'] = self.control_def

            for doc in manual.manuals.values():
                if doc.target is not None:
                    logger.info(f'WebControlDef shortCutTree_add_item: {doc.name}, {doc.target}, {doc.manual_name}, {doc.list_attr()}')
                    self.capa.shortCutTree_add_item('web组件定义', doc.name, 'disp_control_def', manual_name=doc.manual_name)

        def append_web_def(self, attr, attr_type, default_value=None):
            if self.appended_attr_num % 4 == 0:
                self.ms += f'\n    row\n'
            self.ms += f'        text text_{attr}_tip text="{attr}",width=120\n'
            if attr_type == ValueType.bool:
                self.ms += f'        checkbox cb_{attr} value={default_value},bind="bind_{attr}",width=180\n'
            else:
                self.ms += f'        input input_{attr} bind="bind_{attr}",width=180\n'
            self.appended_attr_num += 1

        def control_def(self, ci, db, ctx):
            cd = f'{self.manual.target} ctl_{self.manual.target} '
            logger.info(f'WebControlDef control_def: {cd}')
            b = False
            for attr in self.manual.attrs:
                av = ci.getInput(f'bind_{attr.attr}')
                av = transValue2String(attr.attr_type, av, True, False)
                logger.info(f'WebControlDef bind_{attr.attr}: {av}')
                if not StringIsEmpty(av):
                    if not b:
                        cd += f' {attr.attr}={av}'
                        b = True
                    else:
                        cd += f',{attr.attr}={av}'

            ci.setOutput_base64('control_def', cd)

            ms = f'table table_control_effect header=false,width=600:row\n {cd};'
            self.capa.add_page('disp_control_effect', ms)
            ci.setAttr('button2', 'enabled', True)

        def pre_disp_control_def(self, ci, db, ctx):
            manual_name = ci.getInput('manual_name')
            self.manual = manual.manuals.get(manual_name)
            checkAssert(self.manual is not None, f'找不到手册：{manual_name}')

            self.appended_attr_num = 0
            self.ms = f'table table_control_def header=false,width=1200,alone=true:'
            for attr in self.manual.attrs:
                self.append_web_def(attr.attr, attr.attr_type, attr.default_value)
            self.ms += f'\n    row\n        button button1 text="生成",width=120,motion=cmd,demand=control_def button button2 text="查看效果",width=120,motion=disp,demand=disp_control_effect,dispInDialog=true '
            self.ms += f'\n    row\n        codeEditor codeEditor1 bind=control_def,width=1200,height=300\n;'
            self.ms += ';'

            logger.info(f'WebControlDef pre_disp_control_def: {self.ms}')

            self.capa.add_page('disp_control_def', self.ms)

    class User:
        def __init__(self, name):
            self._name = name
            self._abbr = name
            self._roles = []

        def name(self):
            return self._name

        def abbr(self):
            return self._abbr

        def roles(self):
            return self._roles

    def get_user(user, pwd):
        return User(user)

    set_func_get_user(get_user)

    regex_target = re.compile(r'#\s+(\S+)')
    regex_attr = re.compile(r'###\s+(\S+)')
    regex_attr_type = re.compile(r'类型：(\S+)')
    regex_attr_default_value = re.compile(r'缺省值：(\S*)')

    def get_attrs(txt):
        from jxWebUI.ui_web.demo.manual import ManualAttr
        from jxWebUI.ui_web.jxUtils import ValueType
        target = None
        attrs = []
        lines = txt.split('\n')
        length = len(lines)
        num = 0
        while num < length:
            line = lines[num]
            m = regex_target.match(line)
            if m is not None:
                target = m.group(1)
            m = regex_attr.match(line)
            if m is not None:
                attr = m.group(1)
                num += 1
                if num >= length:
                    break
                line = lines[num]
                m = regex_attr_type.match(line)
                if m is not None:
                    attr_type = ValueType.from_string(m.group(1))
                    num += 1
                    if num >= length:
                        break
                    line = lines[num]
                    m = regex_attr_default_value.match(line)
                    if m is not None:
                        dv = m.group(1)
                        a = ManualAttr(attr, attr_type, dv)
                        attrs.append(a)
            num += 1
        return target, attrs

    def get_md_files(subdir, get_attrs=None):
        logger.info(f'get_md_files: {subdir}')
        pri = {}
        no_pri = []
        dn = os.path.basename(subdir)
        files = [os.path.join(subdir, f) for f in os.listdir(subdir) if os.path.isfile(os.path.join(subdir, f))]
        for f in files:
            fn = os.path.basename(f)
            n, e = os.path.splitext(fn)
            if e == '.md':
                mf = open(f, 'r')
                mt = mf.read()
                mf.close()
                ss = n.split('.')
                if len(ss) == 2:
                    pri[int(ss[1])] = (dn, ss[0], mt)
                else:
                    no_pri.append((dn, n, mt))
        sl = dict(sorted(pri.items(), key=lambda x: x[0]))
        for dn,n,mt in sl.values():
            logger.info(f'add manual pri: {dn}.{n}')
            manual.add_manual_md(dn, n, mt, get_attrs)
        for dn,n,mt in no_pri:
            logger.info(f'add manual no pri: {dn}.{n}')
            manual.add_manual_md(dn, n, mt, get_attrs)

    subdirs = [os.path.abspath(os.path.join(docsRoot, d))
               for d in os.listdir(docsRoot)
               if os.path.isdir(os.path.join(docsRoot, d))]

    fp = os.path.abspath(os.path.join(docsRoot, '整体说明'))
    sp = os.path.abspath(os.path.join(docsRoot, 'web组件说明'))
    op = os.path.abspath(os.path.join(docsRoot, 'jxORM使用说明'))
    if fp in subdirs:
        get_md_files(fp)
    if sp in subdirs:
        get_md_files(sp, get_attrs=get_attrs)
    if op in subdirs:
        get_md_files(op)
    sl = [s for s in subdirs if s not in [fp, sp]]
    for d in sl:
        get_md_files(d)

    if web_def:
        wcd = WebControlDef()

    from jxWebUI.ui_web.ui_tms import server
    server.start(port)

