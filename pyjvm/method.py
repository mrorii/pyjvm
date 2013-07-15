#!/usr/bin/env python

import re
from struct import unpack

import pyjvm.opcode_info
import pyjvm.native

class PyJMethod(object):

    def __init__(self, owner, klass):
        self.owner = owner  # PyJClass that owns this method
        self.klass = klass  # File object
        self.exception_table = []
        self.load()

    def load(self):
        self.access_flag = self._u2()

        self.mname = self.owner.const()[self._u2()]
        self.mdesc = self.owner.const()[self._u2()]

        self.arg_size = self.calc_arg_size()
        self.ret_size = self.calc_ret_size()

        self.max_local = self.arg_size
        self.max_stack = 2

        # attributes (4.7 of jvms7.pdf)
        attributes_count = self._u2()
        for _ in xrange(attributes_count):
            self.load_attributes()

    def load_attributes(self):
        attr_name = self.owner.const()[self._u2()]

        attribute_length = self._u4()

        if attr_name == 'Code':
            self.max_stack = self._u2()
            self.max_local = self._u2()
            self.code_length = self._u4()
            self.code = self.klass.read(self.code_length)

            exception_table_length = self._u2()
            for _ in xrange(exception_table_length):
                start_pc = self._u2()
                end_pc = self._u2()
                handler_pc = self._u2()
                catch_type = self._u2()
                self.exception_table.append([start_pc, end_pc, handler_pc, catch_type])
            attributes_count = self._u2()
            for _ in xrange(attributes_count):
                attr_name = self._u2()
                attr_length = self._u4()
                self.klass.read(attr_length)
        else:
            self.klass.read(attribute_length)

    def __repr__(self):
        return "JavaMethod . {} : {} @ {}".format(self.mname, self.mdesc, self.owner.this_class)

    def verbose(self):
        retval = []
        retval.append('name : {}'.format(self.mname))
        retval.append('type : {}'.format(self.mdesc))
        retval.append('stack: {}'.format(self.max_stack))
        retval.append('local: {}'.format(self.max_local))
        retval.append('len  : {}'.format(self.code_length))
        retval.append('code :')

        if self.is_native():
            retval.append("    : => native method")
            return '\n'.join(retval)

        i = 0
        while i < self.code_length:
            c = self.code[i]
            length = pyjvm.opcode_info.get_opcode_length(c)
            if length == 0:
                length += 1
                length += (4 - (i+1) % 4) % 4
                if c == 0xab:
                    # lookupswitch
                    length += 4
                    pairs = (self.code[i + length] << 24) + \
                            (self.code[i + length + 1] << 16) + \
                            (self.code[i + length + 2] << 8) + \
                            (self.code[i + length + 3])
                    length += 4 + pairs * 2
                else:
                    # tableswitch
                    length += 4
                    low = (self.code[i + length] << 24) + \
                          (self.code[i + length + 1] << 16) + \
                          (self.code[i + length + 2] << 8) + \
                          (self.code[i + length + 3])
                    length += 4
                    high = (self.code[i + length] << 24) + \
                           (self.code[i + length + 1] << 16) + \
                           (self.code[i + length + 2] << 8) + \
                           (self.code[i + length + 3])
                    length += 4

                    length += 4 + (high - low + 1) * 4
            opt = pyjvm.opcode_info.get_opcode_arg(c)
            if opt == 'cc':
                opt = self.owner.const()[(self.code[i+1] << 8) + self.code[i+2]]
            elif opt == 'ii':
                opt = unpack('<h', str(reversed(self.code[i+1, 2])))
            elif opt == '1':
                opt = int(self.code[i+1])

            retval.append("{:4d}\t{} {}".format(i, pyjvm.opcode_info.OPCODE_NAME[c], opt))
            i += length
        return '\n'.join(retval)

    def const(self, idx):
        return self.owner.const()[idx]

    def calc_arg_size(self):
        i = 0
        ret = 0
        lflg = False
        signature = ''
        match = re.search(r'\((.*)\)', self.mdesc)
        if match:
            signature = match.groups()[0]
        for c in signature:
            if lflg:
                if c == ';':
                    lflg = False
                continue

            if c in ('B', 'C', 'F', 'I', 'S', 'Z'):
                ret += 1
            elif c in ('D', 'J'):
                ret += 2
            elif c == 'L':
                ret += 1
                lflg = True

        r = 0 if self.is_static() else 1
        return ret + r

    def calc_ret_size(self):
        match = re.search(r'\(.*\)(.)', self.mdesc)
        if match:
            c = match.groups()[0]
        if c in ('B','C','F','I','S','Z','L','['):
            return 1
        elif c == 'J':
            return 2
        elif c == 'D':
            return 3
        return 0

    def is_static(self):
        return (self.access_flag & 0x008) != 0

    def is_native(self):
        return (self.access_flag & 0x100) != 0

    def invoke_native(self, args):
        pass

    # read helpers
    def _u4(self):
        return unpack('>L', self.klass.read(4))[0]

    def _u2(self):
        return unpack('>H', self.klass.read(2))[0]

    def _u1(self):
        return unpack('B', self.klass.read(1))[0]
