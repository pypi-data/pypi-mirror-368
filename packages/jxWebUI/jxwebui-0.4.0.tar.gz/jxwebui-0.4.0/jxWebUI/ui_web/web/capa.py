#!/usr/bin/python
# -*- coding: UTF-8 -*-

import traceback
import datetime

from jxWebUI.ui_web.jxUtils import CID, logger, checkAssert, schedule, StringIsEmpty, transValue2DateTime
'''
本质上是一个web页面【tab】的代理，打通webUI和python间的操作
'''
from collections import namedtuple
BindMapping = namedtuple('BindMapping', ['attr', 'data_name', 'base64', 'table_data'])

_timedelta_one_day = datetime.timedelta(days=1)

class Capa:
    def __init__(self, name):
        self.name = name
        #一个capa可能有0，或多个wo
        #多个一般为一个主页面，然后多个对话框
        self.web_object = {}

        self.disp_list = {}
        self.cmd_list = {}
        self.sql_list = {}
        self.condition_list = {}

        self.data = {}
        self.data_mapping = {}

        self._btn_list = {}

        from jxWebUI.ui_web.web.ui import register_capa
        register_capa(self)

    def add_mapping(self, bind_name, attr, data_name=None, base64=False, table_data=False):
        self.data_mapping[bind_name] = BindMapping(attr, data_name, base64, table_data)

    def _add_page(self, page_name, page_str, page_disp_event=None):
        from jxWebUI.ui_web.descr.ui_python import UIPython
        from jxWebUI.ui_web.web.wo import Div
        up = UIPython.UiPage(page_str)
        wl, al, cl = up.getUIPage(self)
        wo = Div(page_name, al)
        self.add_wo(wo)
        for swo in wl:
            wo.add_children(swo)
            wo.add_children(swo)
        if cl is not None:
            wo.compSeq = cl
        if page_disp_event is not None:
            self.disp_list[page_name] = page_disp_event

    def add_page(self, page_name, page_str, page_disp_event=None):
        from jxWebUI.ui_web.descr.ui_python import get_out
        try:
            self._add_page(page_name, page_str, page_disp_event)
            get_out()
            return None
        except Exception as e:
            es = e.__str__()
            return f'{es}\n\n{get_out()}'

    def btn_list_add(self, page, motion, demand, authority='common', text='显示到对话框中', dispInDialog=True, **attrs):
        page_fullname = f'{self.name}.disp.{page}'
        bf = f'{self.name}.{motion}.{demand}'
        bl = self._btn_list.get(page_fullname, None)
        if bl is None:
            bl = {}
            self._btn_list[page_fullname] = bl
        al = bl.get(authority, None)
        if al is None:
            al = {}
            bl[authority] = al
        al[bf] = attrs
        attrs['type'] = 'a'
        attrs['text'] = text
        attrs['dispInDialog'] = dispInDialog
        attrs['capaname'] = self.name
        attrs['fullname'] = bf
        attrs['demand'] = demand
        attrs['motion'] = motion

    def list_btn(self, page, user):
        rs = []
        page_fullname = f'{self.name}.disp.{page}'
        bl = self._btn_list.get(page_fullname, None)
        if bl is not None:
            al = bl.get(user.abbr(), None)
            if al is not None:
                for v in al.values():
                    rs.append(v)
            rl = user.roles()
            for r in rl:
                al = bl.get(r, None)
                if al is not None:
                    for v in al.values():
                        rs.append(v)
            al = bl.get('common', None)
            if al is not None:
                for v in al.values():
                    rs.append(v)
        if len(rs) == 0:
            return None
        wo = {
            'woID': 'btnList',
            'data': rs
        }
        return wo

    def add_wo(self, wo):
        self.web_object[wo.name] = wo

    def set(self, name, value):
        self.data[name] = value

    def clear(self):
        from jxWebUI.ui_web.web.ui import clear_wo
        for wn in self.web_object.keys():
            clear_wo(wn)

    def shortCutTree_add_item(self, folder, label, demand, authority='common', **attrs):
        from jxWebUI.ui_web.web.ui import UI
        UI.shortCutTree_add_item(folder, label, self.name, demand, authority, **attrs)

    def _call_init(self, init_func):
        from jxWebUI.ui_web.jx_sql import get_db
        db = get_db()
        with db:
            try:
                init_func(self, db)
                db.commit()
            except Exception as e:
                db.rollback()
                raise e
    #
    #下面六个是修饰符
    #
    def sql(self, func):
        try:
            fn = func.__name__
            str = func.__doc__
            from jxWebUI.ui_web.descr.ui_python import UIPython
            up = UIPython.SQL(str)
            sql = up.getSQL()
            self.sql_list[fn] = sql
            self.condition_list[fn] = func
        except:
            pr = traceback.format_exc()
            logger.error(pr)
        return func

    def page(self, func):
        try:
            self._add_page(func.__name__, func.__doc__, func)
        except:
            pr = traceback.format_exc()
            logger.error(pr)
        return func

    def web(self, func):
        '''
        修饰一个函数，这个函数返回一个web页面
        page是用文本来定义一个页面，web则是用函数来定义一个页面
        由于该函数已经被用于定义一个页面，所以如果这个page需要定义初始化换算，则需要先用event修饰一个初始化函数，名称为：disp_函数名
        :param func:
            签名为：func(p:page)
        '''
        try:
            from jxWebUI.ui_web.web.wo_func import page
            p = page()
            func(p)
            fn = func.__name__
            #df = self.disp_list.get(fn, None)
            ps = str(p)
            logger.info(f'capa[{self.name}] web[{fn}]:{ps}')
            self._add_page(fn, ps)
        except:
            pr = traceback.format_exc()
            logger.error(pr)
        return func

    def disp(self, func):
        fn = func.__name__
        self.disp_list[fn] = func
        return func

    def close(self, func):
        self.cmd_list['on_close'] = func
        return func
    #
    #建议改用cmd
    #
    def event(self, func):
        fn = func.__name__
        self.cmd_list[fn] = func
        return func

    def cmd(self, func):
        fn = func.__name__
        if fn == 'Init':
            self._call_init(func)
            return func
        self.cmd_list[fn] = func
        return func

