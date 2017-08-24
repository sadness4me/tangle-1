#! /usr/bin/env python
# -*- coding: utf-8 -*-
import six


class _Field(property):

    def __init__(self, klass, autowire, *args, **kwargs):
        super(_Field, self).__init__(*args, **kwargs)
        self.klass = klass
        self.autowire = autowire


class Field(object):

    def __init__(self, klass, autowire=False):
        super(Field, self).__init__()
        self.klass = klass
        self.autowire = autowire

    def register(self, fn):
        pass
        """
        if self.autowire:
            registry.register(self.klass)
        """

    def __call__(self, fn):
        self.register(fn)

        def _getter(inst):
            try:
                return getattr(inst, "_" + fn.__name__)
            except AttributeError:
                six.raise_from(AttributeError("property (%s) not set yet!" % fn.__name__), None)

        def _setter(inst, value):
            if not isinstance(value, self.klass):
                raise TypeError("set property type (%s) wrong!" % self.klass.__name__)
            setattr(inst, "_" + fn.__name__, value)

        return _Field(self.klass, self.autowire, _getter, _setter)
