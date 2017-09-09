#! /usr/bin/env python
# -*- coding: utf-8 -*-
import six


class MetaAdd(type):
    def __new__(mcs, name, bases, namespace):
        return super(MetaAdd, mcs).__new__(mcs, name, bases, namespace)

    def __init__(cls, name, bases, namespace):
        cls._tangle_meta_bases = bases
        cls._tangle_meta_namespace = namespace
        super(MetaAdd, cls).__init__(name, bases, namespace)

    def __add__(self, other):
        namespace = {}
        namespace.update(self._tangle_meta_namespace)
        added = self.__class__("xxx", self._tangle_meta_bases, namespace)
        added.get_test = other.wrap(self.get_test)
        return added


@six.add_metaclass(MetaAdd)
class Desc(object):
    def get_test(self):
        print(self)


class Adder(object):
    def wrap(self, fn):
        def wrapped_fn(inst):
            fn(inst)
            print("after")
            print(self)
        return wrapped_fn


def test_add_class():
    Wrapped = Desc + Adder() + Adder()
    Wrapped().get_test()

