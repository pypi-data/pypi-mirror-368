#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sys
import os
import random
import json
import traceback
from threading import RLock

import asyncio
import ssl
import threading
from tornado.options import options
import tornado.ioloop
from tornado.web import RequestHandler, Application
from tornado.httpserver import HTTPServer
import tornado.websocket

import jxWebUI
from jxWebUI.ui_web.jxUtils import logger, Now, CID, get_user, periodicityExec, clearObj, waitClear, get_rsa_decryptor, init_web_log

_ts = 12 * 60 * 60 * 1000

class login(RequestHandler):
    def post(self):
        self.set_header('Server', 'tms/1.0.0')
        try:
            if get_user is None:
                self.set_status(404)
                self.finish({'msg':'none'})
                return

            data = _get_json(self)

            msg = data.get('secret', None)
            if msg is not None:
                d = json.loads(get_rsa_decryptor().decrypt(msg))
                logger.info(f'ui_tms::login:{d}')
                t = d.get('t',None)
                if t is None:
                    self.set_status(404)
                    self.finish({'msg':'none'})
                    return
                ts = Now().timestamp() * 1000
                if ts - t > _ts:
                    self.set_status(404)
                    self.finish({'msg':'none'})
                    return
                user = d.get('Name',None)
                if user is None:
                    self.set_status(404)
                    self.finish({'msg':'none'})
                    return
                pwd = d.get('Passwd',None)
                if pwd is None:
                    self.set_status(404)
                    self.finish({'msg':'none'})
                    return
            else:
                user = data.get('Name',None)
                if user is None:
                    self.set_status(404)
                    self.finish({'msg':'none'})
                    return
                pwd = data.get('Passwd', None)
                if pwd is None:
                    self.set_status(404)
                    self.finish({'msg':'none'})
                    return

            u = get_user(user,pwd)
            if u is None:
                self.set_status(404)
                self.finish({'msg':'none'})
                return
            s = Session(u)
            rs = {
                'jxSessionID': s.id,
                'token': s.token,
            }
            self.set_status(200)
            self.finish(rs)

        except Exception  as e:
            pr = traceback.format_exc()
            logger.error(pr)
            self.set_status(402)
            self.finish({'msg':f'错误的数据格式【{e.__str__()}】'})
            return

_all_session = {}

_lock = RLock()
_wo_name_ui_tms = 'ui_tms'
_interval_session_timeout = 15 * 60

clearObj(_wo_name_ui_tms)

def start_session_timeout_check():
    clearObj(_wo_name_ui_tms)
    wo = mgr()
    waitClear(_wo_name_ui_tms, wo)

class mgr:
    def __init__(self):
        self.scheduler = periodicityExec(60, self.check)

    def check(self):
        logger.info(f'mgr::check session:{len(_all_session)}')
        now = Now().timestamp()
        dl = []
        with _lock:
            for s in _all_session.values():
                if now - s.last_time > _interval_session_timeout:
                    dl.append(s.id)
            for sid in dl:
                s = _all_session.pop(sid, None)
                if s is not None:
                    s.close()

    def clear(self):
        self.scheduler.shutdown(wait=False)

class Session:
    def __init__(self, user):
        self.id = str(CID())
        self.user = user
        self.token = str(random.randint(1000000000,9999999999))
        self.last_time = 0
        from jxWebUI.ui_web.web.ui import UI
        self.ui = UI(user)
        with _lock:
            _all_session[self.id] = self
    def close(self):
        logger.info(f'Session[{self.user.name()}/{self.id}] close')
        with _lock:
            _all_session.pop(self.id, None)
        self.ui.close()

def list_user():
    rs = []
    with _lock:
        for s in _all_session.values():
            rs.append(f'{s.user.name()}/{s.id}')
    return rs

