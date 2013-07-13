#!/usr/bin/env python

from pyjvm.singleton import Singleton

class ClassManager(object):
    __metaclass__ = Singleton

    def load(self, name):
        print(" loading class --> {}".format(name))
