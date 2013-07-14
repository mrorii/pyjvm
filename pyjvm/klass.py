#!/usr/bin/env python

from struct import unpack

from pyjvm.instance import PyJInstance
from pyjvm.method import PyJMethod

class PyJClass(object):

    CONSTANT_UTF8 = 1
    CONSTANT_INTEGER = 3
    CONSTANT_FLOAT = 4
    CONSTANT_LONG = 5
    CONSTANT_DOUBLE = 6
    CONSTANT_CLASS = 7
    CONSTANT_STRING = 8
    CONSTANT_FIELDREF = 9
    CONSTANT_METHODREF =10
    CONSTANT_INTERFACEMETHODREF = 11
    CONSTANT_NAMEANDTYPE = 12

    def __init__(self, klass):
        self.java_methods = {}
        self.java_fields = {}
        self.java_static_fields = {}
        self.java_constants = [None]
        self.java_interfaces = []

        self.klass = klass
        self._load()
        self.klass = None

        self.super = None

    def set_super(self, klass):
        self.super = klass

    def const(self):
        return self.java_constants

    def get_static_method(self, name, argtype):
        key = self._method_name_type(name, argtype)
        if key in self.java_methods:
            return self.java_methods[key]
        else:
            if self.super:
                return self.super.get_static_method(name, argtype)
            else:
                raise Exception("No such static method : {}".format(
                    self._method_name_type(name, argtype)))

    def get_method(self, name, argtype):
        key = self._method_name_type(name, argtype)
        if key in self.java_methods:
            return self.java_methods[key]
        else:
            if self.super:
                return self.super.get_method(name, argtype)
            else:
                raise Exception("No such method : {}".format(key))

    def get_static_field(self, name):
        if name in self.java_static_fields:
            return self.java_static_fields[name]
        else:
            if self.super:
                return self.super.get_static_field(name)
            else:
                raise Exception("No such static field : {} @ {}".format(name,
                    self.this_class))

    def set_static_field(self, name, value):
        if name in self.java_static_fields:
            self.java_static_fields[name] = value
        else:
            if self.super:
                self.super.set_static_field(name, value)
            else:
                raise Exception("No such static field : {} @ {}".format(name,
                    self.this_class))

    def create_instance(self):
        return PyJInstance(self)

    def has_clinit(self):
        key = self._method_name_type('<clinit>', '()V')
        return key in self.java_methods

    def _load(self):
        """klass must be a file object in binary mode"""
        # header
        self.magic = self._u4()
        if self.magic != 3405691582:
            # 'cafe babe'
            raise RuntimeError("This file is not a class file")

        self.minor_version = self._u2()
        self.major_version = self._u2()

        # constant pool
        constant_pool_count = self._u2() - 1  # the value is equal to the number of
                                              # entries in the `constant_pool` table
                                              # plus one

        print 'constant_pool_count: {}'.format(constant_pool_count)
        while constant_pool_count > 0:
            constant_pool_count -= self._load_constants()
        self._sort_constants()

        # etc
        self.access_flag = self._u2()
        self.this_class = self.const()[self._u2()]
        self.super_class = self.const()[self._u2()]

        # interfaces
        interface_count = self._u2()
        for _ in xrange(interface_count):
            self._load_interfaces()

        # fields
        fields_count = self._u2()
        for _ in xrange(fields_count):
            self._load_fields()

        # methods
        methods_count = self._u2()
        for _ in xrange(methods_count):
            self._load_methods()

        # attributes
        attributes_count = self._u2()
        for _ in xrange(attributes_count):
            self._load_attributes()

    def _load_constants(self):
        tag = self._u1()
        if tag == self.CONSTANT_UTF8:
            self.java_constants.append([tag, self.klass.read(self._u2())])
        elif tag == self.CONSTANT_INTEGER:
            self.java_constants.append([tag, self._u4()])
        elif tag == self.CONSTANT_FLOAT:
            self.java_constants.append([tag, self._u4()])
        elif tag == self.CONSTANT_LONG:
            self.java_constants.append([tag, self._u4()])
            self.java_constants.append([tag, self._u4()])
            return 2
        elif tag == self.CONSTANT_DOUBLE:
            self.java_constants.append([tag, self._u4()])
            self.java_constants.append([tag, self._u4()])
            return 2
        elif tag == self.CONSTANT_CLASS:
            self.java_constants.append([tag, self._u2()])
        elif tag == self.CONSTANT_STRING:
            self.java_constants.append([tag, self._u2()])
        elif tag == self.CONSTANT_FIELDREF:
            self.java_constants.append([tag, self._u2(), self._u2()])
        elif tag == self.CONSTANT_METHODREF:
            self.java_constants.append([tag, self._u2(), self._u2()])
        elif tag == self.CONSTANT_INTERFACEMETHODREF:
            self.java_constants.append([tag, self._u2(), self._u2()])
        elif tag == self.CONSTANT_NAMEANDTYPE:
            self.java_constants.append([tag, self._u2(), self._u2()])
        else:
            raise RuntimeError("No such type of Constant : {}".format(tag))
        return 1

    def _sort_constants(self):
        consts = self.java_constants
        new_java_constants = []

        for e in self.java_constants:
            if not e:
                continue

            if e[0] in (self.CONSTANT_UTF8, self.CONSTANT_INTEGER, self.CONSTANT_FLOAT,
                        self.CONSTANT_LONG, self.CONSTANT_DOUBLE):
                e = e[1]
            elif e[0] == self.CONSTANT_CLASS:
                e = consts[e[1]][1]
            elif e[0] == self.CONSTANT_STRING:
                e = consts[e[1]][1]
            elif e[0] in (self.CONSTANT_FIELDREF, self.CONSTANT_METHODREF,
                          self.CONSTANT_INTERFACEMETHODREF):
                e = [consts[consts[e[1]][1]][1],
                     consts[consts[e[2]][1]][1],
                     consts[consts[e[2]][2]][1]]
            elif e[0] == self.CONSTANT_NAMEANDTYPE:
                e = [consts[e[1]][1],consts[e[2]][1]]
            else:
                raise RuntimeError("No such type of Constant : {}".format(e[0]))
            new_java_constants.append(e)
        self.java_constants = new_java_constants

    def _load_interfaces(self):
        self.java_interfaces.append(self.const()[self._u2()])

    def _load_fields(self):
        access_flag = self._u2()
        name_index = self._u2()
        descriptor_index = self._u2()
        attributes_count = self._u2()
        first_value = 0
        for _ in xrange(attributes_count):
            attribute_name_index = self._u2()
            attribute_length = self._u4()

            if self.const()[attribute_name_index] == 'ConstantValue':
                constantvalue_index = self._u2()
                first_value = self.const()[constantvalue_index]
            else:
                self._un(attribute_length)
        self.java_fields[self.const()[name_index]] = \
            [access_flag, self.const()[descriptor_index], first_value]
        if access_flag & 0x008:
            # static field
            self.java_static_fields[self.const()[name_index]] = first_value

    def _load_methods(self):
        m = PyJMethod(self, self.klass)
        self.java_methods[self._method_name_type(m.mname, m.mdesc)] = m

    def _method_name_type(self, nm, ty):
        return "{}:{}".format(nm, ty)

    def _load_attributes(self):
        pass

    # read helpers
    def _un(self, n):
        return self.klass.read(n)

    def _u4(self):
        return unpack('>L', self.klass.read(4))[0]

    def _u2(self):
        return unpack('>H', self.klass.read(2))[0]

    def _u1(self):
        return unpack('B', self.klass.read(1))[0]

    def __repr__(self):
        return "{} (super:{})".format(self.this_class, self.super_class)

    def verbose(self):
        retval = ["{} : {}({})".format(self.klass, self.this_class, self.super_class)]

        for i, constant in enumerate(self.java_constans):
            if not c:
                continue
            retval.append("{:4d}\t{}".format(i + 1, constant))

        for key, value in self.java_methods.iteritems():
            retval.append("{}".format(key))
            retval.append("{}".format(v.verbose()))
        return '\n'.join(retval)

    def native_methods(self):
        retval = []
        for v in self.java_methods.itervalues():
            if v.is_native():
                retval.append(v)
        return retval

if __name__ == '__main__':
    import sys
    filename = sys.argv[1]

    with open(filename, 'rb') as f:
        from pyjvm.klass import PyJClass
        klass = PyJClass(f)
        print klass.verbose()