class webSocketHandler(tornado.websocket.WebSocketHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session = None

    def send(self, data):
        self.write_message(data)

    def open(self, *args, **kwargs):
        sID = self.get_query_argument('sid',None)
        token = self.get_query_argument('token',None)
        logger.info(f'ui_tms::webSocketHandler open:{sID} {token}')
        self.session = _all_session.get(sID,None)
        if self.session is None or self.session.token != token:
            logger.info(f'ui_tms::webSocketHandler close')
            self.send({'close':True})
            return
        self.session.ui.ws = self
        self.session.last_time = Now().timestamp()

    def on_message(self, message):
        #jxGo.log('info', f'ui_tms::webSocketHandler on_message:{message}')
        try:
            self.session.last_time = Now().timestamp()
            if message is None:
                return
            data = json.loads(message)
            mi = data.get('mI', None)
            rs = None
            cmd = data.get('c', None)
            if cmd is None:
                return
            if cmd == 'pollData':
                ps = data.get('p', None)
                rs = self.session.ui.receive('pollData', ps)

            elif cmd == 'motion':
                ps = data.get('p', None)
                cn = ps.get('capaname', None)
                t = ps.get('type', None)
                demand = ps.get('demand', None)
                cid = ps.get('capaid', None)
                params = ps.get('params', None)
                logger.info(f'[{cn}.{cid}]motion[{t}.{demand}] params[{params}]')
                rs = self.session.ui.motion(cn, cid, t, demand, params)
                logger.info(f'[{cn}.{cid}]motion[{t}.{demand}] params[{params}]:{rs}')

            elif cmd == 'unloadCapability':
                ps = data.get('p', None)
                logger.info(f'[{self.session.user.name()}.{self.session.id}]unloadCapability:{ps}]')
                cid = ps.get('capaid', None)
                self.session.ui.close_capa_instance(cid)

            elif cmd == 'shortCutTree':
                from jxWebUI.ui_web.web.ui import UI
                rs = UI.shortCutTree_list(self.session.user)
                logger.info(f'shortCutTree:{rs}')

            elif cmd == 'logout':
                logger.info(f'user[{self.session.user.name()}] logout')
                self.close()
                if self.session is not None:
                    self.session.close()

            if rs is not None:
                if mi is not None:
                    rs['mI'] = mi
                self.send(rs)
        except:
            pr = traceback.format_exc()
            logger.error(pr)


    def on_close(self):
        logger.info(f'ui_tms::webSocketHandler on_close')
        #_all_session.pop(self.sessionID,None)


def _get_json(requestHandler):
    data = None
    #headers = requestHandler.request.headers
    #ct = headers.get('Content-Type')
    #print(ct)
    #if ct is not None and ct.startswith('application/json'):
    ms = str(requestHandler.request.body,'utf-8')
    if not ms is None and len(ms) > 0:
        data = json.loads(ms)
    return data

webRoot = jxWebUI.webRoot
logger.info(f'webRoot:{webRoot}')

_restUri_login = r'/ui/login/'
_restUri_ws = r'/ui/ws'
_handlers_routes = [
    (_restUri_login, login),
    (_restUri_ws, webSocketHandler),
    (r"/(.*)", tornado.web.StaticFileHandler, {"path": webRoot}),
]

class server:
    @classmethod
    def _start(cls, port, sslName):
        logger.info(f"web start at {port}")

        init_web_log()
        start_session_timeout_check()

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        app = Application(handlers=_handlers_routes)
        if not sslName is None:
            ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            #ssl_path_crt = f'./crt/{sslName}.crt'
            ssl_path_pem = f'./crt/{sslName}.pem'
            ssl_path_key = f'./crt/{sslName}.key'
            #ssl_ctx.load_cert_chain(certfile=ssl_path_crt, keyfile=ssl_path_key)
            ssl_ctx.load_cert_chain(certfile=ssl_path_pem, keyfile=ssl_path_key)
            http_server = HTTPServer(app, ssl_options=ssl_ctx)
        else:
            http_server = HTTPServer(app)
        http_server.listen(port)

        tornado.ioloop.IOLoop.current().start()

    @classmethod
    def start(cls, port=10028, ssl=None):
        t=threading.Thread(target=server._start,name='webThread',args=[port,ssl])
        t.start()
