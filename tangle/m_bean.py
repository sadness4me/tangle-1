#! /usr/bin/env python
# -*- coding: utf-8 -*-
import six


class Field(object):

    def __init__(self, klass, autowire=False):
        super(Field, self).__init__()
        self.klass = klass
        self.autowire = autowire
        self.cb_set = None

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return self.get(obj)

    def __set__(self, obj, value):
        self.set(obj, value)
        if self.cb_set:
            self.cb_set(obj, value)

    def __call__(self, fn):
        self.fn = fn
        self.name = fn.__name__
        return self

    def get(self, inst):
        try:
            self.fn(inst)
            return getattr(inst, "_" + self.name)
        except AttributeError:
            six.raise_from(AttributeError("property (%s) not set yet!" % self.name), None)

    def set(self, inst, value):
        if not isinstance(value, self.klass):
            raise TypeError("set property type (%s) wrong!" % self.klass.__name__)
        setattr(inst, "_" + self.name, value)

    def setter(self, fn):
        self.cb_set = fn
