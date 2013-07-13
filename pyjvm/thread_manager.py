#!/usr/bin/env python

from pyjvm.singleton import Singleton
from pyjvm.thread import Thread

class ThreadManager(object):
    __metaclass__ = Singleton

    def create(self):
        return Thread()
