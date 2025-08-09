#!/usr/bin/python
# -*- coding: UTF-8 -*-

import types
import time
import datetime
import random
import traceback
from threading import RLock

from apscheduler.schedulers.background import BackgroundScheduler

from jxWebUI.ui_web.jxUtils import logger, checkAssert, Now

'''
web和capa、ctx之间的桥
'''
wo_list = {}
capa_list = {}

def register_wo(wo):
    wo_list[wo.name] = wo
def clear_wo(wo):
    wo_list.pop(wo.name, None)
def register_capa(capa):
    capa_list[capa.name] = capa
def clear_capa(capa):
    capa.clear()
    capa_list.pop(capa.name,None)

_lock = RLock()
_shortCut_by_authid = {}
def get_shortCut_by_authority(authority='common'):
    return _shortCut_by_authid.get(authority, {})

class UI:
    class Timer:
        def __init__(self, name, ui, ci, scheduler, demand, auto_close=True):
            self.name = name
            self.ui = ui
            self.ci = ci
            self.auto_close = auto_close
            self.scheduler = scheduler
            self.demand = demand

        def active(self):
            rs = self.ci.cmd(self.demand)
            self.ui.ws.send(rs)
            if self.auto_close:
                self.ui.close_timer(self.name)

        def close(self):
            self.ui.close_capa_instance(self.ci)
            self.scheduler.shutdown(wait=False)

    @classmethod
    def shortCutTree_add_item(cls, folder, label, capaname, demand, authority='common', **attrs):
        with _lock:
            fn = f'{folder}.{label}'
            sl = _shortCut_by_authid.get(authority, None)
            if sl is None:
                sl = {}
                _shortCut_by_authid[authority] = sl
            d = {}
            sl[fn] = d
            d['folder'] = folder
            d['label'] = label
            d['attrs'] = {
                'capaname': capaname,
                'demand': demand,
                'motion': 'disp',
                'params': attrs
            }

    @classmethod
    def shortCutTree_list(cls, user):
        from jxWebUI.ui_web.web.wo import ShortCutTree
        shortCutTree = ShortCutTree()
        sct_already = {}
        #
        #只分配给该用户的操作权限
        #
        with _lock:
            sl = get_shortCut_by_authority(user.abbr())
            for k, d in sl.items():
                b = sct_already.get(k, False)
                if b:
                    continue
                sct_already[k] = True
                shortCutTree.add_item(d['folder'], d['label'], **d['attrs'])
            #
            #该用户所有角色的操作权限
            #
            rl = user.roles()
            for r in rl:
                sl = get_shortCut_by_authority(r)
                for k, d in sl.items():
                    b = sct_already.get(k, False)
                    if b:
                        continue
                    sct_already[k] = True
                    shortCutTree.add_item(d['folder'], d['label'], **d['attrs'])
            #
            #所有的公共功能
            #
            sl = get_shortCut_by_authority()
            for k, d in sl.items():
                b = sct_already.get(k, False)
                if b:
                    continue
                sct_already[k] = True
                shortCutTree.add_item(d['folder'], d['label'], **d['attrs'])

        return shortCutTree.toJson()

    def __init__(self, user):
        from jxWebUI.ui_web.web.ctx import Ctx
        self.ctx = Ctx(user)
        self.ws = None

        self.all_capa_instance = {}
        self.all_wo_instance = {}

        self.all_bind_data = {}

        self.timer_list = {}

        self._lock_tmp_out = RLock()
        self.tmp_out = []

    def send(self, data):
        with self._lock_tmp_out:
            self.tmp_out.append(data)

    def get_data(self):
        rs = None
        with self._lock_tmp_out:
            if len(self.tmp_out) > 0:
                rs = {'out': self.tmp_out}
                self.tmp_out = []
        return rs

    def close(self):
        for timer in self.timer_list.values():
            timer.close()

    def close_timer(self, timer_name):
        timer = self.timer_list.pop(timer_name, None)
        if timer is not None:
            timer.close()

    def timer_delay(self, timer_name, delay, capaname, demand):
        ci = self.create_capa_instance(capaname)
        dtnow = Now()
        dt = dtnow + datetime.timedelta(seconds=delay)

        scheduler = BackgroundScheduler()
        timer = UI.Timer(timer_name, self, ci, scheduler, demand)

        scheduler.add_job(timer.active, 'date', run_date=dt)
        scheduler.start()

        self.timer_list[timer_name] = timer

    def timer_interval(self, timer_name, delay, capaname, demand):
        ci = self.create_capa_instance(capaname)
        scheduler = BackgroundScheduler()
        timer = UI.Timer(timer_name, self, ci, scheduler, demand, auto_close=False)
        scheduler.add_job(timer.active, 'interval', seconds=delay, max_instances=2)
        scheduler.start()
        self.timer_list[timer_name] = timer

    def disp(self, capa_name, capa_id, page, params):
        if capa_id is not None:
            ci = self.all_capa_instance.get(capa_id, None)
            logger.info(f'ui disp[{capa_id}]{ci is not None}')
            if ci is None:
                return None
        else:
            ci = self.create_capa_instance(capa_name)
        ci.merge(params)
        return ci.disp(page, self.all_wo_instance, self.all_bind_data)

    def create_capa_instance(self, capa_name):
        capa = capa_list.get(capa_name, None)
        checkAssert(capa is not None, f'ui create_capa_instance capa[{capa_name}] not found')
        from jxWebUI.ui_web.web.capa import CapaInstance
        ci = CapaInstance(self, capa)
        logger.info(f'ui create_capa_instance[{capa_name}]:{ci.id}')
        self.all_capa_instance[ci.id] = ci
        return ci

    def motion(self, capaname, capa_id, mt, demand, params):
        logger.info(f'ui motion[{capaname}/{capa_id}] {mt}.{demand}:{params}')
        if mt == 'cmd':
            ci = self.all_capa_instance.get(capa_id, None)
            checkAssert(ci is not None, f'capa not found[{capa_id}]')
            ci.merge(params)
            return ci.cmd(demand)
        elif mt == 'disp':
            return self.disp(capaname, capa_id, demand, params)

        return None

    def receive(self, event, data):
        if event == 'pollData':
            if data is not None:
                for ps in data:
                    woID = ps.get('woID',None)
                    wi = self.all_wo_instance.get(woID, None)
                    if wi is not None:
                        data = ps.get('data',None)
                        if data is not None:
                            if wi.bind is not None:
                                if isinstance(data, dict):
                                    v = data.get('value',None)
                                    if v is not None:
                                        wi.capa_instance.receive(wi.bind, v)
                            else:
                                if isinstance(data, list):
                                    wi.capa_instance.receive(woID, data)

        return self.get_data()

    def close_capa_instance(self, capa_id):
        ci = self.all_capa_instance.pop(capa_id, None)
        logger.info(f'ui close_capa_instance[{capa_id}]{ci is not None}')
        if ci is None:
            return
        ci.close(self.all_wo_instance, self.all_bind_data)

