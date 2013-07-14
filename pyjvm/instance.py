#!/usr/bin/env python

class PyJInstance(object):
    def __init__(self, owner):
        self.owner = owner
        self.fields = {}
        self._set_fields(owner)

    def __repr__(self):
        pass

    def set_field(self, name, value):
        pass

    def get_field(self, name):
        pass

    def _set_fields(self, cls):
        pass
