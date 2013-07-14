#!/usr/bin/env python

from struct import unpack

import pyjvm.opcode_info
import pyjvm.native

class PyJMethod(object):

    def __init__(self, owner, klass):
        self.klass = klass
        self.owner = owner
        self.exception_table = []
        self.load()

    def load(self):
        self.access_flag = self._u2()

        self.mname = self.owner.const()[self._u2()]
        self.mdesc = self.owner.const()[self._u2()]

        # TODO
        pass

    def load_attributes(self):
        pass

    def __repr__(self):
        return "JavaMethod . {} : {} @ {}".format(self.mname, self.mdesc, self.owner.this_class)

    def verbose(self):
        pass

    # read helpers
    def _u4(self):
        return unpack('>L', self.klass.read(4))[0]

    def _u2(self):
        return unpack('>H', self.klass.read(2))[0]

    def _u1(self):
        return unpack('B', self.klass.read(1))[0]