class CapaInstance:
    def __init__(self, ui, capa):
        self.id = f'ca_{CID()}'
        self.capa = capa
        self.ctx = ui.ctx
        self.ui = ui

        self.wo_instance = {}
        self.wo_instance_wo_name = {}

        self.bind_data = {}

        self.data = {}

        self.sql = None
        self._fullname = None

    def read_bind_data(self, orm_obj, bind_name):
        bm = self.capa.data_mapping.get(bind_name, None)
        checkAssert(bm is not None, f'capa[{self.capa.name}] bind_data[{bind_name}] not define')
        if bm.table_data:
            v = self.getInput(bind_name)
        else:
            if bm.base64:
                v = self.getInput_base64(bind_name)
            else:
                v = self.getInput(bind_name)
        if v is None:
            return
        if bm.data_name is not None:
            js = orm_obj.get(bm.attr)
            if js is None:
                js = {}
            js[bm.data_name] = v
            v = js
        orm_obj.set(**{bm.attr: v})

    def disp_bind_data(self, orm_obj, bind_name):
        bm = self.capa.data_mapping.get(bind_name, None)
        checkAssert(bm is not None, f'capa[{self.capa.name}] bind_data[{bind_name}] not define')
        v = orm_obj.get(bm.attr)
        if bm.data_name is not None:
            if v is not None and isinstance(v, dict):
                v = v.get(bm.data_name, None)
            else:
                v = None
        if v is None:
            return
        if bm.table_data:
            self.set_output_datatable(bind_name, v)
        else:
            if bm.base64:
                self.setOutput_base64(bind_name, v)
            else:
                self.setOutput(bind_name, v)

    def read_bind_data_all(self, db, orm_obj):
        for bn in self.capa.data_mapping:
            self.read_bind_data(orm_obj, bn)
        orm_obj.update(db)

    def disp_bind_data_all(self, orm_obj):
        for bn in self.capa.data_mapping:
            self.disp_bind_data(orm_obj, bn)

    def get_capa_data(self, attr):
        return self.capa.data.get(attr, None)

    def set_capa_data(self, attr, value):
        self.capa.data[attr] = value

    def fullname(self):
        if self._fullname is None:
            self._fullname = f'{self.capa.name}_{self.ctx.fullname()}_{self.id}'
        return self._fullname

    def web_set_poll_speed(self, permit_change, interval):
        self.web_control('poll_speed', {'permit_change': permit_change, 'interval': interval})

    def web_control(self, cmd, params):
        out = {
            'woID': 'control',
            'data': {
                'cmd': cmd,
                'params': params,
            }
        }
        self.tmp_out.append(out)

    def web_info(self, title, msg, type='info'):
        out = {
            'woID': 'jxInfoDialog',
            'data': {
                'type': type,
                'title': title,
                'msg': msg
            }
        }
        self.tmp_out.append(out)

    def set_output_chart(self, chart_name, labels:list, *values_list):
        len_labels = len(labels)
        if len_labels == 0:
            return None
        for values in values_list:
            if len(values) != len_labels:
                return False
        arr = []
        i = 0
        for d in labels:
            js = {'label': d}
            arr.append(js)
            vs = []
            js['value'] = vs
            for values in values_list:
                vs.append(values[i])
            i = i+1

        self.setAttr(chart_name, 'tableData', arr)
        return True

    def getInput(self, name):
        return self.data.get(name, None)

    def setAttr(self, name, attr, value, base64=False):
        if base64:
            if isinstance(value, str):
                from jxWebUI.ui_web.jxUtils import base64_encode
                value = base64_encode(value)
        bw = self.bind_data.get(name, None)
        if bw is not None:
            self.data[name] = value
            wo = bw
        else:
            wo = self.wo_instance.get(name, None)
        checkAssert(wo is not None, f'wo[{name}] is not found')
        js = wo.attr(attr, value)
        self.tmp_out.append(js)

    def set_output_datatable(self, name, data_arr):
        #row = 0
        #for r in data_arr:
        #    r['row'] = row
        #    row += 1
        self.setAttr(name, 'tableData', data_arr)

    def clear_datatable(self, name):
        self.setAttr(name, 'clear', True)

    def setOutput(self, name, value):
        self.setAttr(name, 'value', value)

    def setOutput_base64(self, name, value:str):
        if StringIsEmpty(value):
            return
        from jxWebUI.ui_web.jxUtils import base64_encode
        self.setOutput(name, base64_encode(value))

    def getInput_base64(self, name):
        from jxWebUI.ui_web.jxUtils import base64_decode
        bm = self.data.get(name, None)
        if bm is None:
            return None
        return base64_decode(bm)
    #
    #下面是内部函数
    #
    def merge(self, params):
        if params is not None:
            for k, v in params.items():
                self.data[k] = v

    def close(self, all_wo_instance, all_bind_data):
        self.cmd('on_close')
        for wo in self.wo_instance.values():
            all_wo_instance.pop(wo.name, None)
            all_bind_data.pop(wo.name, None)

    def get_tmp_out(self):
        if self.tmp_out is None:
            return None
        return {'out': self.tmp_out}

    def disp(self, name, all_wo_instance, all_bind_data):
        self.cmd(f'pre_{name}')
        wo = self.capa.web_object.get(name, None)
        logger.info(f'capa[{self.fullname()}] disp[{name}]:{wo is not None}')
        if wo is None:
            return None
        wo.New(self, None, self.wo_instance, self.bind_data, all_wo_instance, all_bind_data)
        wi = self.wo_instance.get(name, None)
        rs = wi.ui()
        result = {'wo': rs}
        #如果有初始化函数，则执行
        to = self.cmd(name, True)
        if to is not None:
            result.update(to)

        bl = self.capa.list_btn(name, self.ctx.user)
        if bl is not None:
            bl['capaid'] = self.id
            schedule(lambda :self.ui.send(bl), delay=3)
        return result

    def cmd(self, name, disp=False):
        from jxWebUI.ui_web.jx_sql import get_db
        db = get_db()
        with db:
            try:
                result = self._cmd(db, name, disp=disp)
                db.commit()
                return result
            except Exception as e:
                db.rollback()
                raise e

    def _cmd(self, db, name, disp=False):
        try:
            self.tmp_out = []
            if name == 'reSearch':
                #设置查询条件
                ds = self.getInput('dataSource')
                checkAssert(ds is not None, f'capa[{self.capa.name}.{self.id}] dataSource is None')
                self.sql = self.capa.sql_list.get(ds, None)
                checkAssert(self.sql is not None, f'capa[{self.capa.name}.{self.id}] dataSource[{ds}] not define')

                dt = self.getInput('start_time')
                if not StringIsEmpty(dt):
                    dt = transValue2DateTime(dt)
                    dt = datetime.datetime(dt.year, dt.month, dt.day, 0, 0, 0)
                    self.data['start_time'] = dt.strftime("%Y-%m-%d %H:%M:%S")

                dt = self.getInput('end_time')
                if not StringIsEmpty(dt):
                    dt = transValue2DateTime(dt)
                    dt = dt + _timedelta_one_day
                    dt = datetime.datetime(dt.year, dt.month, dt.day, 0, 0, 0)
                    self.data['end_time'] = dt.strftime("%Y-%m-%d %H:%M:%S")

                self.sql.reset_where(db, self)
                sql = self.sql.get_sql_count()
                logger.info(f'capa[{self.fullname()}] exec sql:{sql}')

                db.execute(sql)
                rs = db.fetchall()
                rs = db.trans_result(rs)[0]
                logger.info(f'capa[{self.fullname()}] exec sql:{rs}')

                tn = rs.get('totalCount', 0)
                self.setOutput('tableTotalCount', tn)

            elif name == 'search':
                #由分页控件查询使用
                checkAssert(self.sql is not None, f'capa[{self.fullname()}] motion:search must used in pagination define')
                limit = self.getInput('limit')
                offset = self.getInput('offset')
                sql = self.sql.get_sql(limit, offset)
                logger.info(f'capa[{self.fullname()}] exec sql:{sql}')

                db.execute(sql)
                rs = db.fetchall()
                rs = db.trans_result(rs)
                logger.info(f'capa[{self.fullname()}] exec sql:{rs}')

                self.set_output_datatable(self.getInput('listTable'), rs)

            else:
                if disp:
                    e = self.capa.disp_list.get(name, None)
                else:
                    e = self.capa.cmd_list.get(name, None)
                logger.info(f'capa[{self.fullname()}] event[{name}]:{e is not None}')
                if e is None:
                    return None
                e(self, db, self.ctx)
        except:
            self.web_info('执行出错', '请联系管理员或开发人员')
            pr = traceback.format_exc()
            logger.error(pr)

        return self.get_tmp_out()

    def receive(self, name, value):
        logger.info(f'capa[{self.fullname()}] receive[{name}]:{value}')
        if isinstance(value, list):
            #数据表的数据
            t = self.wo_instance_wo_name.get(name, None)
            checkAssert(t is not None, f'capa[{self.fullname()}] receive[{name}] is not found')
            td = self.data.get(t.name, None)
            if td is None:
                td = []
                self.data[t.name] = td
            for d in value:
                rowid = d.get('rowid', None)
                rl = [r for r in td if r['rowid'] == rowid]
                if len(rl) == 0:
                    r = {'rowid': rowid}
                    td.append(r)
                else:
                    r = rl[0]
                for k, v in d.items():
                    if k == 'rowid':
                        continue
                    r[k] = v.get('value')
        else:
            self.data[name] = value
            e = self.capa.cmd_list.get(name, None)
            if e is not None:
                self.cmd(name)
