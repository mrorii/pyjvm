#!/usr/bin/env python

import re

from pyjvm.klass import PyJClass
from pyjvm.singleton import Singleton
from pyjvm.thread import PyJThread

class PyJClassManager(object):
    __metaclass__ = Singleton

    def __initialize__(self):
        self.java_classes = {}

    def load(self, name):
        print(" loading class --> {}".format(name))
        filename = '{}.class'.format(re.sub(r'\.', '/', name))
        c = None
        with open(filename, 'rb') as f:
            c = PyJClass(f)

        self.java_classes[name] = c

        # Deal with super class
        if c.super_class:
            c.set_super(self.get(c.super_class))

        if c.has_clinit():
            clinit_thread = PyJThread()
            clinit_thread.set_clinit(c)
            clinit_thread.interpret()

        return c

    def get(self, name):
        """Gets the class with the name `name`.
        Loads if """
        if name in self.java_classes:
            return self.java_classes[name]
        else:
            return self.load(name)
