
import os

os.makedirs("logs", exist_ok=True)

from importlib_resources import files

webRoot = files('jxWebUI') / 'web'
docsRoot = files('jxWebUI') / 'docs'


from .ui_web.jxUtils import logger as jxWebLogger
from .ui_web.jxUtils import ValueType as jxValueType
from .ui_web.ui_tms import server as jxWebServer
from .ui_web.web.capa import Capa as jxWebCapa

from .ui_web.web.wo_func import Values as jxWebUIValues

from .ui_web.ui_tms import list_user as jxWebUIListUser

from .ui_web.jxUtils import set_func_get_user as jxWebGetUser
from .ui_web.jx_sql import set_func_get_db_connection as jxWebSQLGetDBConnection

from .ui_web.demo.server import start_manual_server as startJxWebUIManualServer

__all__ = ['jxWebLogger', 'jxValueType', 'jxWebServer', 'jxWebCapa', 'jxWebGetUser', 'jxWebSQLGetDBConnection', 'jxWebUIListUser', 'startJxWebUIManualServer', ]
