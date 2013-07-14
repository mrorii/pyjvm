#!/usr/bin/env python

import threading

from pyjvm.singleton import Singleton
import pyjvm.thread

class PyJThreadManager(object):
    __metaclass__ = Singleton

    def __init__(self):
        self.java_threads = []
        self.main = threading.currentThread()

    def create(self):
        t = pyjvm.thread.PyJThread()
        self.java_threads.append(t)
        return t

    def delete(self, t):
        if self.is_empty():
            self.main.start()

    def is_empty(self):
        return len(self.java_threads) == 0
