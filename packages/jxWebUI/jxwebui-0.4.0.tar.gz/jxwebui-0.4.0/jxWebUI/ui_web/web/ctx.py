#!/usr/bin/python
# -*- coding: UTF-8 -*-

import types
import time
import random
import traceback
from threading import RLock

class Ctx:
    def __init__(self, user):
        self.user = user
        self._fullname = None

    def fullname(self):
        if self._fullname is None:
            self._fullname = f'{self.user.name()}_{self.user.abbr()}'
        return self._fullname
